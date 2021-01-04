from mopidy.models import Ref,Track,Album,Artist
import requests
import urllib
import sys
import youtube_dl
from .util import LocalData,MixcloudException
from .uris import *
# backwards compatibility
def urllibquote(s):
    if sys.version_info >= (3, 0):
        return urllib.parse.quote(s)
    else:
        return urllib.quote(s)

def urllibunquote(s):
    if sys.version_info >= (3, 0):
        return urllib.parse.unquote(s)
    else:
        return urllib.unquote(s)

# all cached data is here
cache=LocalData()

# this is where we make calls to mixcloud api
def get_json(uri):
    url=strip_uri(uri)
    r=requests.get(url)
    if not r.ok: raise MixcloudException('Request failed for uri {}'.format(uri))
    return r.json()

# dealing with various internal uri formats
def make_encoded_uri(user_key,uri_prefix,more=''):
    if sys.version_info >= (3, 0):
        special=make_uri(uri_prefix+'#'+user_key)
    else:
        try:
            enc=user_key.encode('base64')
        except:
            enc=user_key.encode('utf-8').encode('base64')
        special=make_uri(uri_prefix+'#'+enc)
    return u'{}#base64#{}'.format(special,more)
        
def strip_encoded_uri(uri,uri_prefix):
    uri=strip_uri(uri)
    if uri.startswith(uri_prefix):
        elements=uri.split('#')
        user_key=elements[1]
        more=elements[-1]
        if sys.version_info >= (3, 0):
            return (user_key,more)
        else:
            return (user_key.decode('base64'),more)
    else:
        return (None,None)
        
def compose_uri(user_key,uri_prefix):
    try:
        return api_prefix+user_key+uri_prefix
    except:
        if sys.version_info >= (3, 0):
            return api_prefix+urllib.parse.quote(user_key)+uri_prefix
        else:
            return api_prefix+urllib.quote(user_key)+uri_prefix

def make_more_name(user_key,group):
    try:
        decoded=urllibunquote(user_key)
        return u"More {}'s {}...".format(decoded,group)
    except:
        return u"More {}...".format(group)

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
    track=cache.tracks.get(uri)
    if track is None:
        is_exclusive=cloudcast.get('is_exclusive',False)
        if is_exclusive and cache.ignore_exclusive:
            return (None,None)
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
        
        cache.tracks.add(uri,track)
        cache.add_thumbnail(cloudcast,uri)
    else:
        refs=cache.refs.get(uri)
        if refs is not None:
            ref=refs[0]
        else:
            ref=Ref.track(name=track.name, uri=uri)
    return (ref,track)

def get_tracks_refs_for_uri(uri,max_tracks):

    if uri.endswith(uri_categories): return ([],[])

    track=cache.tracks.get(uri)
    if track is not None: # this is a cached track
        refs=cache.refs.get(uri)
        if refs is None:
            refs=[Ref.track(name=track.name, uri=track.uri)]
            cache.refs.add(uri,refs)
        return [track],refs
    if track_prefix in uri: # this is a new track
        key=strip_track_uri(uri)
        cloudcast=get_json(api_prefix+key)
        (ref,track)=make_track(cloudcast)
        if ref is None: 
            return [],[]
        refs=[ref]
        tracks=[track]
        cache.refs.add(uri,refs)
        return tracks,refs

    # this is some other list of tracks
    json=get_json(uri)
    cloudcasts=json['data']
    refs=[]
    tracks = []

    count=0
    for cloudcast in cloudcasts:
        (ref,track)=make_track(cloudcast)
        count=count+1
        if ref is not None:
            refs.append(ref)
            tracks.append(track)

    more=next_page_uri(json)
    so_far=len(tracks)
    if so_far+5>count:so_far=count
    if more is not None: 
        if so_far<max_tracks:
            more_tracks,more_refs=get_tracks_refs_for_uri(make_uri(more),max_tracks-so_far)
            tracks=tracks+more_tracks
            refs=refs+more_refs
        else:
            more_param=more.split('/')[-1]
            ref=Ref.directory(
                name=u'More tracks...', 
                uri=make_uri(more))
            refs.append(ref)
   
 
    cache.refs.add(uri,refs)
    return tracks,refs


