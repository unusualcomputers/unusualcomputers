# I have learned a lot from jackyNIX's code for kodi mopidy plugin
# https://github.com/jackyNIX/xbmc-mixcloud-plugin

from mopidy.backend import *
from mopidy.models import Ref,SearchResult,Playlist
import pykka
import urllib
import sys
from .util import MixcloudException
from .uris import *
from .mixcloud_data import *

# top level menus
root_list=[ 
        Ref.directory(name=u'Categories',uri=make_uri(uri_categories)), 
        Ref.directory(name=u'Users',uri=make_uri(uri_users)), 
        Ref.directory(name=u'Tags',uri=make_uri(uri_tags))] 


# Mopidy interface
class MopidyMixcloud(pykka.ThreadingActor, Backend):
    uri_schemes = [u'mixcloud']
 
    def __init__(self, config, audio):
        super(MopidyMixcloud, self).__init__()
        cache.from_config(config)
        
        self.library = MixcloudLibrary(self)
        self.playback = MixcloudPlayback(audio=audio, backend=self)
        self.playlists = MixcloudPlaylists(self)
        
class MixcloudPlaylists(PlaylistsProvider):
    def __init__(self,backend):
        super(MixcloudPlaylists, self).__init__(backend)

    def as_list(self):
        playlists=[]
        for u in cache.users:
            uri=u'{}/{}/{}'.format(api_prefix,u,uri_playlists)
            refs=cache.refs.get(uri)
            if refs is None: 
                refs=list_playlists(uri,'/{}/'.format(u))
            if refs is not None:
                playlists=playlists+refs
        return playlists        

    def get_items(self, uri):
        try:
            return list_refs(uri)
        except MixcloudException:#someone encoded our uris
            if sys.version_info >= (3, 0):
                return list_refs(urllib.parse.unquote(uri))
            else:
                return list_refs(urllib.unquote(uri))

    def lookup(self, uri):
        playlist=cache.playlists.get(uri)
        if playlist is not None: return playlist
        
        name=strip_uri(uri)[len(api_prefix)+1:-len(u'/cloudcasts/')]
        tracks=get_tracks_for_uri(strip_uri(uri),cache.search_max)
        playlist=Playlist(uri=uri,name=name,tracks=tracks)
        cache.playlists.add(uri,playlist)
        return playlist

    def refresh(self):
        cache.clear()

class MixcloudLibrary(LibraryProvider):
    root_uri=uri_root
    root_directory = Ref.directory(uri=root_uri, name='Mixcloud')
 
    def __init__(self, backend):
        super(MixcloudLibrary, self).__init__(backend)
 
    def browse(self, uri):
        cache.refresh()
        if not uri.startswith(uri_prefix):
            return []
                       
        if uri==uri_root:
            return root_list
        else:
            try:
                return list_refs(uri)
            except MixcloudException:#someone encoded our uris
                if sys.version_info >= (3, 0):
                    return list_refs(urllib.parse.unquote(uri))
                else:
                    return list_refs(urllib.unquote(uri))
                           
    def refresh(self, uri=None):
        cache.clear(True)
        
    def lookup(self, uri, uris=None):
        if uri is None and uris is None: return []
        if uri is not None:
            tracks=cache.lookup.get(uri)
            if tracks is not None: return tracks
            track=cache.tracks.get(uri)
            if track is not None: return [track]
            if uri_cloudcasts in uri:
                (username,more)=strip_encoded_uri(uri,uri_cloudcasts)
            elif uri_user in uri:
                (username,more)=strip_encoded_uri(uri,uri_user)
            else:
                ref=get_tracks_for_uri(uri,cache.search_max)
                cache.lookup.add(uri,ref)
                return ref
     
            turi=uri
            if username is not None:
                turi=compose_uri(username,uri_cloudcasts)+more
                ref=get_tracks_for_uri(turi,cache.search_max)
                cache.lookup.add(uri,ref)
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
        cache.refresh()
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
                cache.clear(True)
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
        sr = cache.searches.get(search_uri)
        if sr is not None: return sr
        res=None
        if query_type=='user':
            users=list_users(search_uri,cache.search_max)
            res=SearchResult(uri=search_uri,artists=users)
        elif query_type=='tag':
            tags=list_tags(query_value,search_uri,cache.search_max)
            res=SearchResult(uri=search_uri,albums=tags)
        elif query_type=='city':
            search_uri=uri_city.format(query_value)
            if query_value not in cache.tags: 
                cache.tags=cache.default_tags[:]
                cache.tags.append(query_value)
            tracks=get_tracks_for_uri(search_uri,cache.search_max)
            res=SearchResult(uri=search_uri,tracks=tracks)
        else:
            tracks=get_tracks_for_uri(search_uri,cache.search_max)
            res=SearchResult(uri=search_uri,tracks=tracks)
        cache.searches.add(search_uri,res)
        return res
               
    def get_images(self,uris):
        ret={}
        for uri in uris:
            img=cache.images.get(uri)
            if img: ret[uri]=img
            img=get_user_images(uri)
            if img: ret[uri]=img
        return ret
                   
class MixcloudPlayback(PlaybackProvider):
    def translate_uri(self, uri): 
        return get_stream_url(uri)
