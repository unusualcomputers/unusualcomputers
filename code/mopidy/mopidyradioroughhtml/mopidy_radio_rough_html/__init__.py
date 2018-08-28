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
from dateutil import parser

__version__ = '3.141.5926'

logger = logging.getLogger(__name__)
refresh_html=''
refresh_period=0
_feedparser = CachedFeedParser()
browser = None
def create_browser(core):
    global browser
    if browser is None:
        browser = MopidyBrowser(core,None,False)
    return browser

def flip_refresh( l = 10):
    global refresh_html
    global refresh_period
    if len(refresh_html) == 0 or l>refresh_period:
        refresh_html='<meta http-equiv="refresh" content="{}" >'.format(l)
        refresh_period=l
    else:
        refresh_html=''
        refresh_period=0

current_waiting_to_change=None
first_pass_waiting=False
def setup_waiting_for_change(browser):
    global current_waiting_to_change
    if refresh_html != '': 
        current_waiting_to_change=None
        return
    info = browser.get_current_track_info()
    if info is None:
        current_waiting_to_change='None'
    else:
        current_waiting_to_change=info['uri']
    flip_refresh(3)
            
def check_changed(browser):
    global current_waiting_to_change
    if current_waiting_to_change is None: return
    info = browser.get_current_track_info()
    if (info is None and current_waiting_to_change != 'None') or \
        (info is not None and info['uri'] != current_waiting_to_change):
        current_waiting_to_change=None
        flip_refresh(0)
    
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
    try:
        return s.decode('utf-8','replace')
    except:
        try:
            return s.decode('utf-8','ignore')
        except:
            return s

def uri_quote(uri):
    try:
        return urllib.quote(uri,'')
    except:
        try:
            return urllib.quote(uri.encode('utf-8'),'')
        except:
            return urllib.quote(uri.decode('utf-8'),'')
                
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
        elif action=='clearqueue':
            self.browser.clear_tracks()
        elif action=='restart':
            self.write(restart_confirm_html)
            self.flush()
            return
        elif action=='really_restart':
            logger.info('Restarting mopidy.')
            #import os
            #os.system('sudo reboot')
            from subprocess import Popen
            Popen('sudo pkill -9 mopidy;sleep 5;sudo mopidy > /dev/null 2>&1 &',shell=True)
            self.redirect('/radiorough/')
            return
        elif action=='home':
            self.browser.refresh()
            self.redirect('/radiorough/')
            return
        self.redirect(ref)

class TrackHandler(tornado.web.RequestHandler):
    def initialize(self, core):
        self.core = core
        self.browser = create_browser(core)
        

    def get(self):
        ref = self.request.headers['Referer']
        action=self.get_argument('action',None)
        uri=self.get_argument('uri',None)
        if action=='play_now':
            self.browser.play_now_uri(uri)
            setup_waiting_for_change(self.browser)
        elif action=='play_next':
            self.browser.play_next_uri(uri)
        elif action=='add_to_queue':
            self.browser.add_to_tracks_uri(uri)
        elif action=='remove_from_queue':
            self.browser.remove_from_tracks_uri(uri)
        elif action=='loop_this':
            self.browser.loop_now_uri(uri)
            setup_waiting_for_change(self.browser)
        self.redirect(ref)


class PlaybackHandler(tornado.web.RequestHandler):
    def initialize(self, core):
        self.core = core
        self.browser = create_browser(core)
        

    def get(self):
        ref = self.request.headers['Referer']
        action=self.get_argument('action',None)
        if action == 'prev': 
            self.browser.prev()
            setup_waiting_for_change(self.browser)
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
            setup_waiting_for_change(self.browser)
        uri=self.get_argument('uri',None)
        if uri is not None:
            uri=urllib.unquote(uri)
        if action=='play_now':
            setup_waiting_for_change(self.browser)
            self.browser.play_now_uri(uri)
        elif action=='play_next':
            self.browser.play_next_uri(uri)
            setup_waiting_for_change(self.browser)
        elif action=='add_to_queue':
            self.browser.add_to_tracks_uri(uri)
        elif action=='loop_this':
            self.browser.loop_now_uri(uri)
            setup_waiting_for_change(self.browser)
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

def tryenc(s):
    try:
        return s.encode('utf-8')
    except:
        return s

def trydec(s):
    try:
        return s.decode('utf-8')
    except:
        return s      

def params_enc(i):
    translated={}
    for k in i.keys():
        if k=='name':
            translated[k]=tryenc(i[k])
        else:
            translated[k]=i[k]
    try:
        return urllib.urlencode(translated)
    except:
        for t in translated:
            if t=='uri':
                translated[t]=uri_quote(translated[t])#urllib.unquote(translated[t])
            print t,translated[t]    
            return urllib.urlencode(translated) 
               