def get_tracks_for_uri(uri,max_tracks):
    return get_tracks_refs_for_uri(uri,max_tracks)[0]

def get_refs_for_uri(uri,max_tracks):
    return get_tracks_refs_for_uri(uri,max_tracks)[1]

# get stream url
ydl=youtube_dl.YoutubeDL()
def get_stream_url(uri):
    url=cache.urls.get(uri)
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
        cache.urls.add(uri,url) 
        return url
    else:
        return uri

# traversing mixcloud data
def list_playlists(uri,user_key):
    refs=cache.refs.get(uri)
    if refs is not None: return refs

    json=get_json(uri)
    playlists=json['data']
    refs=[]
    for playlist in playlists:
        user_name=playlist['name']
        key=urllibquote(playlist['key'])
        playlist_uri=api_prefix+key+u'cloudcasts/'
        ref=Ref.playlist(name=user_name,uri=make_uri(playlist_uri))
        refs.append(ref)

    more=next_page_uri(json)
    if more is not None:
        more_param=more.split('/')[-1]
        more_uri=make_encoded_uri(user_key,uri_playlists,more_param)
        ref=Ref.directory(name=make_more_name(user_key,u'playlists'), uri=make_uri(more_uri))
        refs.append(ref)

    cache.refs.add(uri,refs)
    return refs

def list_fols(uri,user_key): # followers or following
    refs=cache.refs.get(uri)
    if refs is not None: return refs

    json=get_json(uri)
    fols=json['data']
    refs=[]
    for fol in fols:
        name=fol['username']
        key=fol['key']
        fol_uri=make_encoded_uri(key,uri_user)
        cache.add_thumbnail(fol,fol_uri)
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

    cache.refs.add(uri,refs)
    return refs
    
def list_tag(tag):
    latest=Ref.directory(name=u'latest',
        uri=make_encoded_uri('/discover{}'.format(tag),uri_latest))
    popular=Ref.directory(name=u'popular',
        uri=make_encoded_uri('/discover{}'.format(tag),uri_popular))

    return [latest,popular]    

def get_user_images(uri):
    (user_key,more)=strip_encoded_uri(uri,uri_user)
    if user_key is None: return []
    #key=urllibquote(user_key)
    key=user_key
    url=api_prefix+key
    data=get_json(url)
    return cache.add_thumbnail(data,make_encoded_uri(user_key,uri_user))

