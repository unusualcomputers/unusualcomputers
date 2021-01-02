# I have learned a lot from jackyNIX's code for kodi mopidy plugin
# https://github.com/jackyNIX/xbmc-mixcloud-plugin

import requests
from mopidy.models import Ref,Track,Album,SearchResult,Artist,Image,Playlist
from mopidy.backend import *
import pykka
import pdb
logger = logging.getLogger(__name__)
import urllib
import youtube_dl
from util import LocalData,MixcloudException

uri_prefix=u'mixcloud:'
track_prefix='track:'
api_prefix=u'https://api.mixcloud.com'
mixcloud_prefix=u'https://mixcloud.com'
uri_root='mixcloud:root'
uri_categories=u'https://api.mixcloud.com/categories/'
uri_users=u'users'
uri_userscategories=u'userscategories'
uri_user=u'user'
uri_tags=u'tags'
uri_tag=u'tag'
uri_cloudcasts=u'cloudcasts/'
uri_favorites=u'favorites/'
uri_playlists=u'playlists/'
uri_playlist=u'playlist/'
uri_following=u'following/'
uri_followers=u'followers/'
uri_listens=u'listens/'
uri_latest=u'latest/'
uri_popular=u'popular/'
uri_search=u'https://api.mixcloud.com/search/?type={}&q={}'
uri_city=u'https://api.mixcloud.com/discover/{}/latest/'

# all cached data is here
_cache=LocalData()

# dealing with mixcloud: uris
def make_uri(uri):
    if uri.startswith(uri_prefix):
        return uri.strip()
    return uri_prefix+uri.strip()
        
def strip_uri(uri):
    if uri.startswith(uri_prefix):
        return uri[len(uri_prefix):]
    else:
        return uri

def get_json(uri):
    r=requests.get(strip_uri(uri))
    if not r.ok: raise MixcloudException('Request failed for uri '+uri)
    return r.json()

root_list=[ 
        Ref.directory(name=u'Categories',uri=make_uri(uri_categories)), 
        Ref.directory(name=u'Users',uri=make_uri(uri_users)), 
        Ref.directory(name=u'Tags',uri=make_uri(uri_tags))] 

# dealing with complex uri composition (e.g. when username has spaces
#   they have to be base64 encoded etc) 
def make_encoded_uri(user_key,uri_prefix,more=''):
    try:
        enc=user_key.encode('base64')
    except:
        enc=user_key.encode('utf-8').encode('base64')
    special=make_uri(uri_prefix+':'+enc)
    return u'{}:base64:{}'.format(special,more)
        
def strip_encoded_uri(uri,uri_prefix):
    uri=strip_uri(uri)
    if uri.startswith(uri_prefix):
        elements=uri.split(':')
        user_key=elements[1]
        special=user_key.decode('base64')
        more=elements[-1]
        return (special,more)
    else:
        return (None,None)
        
def compose_uri(user_key,uri_prefix):
    try:
        return api_prefix+user_key+uri_prefix
    except:
        return api_prefix+urllib.quote(user_key)+uri_prefix

def make_more_name(user_key,group):
    try:
        decoded=urllib.unquote(user_key)
        return u"More {}'s {}...".format(decoded,group)
    except:
        return u"More {}...".format(group)

def refs_from_encoded_uri(uri, more_uri, list_f):
    (user_key,more)=strip_encoded_uri(uri,more_uri)
    if user_key is None: return None
    urir=compose_uri(user_key,more_uri)+more
    refs=list_f(urir,user_key)
    _cache.refs.add(uri,refs)
    return refs    

def next_page_uri(json_dict):
    if 'paging' not in json_dict: return None
    paging = json_dict['paging']
    if 'next' not in paging: return None
    return paging['next']

def next_page_ref(json_dict, name):
    page=next_page_uri(json_dict)
    if page is None: return None
    name = u'More {}...'.format(name)
    return Ref.directory(name=name, uri=make_uri(page))


# handling tracks
def make_track_uri(track_key):
    return make_uri(track_prefix+track_key)

def strip_track_uri(uri):
    if track_prefix in uri:
        return strip_uri(uri)[len(track_prefix):]
    else:
        return uri

