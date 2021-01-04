from .cache import Cache
import time
from mopidy.models import Image

class LocalData:

    def __init__(self):
        self.users=[]
        self.default_users=[]
        self.tags=[]
        self.default_tags=[]
        self.search_max=20
        self.images=Cache() # uri -> [Image]
        self.tracks=Cache() # uri -> Track
        self.refs=Cache()   # uri -> list of Ref              
        self.searches=Cache() # uri -> SearchResult
        self.playlists=Cache() #uri -> Playlist
        self.lookup=Cache() #uri -> [Track]
        self.urls=Cache() #uri -> url
        self.refresh_period=600 #10 min
        self.last_refresh_time=0
        self.ignore_exclusive=True

    def from_config(self,config):
        cfg=config['mixcloud']['users']
        if cfg:
            self.default_users=cfg.split(',')
            self.default_users=[x.strip() for x in self.default_users]
        else:
            self.default_users=[]
        self.users=self.default_users[:]
        cfg=config['mixcloud']['tags']
        if cfg:
            self.default_tags=cfg.split(',')
            self.default_tags=[x.strip() for x in self.default_tags]
        else:
            self.default_tags=[]
        self.tags=self.default_tags[:]
        cfg=config['mixcloud']['search_max']
        if cfg:
            self.search_max=cfg
        cfg=config['mixcloud']['refresh_period']
        if cfg:
            self.refresh_period=cfg
        cfg=config['mixcloud']['ignore_exclusive']
        if cfg is not None:
            self.ignore_exclusive=cfg

    def refresh(self):
        t=time.time()
        if t==0 or (t-self.last_refresh_time) > self.refresh_period:
            self.last_refresh_time=t
            self.clear()
        
    def clear(self,reset_users=False):
        self.tracks.clear()
        self.refs.clear()
        self.searches.clear()
        self.playlists.clear()
        self.lookup.clear()
        self.urls.clear()
        if reset_users:
            self.users=self.default_users[:]
            self.tags=self.default_tags[:]

    # thumbnails have a bit of a fiddly handling
    def add_thumbnail(self,jsdict,uri):
        pics = []
        if 'pictures' in jsdict:
            if 'medium' in jsdict['pictures']:
                pics.append(Image(uri=jsdict['pictures']['medium'])) 
            elif 'large' in jsdict['pictures']:
                pics.append(Image(uri=jsdict['pictures']['large'])) 
            elif 'thumbnail' in jsdict['pictures']:
                pics.append(Image(uri=jsdict['pictures']['thumbnail'])) 
        if len(pics)>0:
            self.images.add(uri,pics) 
        return pics    
        
class MixcloudException(Exception):
    def __init__(self, value):
        self.parameter = value
    
    def __str__(self):
        return repr(self.parameter)
