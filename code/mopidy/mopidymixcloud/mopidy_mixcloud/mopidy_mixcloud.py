import requests
from mopidy.models import Ref,Track,Album,SearchResult,Artist,Image,Playlist
from mopidy.backend import *
import pykka
import pdb
import time
logger = logging.getLogger(__name__)
import urllib
from threading import Lock

# I have learned a lot from jackyNIX's code for kodi mopidy plugin
# https://github.com/jackyNIX/xbmc-mixcloud-plugin

search_max=150
uri_scheme=u'mixcloud'
uri_prefix=uri_scheme+':'
api_prefix=u'https://api.mixcloud.com'
downloader_prefix=u'http://download.mixcloud-downloader.com/d/mixcloud'
uri_root='mixcloud:root'
uri_categories=u'https://api.mixcloud.com/categories/'
uri_popular=u'https://api.mixcloud.com/popular/'
uri_hot=u'https://api.mixcloud.com/popular/hot/'
uri_new=u'https://api.mixcloud.com/new/'
uri_users=u'users'
uri_user=u'user'
uri_category=u'category'
uri_cloudcasts=u'cloudcasts/'
uri_favorites=u'favorites/'
uri_playlists=u'playlists/'
uri_playlist=u'playlist/'
uri_following=u'following/'
uri_followers=u'followers/'
uri_listens=u'listens/'
uri_search=u'https://api.mixcloud.com/search/?type={}&q="{}"'
users=[]
default_users=[]


class Cache:
    def __init__(self):
        self.data=[]
        self.max_size=2000
        self.lock=Lock()
        
    def clear(self):
        with self.lock:
            self.data=[]
        
    def add(self, uri, item):
        i = self.get(uri)
        with self.lock:
            if i is None:
                if len(self.data) >= self.max_size: 
                    self.data=self.data[(self.max_size/2):]
                self.data.append((uri,item))

    def get(self,uri):
        with self.lock:
            item = next((i for i in self.data if i[0]==uri),None)
        if item is not None: return item[1]
        else: return None

images_cache=Cache() # uri -> Image
tracks_cache=Cache() # uri -> Track
refs_cache=Cache()   # uri -> list of Ref              
searches_cache=Cache() # uri -> SearchResult
playlists_cache=Cache() #uri -> Playlist
lookup_cache=Cache() #uri -> [Track]
cache_refresh_period=600 #10 min
last_refresh_time=0

def refresh_cache():
    global last_refresh_time
    t=time.time()
    if t==0 or (t-last_refresh_time) > cache_refresh_period:
        last_refresh_time=t
        clear_caches()
        
def clear_caches(reset_users=False):
    global users
    tracks_cache.clear()
    refs_cache.clear()
    images_cache.clear()
    searches_cache.clear()
    playlists_cache.clear()
    lookup_cache.clear()
    if reset_users:
        users=default_users[:]
        
    
class MixcloudException(Exception):
    def __init__(self, value):
        self.parameter = value
    
    def __str__(self):
        return repr(self.parameter)

def enc(s):
    try:
        return s.encode('utf-8')
    except:
        return s
        
def dec(s):
    try:
        return s.decode('utf-8')
    except:
        return s
    

def make_uri(uri):
    return uri_prefix+uri.strip()
               
def strip_uri(uri):
    uri=dec(uri)
    if uri.startswith(uri_prefix):
        return uri[len(uri_prefix):]
    else:
        return uri

root_list=[ 
        Ref.directory(name=u'Categories',uri=make_uri(uri_categories)), 
        Ref.directory(name=u'Popular',uri=make_uri(uri_popular)), 
        Ref.directory(name=u'Hot',uri=make_uri(uri_hot)), 
        Ref.directory(name=u'New',uri=make_uri(uri_new)),
        Ref.directory(name=u'Users',uri=make_uri(uri_users))] 

def uri_json(uri):
    decoded=enc(uri)
    r=requests.get(decoded)
    if not r.ok: raise MixcloudException('Request failed for uri '+uri)
    return r.json()
 