def make_track(cloudcast):
    key=cloudcast['key']
    uri=make_track_uri(key)
    track=_cache.tracks.get(uri)
    if track is None:
        name=cloudcast['name']
        user=cloudcast['user']['username']
        user_key=cloudcast['user']['key']
        time=cloudcast.get('created_time','1943-11-29T13:13:13Z')
        length=cloudcast.get('audio_length',None)
        date=time.split('T')[0]
        album_uri=make_encoded_uri(user_key,uri_user)
        album=Album(uri=album_uri,name=user)
        artist=Artist(uri=album_uri,name=user)
        if length is None:
            l=None
        else:
            l=int(length)*1000
        
        track=Track(uri=uri,name=name,album=album,
            artists=[artist],date=date,length=l)
        ref=Ref.track(name=track.name, uri=uri)
        
        _cache.tracks.add(uri,track)
        _cache.add_thumbnail(cloudcast,uri)
    else:
        refs=_cache.refs.get(uri)
        if refs is not None:
            ref=refs[0]
        else:
            ref=Ref.track(name=track.name, uri=uri)
    return (ref,track)

def get_tracks_refs_for_uri(uri,max_tracks):

    if uri.endswith(uri_categories): return ([],[])

    track=_cache.tracks.get(uri)
    if track is not None: # this is a cached track
        refs=_cache.refs.get(uri)
        if refs is None:
            refs=[Ref.track(name=track.name, uri=track.uri)]
            _cache.refs.add(uri,refs)
        return [track],refs
    if track_prefix in uri: # this is a new track
        key=strip_track_uri(uri)
        cloudcast=get_json(api_prefix+key)
        (ref,track)=make_track(cloudcast)
        refs=[ref]
        tracks=[track]
        _cache.refs.add(uri,refs)
        return tracks,refs

    # this is some other list of tracks
    json=get_json(uri)
    cloudcasts=json['data']
    refs=[]
    tracks = []

    for cloudcast in cloudcasts:
        (ref,track)=make_track(cloudcast)
        refs.append(ref)
        tracks.append(track)

    more=next_page_uri(json)
    so_far=len(tracks)
    if more is not None and so_far<max_tracks:
        more_tracks,more_refs=get_tracks_refs_for_uri(make_uri(more),max_tracks-so_far)
        tracks=tracks+more_tracks
        refs=refs+more_refs
    
    _cache.refs.add(uri,refs)
    return tracks,refs


def get_tracks_for_uri(uri,max_tracks):
    return get_tracks_refs_for_uri(uri,max_tracks)[0]

def get_refs_for_uri(uri,max_tracks):
    return get_tracks_refs_for_uri(uri,max_tracks)[1]

# get stream url 
ydl=youtube_dl.YoutubeDL()
def get_stream_url(uri):
    url=_cache.urls.get(uri)
    if url is not None:
        return url
    if track_prefix in uri:
        track_uri=strip_track_uri(uri)
        try:
            info=ydl.extract_info(mixcloud_prefix+track_uri,download=False)
        except youtube_dl.DownloadError as de:
            logger.warning(de)
            return None
        url=info['url']
        _cache.urls.add(uri,url) 
        return url
    else:
        return uri

# traversing mixcloud data
def list_playlists(uri,user_key):
    refs=_cache.refs.get(uri)
    if refs is not None: return refs

    json=get_json(uri)
    playlists=json['data']
    refs=[]
    for playlist in playlists:
        user_name=playlist['name']
        key=urllib.quote(playlist['key'])
        playlist_uri=api_prefix+key+u'cloudcasts/'
        ref=Ref.playlist(name=user_name,uri=make_uri(playlist_uri))
        refs.append(ref)

    more=next_page_uri(json)
    if more is not None:
        more_param=more.split('/')[-1]
        more_uri=make_encoded_uri(user_key,uri_playlists,more_param)
        ref=Ref.directory(name=make_more_name(user_key,u'playlists'), uri=make_uri(more_uri))
        refs.append(ref)

    _cache.refs.add(uri,refs)
    return refs

