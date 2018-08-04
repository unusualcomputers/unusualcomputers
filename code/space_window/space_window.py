from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from urlparse import urlparse, parse_qs
import os
import signal
import subprocess
from collections import OrderedDict
from time import sleep
from nasa_pod import *
from threading import Timer
import wifi_setup_ap.py_game_msg as msg
import sys
import wifi_setup_ap.wifi_control as wifi
import wifi_setup_ap.connection_http as connection
from jsonable import Jsonable
from mopidy_listener import MopidyUpdates
from html import get_main_html,build_html
import pygame
PORT_NUMBER = 80

_msg=msg.MsgScreen()
def status_update(txt):
    _msg.set_text(txt)

_mopidy=MopidyUpdates(status_update)

_streams_data='.space.window'
_base_path=os.path.join(os.path.expanduser('~'),_streams_data)
_config_path=os.path.join(_base_path,_streams_data)
_cnt=0 # global counter, used to make html more responsive

# streams
#   main class managing sreams to play
class Streams(Jsonable):

    @classmethod
    def load(cls):
        if not cls.file_exists(_base_path):
            os.mkdir(_base_path)
        path=_config_path
        if cls.file_exists(path):
            return cls.from_file(path)
        s=cls()
        s.save()
        return s                

    def save(self):
        self.to_file(_config_path)

    def __init__(self,streams=OrderedDict()):
        self.streams=streams

    def len(self):
        return len(self.streams.items())

    def first(self):
        return self.at(0)

    def at(self,i):
        if i >= self.len():
            return None
        else:
            return self.streams.items()[i][0]
  	
    def next(self, name):
        for k in range(self.len()):
           if self.at(k)==name:
               return self.at(k+1)
        return self.at(0)

    def add(self, name, uri, quality):
        self.streams[name]=(uri,quality)
        self.save()
        
    def remove(self,name):
        self.streams.pop(name,None)
        self.save()
    
    def find(self,name):
        for i in range(0,self.len()):
            if self.at(i) == name: return i
        return -1

    def up(self,name):
        i=self.find(name)
        if i==-1: return
        if i<=0 or i>=self.len():
            return
        l=self.streams.keys()
        c=l[i]
        l[i]=l[i-1]
        l[i-1]=c
        d=OrderedDict()
        for i in l:
            d[i]=self.streams[i]
        self.streams=d
        self.save()

    def make_remove_html(self,name):
        form = u"""    
            <p style="font-size:45px">Really, really remove {}?</p>

            <form action="/really_remove">
            <input type="hidden" name="hidden_{}" value="{}">
            <button type="submit" name="action" value="really remove {}">
                    Yes, really remove it!
            </button></td><td>
            </form>
        """.format(name,name,name,name)
        return build_html(form)

    def make_html(self):
        global _cnt
        _cnt+=1
        html=u''
        for name in self.streams:
            (uri,quality)=self.streams[name]
            row = u"""<tr><td>{}</td><td><a href="{}">{}</a></td><td>{}</td><td>
                <input type="hidden" name="hidden_{}" value="{}">
                <button type="submit" name="action" value="play {}">
                    play
                </button></td><td>
                <button type="submit" name="action" value="moveup {}">
                    up</button></td>
                <td>
                <button type="submit" name="action" value="remove {}">
                        remove
                </button></td>
                </tr>
                """.format(name,uri,uri,quality,_cnt,name,name,name,name)
            html+=row
        return html
        
    def make_command_line(self,name):
        (uri,quality)=self.streams[name]
        # raspberry version
        command= u'streamlink {} {} --player "omxplayer --vol 500 --timeout 60" --player-fifo'.format(uri,quality)
        return command
        # ubuntu version
        #return u'streamlink {} {} --player "mplayer -cache 8000" --player-continuous-http'.format(uri,quality)

_streams=Streams.load()


current_process=None
current_stream=None
running_apod=False
check_timer_delay=90
check_timer = None
wifi_setup=False
streaming=False

def kill_running():
    global running_apod 
    global streaming
    global check_timer
    print 'stopping running shows'
    status_update('stopping running shows')
    if check_timer is not None: 
        check_timer.cancel()
    if current_process is not None:
        os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
        current_process.terminate()
    sleep(1)
    if check_timer is not None: 
        check_timer.cancel()
    check_timer=None
    if current_process is not None:
        os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
        current_process.terminate()
    stop_apod()
    wifi.run('pkill -9 mopidy')
    sreaming=False
    running_apod=False
        
def play_stream(name):
    global current_stream
    global current_process 
    global running_apod 
    global streaming

    print 'starting stream %s' % name 
    if current_stream==name and is_running():
        print 'stream %s is aready playing'
        return
    kill_running()   
    status_update('starting stream %s' % name)
    current_stream=name
    cmd=_streams.make_command_line(current_stream)
    current_process=subprocess.Popen(cmd, shell=True,
        stdin=None, stdout=None, stderr=None, 
        close_fds=True,preexec_fn=os.setsid)
    streaming=True

def play_apod():
    global current_stream
    global current_process 
    global running_apod
    global streaming
    streaming=False
    if current_process is not None:
        os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
        current_process.terminate()
        current_stream=None
        current_process=None 
    start_apod()
    running_apod=True
    