def get_next_page(json_dict, name):
    if 'paging' not in json_dict: return None
    paging = json_dict['paging']
    if 'next' not in paging: return None
    name = u'More {}...'.format(name)
    return Ref.directory(name=name, uri=make_uri(paging['next']))

def get_next_page_uri(json_dict):
    if 'paging' not in json_dict: return None
    paging = json_dict['paging']
    if 'next' not in paging: return None
    return paging['next']


def make_special_uri(user_key,uri_prefix,more=''):
    try:
        enc=user_key.encode('base64')
    except:
        enc=user_key.encode('utf-8').encode('base64')
    special=make_uri(uri_prefix+':'+enc)
    return u'{}:more:{}'.format(special,more)
        
def strip_special_uri(uri,uri_prefix):
    uri=strip_uri(uri)
    if dec(uri).startswith(uri_prefix):
        elements=uri.split(':')
        user_key=elements[1]
        special=user_key.decode('base64')
#        special=front[len(uri_prefix):].decode('base64')
        more=elements[-1]
        return (special,more)
    else:
        return (None,None)
        
def make_special_api(user_key,uri_prefix):
    try:
        return api_prefix+user_key+uri_prefix
    except:
        return api_prefix+urllib.quote(user_key)+uri_prefix

def make_more_name(user_key,group):
    try:
        name=enc(user_name[1:-1])
        decoded=dec(urllib.unquote(name))
        pre0=u'{} '.format(decoded)
        return u"More {}'s {}...".format(decoded,group)
    except:
        return u"More {}...".format(group)

def list_playlists(uri,user_key):
    uri=strip_uri(uri)
    refs=refs_cache.get(uri)
    if refs is not None: return refs

    json=uri_json(uri)
    playlists=json['data']
    refs=[]
    for playlist in playlists:
        user_name=playlist['name']
        key=urllib.quote(playlist['key'])
        playlist_uri=api_prefix+key+u'cloudcasts/'
        ref=Ref.playlist(name=user_name,uri=make_uri(playlist_uri))
        refs.append(ref)

    more=get_next_page_uri(json)
    if more is not None:
        more_param=more.split('/')[-1]
        more_uri=make_special_uri(user_key,uri_playlists,more_param)
        ref=Ref.directory(name=make_more_name(user_key,u'playlists'), uri=make_uri(more_uri))
        refs.append(ref)

    refs_cache.add(uri,refs)
    return refs

def list_category_users(uri):
    uri=strip_uri(uri)
    refs=refs_cache.get(uri)
    if refs is not None: return refs

    json=uri_json(uri)
    fols=json['data']
    refs=[]
    for fol in fols:
        name=fol['username']
        key=fol['key']
        fol_uri=make_special_uri(key,uri_user)
        ref=Ref.directory(name=enc(name),uri=fol_uri)
        refs.append(ref)

    more=get_next_page(json,u'users')
    if more is not None:
        refs.append(more)

    refs_cache.add(uri,refs)
    return refs
    
def list_fols(uri,user_key): # followers or following
    uri=strip_uri(uri)
    refs=refs_cache.get(uri)
    if refs is not None: return refs

    json=uri_json(uri)
    fols=json['data']
    refs=[]
    for fol in fols:
        name=fol['username']
        key=fol['key']
        fol_uri=make_special_uri(key,uri_user)
        ref=Ref.directory(name=enc(name),uri=fol_uri)
        refs.append(ref)

    more=get_next_page_uri(json)

    if more is not None:
        if 'following' in uri:
            name_for_more=make_more_name(user_key,u'follows')
            uri_for_more=uri_following
        else:
            name_for_more=make_more_name(user_key,u'followers')
            uri_for_more=uri_followers
        more_param=more.split('/')[-1]
        more_uri=make_special_uri(user_key,uri_for_more,more_param)
        ref=Ref.directory(name=name_for_more, uri=make_uri(more_uri))
        refs.append(ref)

    refs_cache.add(uri,refs)
    return refs
    

