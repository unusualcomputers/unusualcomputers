from __future__ import unicode_literals

import logging
import os
import tornado.web
from mopidy.models import Ref
from mopidy import config, ext
from mopidy_rough_base.mopidy_browser import MopidyBrowser
from mopidy_rough_base.feedparsing import CachedFeedParser
import datetime
from htmltemplates import *
import urllib

__version__ = '1.0.0'

logger = logging.getLogger(__name__)
_feedparser = CachedFeedParser()
browser = None
def create_browser(core):
    global browser
    if browser is None:
        browser = MopidyBrowser(core,None,False)
    return browser

refresh_html=''
def flip_refresh():
    global refresh_html
    if len(refresh_html) == 0:
        refresh_html='<meta http-equiv="refresh" content="10" >'
    else:
        refresh_html=''
    
# miliseconds to a time string
def to_time_string(ms):
    ss=int(ms)/1000
    h=ss/(60*60)
    m=(ss-h*60*60)/60
    s=(ss-h*60*60-m*60)
    if h!=0:
        return '{}:{:02d}:{:02d}'.format(h,m,s)
    else:
        return '{:02d}:{:02d}'.format(m,s)

def dec(s):
    return s.decode('utf-8','replace')
    

class GlobalsHandler(tornado.web.RequestHandler):
    def initialize(self, core):
        self.core = core
        self.browser = create_browser(core)
        

    def get(self):
        ref = self.request.headers['Referer']
        action=self.get_argument('action',None)
        if action=='refresh_onoff':
            flip_refresh()
        elif action=='loopall':
            self.browser.flip_loop()
        self.redirect(ref)

class TrackHandler(tornado.web.RequestHandler):
    def initialize(self, core):
        self.core = core
        self.browser = create_browser(core)
        

    def get(self):
        ref = self.request.headers['Referer']
        action=self.get_argument('action',None)
        uri=self.get_argument('uri',None)
        uri=urllib.unquote(uri)
        if action=='play_now':
            self.browser.play_now_uri(uri)
        elif action=='play_next':
            self.browser.play_next_uri(uri)
        elif action=='add_to_queue':
            self.browser.add_to_tracks_uri(uri)
        elif action=='remove_from_queue':
            self.browser.remove_from_tracks_uri(uri)
        elif action=='loop_this':
            self.browser.loop_now_uri(uri)
        self.redirect(ref)

#   playback( action = "prev" | "rew10m" | "rew3m" | "rew20s" | "playpause" | "ffwd20s" | "ffwd3m" | "ffwd10m" | "next" )

class PlaybackHandler(tornado.web.RequestHandler):
    def initialize(self, core):
        self.core = core
        self.browser = create_browser(core)
        

    def get(self):
        ref = self.request.headers['Referer']
        action=self.get_argument('action',None)
        if action == 'prev': 
            self.browser.prev()
        elif action == 'rew10m': 
            self.browser.player.skip_back(10*60*1000)
        elif action == 'rew3m': 
            self.browser.player.skip_back(3*60*1000)
        elif action == 'rew20s': 
            self.browser.player.skip_back(20*1000)
        elif action == 'playpause': 
            self.browser.play_pause()
        elif action == 'ffwd20s': 
            self.browser.player.skip_fwd(20*1000)
        elif action == 'ffwd3m': 
            self.browser.player.skip_fwd(3*60*1000)
        elif action == 'ffwd10m':
            self.browser.player.skip_fwd(10*60*1000)
        elif action == 'next':
            self.browser.next()
        
        uri=self.get_argument('uri',None)
        if uri is not None:
            uri=urllib.unquote(uri)
        if action=='play_now':
            self.browser.play_now_uri(uri)
        elif action=='play_next':
            self.browser.play_next_uri(uri)
        elif action=='add_to_queue':
            self.browser.add_to_tracks_uri(uri)
        elif action=='loop_this':
            self.browser.loop_now_uri(uri)
        self.redirect(ref)