def list_fols(uri,user_key): # followers or following
    refs=_cache.refs.get(uri)
    if refs is not None: return refs

    json=get_json(uri)
    fols=json['data']
    refs=[]
    for fol in fols:
        name=fol['username']
        key=fol['key']
        fol_uri=make_encoded_uri(key,uri_user)
        ref=Ref.directory(name=name,uri=fol_uri)
        refs.append(ref)

    more=next_page_uri(json)

    if more is not None:
        if 'following' in uri:
            name_for_more=make_more_name(user_key,u'follows')
            uri_for_more=uri_following
        else:
            name_for_more=make_more_name(user_key,u'followers')
            uri_for_more=uri_followers
        more_param=more.split('/')[-1]
        more_uri=make_encoded_uri(user_key,uri_for_more,more_param)
        ref=Ref.directory(name=name_for_more, uri=make_uri(more_uri))
        refs.append(ref)

    _cache.refs.add(uri,refs)
    return refs
    
def list_tag(tag):
    latest=Ref.album(name=u'latest',
        uri=make_encoded_uri(u'/discover'+tag,uri_latest))
    popular=Ref.album(name=u'popular',
        uri=make_encoded_uri(u'/discover'+tag,uri_popular))

    return [latest,popular]    

def list_user(user_name):
    
    try:
        name=user_name[1:-1]
        decoded=urllib.unquote(name)
        pre0=u'{} '.format(decoded)
        pre=u"{}'s ".format(decoded)
    except:
        pre0=''
        pre = u''
        
    cloudcasts=Ref.album(name=pre+u'cloudcasts',
        uri=make_encoded_uri(user_name,uri_cloudcasts))
    favorites=Ref.directory(name=pre+u'favorites',
        uri=make_encoded_uri(user_name,uri_favorites))
    playlists=Ref.directory(name=pre+u'playlists',
        uri=make_encoded_uri(user_name,uri_playlists))
    following=Ref.directory(name=pre0+u'follows',
        uri=make_encoded_uri(user_name,uri_following))
    followers=Ref.directory(name=pre+u'followers',
        uri=make_encoded_uri(user_name,uri_followers))
    listens=Ref.directory(name=pre0+u'listened to',
        uri=make_encoded_uri(user_name,uri_listens))
    return [cloudcasts,favorites,playlists,following,followers,listens]
                   
def list_user_categories():
    cat_refs=_cache.refs.get(uri_userscategories)
    if cat_refs is not None: return cat_refs
    categories = get_json(uri_categories)['data']
    cat_refs = []
    for category in categories:
        uri=make_uri(api_prefix+category['key']+u'users/')
        name=category['name']
        cat_refs.append(Ref.directory(name=name,uri=uri))
    _cache.refs.add(uri_userscategories, cat_refs)
    return cat_refs

def list_cloudcast_categories():
    cat_refs=_cache.refs.get(uri_categories)
    if cat_refs is not None: return cat_refs
    categories = get_json(uri_categories)['data']
    cat_refs = []
    for category in categories:
        uri=make_uri(api_prefix+category['key']+u'cloudcasts/')
        name=category['name']
        cat_refs.append(Ref.directory(name=name,uri=uri))
    _cache.refs.add(uri_categories, cat_refs)
    return cat_refs

def list_category_users(uri):
    refs=_cache.refs.get(uri)
    if refs is not None: return refs

    json=get_json(uri)
    users=json['data']
    refs=[]
    for user in users:
        name=user['username']
        key=user['key']
        user_uri=make_encoded_uri(key,uri_user)
        ref=Ref.directory(name=name,uri=user_uri)
        refs.append(ref)

    more=next_page_ref(json,u'users')
    if more is not None:
        refs.append(more)

    _cache.refs.add(uri,refs)
    return refs

def list_cloudcasts(uri,unused=''):
    return get_refs_for_uri(uri,_cache.search_max)
    
