import sys
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from urlparse import urlparse, parse_qs
import wifi_control as wifi
import time
import socket
from config_util import Config
from subprocess import Popen
import shlex
import py_game_msg as msg
import pygame


_ap_name=wifi.ap_name
_to_launch=wifi.config.get('access-point','execute_when_connected')
_sleep_on_connect=wifi.config.getint('access-point','sleep_on_connect',10)

if wifi.config.getbool('access-point','use_pygame',False):
    pygame.init()
    _msg=msg.MsgScreen()
else:
    _msg=None

_keep_running=True

def _default_reporting_func( s ):
    if _msg is not None:
        _msg.set_text( s )
    else:
        print s

_reporting_func=_default_reporting_func

def set_reporting_func( f ):
    global _reporting_func
    _reporting_func=f

def _report( s ): 
    if _reporting_func: _reporting_func( s ) 

_cnt=0
_attempting_html_template=u"""
    <!doctype html>
    <html>
    <head>
        <title>%s - Wifi</title>
        <meta name="description" content"%s - WiFi">
        <meta name="viewport" content="width=device-width">
        <meta http-equiv="Cache-Control" content="no-cache, no-store,must-revalidate"/>
        <meta http-equiv="Pragma" content="no-cache"/>
        <meta http-equiv="Expires" content="-1"/>
    <style>
        body {
            color: #ff8000;
            background-color: #200020;
            font-family: "Comic Sans MS";
            border-radius: 5px; 
            }
        input[type=submit]{
            color: #ff8000;
            background-color: #200020;
            border-color: #600060;
            border-radius: 7px; 
            border-style: solid;
            font-family: "Comic Sans MS";
            }
        input[type=password]{
            color: #ff8000;
            background-color: #800080;
            border-color: #600060;
            border-radius: 7px; 
            border-style: solid;
            font-family: "Comic Sans MS";
          }
    </style>
    </head>
    <body>

    <h1>%s - Wifi</h1>
    <br><br>
    <big>Now trying to setup wifi, follow the instructions on the screen device.</big>
    </body>
    """ % (_ap_name,_ap_name,_ap_name)

_html_template=u"""
    <!doctype html>
    <html>
    <head>
        <title>%s - Wifi</title>
        <meta name="description" content"%s - WiFi">
        <meta name="viewport" content="width=device-width">
        <meta http-equiv="Cache-Control" content="no-cache, no-store,must-revalidate"/>
        <meta http-equiv="Pragma" content="no-cache"/>
        <meta http-equiv="Expires" content="-1"/>
    <style>
        body {
            color: #ff8000;
            background-color: #200020;
            font-family: "Comic Sans MS";
            border-radius: 5px; 
            }
        input[type=submit]{
            color: #ff8000;
            background-color: #200020;
            border-color: #600060;
            border-radius: 7px; 
            border-style: solid;
            font-family: "Comic Sans MS";
            }
        input[type=password]{
            color: #ff8000;
            background-color: #800080;
            border-color: #600060;
            border-radius: 7px; 
            border-style: solid;
            font-family: "Comic Sans MS";
          }
    </style>
    </head>
    <body>

    <h1>%s - Wifi</h1>
    <br><br>

    <form align="left" action="/connect">
    <table width=100%%>
        WIFI_ROWS
    </table>
    </form>
    </body>
    """ % (_ap_name,_ap_name,_ap_name)

_ap_html_public=u"""
<tr><td>AP_NAME<td><input type="hidden" name="hiddenAP_NAMECNT" value="AP_NAME"></td><td></td><td><input type="submit" name="AP_NAME" value="Connect"></td></tr>
"""

_ap_html_private=u"""
<tr><td>AP_NAME</td><td><input type="hidden" name="hiddenAP_NAMECNT" value="AP_NAME"></td><td><input size="10" type="password" name="password"></td><td><input type="submit" name="AP_NAME" value="Connect"></td></tr>
"""
    
