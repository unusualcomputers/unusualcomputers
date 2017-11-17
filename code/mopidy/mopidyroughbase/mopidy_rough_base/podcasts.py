import jsonpickle
import urllib
import os
import io
import hashlib
import logging
from feedparsing import CachedFeedParser
from util import *
import pdb
import pathlib
import threading

# configuration

_subscriptions_data='.rough.subscriptions'
_base_path=os.path.join(os.path.expanduser('~'),'.rough')
_n_to_keep=3# TODO: load this from rough settings
_new_to_get=1# TODO: load this from rough settings

_feedparser=CachedFeedParser()
_logger=logging.getLogger('Subscriptions')

def _channel_path(name):
    return os.path.join(_base_path, enc_for_file(name) )
    
def _podcast_path(channel_name,podcast_name):
    cpath=_channel_path(channel_name)
    filename='{}.mp3'.format(enc_for_file(podcast_name))
    return os.path.join(cpath,filename)
        
def _status(description,update_func):
    if update_func is None: return
    update_func(description)

def _download_status(description,update_func,path):
    kb=1024
    mb=1024*kb
    gb=1024*mb
    pattern=" :)"
    
    tm=0.1
    class StatusUpdater():
        # update func takes one argument, a string 
        def __init__(self, description, update_func=None): 
            self.update_func=update_func
            self.description=description
            self.step=0
            self.remaining=None
            self.checked_disk=False
            threading.Timer(tm,self.update).start()
            
        def stop(self):
            self.remaining=-1
                
        def _format_bytes(self,bytes):
            if bytes<0: return '0 bytes'
            if bytes > gb:
                return '{} Gb'.format(int(round(float(bytes)/gb,0)))
            elif bytes > mb:
                return '{} Mb'.format(int(round(float(bytes)/mb,0)))
            elif bytes > kb:
                return '{} Kb'.format(int(round(float(bytes)/kb,0)))
            else:
                return '{} bytes'.format(bytes)

        def update(self, t=None):
            if self.remaining is None:
                rem=''
            elif self.remaining==-1:
                return
            else:
                rem='{} remaining.'.format(
                    self._format_bytes(self.remaining))
            if len(self.description)< (len(rem)+10):
                self.description+=10*' '
            l=(len(self.description)-len(rem))/len(pattern)
            wave=l*pattern
            n=self.step%len(wave)
            w=wave[n:]+wave[:n]
            pad=(len(self.description)-len(rem)-len(wave))*' '
            
            self.step+=1
            msg='{}\n{}{}{}'.format(self.description,rem,pad,w)
            self.update_func(msg)
            if self.remaining!=0:
                threading.Timer(tm,self.update).start()
            else:
                self.update_func(None)
                
        def urllib_response(self, blocks_so_far, block_size_in_bytes, total_bytes):
            if self.update_func is None: return
            bytes_so_far=block_size_in_bytes*blocks_so_far
            if not self.checked_disk:
                self.checked_disk=True
                st = os.statvfs(path)
                free = st.f_bavail * st.f_frsize
                if free < total_bytes:
                    self.remaining=-1
                    status = '{}\nNot enough free disk space!'\
                        .format(self.description)
                    self.update_func(status)
                    raise status
            self.remaining=(total_bytes-bytes_so_far)
            if self.remaining < 0: self.remaining=0

    if update_func is None: return None
    return StatusUpdater(description, update_func)

class Jsonable(object):
    # base class for object that canbe serialised to Json

    def to_json(self):
        return jsonpickle.encode(self)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)      
    
    def __eq__(self,other):
        return self.__dict__==other.__dict__
        
    @classmethod
    def from_json(cls,json_string):
        d=jsonpickle.decode(json_string)
        return d
        
    @classmethod
    def from_file(cls,path):
        f=io.open(path,'r',encoding='utf-8')
        return cls.from_json(f.read())

    def to_file(self,path):
        f=io.open(path,'w',encoding='utf8')
        f.write(unicode(self.to_json()))
    
        