class FavouritesHandler(tornado.web.RequestHandler):
    def initialize(self, core):
        self.core = core
        self.browser = create_browser(core)
        

    def get(self):
        ref = self.request.headers['Referer']
        action=self.get_argument('action',None)
        uri=self.get_argument('uri',None)
        name=self.get_argument('name',None)
        if action=='add':
            self.browser.add_to_favourites_uri(name,uri)
        elif action=='remove':
            self.browser.remove_from_favourites_uri(name,uri)
        self.redirect(ref)
    
class VolumeHandler(tornado.web.RequestHandler):
    def initialize(self, core):
        self.core = core
        self.browser = create_browser(core)
        

    def get(self):
        ref = self.request.headers['Referer']
        vol=int(self.get_argument('vol',None))
        self.browser.set_volume(vol)
        self.redirect(ref)

class BrowsingHandler(tornado.web.RequestHandler):
    def process(self, uri=None):
        title = self.browser.current_title()
        if title == '':
            html=main_html.replace(u'[%TITLE%]','').\
                replace('[%REFRESH%]',refresh_html)
        else:
            html=main_html.replace(u'[%TITLE%]',u'- {}'.format(title)).\
                replace('[%REFRESH%]',refresh_html)
        
        if uri is not None and not uri.startswith('rough+queue') \
            and not uri.startswith('rough+history') and not uri.startswith('rough+favourites'): # no searching on top level
            uri=urllib.unquote(uri)
            if self.browser.is_channel_uri(uri) and uri.strip()!='podcast+itunes:':
                comment = _feedparser.parse_channel_desc(uri[len('podcast+'):])
                if comment is not None and len(comment) > 0: comment = comment+'<hr>'
                html=html.replace(u'[%COMMENTTEXT%]',comment)
                html=html.replace(u'[%SEARCH%]','')
            else:
                html=html.replace(u'[%SEARCH%]',search_html)
                html=html.replace(u'[%COMMENTTEXT%]','')
        else:
            html=html.replace(u'[%COMMENTTEXT%]','')
            html=html.replace(u'[%SEARCH%]','')
                
        current_track=self.browser.get_current_track_info()
        if current_track is not None:
            title=current_track['title']
            if current_track['artists'] is not None and current_track['artists']!='':
                title=title+' - ' + current_track['artists']
            playback_html=playback_control_html.replace(u'[%TRACKTITLE%]',dec(title))
            if current_track['length'] is not None \
                and current_track['current_tm'] is not None \
                and len(refresh_html)!=0:
                l=to_time_string(current_track['length'])
                c=to_time_string(current_track['current_tm'])
                t=u'{}/{}'.format(c,l)
                playback_html=playback_html.replace(u'[%TRACKTIMES%]',t)
            else:
                playback_html=playback_html.replace(u'[%TRACKTIMES%]',u'')
            html=html.replace(u'[%PLAYCONTROL%]',playback_html)        
            current_track_uri=current_track['uri']
        else:
            html=html.replace(u'[%PLAYCONTROL%]',playback_tools_html)
            current_track_uri=None       
        vol=self.browser.player.volume()
        vol_html=volume_html
        if vol == 0:
            vol_html=vol_html.replace(u'volume_mute.png',u'volume_mute_sel.png')
        elif vol == 25:
            vol_html=vol_html.replace(u'volume-1.png',u'volume-1_sel.png')
        elif vol == 50:
            vol_html=vol_html.replace(u'volume-2.png',u'volume-2_sel.png')
        elif vol == 75:
            vol_html=vol_html.replace(u'volume-3.png',u'volume-3_sel.png')
        elif vol == 100:
            vol_html=vol_html.replace(u'volume-4.png',u'volume-4_sel.png')
                    
        html=html.replace(u'[%VOLUMECONTROL%]', vol_html)
        
        items=self.browser.current_refs_data() # {'name':_,'type':_,'uri':_}
        itemshtml=[]
        has_tracks=False    
        for i in items:
            if i['name']=='Podcasts': continue
            is_track=i['type'] == Ref.TRACK
            if is_track:
                iuri=urllib.quote(i['uri'],'')
                if i['uri'].startswith('youtube:'):
                    info={'title':i['name'],'artists':None,'album':None,
                        'comment':None,'length':None, 'favorited':self.browser.is_favourited(i['uri'])} 
                else:
                    info=self.browser.get_track_info_uri(i['uri'])
                if info is None: continue
            # {'title':_,'artists':_,'album':_,'comment':_,'length':_,'favorited':_}  
                name=i['name']
                #title=info['title']
                title=name #titles look too long and ugly
                if info['favorited']:
                  ihtml=playable_item_html_favorited
                else:
                  ihtml=playable_item_html
                if self.browser.is_queue():
                    ihtml=ihtml.replace(u'action=add_to_queue',u'action=remove_from_queue').\
                        replace(u'queue_add.png',u'queue_remove.png').\
                        replace(u'alt="add to queue" title="add to queue"',u'alt="remove from queue" title="remove from queue"')
                ihtml=ihtml.replace(u'[%URI%]',iuri).replace(u'[%TITLE%]',dec(title)).\
                    replace(u'[%NAME%]',dec(name))
                if current_track_uri is not None and current_track_uri==iuri:
                    ihtml=ihtml.replace(u'play.png', u'playing.png')
                if not iuri.startswith('youtube:'):
                    comment=None
                else:
                    comment=info['comment']
                    if comment is None and \
                        title is not None and info['title'] !=name:
                            comment=info['title']
                if comment is not None:
                    chtml=comment_html.replace(u'[%COMMENTTEXT%]',comment)
                    ihtml=ihtml+chtml    
                itemshtml.append(ihtml)
                has_tracks=True
            else:
                params=urllib.urlencode(i)
                ihtml=non_playable_item_html.replace(u'[%TITLE%]',dec(i['name'])).\
                    replace(u'[%TYPENAMEURI%]',params)
                itemshtml.append(ihtml)

            
        if has_tracks:
            html=html.replace(u'[%ITEMS%]',u'<table width="100%">'+\
                    u''.join(itemshtml)+u'</table>')        
        else:
            html=html.replace(u'[%ITEMS%]',u''.join(itemshtml))        
            
        gth=global_toolbar_html
        if self.browser.is_queue():
            gth=gth.replace(u'[%LOOPALL%]',loop_all_html)
        else:
            gth=gth.replace(u'[%LOOPALL%]',u'')

        html=html.replace(u'[%GLOBAL%]',gth)          
        self.write(html)
        self.flush()
        
