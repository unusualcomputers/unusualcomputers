import requests
from mopidy.models import Ref,Track,Album,SearchResult,Artist,Image
from mopidy.backend import *
import pykka
import pdb

logger = logging.getLogger(__name__)

search_max=100
uri_scheme='mixcloud'
uri_prefix=uri_scheme+':'
api_prefix='https://api.mixcloud.com'
#downloader_prefix='http://www.mixcloud-downloader.com/dl/mixcloud'
downloader_prefix='http://download.mixcloud-downloader.com/d/mixcloud'
uri_categories='https://api.mixcloud.com/categories/'
uri_popular='https://api.mixcloud.com/popular/'
uri_hot='https://api.mixcloud.com/popular/hot/'
uri_new='https://api.mixcloud.com/new/'
uri_faction='https://api.mixcloud.com/FactionMix/cloudcasts/'

class MixcloudException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

def make_uri(uri):
    return uri_prefix+uri.strip()
               
def strip_uri(uri):
    if uri.startswith(uri_prefix):
        return uri[len(uri_prefix):]
    else:
        return uri

root_list=[ Ref.directory(name='Categories',uri=make_uri(uri_categories)), 
            Ref.directory(name='Popular',uri=make_uri(uri_popular)), 
            Ref.directory(name='Hot',uri=make_uri(uri_hot)), 
            Ref.directory(name='New',uri=make_uri(uri_new)),
            Ref.directory(name='FactionMix',uri=make_uri(uri_faction))] 

# uri for users: https://api.mixcloud.com/FactionMix/cloudcasts/
# search returns either:
#             a list of albums (is query was prepended by 'user:'), each of which contains a uri for users cloudcasts
#             or
#             a list of cloudcasts (with a link to more)
# so any uri that is delivered to users is either a list of cloudcasts + a uri for next page or a list of categories
 
class Cache:

    def __init__(self):
        self.data=[]
        self.max_size=250

    def clear(self):
        self.data=[]
        
    def add(self, uri, item):
        i = self.get(uri)
        if i is None:
            if len(self.data) >= self.max_size: self.data=self.data[(self.max_size/2):]
            self.data.append((uri,item))

    def get(self,uri):
        item = next((i for i in self.data if i[0]==uri),None)
        if item is not None: return item[1]
        else: return None

    

images_cache=Cache() # uri -> Image
tracks_cache=Cache() # uri -> Track
refs_cache=Cache()   # uri -> list of Ref              
searches_cache=Cache() # uri -> SearchResult
 
def clear_caches():
    tracks_cache.clear()
    refs_cache.clear()
    images_cache.clear()
    searches_cache.clear()

def uri_json(uri):
    r=requests.get(uri)
    if not r.ok: raise MixcloudException('Request failed for uri '+uri)
    return r.json()
 
def get_next_page(json_dict):
    if 'paging' not in json_dict: return None
    paging = json_dict['paging']
    if 'next' not in paging: return None
    return Ref.directory(name='More...', uri=make_uri(paging['next']))
               
def list_categories():
    cat_refs=refs_cache.get(uri_categories)
    if cat_refs is not None: return cat_refs
   
    categories = uri_json(uri_categories)['data']
    cat_refs = []
    for category in categories:
        uri=make_uri(api_prefix+category['key']+'cloudcasts/')
        name=category['name']
        cat_refs.append(Ref.directory(name=name,uri=uri))
    refs_cache.add(uri_categories, cat_refs)
    return cat_refs

def track_uri(track_key):
    return make_uri(downloader_prefix+track_key)
    
def make_track(track_key, name, user, time, length):
    uri=track_uri(track_key)
    date=time.split('T')[0]
    album=Album(uri=api_prefix+'/'+user+'/',name=user)
    artist=Artist(uri=album.uri,name=user)
    track=Track(uri=uri,name=name,album=album,artists=[artist],date=date,length=int(length)*1000)
    ref = Ref.track(name=track.name, uri=uri)
    tracks_cache.add(uri,track)
    return (ref,track)

