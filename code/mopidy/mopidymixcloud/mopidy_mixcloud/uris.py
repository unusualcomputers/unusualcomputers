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

