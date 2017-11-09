from mopidy.models import Ref
from mopidy_known_schemes import *
from mopidy_play_control import MopidyPlayControl
from mopidy_search import MopidySearch,RefWithData,make_ref 
import logging
import urlparse
import os
import urllib
from podcasts import Subscriptions
from favourites import Favourites
from util import *
import threading
import pdb

# interface to mopidy used by various rough front ends

# some refs and uris are created by us, makes browsing easier
_subscriptions_ref=Ref.directory(name = 'Subscriptions',
            uri = 'podcast+subscriptions')
_favourites_ref=Ref.directory(name = 'Favourites',
            uri = 'rough+favourites')
_queue_ref=Ref.directory(name = 'Queue',
            uri = 'rough+queue')
_history_ref=Ref.directory(name = 'History',
            uri = 'rough+history')
_youtube_ref=Ref.directory(name = 'YouTube (searching)',
            uri = 'youtube:')
_channels_scheme='channel+'
_search_scheme='searchres:'

# main interface class to be used by rough ucc guis
class MopidyBrowser:
    def __init__(self, core, status_func, single_thread): 
        self.core = core
        self.logger = logging.getLogger(__name__) 
        self.logger.setLevel(logging.DEBUG)
        self.status_func=status_func

        self.available_schemes=self.core.get_uri_schemes().get()
        self.library_levels = [None] 
        self.refresh_list()
        self.player = MopidyPlayControl(core)
        self.searching = MopidySearch(core)
        self.playable_types = [Ref.TRACK, Ref.ALBUM, Ref.ARTIST, Ref.PLAYLIST]
        self.tracklist = core.tracklist
        self.tracklist.set_consume(True) 
        self.subscriptions=Subscriptions.load()
        self.favourites=Favourites.load()
        self.status=None
        self.yt_default=yt_default
        self.__fix_current_list()
        self.single_thread=single_thread
        self.update_timer=threading.Timer(5,self.auto_update)
        self.update_timer.start()

    # status
    def set_status(self,msg):
        self.status=msg
        if self.status_func is not None:
            self.status_func(msg)
        self.logger.debug(msg)
                
    # properties of references        
    def is_favourites(self):
        return self.__current_level()==_favourites_ref
        
    def is_subscriptions(self):
        return self.__current_level()==_subscriptions_ref
        
    def is_queue(self):
        return self.__current_level()==_queue_ref    

    def is_history(self):
        return self.__current_level()==_history_ref    
    
    def is_playable(self,index):
        if not self.__index_ok(index): return False
        ref=self.current_list[index]
        return ref.type in self.playable_types
        
    def is_top_level(self):
        return self.current_sel is None
        
    def is_channel_ref(self,ref):
        return ref.type==Ref.ALBUM and \
            (ref.uri.startswith(podcast_scheme) or ref.uri.startswith(_channels_scheme))
    
    def is_channel(self, index):
        if not self.__index_ok(index): return False
        ref=self.current_list[index]
        return self.is_channel_ref(ref)
    
    def is_subscribed(self,index):
        if not self.__index_ok(index): return False
        ref=self.current_list[index]
        return self.subscriptions.is_subscribed(ref.name)
        
    def is_podcast(self,index):
        if not self.__index_ok(index): return False
        scheme=self.__current_scheme()
        if scheme is None: return False
        ref=self.current_list[index]
        return ref.type==Ref.TRACK and \
        (scheme.startswith(podcast_scheme) or \
        ref.uri.startswith(podcast_scheme))
    
    def is_podcast_on_disk(self,index):
        if not self.__index_ok(index): return False
        if self.__current_level() is None: return False
        channel_name=self.__current_level().name
        ref=self.current_list[index]
        podcast_name=ref.name.strip()
        return self.subscriptions.is_on_disk(channel_name,podcast_name)

    # names of current list to display
    def current_names(self,decorate=True):
        ret = []
        cl=self.__current_level()
        all_sources=set([name_from_scheme(p.uri) for p in self.current_list])
        add_src= len(all_sources)>1 and (cl is not None and cl.uri=='searchres:')
     
        for c in self.current_list:
            if add_src: name=u'{} ({})'.format(c.name.strip(),name_from_scheme(c.uri))
            else: name = c.name.strip()

            if c.type == Ref.DIRECTORY:
                if name=='Podcasts': name='Mopidy Podcasts'
                elif name=='iTunes Store: Podcasts': name='iTunes Podcasts'
                if decorate:
                    name=u'[{}]'.format(name)
            elif c.type == Ref.ALBUM and \
                self.subscriptions.is_subscribed(name):
                if decorate:
                    name=u'*({})'.format(name) 
            elif c.type in [Ref.ALBUM, Ref.ARTIST, Ref.PLAYLIST]:
                if decorate:
                    name=u'({})'.format(name)
            else: # track
                if decorate and c.uri.startswith(file_scheme):
                    name=u'*{}'.format(name)
                elif c.uri.startswith(tunein_scheme):
                    if isinstance(c,RefWithData):
                        if c.data.album.name is not None:
                            name=c.data.album.name
            ret.append(name)            

        return ret
   
    # track information to display
    def format_track_info_by_idx(self,index,include_name=True):
        if not self.__index_ok(index): return None
        ref=self.current_list[index]
        if ref.type == Ref.TRACK:
            ts=self.core.library.lookup(ref.uri).get()
            if len(ts)==0: return ref.name
            t=ts[0]
            return self.format_track_info(t,None,include_name)
        elif self.is_channel_ref(ref):
            uri=ref.uri[len(podcast_scheme):]
            return self.subscriptions.channel_desc(uri)
        else:
            return ref.name
        
    def format_track_info(self,track,title=None,include_name=True):
        name=track.name+'\n'
        if title is None or (title+'\n')==name: title=''
        else: title+='\n'
        
        if track.artists is not None and len(track.artists)>0:
            artists=','.join([t.name for t in track.artists])
        else:
            artists=''
        if track.album is not None:
            album=track.album.name
        else:   
            album=''
        if album==artists or album in name or album in title: album=''
        else: album+='\n'
        if artists in name or artists in title: artists=''
        else: artists+='\n'
        
        # you tube commments are ugly
        if album=='YouTube\n' or artists=='YouTube\n' or track.comment is None:
            comment=u''
        else:
            comment=u'\n'+track.comment
        if not include_name: name=''
        if album!='' or artists!='':
            return u'{}{}{}{}{}'.format(title,name,album,artists,comment)      
        else:
            return u'{}{}{}'.format(title,name,comment)      

    def format_current_track_info(self,include_name=True):
        track=self.player.get_current_track()
        if track is None: return ''
        
        title=self.player.get_title()
        return self.format_track_info(track, title,include_name)
            
    # private helpers
    def __current_level(self):
        if len(self.library_levels)==0: return None
        return self.library_levels[-1]
        
    def __current_scheme(self):
        cl = self.__current_level()
        if cl is None: return None
        if cl.type == Ref.DIRECTORY:
            s = get_scheme(cl.uri,cl.name)
            if s is not None:
                return s
        for ref in reversed(self.library_levels):
            if ref is not None and ref.type == Ref.DIRECTORY: 
                s = get_scheme(ref.uri,ref.name)
                if s is not None:
                    return s
        return None

    def __index_ok(self,index):
        return index >= 0 and index < len(self.current_list)
    
    def __filter_refs(self,indices):
        refs=[self.current_list[i] for i in indices if \
            self.__index_ok(i)]
        return refs
    
    # helpers to make the list display pretty
    def __sort_current_list(self):
        def _file_time(ref):
            return os.path.getmtime(urllib.unquote(ref.uri[7:]))
        def _is_subscribed(ref):
            return self.subscriptions.is_subscribed(ref.name)
        def _dir_order(ref):
            name=ref.name
            if name==_queue_ref.name: return 200#last
            elif name==_history_ref.name: return 190
            elif name=='Files': return 100
            elif name==_youtube_ref.name: return 95
            elif name=='Podcasts': return 90
            elif name=='iTunes Store: Podcasts': return -90
            elif name=='TuneIn': return -100
            elif name==_subscriptions_ref.name: return -200
            elif name==_favourites_ref.name: return -300
            else: return 0
            
        if all(p.uri.startswith(file_scheme) for p in self.current_list):
            self.current_list.sort(key=_file_time,reverse=True)
        elif all(self.is_channel_ref(p) for p in self.current_list):
            self.current_list.sort(key=_is_subscribed,reverse=True)
        elif all(p.type==Ref.DIRECTORY for p in self.current_list):
            self.current_list.sort(key=_dir_order)
            
    def __replace_downloaded(self):
        def repl(p):
            if p.type == Ref.TRACK and p.uri.startswith(podcast_scheme):
                if self.__current_level() is not None:
                    cname = self.__current_level().name
                    path=self.subscriptions.path_on_disk(cname,p.name)
                    if path is not None:
                        return Ref.track(name=p.name,uri=path)
                
            return p

        cl=self.__current_level()
        if cl is None: return
        else:    
            self.current_list=[repl(p) for p in self.current_list]    

    def __fix_current_list(self):
        self.__sort_current_list()
        self.__replace_downloaded()

    # favourites
    def add_to_favourites(self,indices):
        if self.__current_level() is None: return
        for i in indices:
            if not self.__index_ok(i): continue
            ref=self.current_list[i]
            self.favourites.add(ref.name,ref.uri)

    def remove_from_favourites(self,indices):
        if self.current_sel!=_favourites_ref: return
        for i in indices:
            if not self.__index_ok(i): continue
            ref=self.current_list[i]
            self.favourites.remove(ref.name)
    
    # handling podcast subscriptions                
    def __podcast_details_at(self,index):
        if not self.__index_ok(index):
            return (None,None)
        ref=self.current_list[index]
        if ref is None: return (None,None)
        if ref.uri.startswith(podcast_scheme):
            if ref.type == Ref.ALBUM:#channel
                return (ref.uri[len(podcast_scheme):],None)
            elif ref.type == Ref.TRACK:
                uri=ref.uri[len(podcast_scheme):]
                (uri,guid)=urlparse.urldefrag(uri)
                return (uri,urllib.unquote(guid).decode('utf8'))
        return (None,None)

            
    def download_podcasts(self, indices):
        refs=[self.__podcast_details_at(i) for i in indices]
        if self.single_thread:
            self.subscriptions.download_podcasts(refs,self.set_status)
        else:
            threading.Thread(
                target=self.subscriptions.download_podcasts,
                args=(refs,self.set_status)).start()
            
    def keep_podcasts(self, indices):
        refs=[self.__podcast_details_at(i) for i in indices]
        if self.single_thread:
            self.subscriptions.keep_podcasts(refs,self.set_status)
        else:
            threading.Thread(
                target=self.subscriptions.keep_podcasts,
                args=(refs,self.set_status)).start()
                    
    def delete_podcasts(self,indices):
        if self.__current_level() is None: return
        channel_name=self.__current_level().name
        refs=[]
        for i in indices:
            if not self.__index_ok(i): continue
            refs.append((channel_name,self.current_list[i].name.strip()))
        self.subscriptions.delete_podcasts(refs,self.set_status)

    def subscribe(self, indices):
        refs=self.__filter_refs(indices)
        channel_uris=[r.uri[len(podcast_scheme):] for r in refs \
            if self.is_channel_ref(r)]

        if self.single_thread:
            self.subscriptions.subscribe(channel_uris,self.set_status)
        else:
            threading.Thread(
                target=self.subscriptions.subscribe,
                args=(channel_uris,self.set_status)).start()

    def unsubscribe(self, indices):
        refs=self.__filter_refs(indices)
        channel_uris=[r.uri[len(podcast_scheme):] for r in refs \
            if self.is_channel_ref(r)]

        if self.single_thread:
            self.subscriptions.unsubscribe(channel_uris,self.set_status)
        else:
            threading.Thread(
                target=self.subscriptions.unsubscribe,
                args=(channel_uris,self.set_status)).start()
                
    def update(self, indices):
        refs=self.__filter_refs(indices)
        channel_uris=[r.uri[len(podcast_scheme):] for r in refs \
            if self.is_channel_ref(r)]
        if self.single_thread:
            self.subscriptions.update(channel_uris,self.set_status)
        else:
            threading.Thread(
                target=self.subscriptions.update,
                args=(channel_uris,self.set_status)).start()
    
    def auto_update(self):
        self.update([])
        self.update_timer.cancel()
        self.update_timer=threading.Timer(86400,self.auto_update)
        self.update_timer.start()
    
    # navigation
    def select_channel(self,ref):
        self.add_level(ref)
        channel=self.subscriptions.channel_by_name(ref.name)
        if channel is None: raise 'Channel {} not found in subscriptions'.format(ref.name)
        refs=[]
        for p in channel.podcasts:
            path=self.subscriptions.path_on_disk(p.channel_name,p.name)
            if path is not None:
                refs.append(Ref.track(name=p.name,uri=path))
            else:
                refs.append(Ref.track(name=p.name,
                    uri='{}{}#{}'.format(podcast_scheme,p.channel_uri,p.guid)))
        self.current_list = refs
    
    def select_subscriptions(self):
        self.add_level(_subscriptions_ref)
        refs=[Ref.album(name=c.name,
            uri='{}{}'.format(_channels_scheme,c.uri)) for c in \
            self.subscriptions.channels]  
        self.current_list = refs

    def select_favourites(self):
        self.add_level(_favourites_ref)
        favs=self.favourites.favourites
        refs=[Ref.track(name=f[0],uri=f[1]) for f in favs]
        self.current_list = refs
    
    def select_queue(self):
        self.add_level(_queue_ref)
        refs=self.tracks()
        self.current_list = refs

    def select_history(self):
        self.add_level(_history_ref)
        refs=self.core.history.get_history().get()
        refs=[r[1] for r in refs]
        self.current_list = refs
                        
    def select_youtube(self):
        self.add_level(_youtube_ref)
        if self.yt_default is None:
            if self.searching.last_query is None:
                self.set_status('Searching YouTube for trending music')
                self.yt_default=self.searching.search_any(
                    'take five',uris=['youtube:'])
            else:
                q=self.searching.last_query
                self.set_status('Searching YouTube for '.format(q))
                self.yt_default=self.searching.search_any(q,uris=['youtube:'])
            self.set_status(None)
        for p in self.yt_default:
            print p
        self.current_list = self.yt_default

    def add_level(self,ref):
        if ref != self.__current_level():
            self.library_levels.append(ref)

    def select_ref(self,ref):
        self.current_sel = ref
        if ref is not None and ref.type == Ref.TRACK: 
            return
        if ref is None:
            self.add_level(None)
            self.current_list = self.core.library.browse(None).get()
            self.current_list.insert(0,_subscriptions_ref)
            self.current_list.insert(0,_favourites_ref)
            self.current_list.insert(0,_queue_ref)
            self.current_list.insert(0,_history_ref)
            if 'youtube' in self.available_schemes:
                self.current_list.insert(0,_youtube_ref)
        elif ref.uri==_search_scheme:
            self.current_list=self.searching.flat_res()
        elif ref.uri==_subscriptions_ref.uri:
            self.select_subscriptions()
        elif ref.uri==_favourites_ref.uri:
            self.select_favourites()
        elif ref.uri==_queue_ref.uri:
            self.select_queue()
        elif ref.uri==_history_ref.uri:
            self.select_history()
        elif ref.uri==_youtube_ref.uri:
            self.select_youtube()
        elif ref.uri.startswith(_channels_scheme):
            self.select_channel(ref)
        else:
            self.add_level(ref)
            self.current_list = self.core.library.browse(ref.uri).get()
        self.__fix_current_list()


    def back(self):
        if len(self.library_levels) > 1:
            self.library_levels = self.library_levels[:-1]
            self.refresh_list()
        
    def refresh_list(self):
        self.select_ref(self.__current_level())

    def select(self, index):
        if not self.__index_ok(index): return
        ref = self.current_list[index]
        self.select_ref(ref)
    
    def search(self,query):
        scheme = self.__current_scheme()
        self.set_status('Searching for...{}'.format(query))
        if scheme is None:
            uris = None
        else:
            uris = [scheme]

        if scheme is not None and scheme.startswith(podcast_scheme):
            search_res = self.searching.search_album(query,uris)
        else:
            search_res = self.searching.search_any(query,uris)
        if len(search_res)==0:
            self.set_status('Search returned no results')
            time.sleep(5)
            self.set_status(None)
            return
        self.add_level(Ref.directory(
            name = 'search: {}'.format(query),
            uri = 'searchres:'))
        self.current_list = search_res
        self.__fix_current_list()    
        self.current_sel = self.__current_level()
        self.set_status(None)
    
    # tracklist and playback
    def add_to_tracks(self,indices,pos = None):
        sz = len(self.current_list)
        filtered_indices = [i for i in indices if (i >=0 and i < sz)]
        uris = [self.current_list[i].uri for i in filtered_indices]
        self.tracklist.add(uris=uris,at_position = pos)
        self.trace_tracks()
        if not self.player.is_playing(): 
            self.player.play()
    
    def play_next(self,indices):
        self.add_to_tracks(indices,1)
        self.tracklist.set_repeat(False)
        self.tracklist.set_consume(True)
    
    def play_now(self,indices):
        self.player.stop()
        if self.tracklist.get_length() > 0:
            self.remove_tracks([0])
        self.add_to_tracks(indices,0)
        self.tracklist.set_repeat(False)
        self.tracklist.set_consume(True)

    def loop_now(self,indices):
        self.player.stop()
        self.clear_tracks()
        self.add_to_tracks(indices,0)
        self.tracklist.set_repeat(True)
        self.tracklist.set_consume(False) 

    def play_current(self):
        ref=self.current_sel
        if ref is None or (ref.type not in self.playable_types):
            return
        
        self.player.stop()
        if self.tracklist.get_length() > 0:
            self.remove_tracks([0])

        tracks=self.core.library.lookup(ref.uri).get()
        uris=[t.uri for t in tracks]
        self.tracklist.add(uris=uris,at_position = 0)

        self.player.play()

    def clear_tracks(self):
        self.tracklist.clear()
        self.trace_tracks()

    def shuffle(self):
        self.tracklist.shuffle()
        self.trace_tracks()

    def tracks(self):
        ts = self.tracklist.get_tracks().get()
        return [make_ref(t) for t in ts]
    
    def get_current_tl_index(self):
        tlt=self.player.get_current_tl_track()
        if tlt is None: return None
        return self.core.tracklist.index(tlt).get() 

    def get_next(self):
        nxt=self.tracklist.get_next_tlid().get()
        if nxt is None: return None
        idx=self.tracklist.index(tlid=nxt).get()
        if idx is None: return None
        ts = self.tracklist.get_tracks().get()
        return ts[idx]
    
    def get_prev(self):
        prev=self.tracklist.get_previous_tlid().get()
        if prev is None: return None
        idx=self.tracklist.index(tlid=prev).get()
        if idx is None: return None
        ts = self.tracklist.get_tracks().get()
        return ts[idx]

    def flip_loop(self):
        cur = self.core.tracklist.get_repeat().get()
        self.tracklist.set_repeat(not cur)
        self.tracklist.set_consume(cur) 

    def is_looping(self):
        return self.core.tracklist.get_repeat().get()

    def remove_tracks(self, indices):
        if len(indices)==0: return    
        tls = self.tracklist.get_tl_tracks().get()
        filtered_indices = [i for i in indices if (i < len(tls) and i >= 0)]
        tlids = [tls[i].tlid for i in filtered_indices]
        filt = {'tlid' : tlids}
        self.tracklist.remove(filt)
        self.trace_tracks()
    
    # player controls
    def set_volume(self,volume):
        self.player.set_volume(volume)
    
    def is_playing(self):
        return self.player.is_playing()
    
    def is_stopped(self):
        return self.player.is_stopped()
 
    def get_current_tm(self):
        return self.player.get_current_tm()

    def seek(self,tm):
        self.player.seek(tm)
    
    def next(self):
        self.player.next()
    
    def prev(self):
        self.player.prev()
        
    def play(self):
        self.player.play()
        
    def play_pause(self):
        self.player.play_pause()                

    # event handling
    def mopidy_event(self,msg,**kwargs):
        pass
        
    # debugging
    def trace_state(self):
        self.logger.debug('levels: {}'.format(self.library_levels))
        self.logger.debug('current list: {}'.format(self.current_list))
        self.logger.debug('current scheme: {}'.format(self.__current_scheme()))
        self.logger.debug('current sel: {}'.format(self.current_sel))
        
    def trace_tracks(self):
        self.logger.info('tracks: {}'.format(self.tracks()))

        