def make_track_from_json(cloudcast):
    key=cloudcast['key']
    uri=track_uri(key)
    track=tracks_cache.get(uri)
    if track is None:
        name=cloudcast['name']
        user=cloudcast['user']['username']
        time=cloudcast['created_time']
        length=cloudcast['audio_length']
        (ref,track)=make_track(key,name,user, time, length)
        if 'pictures' in cloudcast and \
           'thumbnail' in cloudcast['pictures']:
                images_cache.add(ref.uri, Image(uri=cloudcast['pictures']['thumbnail']))
    else:
        ref = Ref.track(name=track.name, uri=uri)
    return (ref,track)
    
def list_refs(uri):
    uri=strip_uri(uri)
    if uri == uri_categories: return list_categories()
    refs=refs_cache.get(uri)
    
    if refs is not None: return refs

    json=uri_json(uri)
    cloudcasts=json['data']
    refs = []

    for cloudcast in cloudcasts:
        (ref,track)=make_track_from_json(cloudcast)
        refs.append(ref)

    more=get_next_page(json)
    if more is not None:
        refs.append(more)

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

    more=get_next_page(json)
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
    for album in albums_dict:
        key=album['key']
        name=album['name']
        uri=make_uri(api_prefix+key+'cloudcasts/')
        ref=Album(name=name, uri=uri)
        if 'pictures' in album:
            if 'thumbnail' in album['pictures']:
                images_cache.add(ref.uri, Image(uri=album['pictures']['thumbnail']))
        albums.append(ref)
    more=get_next_page(json)
    so_far = len(albums)
    if more is not None and so_far < max_tracks:
            more_albums=list_albums(more.uri,max_albums-so_far)
            albums=albums+more_albums
    return albums
               
class MopidyMixcloud(pykka.ThreadingActor, Backend):
    uri_schemes = ['mixcloud','mixcloud:']
 
    def __init__(self, config, audio):
        super(MopidyMixcloud, self).__init__()
 
        self.library = MixcloudLibrary(self)
        self.playback = MixcloudPlayback(audio=audio, backend=self)
                   
class MixcloudLibrary(LibraryProvider):
    root_uri='mixcloud:root'
    root_directory = Ref.directory(uri=root_uri, name='Mixcloud')
 
    def __init__(self, backend):
        super(MixcloudLibrary, self).__init__(backend)
 
    def browse(self, uri):
        print 'BROWSING: {}'.format(uri)
        if not uri.startswith(uri_scheme):
            return []
                       
        if uri=='mixcloud:root':
            return root_list
        else:
            return list_refs(uri)
                       
    def refresh(self, uri=None):
        clear_caches()
                       
    def lookup(self, uri, uris=None):
        print 'LOOKUP: {}'.format(uri)
        if uri is None and uris is None: return []
        if uri is not None:
            return get_tracks_for_uri(uri)
        else:
            ret={}
            for uri in uris:
                l=get_tracks_for_uri(strip_uri(uri))
                if len(l) > 0: ret[uri]=l
            return ret
                       
    def search(self, query=None, uris=None, exact=False):
        print 'SEARCHING: {} {}'.format(query,uris)

        if uris is not None:
            if next((uri for uri in uris if uri.startswith(uri_scheme)),None) is None:
                return None
                   
        if query is None: return None
 
        query_type='cloudcast'
        query_val=''
                   
        # look for the first query key that we can deal with
        for k in query:
            if k in ['artist','album','albumartist','composer','performer']:
                query_type='user'
                query_value=query[k][0]
                break
            if k in ['any','track_name']:
                q=query[k]
                if q[0].startswith('user:'):
                    query_type='user'
                    query_value=q[0][len('user:'):]
                else:
                    query_value=q[0]
                break
                               
        if query_value=='': return None
 
        search_uri='https://api.mixcloud.com/search/?type={}&q={}'.format(query_type,query_value)
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
            print 'GETTING IMAGE FOR: {}'.format(uri)
            img=images_cache.get(uri)
            if img is not None: ret[uri]=[img]
        return ret
                   
class MixcloudPlayback(PlaybackProvider):
    def translate_uri(self, uri):     
        return strip_uri(uri)
