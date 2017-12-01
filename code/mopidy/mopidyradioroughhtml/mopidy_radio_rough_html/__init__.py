from __future__ import unicode_literals

import logging
import os
import tornado.web
from mopidy import config, ext
from mopidy_rough_base.mopidy_browser import MopidyBrowser

__version__ = '0.1.0'

# TODO: If you need to log, use loggers named after the current Python module
logger = logging.getLogger(__name__)

browser = None
def create_browser(core):
    global browser
    if browser is None:
        browser = MopidyBrowser(core,None)
    return browser
# miliseconds to a time string
def to_time_string(ms):
    ssi=int(ms)/1000
    h=ss/(60*60)
    m=(ss-h*60*60)/60
    s=(ss-h*60*60-m*60)
    if h!=0:
        return '{}:{:02d}:{:02d}'.format(h,m,s)
    else:
        return '{:02d}:{:02d}'.format(m,s)

class ListHandler(tornado.web.RequestHandler):
    list_html= """<!doctype html>
<html>
<head>
    <title>Radio Rough [%TITLE%] </title>
    <meta name="description" content"Radio Rough">
</head>
<body>

<h1>Radio Rough [%TITLE%] </h1>
<br><br>
[%SEARCH%]

<hr>
[%TRACKCONTROL%]
<div align="left"><pre><a href="/volume&vol=0"><img src="icons/volume_mute.png" alt="mute" title="mute" height="20"></a>   <a href="/volume&vol=25"><img src="icons/volume-1.png" alt="quiet" title="quiet" height="20"></a>   <a href="/volume&vol=50"><img src="icons/volume-2.png" alt="a bit louder" title="a bit louder" height="20"></a>   <a href="/volume&vol=75"><img src="icons/volume-3.png" alt="louder" title="louder" height="20"></a>   <a href="/volume&vol=100"><img src="icons/volume-4.png" alt="loud" title="loud" height="20"></a></pre></div>
<br>

</body>
"""
    search_html="""<div align="left">
<form align="center" action="/action_page.php">
<input type="text" name="query" value="">
<input type="submit" value="Search">
</form></div>
"""

    track_control_html="""<table width="100%">
<tr>
<td>[%TRACKTITLE%]<br>[%TRACKTIMES%]</td>
<td>
<div align="right"><pre><a href="/previous"><img src="icons/previous.png" alt="previous" title="restart/previous" height="20"></a>   <a href="/rewind&by=10m"><img src="icons/rewind-4.png" alt="skip back 10m" title="skip back 10m" height="20"></a>   <a href="/rewind&by=3m"><img src="icons/rewind-3.png" alt="skip back 3m" title="skip back 3m" height="20"></a>   <a href="/rewind&by=20s"><img src="icons/rewind-2.png" alt="skip back 20s" title="skip back 20s" height="20"></a>   <a href="/play_pause"><img src="icons/play_pause.png" alt="play/pause" title="play/pause" height="20"></a>   <a href="/ffwd&by=20s"><img src="icons/ffwd-2.png" alt="skip forward 20s" title="skip forward 20s" height="20"></a>   <a href="/ffwd&by=3m"><img src="icons/ffwd-3.png" alt="skip forward 3m" title="skip forward 3m" height="20"></a>   <a href="/ffwd&by=10m"><img src="icons/ffwd-4.png" alt="skip fowrard 10m" title="skip forward 10m" height="20"></a>   <a href="/next"><img src="icons/next.png" alt="next" title="next" height="20"></a></pre></div>
</td></tr></table>
<hr>
"""
    

    def initialize(self, core):
        self.core = core
        self.browser = create_browser(core)
        

    def get(self):
        refType=self.get_argument('type',None)
        if refType == 'track': return # this should never happen
        name = self.get_argument('name',None)
        uri=self.get_argument('uri',None)
        self.browser.request(refType,name,uri)
                
        title = self.browser.current_title()
        if title == '':
            html=self.list_html.replace('[%TITLE%]','')
        else:
            html=self.list_html.replace('[%TITLE%]',title)

        if uri is not None: # no searching on top level
            html=html.replace('[%SEARCH%]',self.search_html)
        
        current_track=self.browser.get_current_track_info()
        if current_track is not None:
            title=current_track['title']
            if current_track['artists'] is not None:
                title=title+' - ' + current_track['artists']
            track_html=replace(track_control_html,'[%TRACKTITLE%]',title)
            if current_track['length'] is not None and current_track['current_tm'] is not None:
                l=to_time_string(current_track['length'])
                c=to_time_string(current_track['current_tm'])
                t='{}/{}'.format(l,c)
                track_html=self.track_html.replace('[%TRACKTIMES%]',t)
            else:
                track_html=self.track_html.replace('[%TRACKTIMES%]','')
            html=html.replace('[%TRACKCONTROL%]',track_html)        
        else:
            html=html.replace('[%TRACKCONTROL%]','')        
        #args = self.get_argument('first')
        #print('args: {} {}'.format(self.get_argument('first'),self.get_argument('second')))
        print(self.browser.current_refs_data())
        
        self.write(html)
        self.flush()


def rough_factory(config, core):
    return [
        ('/', ListHandler, {'core': core})
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
