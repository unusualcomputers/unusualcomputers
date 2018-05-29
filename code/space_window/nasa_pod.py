import requests
from random import *
import io
import pygame as pg
from time import *
import threading
import os
import sys
import traceback

#os.putenv('SDL_VIDEODRIVER','fbcon')
#os.putenv('SDL_FBDEV','/dev/fb0')
delay=5 # delay between frames in seconds
_apod_url='https://apod.nasa.gov/apod/'
_apod_archive_url='https://apod.nasa.gov/apod/archivepix.html'
_pics_at_once=5
_scrh=None
_scrw=None


def build_list():
    html = requests.get(_apod_archive_url).content
    s=html.find("<b>")
    e=html.find("</b>")
    pages=filter(lambda x:'<a href="' in x,html[s:e].split('\n'))
    return pages

def load_at_index(x,pages):
    l=pages[x]
    t=l.split(':')
    uri=_apod_url+t[1].split('"')[1]
    html=requests.get(uri).content
    s=html.find('<IMG SRC="')
    if s != -1:    
        l=len('<IMG SRC="')
        e=html.find('"',s+l)
        uri='https://apod.nasa.gov/apod/'+html[s+l:e]
        date=t[0]
        name=t[1].split('>')[1].split('<')[0]
        image_file = io.BytesIO(requests.get(uri).content)
        image = pg.image.load(image_file)
        h=image.get_height()
        w=image.get_width()
        sw=h/float(_scrh)
        sh=w/float(_scrw)
        s=max(sh,sw)
        h=int(h/s)
        w=int(w/s)
        print s, w,h
        image=pg.transform.scale(image,(w,h)).convert()
        return (name, date, image)
    else:
        return None
        
def load(x,pages):
    r=load_at_index(x,pages)
    if r is not None: return r
    l=len(pages)
    if x >=l: x=0
    else: x+=1
    return load(x,pages)
 
def place_text(p,font,y=0,pref=""):
    text = font.render(pref+p[0], True, (100, 100, 100))
    textrect = text.get_rect()
    textrect.centerx = screen.get_rect().centerx
    textrect.centery = screen.get_height()/10+y#screen.get_rect().centery
    return (text,textrect)

running=False
screen=None
def slideshow():    
    global running
    global screen
    global _scrh
    global _scrw
    try:
        pg.mouse.set_visible(False)	
        screen = pg.display.set_mode((0,0),pg.FULLSCREEN )
        _scrh=screen.get_height()
        _scrw=screen.get_width()
        black=screen.copy()
        black.fill((0,0,0))
        pg.font.init()
        basicfont = pg.font.SysFont('comicsansms', 48)
        (text,textrect)=place_text(("Loading first image",""),basicfont)
        screen.blit(text, textrect)
        pg.display.flip()

        pages=build_list()
        running=True
        p=load(0, pages) 
        prev_p=None
        t0=time()-delay
        screen.blit(black,(0,0))
        pg.display.flip()
        while running:
            for event in pg.event.get():
                if event.type==pg.QUIT or \
                    (event.type==pg.KEYDOWN and event.key==pg.K_c and \
                    (pg.key.get_mods() & pg.KMOD_CTRL)):
                    pg.quit()
                    raise SystemExit
            t1=time()
            if t1-t0 < delay: continue
            t0=t1
            if prev_p is not None:
                image = prev_p[2]
                ih=image.get_height()
                iw=image.get_width()
                x=(_scrw-iw)/2
                y=(_scrh-ih)/2
                (text,textrect)=place_text(prev_p,basicfont)
                (nt,ntr)=place_text(p,basicfont,40,"Next: ")
                black.blit(text, textrect)
                black.blit(nt, ntr)
                #fading out
                for i in range(0,255,1):
                    if not running: 
                        return
                    #sleep(0.02)
                    image.set_alpha(255-i)
                    screen.blit(black,(0,0))
                    screen.blit(image,(x,y))
                    pg.display.flip()
                black.fill((0,0,0))
            image = p[2]
            ih=image.get_height()
            iw=image.get_width()
            x=(_scrw-iw)/2
            y=(_scrh-ih)/2
            if prev_p is None: prev_p=p
            (text,textrect)=place_text(prev_p,basicfont)
            (nt,ntr)=place_text(p,basicfont,40,"Next: ")
            screen.blit(black,(0,0))
            screen.blit(text, textrect)
            screen.blit(nt, ntr)
            # fading in
            for i in range(0,255,1):
                if not running: 
                    return
                #sleep(0.02)
                image.set_alpha(i)
                screen.blit(image,(x,y))
                pg.display.flip()
            screen.blit(black,(0,0))
            image.set_alpha(255)
            screen.blit(image,(x,y))
            pg.display.flip()
            prev_p=p
            p=load(randint(1,len(pages)-1),pages)
    except:
        traceback.print_stack()
        raise

def start_apod():
    global running
    if running: return
    running=True
    pg.init()
    threading.Thread(target=slideshow).start()

def stop_apod():
    global running
    running=False

if __name__=="__main__":    
    try:
        start_apod()
    finally:
        pg.quit()