def _make_wifi_rows(): 
    ret = ''
    nd=wifi.list_network_data()
    if len(nd)==0:
        return 'No networks found, refresh to try again.'
    
    for (adapter,name,tp) in nd:
        global _cnt
        cntstr='%i' % _cnt
        _cnt += 1
        if tp!='OPEN':
            ret+=_ap_html_private.replace(u'AP_NAME',name)\
                .replace('CNT',cntstr)
        else:
            ret+=_ap_html_public.replace(u'AP_NAME',name)\
                .replace('CNT',cntstr)
            
    return ret

def make_wifi_html():
    return _html_template.replace(u'WIFI_ROWS',_make_wifi_rows())

class WifiServer(BaseHTTPRequestHandler):


    def _make_attempting_html():
        return _attempting_html_template


    def _handle_start_wifi_req(self,params):
        wifi_name='noname'
        password=None
        for n in params:
            v=params[n]
            if v==['Connect']:
                wifi_name=n
            elif n=='password':
                password=v[0]
        _report('thanks! trying to connect to %s now\n' % wifi_name)
        #server.wfile.write(make_attempting_html())
        wifi.set_wifi(wifi_name,password)
        wifi.start_wifi()
        if test_connection():
            return True

        _report('can\'t connect to wifi :(\nbringing access point up again')
        wifi.start_ap()
        self._return_to_front()
        return False

    def _return_to_front(self):
        self.send_response(301)
        self.send_header('Location', '/')
        self.end_headers()

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
    
    def do_GET(self):
        global _keep_running
        try:
            params = parse_qs(urlparse(self.path).query)
            if 'connect' in self.path:
                if self._handle_start_wifi_req(params):
                    _keep_running=False
                    return
            else:
                html = make_wifi_html()
                self.wfile.write(html)
        except:
            _report('something went very wrong :(\nbest to reboot')
            print sys.exc_info()[0]
            raise


def start_ap():
    _report('starting access point')
    start_ap()
    _report('access point is running, I think :)')
    time.sleep(5)
    _report('connect to network %s\n( that\'s me :) )\n' % _ap_name +
        'then type %s in a browser' % wifi.ap_ip)

def test_connection(s):                
    _report(s)
    for i in range(0,120):
        msg=s+' . '
        _report(msg)
        if wifi.is_connected():
            return True
        time.sleep(1)
    return False

def run_wifi_server():
    try:
        start_ap()
        handler=WifiServer
        server = HTTPServer(('', 80),handler )
        print 'Started httpserver.' 
        while(_keep_running):
            server.handle_request()
        
    except KeyboardInterrupt:
        server.socket.close()


def configure_wifi(sleep=_sleep_on_connect,display_details=True):
    ip=""
    try:
        print 'testing connection'
        while not test_connection('checking wifi connection\n'+
            'be patient, this can take a few minutes\n'):
            _report('not connected to wifi, starting access point\n'+
                'this will take a minute or two')
            run_wifi_server()
    except:
        _report('something went very wrong :(\nbest to reboot')
        time.sleep(sleep)
        return  
    finally:
        if display_details:
            print 'displaying connection details in connection module'
            display_connection_details()
            time.sleep(sleep)

def display_connection_details():
    connections=wifi.get_interfaces_info()
    # first check for wifi connections
    # but keep track of lan 
    lan=None
    for con in connections:
        if con.is_wifi: 
            if con.ssid is not None: 
                network=con.ssid
                ip_address=con.ip_address
                hostname=wifi.get_host_name()
                msg=('I am now on network %s\n'+
                    'and my name is %s.local\n'+
                    '(or %s if that fails)') % (network,hostname,ip_address)
                _report(msg)
                return
            else:
                print 'ssid is None, wifi will be ignored\n',con
        else:
            lan=con
    
    # no wifi, wired connection?
    if lan is not None:
            ip=con.ip_address
            hostname=socket.gethostname()
            msg=('connected by wire\n'+
                'my name is %s.local\n'+
                '(or %s if that fails)') % (hostname,ip)
            _report(msg)
            return
    time.sleep(1)

if __name__ == "__main__":
    configure_wifi()
    if _to_launch is not None:
        Popen(shlex.split(_to_launch))    