def list_user(user_name):
    
    try:
        name=enc(user_name[1:-1])
        decoded=dec(urllib.unquote(name))
        pre0=u'{} '.format(decoded)
        pre=u"{}'s ".format(decoded)
    except:
        pre0=''
        pre = u''
        
    cloudcasts=Ref.album(name=pre+u'cloudcasts',
        uri=make_special_uri(user_name,uri_cloudcasts))
    favorites=Ref.directory(name=pre+u'favorites',
        uri=make_special_uri(user_name,uri_favorites))
    playlists=Ref.directory(name=pre+u'playlists',
        uri=make_special_uri(user_name,uri_playlists))
    following=Ref.directory(name=pre0+u'follows',
        uri=make_special_uri(user_name,uri_following))
    followers=Ref.directory(name=pre+u'followers',
        uri=make_special_uri(user_name,uri_followers))
    listens=Ref.directory(name=pre0+u'listened to',
        uri=make_special_uri(user_name,uri_listens))
    return [cloudcasts,favorites,playlists,following,followers,listens]
                   
def list_categories():
    cat_refs=refs_cache.get(uri_categories)
    if cat_refs is not None: return cat_refs
   
    categories = uri_json(uri_categories)['data']
    cat_refs = []
    for category in categories:
        uri=make_uri(api_prefix+category['key']+u'users/')
        name=category['name']
        cat_refs.append(Ref.directory(name=name,uri=uri))
    refs_cache.add(uri_categories, cat_refs)
    return cat_refs

def track_uri(track_key):
    return dec(make_uri(downloader_prefix+track_key))
    
def make_track(track_key, name, user, time, length,user_key):
    uri=track_uri(track_key)
    date=time.split('T')[0]
    
    
    album_uri=make_special_uri(user_key,uri_user)#make_uri(api_prefix+user_key+u'cloudcasts/')
    album=Album(uri=album_uri,name=user)
    artist=Artist(uri=album_uri,name=user)
    if length is None:
        l=None
    else:
        l=int(length)*1000
    track=Track(uri=uri,name=name,album=album,
        artists=[artist],date=date,length=l)
    ref=Ref.track(name=track.name, uri=uri)
    tracks_cache.add(uri,track)
    return (ref,track)

def get_thumbnail(uri,jsdict):
    if 'pictures' in jsdict:
        if 'thumbnail' in jsdict['pictures']:
                images_cache.add(uri, 
                    Image(uri=jsdict['pictures']['thumbnail'])) 
                       
def make_track_from_json(cloudcast):
    key=cloudcast['key']
    uri=track_uri(key)
    track=tracks_cache.get(uri)
    if track is None:
        name=cloudcast['name']
        user=cloudcast['user']['username']
        user_key=cloudcast['user']['key']
        time=cloudcast.get('created_time','1943-11-29T13:13:13Z')
        length=cloudcast.get('audio_length',None)
        (ref,track)=make_track(key,name,user, time, length,user_key)
        get_thumbnail(cloudcast,ref.uri)
    else:
        ref=Ref.track(name=track.name, uri=uri)
    return (ref,track)

def list_cloudcasts(uri,user_key=''):
    suri=strip_uri(uri)
    if suri.startswith(downloader_prefix):
        key=strip_uri(uri)[len(downloader_prefix):]
        curi=api_prefix+key
        ref=make_track_from_json(uri_json(curi))[0]
        refs_cache.add(uri,ref)
        return [ref]
    json=uri_json(uri)
    cloudcasts=json['data']
    refs=[]
    tracks=[]
    for cloudcast in cloudcasts:
        (ref,track)=make_track_from_json(cloudcast)
        refs.append(ref)
        tracks.append(track)
    for t in tracks:
        if tracks_cache.get(t.uri) is None:
            tracks_cache.add(uri,t)
    more=get_next_page(json,u'tracks')
    if more is not None:
        refs.append(more)

    refs_cache.add(uri,refs)
    return refs
    