def list_user(user_name):
    
    try:
        name=user_name[1:-1]
        decoded=urllibunquote(name)
        pre0=u'{} '.format(decoded)
        pre=u"{}'s ".format(decoded)
    except:
        pre0=''
        pre = u''
        
    cloudcasts=Ref.directory(name=pre+u'cloudcasts',
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
    cat_refs=cache.refs.get(uri_userscategories)
    if cat_refs is not None: return cat_refs
    categories = get_json(uri_categories)['data']
    cat_refs = []
    for category in categories:
        uri=make_uri(api_prefix+category['key']+u'users/')
        name=category['name']
        cat_refs.append(Ref.directory(name=name,uri=uri))
    cache.refs.add(uri_userscategories, cat_refs)
    return cat_refs

def list_cloudcast_categories():
    cat_refs=cache.refs.get(uri_categories)
    if cat_refs is not None: return cat_refs
    categories = get_json(uri_categories)['data']
    cat_refs = []
    for category in categories:
        uri=make_uri(api_prefix+category['key']+u'cloudcasts/')
        name=category['name']
        cat_refs.append(Ref.directory(name=name,uri=uri))
    cache.refs.add(uri_categories, cat_refs)
    return cat_refs

def list_category_users(uri):
    refs=cache.refs.get(uri)
    if refs is not None: return refs

    json=get_json(uri)
    users=json['data']
    refs=[]
    for user in users:
        name=user['username']
        key=user['key']
        user_uri=make_encoded_uri(key,uri_user)
        cache.add_thumbnail(user,user_uri)
        ref=Ref.directory(name=name,uri=user_uri)
        refs.append(ref)

    more=next_page_ref(json,u'users')
    if more is not None:
        refs.append(more)

    cache.refs.add(uri,refs)
    return refs

def list_cloudcasts(uri,unused=''):
    return get_refs_for_uri(uri,cache.search_max)
    
def refs_from_encoded_uri(uri, more_uri, list_f):
    (user_key,more)=strip_encoded_uri(uri,more_uri)
    if user_key is None: return None
    urir=compose_uri(user_key,more_uri)+more
    refs=list_f(urir,user_key)
    cache.refs.add(uri,refs)
    return refs    

# list refs is the main browsing function
def list_refs(uri):
    # listing categories
    if uri.endswith(uri_categories): return list_cloudcast_categories()
    if uri.endswith(uri_userscategories): return list_user_categories()
    
    # something already cached
    refs=cache.refs.get(uri)
    if refs is not None: return refs
    
    refs = []
    
    # users
    if uri.endswith(uri_users):
        #first users per category
        refs.append(
            Ref.directory(name=u'Categories',uri=make_uri(uri_userscategories)))
        for user in cache.users:
            ref=Ref.directory(name=user,
                uri=make_encoded_uri(u'/{}/'.format(user),uri_user))
            refs.append(ref)
        return refs
    
    # a user
    (user_key,more)=strip_encoded_uri(uri,uri_user)
    if user_key is not None:
        refs=list_user(user_key)
        cache.refs.add(uri,refs)
        return refs

    # tags
    if uri.endswith(uri_tags):
        for tag in cache.tags:
            ref=Ref.directory(name=tag,
                uri=make_encoded_uri(u'/{}/'.format(tag),uri_tag))
            refs.append(ref)
        return refs
    
    # a tag
    (tag,more)=strip_encoded_uri(uri,uri_tag)
    if tag is not None:
        refs=list_tag(tag)
        cache.refs.add(uri,refs)
        return refs

    # list of cloudcasts, could be from a number of sources
    refs=refs_from_encoded_uri(uri, uri_cloudcasts, list_cloudcasts)
    if refs is not None: 
        cache.refs.add(uri,refs)
        return refs        
    refs=refs_from_encoded_uri(uri, uri_popular, list_cloudcasts)
    if refs is not None: 
        cache.refs.add(uri,refs)
        return refs        
    refs=refs_from_encoded_uri(uri, uri_latest, list_cloudcasts)
    if refs is not None: 
        cache.refs.add(uri,refs)
        return refs        

    # user's lists
    refs=refs_from_encoded_uri(uri, uri_listens, list_cloudcasts)
    if refs is not None: 
        cache.refs.add(uri,refs)
        return refs        
    refs=refs_from_encoded_uri(uri, uri_favorites, list_cloudcasts)
    if refs is not None: 
        cache.refs.add(uri,refs)
        return refs        
    refs=refs_from_encoded_uri(uri, uri_playlists, list_playlists)
    if refs is not None: 
        cache.refs.add(uri,refs)
        return refs        
    refs=refs_from_encoded_uri(uri, uri_following, list_fols)
    if refs is not None: 
        cache.refs.add(uri,refs)
        return refs        
    refs=refs_from_encoded_uri(uri, uri_followers, list_fols)
    if refs is not None: 
        cache.refs.add(uri,refs)
        return refs        
    
    
    # category of users
    if uri_users in uri and 'categories' in uri:
       refs=list_category_users(uri)
       cache.refs.add(uri,refs)
       return refs    

    # everything else
    refs=list_cloudcasts(uri)
    cache.refs.add(uri,refs)
    return refs    

def list_users(uri, max_artists):
    json=get_json(uri)
    artists_dict=json['data']
    artists = []
    #artists are in fact users
    cache.users=cache.default_users[:]
    for artist in artists_dict:
        key=artist['key']
        name=artist['name']
        username=artist['username']
        uri=make_uri(api_prefix+key+u'cloudcasts/')
        ref=Artist(name=name, uri=uri)
        cache.add_thumbnail(artist,make_encoded_uri(key,uri_user))
        cache.add_thumbnail(artist,uri)
        artists.append(ref)
        if username not in cache.users: cache.users.append(username)
        
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
        cache.add_thumbnail(album,uri)
        albums.append(ref)
        
    more=next_page_uri(json)
    so_far = len(albums)
    if more is not None and so_far < max_albums:
            more_albums=list_tags(tag,make_uri(more),max_albums-so_far)
            albums=albums+more_albums
    if tag not in cache.tags: 
        cache.tags=cache.default_tags[:]
        cache.tags.append(tag)
    return albums