class Podcast(Jsonable):
    def __init__(self,
            name=None,uri=None,guid=None,artist=None,description=None,
            date=None,length=None,image_uri=None,
            channel_uri=None,channel_name=None,keep=False):
        self.uri=uri
        self.guid=guid
        self.name=name
        self.artist=artist
        self.description=description
        self.date=date
        self.length=length
        self.image_uri=image_uri 
        self.channel_uri=channel_uri 
        self.channel_name=channel_name
        self.keep=keep
        if uri is not None:
            self.file_path=self.__get_full_path()
            self.hash=hashlib.sha1(self.uri).digest()
        else:
            self.hash=None
            self.file_path=None
        
    def __get_full_path(self):
        return _podcast_path(self.channel_name,self.name)
    
    def __enrich_mp3(self, path):
        if not path.lower().endswith('mp3'): return 
        
        from mutagen.id3 import ID3NoHeaderError
        from mutagen.id3 import ID3, TIT2, TALB, TPE1, COMM

        # create ID3 tag if not present
        try: 
            tags = ID3(path)
        except ID3NoHeaderError:
            tags = ID3()
        if self.name is not None: 
            tags['TIT2'] = TIT2(encoding=3, text=self.name)
        if self.channel_name is not None: 
            tags['TALB'] = TALB(encoding=3, 
                text=unicode(self.channel_name))
        if self.description is not None:
            frame=COMM(encoding=3, lang=u'eng', 
                desc=u'', text=[unicode(self.description)])
            tags.add(frame)    
        if self.artist is not None:
            tags['TPE1'] = TPE1(encoding=3, text=unicode(self.artist))
        tags.save()
        
    def delete_from_disk(self):
        try:
            os.remove(self.file_path)
        except:
            _logger.error('Failed to delete file {}'.\
                format(self.file_path))
        
    def exists_on_disk(self):
        return file_exists(self.file_path)
        
    def download(self,update_func,response_func=None):
        if self.exists_on_disk(): 
            if response_func is not None: response_func.stop()
            return
        cpath=_channel_path(self.channel_name)
        if not file_exists(cpath): os.mkdir(cpath)
        try:
            urllib.urlretrieve(self.uri.decode('utf-8') ,self.file_path,
                response_func.urllib_response)
        except:
            self.delete_from_disk()
            return
        self.__enrich_mp3(self.file_path)
        _status('Updated',update_func)
        
class Channel(Jsonable):
    def __init__(self,name=None,description=None,uri=None,
            image_uri=None,podcasts=[]):
        self.name=name
        self.description=description
        self.uri=uri
        self.image_uri=image_uri 
        self.podcasts=podcasts
        self.path=self.__get_full_path()

    def __get_full_path(self):
        if self.name is None: return None
        return _channel_path(self.name)
    
    def has(self,podcast):
        p=next((x for x in self.podcasts if x.hash==podcast.hash),None)
        return p is not None
        
    def podcast_by_guid(self,guid,deleted,response_func):
        p=next((x for x in self.podcasts if x.guid==guid),None)
        if p is None:
            self.update(deleted,response_func,False)
            p=next((x for x in self.podcasts if x.guid==guid),None)
        return p

    def update(self,deleted,response_func,ignore_existing = False):
        status='Getting new episodes for {}'.format(enc(self.name))
        _status(status,response_func)
        new_p=_feedparser.update(self.uri.decode('utf-8')).podcasts
        if not ignore_existing:
            new_p=[p for p in new_p if not self.has(p)]        
        self.podcasts=new_p+self.podcasts
        self.podcasts=sorted(self.podcasts,key=lambda p: p.date,reverse=True)

        def downloadable(p):
            return p.hash not in deleted and not p.exists_on_disk()
        
        new_p=[p for p in new_p if downloadable(p)][:_new_to_get]

        i=1
        n=len(new_p)
        ch_path=_channel_path(p.channel_name)
        for p in new_p:
            status='Downloading episode {} ({} of {}).'.format(p.name,i,n)
            i+=1
            updates=_download_status(status,response_func,ch_path)
            p.download(response_func,updates)
        
    def delete_all(self):
        for p in self.podcasts:
            if not p.keep: p.delete_from_disk()
    
    def cleanup(self,to_keep=_n_to_keep):
        for p in self.podcasts:
            if not p.keep and p.exists_on_disk():
                if to_keep==0:
                    p.delete_from_disk()
                to_keep-=1    
        