class BrowsingHandler(tornado.web.RequestHandler):
    def process(self, page_title, uri=None, refType=None, message=None):
        check_changed(self.browser)    
        if page_title is None or page_title == '':
            html=main_html.replace(u'[%TITLE%]','').\
                replace('[%REFRESH%]',refresh_html)
        else:
            html=main_html.replace(u'[%TITLE%]',u'- {}'.format(page_title)).\
                replace('[%REFRESH%]',refresh_html)
        if uri is not None and not uri.startswith('rough+queue') \
            and not uri.startswith('rough+history') and not uri.startswith('rough+favourites'): # no searching on top level
            #uri=urllib.unquote(uri)
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
                if current_track['length'] is not None:
                    l=to_time_string(current_track['length'])
                    t=u'{}'.format(l)
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
        if message is None:    
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
                            'comment':None,'length':None, 
                            'favorited':self.browser.is_favourited(i['uri']),
                            'date':None} 
                    else:
                        info=self.browser.get_track_info_uri(i['uri'])

                    if info is None: continue
                    name=i['name']
                    title=name #titles look too long and ugly
                    pub_date=info['date']
                    if pub_date is None: pub_date=''
                    elif len(pub_date)==10:
                        pub_date=parser.parse(pub_date).strftime(u' (%d %b %Y) ')
                    else:
                        pub_date=u' ({}) '.format(pub_date)    


                    if info['favorited']:
                      ihtml=track_item_html_favourited
                    else:
                      ihtml=track_item_html
                    ihtml=ihtml.replace(u'[%DATE%]',pub_date)
                    if uri is not None and uri.startswith('rough+queue'):
                        ihtml=ihtml.replace(u'action=add_to_queue',u'action=remove_from_queue').\
                            replace(u'queue_add.png',u'queue_remove.png').\
                            replace(u'alt="add to queue" title="add to queue"',u'alt="remove from queue" title="remove from queue"')
                    ihtml=ihtml.replace(u'[%URI%]',iuri).replace(u'[%TITLE%]',dec(title)).\
                        replace(u'[%NAME%]',dec(name))
                    if current_track_uri is not None and current_track_uri==iuri:
                        ihtml=ihtml.replace(u'play.png', u'playing.png')
                    if iuri.startswith('youtube:'):
                        comment=None
                    else:
                        comment=info['comment']
                        if comment is None:
                            if title is not None and info['title'] !=name:
                                comment=info['title']
                    
                    if info['album'] is not None or info['artists'] is not None:
                        album_name=''
                        album_uri=None
                        album_html=''
                        artists_html=''
                        if info['album'] is not None and info['album'][0] != page_title and \
                            info['album'][0] is not None and info['album'][1] is not None and\
                            u'tunein' not in info['album'][1] and u'somafm' not in info['album'][1]:
                            album_name=trydec(info['album'][0])
                            album_uri=urllib.quote(info['album'][1],'')
                            typenameuri=u'type=album&name={}&uri={}'.format(album_name,album_uri)
                            album_html=named_link_html.replace(u'[%TYPENAMEURI%]',typenameuri).replace(u'[%NAME%]',album_name)
                        
                        if info['artists'] is not None:
                            artists=info['artists']
                            artists=[a for a in artists if a[0]!=album_name]
                            if len(artists) > 0:
                                artists_html=''
                                for a in artists:
                                    artist_name=trydec(a[0])
                                    if artist_name!=page_title and u'tunein' not in a[1] and u'somafm' not in a[1]:
                                        artist_uri=urllib.quote(a[1],'')
                                        typenameuri=u'type=artist&name={}&uri={}'.format(artist_name,artist_uri)
                                        artist_html=named_link_html.replace(u'[%TYPENAMEURI%]',typenameuri).replace(u'[%NAME%]',artist_name)
                                        if artists_html=='': artists_html=artist_html
                                        else: artists_html=artists_html+','+artist_html
                        
                        if album_html!='' and artists_html!='':
                            albumartist_html=u'{} - {}'.format(artists_html, album_html)
                        elif album_html!='':
                            albumartist_html=album_html
                        elif artists_html!='':
                            albumartist_html=artists_html
                        else:
                            albumartist_html=''
                    else:
                            albumartist_html=''

                    if comment is None: comment=u''        
                    if comment!='' or albumartist_html!='':
                        if comment=='':
                            chtml=comment_html.replace(u'[%COMMENTTEXT%]',albumartist_html).replace(u'[%ARTISTALBUM%]','')
                        elif albumartist_html=='':
                            chtml=comment_html.replace(u'[%COMMENTTEXT%]',comment).replace(u'[%ARTISTALBUM%]','')
                        else:    
                            chtml=comment_html.replace(u'[%COMMENTTEXT%]',comment).replace(u'[%ARTISTALBUM%]','<br/>&nbsp;&nbsp;&nbsp;   '+albumartist_html)
                        ihtml=ihtml+chtml   
                         
                    itemshtml.append(ihtml)
                    has_tracks=True
                else:# not track
                    is_playlist=i['type'] == Ref.PLAYLIST
                    if is_playlist:
                        name=i['name']
                        title=name #titles look too long and ugly
                        if self.browser.is_favourited(i['uri']):
                          ihtml=playlist_item_html_favorited
                        else:
                          ihtml=playlist_item_html
                        
                        params=params_enc(i)

                        iuri=urllib.quote(i['uri'],'')
                        ihtml=ihtml.replace(u'[%TYPENAMEURI%]',params)
        
                        ihtml=ihtml.replace(u'[%URI%]',iuri).replace(u'[%TITLE%]',dec(name)).\
                            replace(u'[%NAME%]',dec(name))
                        if current_track_uri is not None and current_track_uri==iuri:
                            ihtml=ihtml.replace(u'play.png', u'playing.png')
                        comment=None
                        itemshtml.append(ihtml)
                        has_tracks=True
                    else:# not playlist and not track
                        params=params_enc(i)
                        iuri=urllib.quote(i['uri'])
                        name=dec(i['name'])
                        is_playable = i['type']==Ref.ALBUM or i['type']==Ref.ARTIST
                        if uri is None:
                            ihtml=root_item_html.replace(u'[%TITLE%]',name).\
                                replace(u'[%TYPENAMEURI%]',params)
                        elif self.browser.is_favourited(i['uri']):
                            if is_playable:
                                ihtml=playable_item_html_favorited.replace(u'[%TITLE%]',name).\
                                    replace(u'[%TYPENAMEURI%]',params).\
                                    replace(u'[%URI%]',iuri).replace(u'[%NAME%]',name)
                            else:
                                ihtml=non_playable_item_html_favorited.replace(u'[%TITLE%]',name).\
                                    replace(u'[%TYPENAMEURI%]',params).\
                                    replace(u'[%URI%]',iuri).replace(u'[%NAME%]',name)
                        else:
                            if is_playable:
                                ihtml=playable_item_html.replace(u'[%TITLE%]',name).\
                                    replace(u'[%TYPENAMEURI%]',params).\
                                    replace(u'[%URI%]',iuri).replace(u'[%NAME%]',name)
                            else:    
                                ihtml=non_playable_item_html.replace(u'[%TITLE%]',name).\
                                    replace(u'[%TYPENAMEURI%]',params).\
                                    replace(u'[%URI%]',iuri).replace(u'[%NAME%]',name)
                        
                        itemshtml.append(ihtml)
            html=html.replace(u'[%ITEMS%]',u'<table cellspacing="3" width="100%">'+\
                u''.join(itemshtml)+u'</table>')        
        else:
            html=html.replace(u'[%ITEMS%]',message)
                
        if len(refresh_html)==0:
            gth=global_toolbar_html_ref_off
        else:
            gth=global_toolbar_html_ref_on
        if refType is not None and (refType=='album' or refType=='artist' or refType=='playlist'):
            play_html=play_all_html.replace(u'[%URI%]',uri_quote(uri))
        else:
            play_html=u''
        if self.browser.is_queue():
            gth=gth.replace(u'[%LOOPALL%]',loop_all_html).replace(u'[%QUEUEHTML%]',clear_queue_html).\
                replace(u'[%PLAYALL%]',play_html)
        else:
            gth=gth.replace(u'[%LOOPALL%]',u'').replace(u'[%QUEUEHTML%]',show_queue_html).\
                replace(u'[%PLAYALL%]',play_html)
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

        found=self.browser.search(query)
        if found==0:
            m=u'<br/><font size="4"><strong>&nbsp;&nbsp;Search returned no results.</strong></font><br/><br/><br/>'
            self.process('Search: '+query,'rough+search',message=m)
        else:
            self.process('Search: '+query,'rough+search')
        
class ListHandler(BrowsingHandler):
    def initialize(self, core):
        self.core = core
        self.browser = create_browser(core)
        
    def get(self):
        refType=self.get_argument('type',None)
        if refType == 'track': return # this should never happen
        name = self.get_argument('name',None)
        uri=self.get_argument('uri',None)
        try:
            self.browser.request(refType,name,uri)
        except:
            uri=urllib.unquote(uri)
            self.browser.request(refType,name,uri)
        self.process(name,uri,refType)   

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
        (r'/icons/(.*)', tornado.web.StaticFileHandler, {'path': dir_path+"/icons"})
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
        return schema

    def setup(self, registry):
        
        registry.add('http:app', {
            'name': 'radiorough',
            'factory': rough_factory,
        })