def list_refs(uri):
    # listing categories
    if uri.endswith(uri_categories): return list_cloudcast_categories()
    if uri.endswith(uri_userscategories): return list_user_categories()
    
    # something already cached
    refs=_cache.refs.get(uri)
    if refs is not None: return refs
    
    refs = []
    
    # users
    if uri.endswith(uri_users):
        #first users per category
        refs.append(
            Ref.directory(name=u'Categories',uri=make_uri(uri_userscategories)))
        for user in _cache.users:
            ref=Ref.directory(name=user,
                uri=make_encoded_uri(u'/{}/'.format(user),uri_user))
            refs.append(ref)
        return refs
    
    # a user
    (user_key,more)=strip_encoded_uri(uri,uri_user)
    if user_key is not None:
        refs=list_user(user_key)
        _cache.refs.add(uri,refs)
        return refs

    # tags
    if uri.endswith(uri_tags):
        for tag in _cache.tags:
            ref=Ref.directory(name=tag,
                uri=make_encoded_uri(u'/{}/'.format(tag),uri_tag))
            refs.append(ref)
        return refs
    
    # a tag
    (tag,more)=strip_encoded_uri(uri,uri_tag)
    if tag is not None:
        refs=list_tag(tag)
        _cache.refs.add(uri,refs)
        return refs

    # list of cloudcasts, could be from a number of sources
    refs=refs_from_encoded_uri(uri, uri_cloudcasts, list_cloudcasts)
    if refs is not None: 
        _cache.refs.add(uri,refs)
        return refs        
    refs=refs_from_encoded_uri(uri, uri_popular, list_cloudcasts)
    if refs is not None: 
        _cache.refs.add(uri,refs)
        return refs        
    refs=refs_from_encoded_uri(uri, uri_latest, list_cloudcasts)
    if refs is not None: 
        _cache.refs.add(uri,refs)
        return refs        

    # user's lists
    refs=refs_from_encoded_uri(uri, uri_listens, list_cloudcasts)
    if refs is not None: 
        _cache.refs.add(uri,refs)
        return refs        
    refs=refs_from_encoded_uri(uri, uri_favorites, list_cloudcasts)
    if refs is not None: 
        _cache.refs.add(uri,refs)
        return refs        
    refs=refs_from_encoded_uri(uri, uri_playlists, list_playlists)
    if refs is not None: 
        _cache.refs.add(uri,refs)
        return refs        
    refs=refs_from_encoded_uri(uri, uri_following, list_fols)
    if refs is not None: 
        _cache.refs.add(uri,refs)
        return refs        
    refs=refs_from_encoded_uri(uri, uri_followers, list_fols)
    if refs is not None: 
        _cache.refs.add(uri,refs)
        return refs        
    
    
    # category of users
    if uri_users in uri and 'categories' in uri:
       refs=list_category_users(uri)
       _cache.refs.add(uri,refs)
       return refs    

    # everything else
    refs=list_cloudcasts(uri)
    _cache.refs.add(uri,refs)
    return refs    

def list_users(uri, max_artists):
    json=get_json(uri)
    artists_dict=json['data']
    artists = []
    #artists are in fact users
    _cache.users=_cache.default_users[:]
    for artist in artists_dict:
        key=artist['key']
        name=artist['name']
        username=artist['username']
        uri=make_uri(api_prefix+key+u'cloudcasts/')
        ref=Artist(name=name, uri=uri)
        _cache.add_thumbnail(artist,ref.uri)
        artists.append(ref)
        if username not in _cache.users: _cache.users.append(username)
        
    more=next_page_uri(json)
    so_far = len(artists)
    if more is not None and so_far < max_artusts:
            more_artists=list_users(make_uri(more),max_artists-so_far)
            artists=artists+more_artists
    return artists

def list_tags(tag, uri, max_albums):
    json=get_json(uri)
    albums_dict=json['data']
    albums = []
    #albums are in fact tags
    for album in albums_dict:
        key=album['key']
        name=album['name']
        uri=make_uri(api_prefix+key+u'latest/')
        ref=Album(name=name, uri=uri)
        _cache.add_thumbnail(album,ref.uri)
        albums.append(ref)
        
    more=next_page_uri(json)
    so_far = len(albums)
    if more is not None and so_far < max_albums:
            more_albums=list_tags(tag,make_uri(more),max_albums-so_far)
            albums=albums+more_albums
    if tag not in _cache.tags: 
        _cache.tags=_cache.default_tags[:]
        _cache.tags.append(tag)
    return albums

class MopidyMixcloud(pykka.ThreadingActor, Backend):
    uri_schemes = [u'mixcloud']
 
    def __init__(self, config, audio):
        super(MopidyMixcloud, self).__init__()
        _cache.from_config(config)
        
        self.library = MixcloudLibrary(self)
        self.playback = MixcloudPlayback(audio=audio, backend=self)
        self.playlists = MixcloudPlaylists(self)
        