def list_refs(uri):
    def handle_special_uri(uri, special_uri, list_f):
        (user_key,more)=strip_special_uri(uri,special_uri)
        if user_key is None: return None
        urir=make_special_api(user_key,special_uri)+more
        refs=list_f(urir,user_key)
        refs_cache.add(uri,refs)
        return refs    
    uri=strip_uri(uri)
    if uri == uri_categories: return list_categories()
    refs=refs_cache.get(uri)
    if refs is not None: 
        return refs
    refs = []
    if uri == uri_users:
        for user in users:
            ref=Ref.directory(name=user,
                uri=make_special_uri(u'/{}/'.format(user),uri_user))
            refs.append(ref)
        return refs
    (user_key,more)=strip_special_uri(uri,uri_user)
    if user_key is not None:
        refs=list_user(user_key)
        refs_cache.add(uri,refs)
        return refs

    refs=handle_special_uri(uri, uri_cloudcasts, list_cloudcasts)
    if refs is not None: return refs        

    refs=handle_special_uri(uri, uri_listens, list_cloudcasts)
    if refs is not None: return refs        

    refs=handle_special_uri(uri, uri_favorites, list_cloudcasts)
    if refs is not None: return refs        

    refs=handle_special_uri(uri, uri_playlists, list_playlists)
    if refs is not None: return refs        

    refs=handle_special_uri(uri, uri_following, list_fols)
    if refs is not None: return refs        

    refs=handle_special_uri(uri, uri_followers, list_fols)
    if refs is not None: return refs        

    if 'users' in uri:
        refs=list_category_users(uri)
        refs_cache.add(uri,refs)
        return refs
    refs=list_cloudcasts(uri)
    refs_cache.add(uri,refs)
    return refs    

def get_track_for_uri(uri):
    track=tracks_cache.get(uri)
    if track is not None: return track
    key=strip_uri(uri)[len(downloader_prefix):]
    cloudcast=uri_json(api_prefix+key)
    (ref,track)=make_track_from_json(cloudcast)
    return track

def get_tracks_for_uri(uri,max_tracks=search_max):
    track=tracks_cache.get(uri)
    if track is not None: return [track]

    uri=strip_uri(uri)
    if uri == uri_categories: return []


    if downloader_prefix in uri: # this is a track
        return [get_track_for_uri(uri)]    

    json=uri_json(uri)
    cloudcasts=json['data']
    tracks = []

    for cloudcast in cloudcasts:
        (ref,track)=make_track_from_json(cloudcast)
        tracks.append(track)

    more=get_next_page(json,u'')
    so_far=len(tracks)
    if more is not None and so_far<max_tracks:
        more_tracks=get_tracks_for_uri(more.uri,max_tracks-so_far)
        tracks=tracks+more_tracks
    return tracks

def list_albums(uri, max_albums=search_max):
    uri=strip_uri(uri)
    json=uri_json(uri)
    albums_dict=json['data']
    albums = []
    #albums are in fact users
    global users
    users=default_users[:]
    for album in albums_dict:
        key=album['key']
        name=album['name']
        username=album['username']
        uri=make_uri(api_prefix+key+u'cloudcasts/')
        ref=Album(name=name, uri=uri)
        get_thumbnail(album,ref.uri)
        albums.append(ref)
        if username not in users: users.append(username)
        
    more=get_next_page(json,u'users')
    so_far = len(albums)
    if more is not None and so_far < max_albums:
            more_albums=list_albums(more.uri,max_albums-so_far)
            albums=albums+more_albums
    return albums
               
class MopidyMixcloud(pykka.ThreadingActor, Backend):
    uri_schemes = [u'mixcloud']
 
    def __init__(self, config, audio):
        super(MopidyMixcloud, self).__init__()
        global default_users,users
        default_users=config['mixcloud']['users'].split(',')
        users=default_users[:]
        self.library = MixcloudLibrary(self)
        self.playback = MixcloudPlayback(audio=audio, backend=self)
        self.playlists = MixcloudPlaylists(self)
        