class SearchHandler(BrowsingHandler):
    def initialize(self, core):
        self.core = core
        self.browser = create_browser(core)
        

    def get(self):
        query=self.get_argument('query',None)
        if query is None or query == '': 
            ref = self.request.headers['Referer']
            self.redirect(ref)
            return

        self.browser.search(query)
        self.process()
        
class ListHandler(BrowsingHandler):
    def initialize(self, core):
        self.core = core
        self.browser = create_browser(core)
        

    def get(self):
        refType=self.get_argument('type',None)
        if refType == 'track': return # this should never happen
        name = self.get_argument('name',None)
        uri=self.get_argument('uri',None)
        if uri is not None: 
            uri =urllib.unquote(uri)
        self.browser.request(refType,name,uri)
        self.process(uri)            


path = os.path.abspath(__file__)
dir_path = os.path.dirname(__file__)
def rough_factory(config, core):
    return [
        ('/', ListHandler, {'core': core}),
        (r'/request.*', ListHandler, {'core': core}),
        (r'/search.*', SearchHandler, {'core': core}),
        (r'/favorites.*', FavouritesHandler, {'core': core}),
        (r'/volume.*', VolumeHandler, {'core': core}),
        (r'/track.*', TrackHandler, {'core': core}),
        (r'/playback.*', PlaybackHandler, {'core': core}),
        (r'/global.*', GlobalsHandler, {'core': core}),
        (r'/icons/(.*)', tornado.web.StaticFileHandler, {'path': dir_path+"/icons"})#/home/sheridan/unusual/code/mopidy/mopidyradioroughhtml/mopidy_radio_rough_html/icons"})
    ]


class Extension(ext.Extension):

    dist_name = 'Radio_Rough_HTML'
    ext_name = 'radio_rough_html'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        # TODO: Comment in and edit, or remove entirely
        #schema['username'] = config.String()
        #schema['password'] = config.Secret()
        return schema

    def setup(self, registry):
        
        registry.add('http:app', {
            'name': 'radiorough',
            'factory': rough_factory,
        })