def play_next():
    if current_stream is None:
        name=_streams.first()
    else:
        name=_streams.next(current_stream) 
    if name is None: 
        print 'about to play apod'
        play_apod()
    else: 
        print 'about to play stream %s' % name
        play_stream(name)


def is_running():
    global current_stream
    global current_process 
    if wifi_setup: return True
    if current_process is not None:
        current_process.poll()
    if running_apod: return True
    if current_process is None: return False
    try:
        os.kill(current_process.pid, 0)
        return True
    except:
        current_process=None
        return False

def check_running():
    global check_timer
    if wifi_setup: return
    if not is_running():
        play_next()
    if streaming:
        check_timer=Timer(check_timer_delay, check_running)
        check_timer.start()
        
def handle_wifi_change_req(params,server):
    wifi_name='noname'
    password=None
    for n in params:
        v=params[n]
        if v==['Connect']:
            wifi_name=n
        elif n=='password':
            password=v[0]
    status_update('thanks! trying to connect to %s now' % wifi_name)
    wifi.set_wifi(wifi_name,password)
    wifi.restart_wifi()
    server.return_to_front()
    return True


class SpaceWindowServer(BaseHTTPRequestHandler):
    def return_to_front(self):
        self.send_response(301)
        self.send_header('Location', '/')
        self.end_headers()

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
    
    def send_to_mopidy(self):
        self.send_response(301)
        ip=wifi.get_ip()
        self.send_header('Location', 'http://%s:6680/radiorough' %ip)
        self.end_headers()

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
    
    #Handler for the GET requests
    def do_GET(self):
        global current_process
        global _cnt
        global wifi_setup
        params = parse_qs(urlparse(self.path).query)

        if 'play_remove' in self.path:
            ps=params['action'][0]
            if u'remove' in ps:
                html=_streams.make_remove_html(ps[len('remove '):])
                self.wfile.write(html)
                return
            elif 'moveup' in ps:
                _streams.up(ps[len('moveup '):])
            else: #if it's not remove, then it's play
                play_stream(ps[len('play '):])
                if check_timer is None: check_running()
            self.return_to_front()
            return
        elif 'really_remove' in self.path:
            ps=params['action'][0]
            _streams.remove(ps[len('really remove '):])
            self.return_to_front()
            return
        elif 'add' in self.path:
            if params['name'][0] != 'NAME' and params['link'][0]!='LINK':
                name=params['name'][0].replace(' ','')
                _streams.add(params['name'][0],params['link'][0],
                    params['quality'][0])
            self.return_to_front()
            return
        elif 'slideshow' in self.path:
            play_apod()
            self.return_to_front()
            return
        elif 'wifi' in self.path:
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            # Send the html message
            html = connection.make_wifi_html() 
            self.wfile.write(html)
            return
        elif 'connect' in self.path:
            wifi_setup=True
            kill_running()
            sleep(2)
            kill_running()
            self.return_to_front()
            status_update("changing wifi networks\nthis is a fragile process\ngive it a few minutes\nif it didn't work, reboot")
            handle_wifi_change_req(params,self)
            status_update('testing the new connection')
            if connection.test_connection():
                display_connection_details()
                sleep(20)
            wifi_setup=False
            #check_running()
            return
        elif 'shutdown' in self.path:
            os.system('shutdown -h now')
            return
        elif 'kodi' in self.path:
            wifi_setup=True
            kill_running()
            sleep(2)
            kill_running()
            status_update('starting kodi')
            print 'starting kodi'
            os.system('sudo -u pi kodi-standalone')
            print 'started kodi'
            sleep(40)
            print 'slept a bit'
            ip=wifi.get_ip()
            txt='enjoy'
            print txt
            status_update(txt)
            self.return_to_front()
            wifi_setup=False
            return
        elif 'rough' in self.path:
            wifi_setup=True
            kill_running()
            sleep(2)
            kill_running()
            status_update('starting radio rough')
            print 'starting mopidy'
            subprocess.Popen(['mopidy'])
            print 'started mopidy'
            sleep(40)
            print 'slept a bit'
            ip=wifi.get_ip()
            txt='go to spacewindow.local:6680/radiorough\nor %s:6680/radiorough' % ip
            print txt
            status_update(txt)
            self.send_to_mopidy()
            wifi_setup=False
            return
        elif 'next' in self.path:
            play_next()
            self.return_to_front()
            return
        elif self.path.endswith('.jpg'):
            mimetype='image/jpg'
            #Open the static file requested and send it
            f = open('/home/pi/' + self.path) 
            self.send_response(200)
            self.send_header('Content-type',mimetype)
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
            return
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        # Send the html message
        html = get_main_html(_streams.make_html())
        self.wfile.write(html)

_server=None
try:
    print 'configuring wifi'
    connection.configure_wifi(30,False)
    #Create a web server and define the handler to manage the
    #incoming request
    handler=SpaceWindowServer
    _server = HTTPServer(('', PORT_NUMBER),handler )
    print 'Started httpserver on port ' , PORT_NUMBER, _server.server_address
    connection.display_connection_details()
    sleep(10)
    check_running()    
    #Wait forever for incoming http requests
    _server.serve_forever()

except KeyboardInterrupt:
    print 'space window is shutting down'
    kill_running()
    if _server is not None:
        _server.socket.close()
finally:
    pygame.quit()
    