class MixcloudPlaylists(PlaylistsProvider):
    def __init__(self,backend):
        super(MixcloudPlaylists, self).__init__(backend)

    def as_list(self):
        playlists=[]
        for u in _cache.users:
            uri=u'{}/{}/{}'.format(api_prefix,u,uri_playlists)
            refs=_cache.refs.get(uri)
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
        playlist=_cache.playlists.get(uri)
        if playlist is not None: return playlist
        
        name=strip_uri(uri)[len(api_prefix)+1:-len(u'/cloudcasts/')]
        tracks=get_tracks_for_uri(strip_uri(uri),_cache.search_max)
        playlist=Playlist(uri=uri,name=name,tracks=tracks)
        _cache.playlists.add(uri,playlist)
        return playlist

    def refresh(self):
        _cache.clear()

class MixcloudLibrary(LibraryProvider):
    root_uri=uri_root
    root_directory = Ref.directory(uri=root_uri, name='Mixcloud')
 
    def __init__(self, backend):
        super(MixcloudLibrary, self).__init__(backend)
 
    def browse(self, uri):
        _cache.refresh()
        if not uri.startswith(uri_prefix):
            return []
                       
        if uri==uri_root:
            return root_list
        else:
            try:
                return list_refs(uri)
            except MixcloudException:#someone encoded our uris
                return list_refs(urllib.unquote(uri))
                           
    def refresh(self, uri=None):
        _cache.clear(True)
        
    def lookup(self, uri, uris=None):
        if uri is None and uris is None: return []
        if uri is not None:
            tracks=_cache.lookup.get(uri)
            if tracks is not None: return tracks
            track=_cache.tracks.get(uri)
            if track is not None: return [track]
            if uri_cloudcasts in uri:
                (username,more)=strip_encoded_uri(uri,uri_cloudcasts)
            elif uri_user in uri:
                (username,more)=strip_encoded_uri(uri,uri_user)
            else:
                ref=get_tracks_for_uri(uri,_cache.search_max)
                _cache.lookup.add(uri,ref)
                return ref
     
            turi=uri
            if username is not None:
                turi=compose_uri(username,uri_cloudcasts)+more
            if turi is not None:
                ref=get_tracks_for_uri(turi,_cache.search_max)
                _cache.lookup.add(uri,ref)
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
        _cache.refresh()
        if uris is not None:
            if next((uri for uri in uris if uri.startswith(uri_prefix)),
                None) is None:
                return None
                   
        if query is None or len(query)==0: return None
 
        query_type=u'cloudcast'
        query_value=u''
                   
        # look for the first query key that we can deal with
        for k in query:
            q=query[k]
            if q[0].startswith('refresh:'):
                _cache.clear(True)
                q[0]=q[0][len('refresh:'):]
            
            if q[0].startswith('user:'):
                query_type='user'
                query_value=q[0][len('user:'):]
                break
            if q[0].startswith('tag:'):
                query_type='tag'
                query_value=q[0][len('tag:'):]
                break
            if q[0].startswith('city:'):
                query_type='city'
                query_value=q[0]
                break
            if k in ['artist','albumartist','composer','performer']:
                query_type='user'
                query_value=q[0]
                break
            if k in ['any','track_name']:
                query_value=q[0]
                break
                               
        if query_value==u'': return None
 
        search_uri=uri_search.format(query_type,query_value)
        sr = _cache.searches.get(search_uri)
        if sr is not None: return sr
        res=None
        if query_type=='user':
            users=list_users(search_uri,_cache.search_max)
            res=SearchResult(uri=search_uri,artists=users)
        elif query_type=='tag':
            tags=list_tags(query_value,search_uri,_cache.search_max)
            res=SearchResult(uri=search_uri,albums=tags)
        elif query_type=='city':
            search_uri=uri_city.format(query_value)
            if query_value not in _cache.tags: 
                _cache.tags=_cache.default_tags[:]
                _cache.tags.append(query_value)
            tracks=get_tracks_for_uri(search_uri,_cache.search_max)
            res=SearchResult(uri=search_uri,tracks=tracks)
        else:
            tracks=get_tracks_for_uri(search_uri,_cache.search_max)
            res=SearchResult(uri=search_uri,tracks=tracks)
        _cache.searches.add(search_uri,res)
        return res
               
    def get_images(self,uris):
        ret={}
        for uri in uris:
            img=_cache.images.get(uri)
            if img is not None: ret[uri]=[img]
        return ret
                   
class MixcloudPlayback(PlaybackProvider):
    def translate_uri(self, uri): 
        return get_stream_url(uri)
