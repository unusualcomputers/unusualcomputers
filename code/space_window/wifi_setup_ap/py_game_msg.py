import pygame as pg
from time import *
import threading
import os
import sys
from config_util import Config
from borg import borg_init_once
#os.putenv('SDL_VIDEODRIVER','fbcon')
#os.putenv('SDL_FBDEV','/dev/fb0')

class MsgScreenThread:
    def __init__(self):
        config = Config('py_game_msg.conf')

        self.border=config.getint('position','border',10)
        self.left=config.getbool('position','left',False)
        self.top=config.getbool('position','top',False)
        self.forecol=config.getcolor('colors','foreground',(255,128,0))
        self.bckcol=config.getcolor('colors','background',(32,0,32))
        self.fontname=config.get('font','name','comicsansms')
        self.fontsz=config.getint('font','size',68)
        
        self.screen = None
        self.running=False
        self.delay=1
        self.screen=None
        self.text=None
        self.black=None
        self.font=None
        pg.init()
        #sleep(1)
        pg.mouse.set_visible(False)	
        self.screen = pg.display.set_mode((0,0),pg.FULLSCREEN )
        self.black=self.screen.copy()
        self.black.fill(self.bckcol)
        self.font = pg.font.SysFont(self.fontname, self.fontsz)
        self.lock=threading.Lock()

    def lock_t(self):
        while not (self.lock.acquire(False)):
            sleep(0.1)
    
    def get_running(self):
        self.lock_t()
        r=self.running
        self.lock.release()
        return r

    def get_text(self):
        self.lock_t()
        t=self.text
        self.lock.release()
        return t

    def place_text(self):
        rows=self.get_text().split('\n')
        surfaces=[self.font.render(x,True,self.forecol) for x in rows]
        total_height=sum([s.get_height() for s in surfaces])
        avail_height=self.screen.get_height()-2*self.border
        while((total_height-surfaces[0].get_height())>avail_height):
            total_height-=surfaces[0].get_height()
            surfaces=surfaces[1:]
        rects=[s.get_rect() for s in surfaces]
        if self.top:
            top=self.border
        else:
            top = (self.screen.get_height()-total_height)/2.0
        width=self.screen.get_width()
        current_top=top
        for r in rects:
            r.top=current_top
            current_top=r.bottom
            if self.left:
                r.x=self.border
            else:
                r.x=(width-r.width)/2.0
        return zip(surfaces,rects)   
    
    def run_msg(self):
        #pg.init()
        local_text=''
        while(self.get_running()):
            for event in pg.event.get():
                if event.type==pg.QUIT or \
                (event.type==pg.KEYDOWN and event.key==pg.K_c and \
                (pg.key.get_mods() & pg.KMOD_CTRL)):
                    print "ctrl-c pressed"
                    pg.quit()
                    sys.exit(0)
                    return
            if self.get_text()!=local_text:
                local_text=self.get_text()
                rows=self.place_text()
                self.screen.blit(self.black,(0,0))
                for row in rows:
                    self.screen.blit(row[0], row[1])
                pg.display.flip()
            sleep(self.delay)

class MsgScreen(borg_init_once):
    def __init__(self):
        borg_init_once.__init__(self)

    def init_once(self):
        self._msg=MsgScreenThread()

    def start_thread(self):
        if self._msg.get_running(): return
        self._msg.running = True
        threading.Thread(target=self._msg.run_msg).start()
    
    def lock_t(self):
        self._msg.lock_t()
    
    def stop(self):
        self.lock_t()
        self._msg.running=False
        self._msg.lock.release()

    def set_text(self,msg):  
        self.lock_t()
        self._msg.text=msg
        self._msg.lock.release()
        self.start_thread()

    def get_text(self):
        self.lock_t()
        t=self._msg.text
        self._msg.lock.release()
        return t

if __name__=='__main__':
    msg=MsgScreen()
    msg.set_text('Hello World!')
    sleep(5)
    msg.stop()
    pg.display.quit()
    pg.quit()