class MixcloudPlaylists(PlaylistsProvider):
    def __init__(self,backend):
        super(MixcloudPlaylists, self).__init__(backend)

    def as_list(self):
        playlists=[]
        for u in users:
            uri=u'{}/{}/{}'.format(api_prefix,u,uri_playlists)
            refs=refs_cache.get(uri)
            if refs is None: 
                refs=list_playlists(uri,'/'+u+'/')
            if refs is not None:
                playlists=playlists+refs
        return playlists        

    def get_items(self, uri):
        try:
            return list_refs(uri)
        except MixcloudException:#someone encoded our uris
            return list_refs(urllib.unquote(uri))

    def lookup(self, uri):
        playlist=playlists_cache.get(uri)
        if playlist is not None: return playlist
        
        suri=strip_uri(uri)
        
        if not (suri.startswith(api_prefix) and suri.endswith(u'/cloudcast/')):
            return None
        playlist_name=suri[len(api_prefix)+1:-len(u'/cloudcasts/')]
        tracks=get_tracks_for_uri(uri)
        playlist=Playist(uri=uri,name=name,tracks=tracks,
            length=len(tracks),last_modified=None)
        playlists_cache.add(uri,playlist)
        return playlist


    def refresh(self):
        clear_caches()

class MixcloudLibrary(LibraryProvider):
    root_uri=uri_root
    root_directory = Ref.directory(uri=root_uri, name='Mixcloud')
 
    def __init__(self, backend):
        super(MixcloudLibrary, self).__init__(backend)
 
    def browse(self, uri):
        refresh_cache()
        if not dec(uri).startswith(uri_scheme):
            return []
                       
        if uri==uri_root:
            return root_list
        else:
            try:
                ret=list_refs(uri)
                return ret
            except MixcloudException:#someone encoded our uris
                ret=list_refs(uri)
                return ret
                           
    def refresh(self, uri=None):
        clear_caches(True)
        
    def lookup(self, uri, uris=None):
        if uri is None and uris is None: return []
        if uri is not None:
            tracks=lookup_cache.get(uri)
            if tracks is not None: return tracks
            track=tracks_cache.get(uri)
            if track is not None: return [track]
            suri=strip_uri(uri)
            if uri_cloudcasts in uri:
                (username,more)=strip_special_uri(suri,uri_cloudcasts)
            elif uri_user in uri:
                (username,more)=strip_special_uri(suri,uri_user)
            else:
                ref=get_tracks_for_uri(suri)
                lookup_cache.add(uri,ref)
                return ref
     
            turi=uri
            if username is not None:
                turi=make_special_api(username,uri_cloudcasts)+more
            if turi is not None:
                ref=get_tracks_for_uri(turi)
                lookup_cache.add(uri,ref)
                return ref
            else:
                return []
        else:
            ret={}
            for uri in uris:
                l=self.lookup(uri=uri)
                if len(l) > 0: ret[uri]=l
            return ret
                       
    def search(self, query=None, uris=None, exact=False):
        refresh_cache()
        if uris is not None:
            if next((uri for uri in uris if uri.startswith(uri_scheme)),
                None) is None:
                return None
                   
        if query is None or len(query)==0: return None
 
        query_type=u'cloudcast'
        query_val=u''
                   
        # look for the first query key that we can deal with
        for k in query:
            q=query[k]
            if q[0].startswith('refresh:'):
                clear_caches(True)
                q[0]=q[0][len('refresh:'):]
            if k in ['artist','albumartist','composer','performer']:
                query_type='user'
                query_value=query[k][0]
                break
            if k in ['any','track_name']:
                if q[0].startswith('user:'):
                    query_type='user'
                    query_value=q[0][len('user:'):]
                else:
                    query_value=q[0]
                break
                               
        if query_value=='': return None
 
        search_uri=uri_search.format(query_type,query_value)
        sr = searches_cache.get(search_uri)
        if sr is not None: return sr
        res=None
        if query_type=='user':
            albums=list_albums(search_uri)
            res=SearchResult(uri=search_uri,albums=albums)
        else:
            tracks=get_tracks_for_uri(search_uri)
            res=SearchResult(uri=search_uri,tracks=tracks)
        searches_cache.add(search_uri,res)
        return res
               
    def get_images(self,uris):
        ret={}
        for uri in uris:
            img=images_cache.get(uri)
            if img is not None: ret[uri]=[img]
        return ret
                   
class MixcloudPlayback(PlaybackProvider):
    def translate_uri(self, uri): 
        return strip_uri(uri)