class Subscriptions(Jsonable):

    @classmethod
    def _config_path(cls):
        return os.path.join(_base_path,_subscriptions_data)
    
    @classmethod
    def load(cls):
        if not file_exists(_base_path):
            os.mkdir(_base_path)
        path=cls._config_path()
        if file_exists(path):
            return cls.from_file(path)
        s=cls()
        s.save()
        return s        

    def save(self):
        full_path=os.path.join(_base_path,_subscriptions_data)        
        self.to_file(full_path)

    def __init__(self,channels=[],deleted=[]):
        self.channels=channels
        self.deleted=deleted
    
    def channel_by_uri(self,uri):
        c=next((x for x in self.channels if x.uri==uri),None)
        if c is not None: return c
        return _feedparser.parse(uri.decode('utf-8') )

    def channel_desc(self,uri):
        c=next((x for x in self.channels if x.uri==uri),None)
        if c is not None: return c.description
        else: return _feedparser.parse_channel_desc(uri.decode('utf-8') )
            
    def channel_by_name(self,name):
        c=next((x for x in self.channels if x.name==name),None)
        return c
        
    def is_subscribed(self,channel_name):
        c=next((x for x in self.channels if x.name==channel_name),None)
        return c is not None

    def is_on_disk(self, channel_name, podcast_name):
        pp=_podcast_path(channel_name,podcast_name)
        return file_exists(pp)
        
    def path_on_disk(self,channel_name,podcast_name):
        fullpath=_podcast_path(channel_name,podcast_name)
        if file_exists(fullpath):
            return pathlib.Path(fullpath).as_uri()
        else:
            return None
    
    def base_path_as_uri(self):
        return path_to_uri(_base_path)

    def has(self,uri):
        c=next((x for x in self.channels if x.uri==uri),None)
        return c is not None
        
    def download_podcasts(self, ugs, update_func,keep=False):
        # ugs is list of pairs (channel uri, podcast guid)
        ugs=[(u,g) for u,g in ugs if u is not None and g is not None]
        i=1
        n=len(ugs)
        for channel_uri,podcast_guid in ugs:
            c=self.channel_by_uri(channel_uri)
            p=c.podcast_by_guid(podcast_guid,self.deleted,update_func)
            status='Downloading episode {} ({} of {})'.format(p.name,i,n)
            i+=1
            if keep: p.keep=True
            updates=_download_status(status,update_func,
                _channel_path(p.channel_name))
            p.download(update_func,updates)
        
    def keep_podcasts(self, ugs, update_func):
        self.download_podcasts(ugs,update_func,True)
        
    def delete_podcasts(self,name_pairs,update_func=None):
        # name_pairs is list of pairs (channel name, podcast name)
        name_pairs=[(u,g) for u,g in name_pairs if u is not None and g is not None]
        i=1
        n=len(name_pairs)
        for channel_name,podcast_name in name_pairs:
            status='Deleting episode {} ({} of {})'.format(podcast_name,i,n)
            _status(status,update_func)
            i+=1
            c=self.channel_by_name(channel_name)
            if c is None:
                path=_podcast_path(channel_name,podcast_name)
                try:
                    os.remove(path)
                except:
                    _logger.error('Failed to delete file {}'.\
                        format(pat))
                continue
            p=next((x for x in c.podcasts if x.name==podcast_name),None)
            if p is None or not p.exists_on_disk(): continue
            p.delete_from_disk()
            h=p.hash
            if not h in self.deleted: self.deleted.append(h)
        self.save()
        _status('Updated',update_func)
    
            
    def subscribe(self,channel_uris,update_func=None):
        for uri in channel_uris:
            if self.has(uri): 
                _logger.warn('Alredy subscribed to {}'.format(uri)) 
                continue
            status='Subscribing to {}'.format(uri)
            _status(status,update_func)
            c = self.channel_by_uri(uri)
            if c is None:
                status='Channel not found\n{} '.format(uri)
                _status(status,update_func)
                continue
            c.update(self.deleted,update_func,True)
            self.channels.append(c)
            self.save()
            _status(None,update_func)    
    
    def unsubscribe(self,channel_uris,update_func=None):
        for uri in channel_uris:
            c=next((x for x in self.channels if x.uri==uri),None)
            if c is None: 
                _logger.warn('Not subscribed to {}'.format(uri)) 
                continue
            status='Deleting podcasts for {}'.format(c.name)
            _status(status,update_func)
            for p in c.podcasts:
                if p.hash in self.deleted:
                    self.deleted.remove(p.hash)
            c.delete_all()
            if not os.listdir(c.path):
                os.rmdir(c.path)
            self.channels=[ch for ch in self.channels if ch.uri!=uri]
            self.save()
            _status(None,update_func)
    
    def update(self,channel_uris, update_func=None):
        _feedparser.clear()
        if channel_uris==[]:
            channels=self.channels
        else:
            channels=[ch for ch in self.channels \
                if ch.uri in channel_uris]
        for c in channels:
            c.cleanup()
            c.update(self.deleted,update_func)
        self.save()
        _status(None,update_func)
