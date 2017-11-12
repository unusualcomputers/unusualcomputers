try:
    from Tkinter import *
except ImportError:
    from tkinter import *
try:
    import ttk
except ImportError:
    from tkinter import ttk
import threading
from search_dialog import Search
from mopidy_rough_base.mopidy_browser import MopidyBrowser
from mopidy_rough_base.mopidy_search import MopidySearch
from mopidy_rough_base.mopidy_play_control import MopidyPlayControl
from mopidy_rough_base.util import *
from mopidy.models import Ref
from Queue import Queue
import re
import logging
from tooltip import ToolTip
import tkMessageBox
import pdb

# helper to pack widgets uniformly
def pack(widget, side=None):
    if side is None:
        widget.pack(fill=BOTH,expand=1,padx=2,pady=2)
    else:
        widget.pack(fill=BOTH,expand=1,side=side,padx=2,pady=2)

# main tk frame
# runs on its own thread controlled by class GuiThread 
# (at the bottom of the file) 
class RadioRough(Tk):
    def __init__(self, q, core):
        Tk.__init__(self)
        # q is the queue used to send events from mopidy and status to
        # this thread
        self.q=q
        
        self.logger = logging.getLogger(__name__)
        
        # browser is the interface to mopidy functions
        self.browser=MopidyBrowser(core,self.send_status,False)
        self.browser.set_volume(50)
        
        # loop tracks, or not
        self.loop = BooleanVar()

        # ingnore _next_selet used to synchronise list updates as they  
        # are sometimes required by mopidy events on other threads
        self.ignore_next_select=False
        
        # tkinter layout setup
        self.style=ttk.Style()
        self.style.theme_use('clam')
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.title('radio rough')
        self.geometry('480x360')
        iconfile=os.path.join(os.path.dirname(os.path.realpath(__file__)),'ucc.gif')
        img = Image("photo", file=iconfile)
        self.call('wm','iconphoto',self._w,img)

        base_frame=Frame(self)
        pack(base_frame)
        top_frame=Frame(base_frame)
        pack(top_frame,TOP)
        
        list_frame=Frame(top_frame,bd=0)
        pack(list_frame,LEFT)
        
        self.list_popup=Menu(list_frame,tearoff=0)
        self.list_popup.bind('<Leave>',self.on_list_popup_focus_out)
        self.the_list=\
            Listbox(list_frame,selectmode='extended',exportselection=0)
        pack(self.the_list,LEFT)
        scrollbar=Scrollbar(self.the_list)
        scrollbar.pack(side=RIGHT,fill=Y)
        self.the_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.the_list.yview)
        self.the_list.bind('<Double-Button-1>', self.on_list_dbl_clk)
        self.the_list.bind('<Return>', self.on_list_dbl_clk)
        self.the_list.bind('<Button-1>', self.on_list_click)
        self.the_list.bind('<<ListboxSelect>>', self.on_list_select)
        self.the_list.bind('<Button-3>', self.on_list_popup)
        self.bind('<BackSpace>',self.on_backspace)
        self.bind('<Control-a>',self.on_select_all)
        self.bind('<Control-A>',self.on_deselect_all)
        
        tooltip=ToolTip(self.the_list, 
            None, self.the_list_tooltip, 0.5, False) 
        buttons_frame=Frame(top_frame,bd=0)
        pack(buttons_frame)
        
        self.play_pause_btn=Button(buttons_frame, text='play', width='10',
                command=self.on_play_pause)
        self.play_pause_btn.pack(padx=2,pady=2)

        next_prev_frame=Frame(buttons_frame)
        next_prev_frame.pack()
        next_btn=Button(next_prev_frame, text='>>', width='5',
                command=self.on_next)
        next_btn.pack(side=RIGHT, padx=2,pady=2)
        prev_btn=Button(next_prev_frame, text='<<', width='5',
                command=self.on_prev)
        prev_btn.pack(side=RIGHT, padx=2,pady=2)
        
        search_btn=Button(buttons_frame,text='search',width='10',
                command=self.on_search)
        search_btn.pack(padx=2,pady=2)

        self._ignore_vol_slide=True
        self.volume=Scale(buttons_frame,from_=0,to=100,showvalue=0,
            orient=HORIZONTAL,command=self.on_vol_slide)
        self.volume.pack(fill=X,expand=1,anchor=S)
        self.volume.set(50)
        self._vol_delay=None

        mid_frame=Frame(base_frame,bd=0)
        mid_frame.pack(fill=BOTH,expand=1)
        self.style.configure('orange.Horizontal.TProgressbar', 
            foreground='orange', background='orange')
        self.progress=ttk.Progressbar(mid_frame,orient='horizontal',
            mode='determinate',style='orange.Horizontal.TProgressbar')
        self.progress_update=None
        self.t0=StringVar()
        self.label_t0=Label(mid_frame,text='0:00',font=('',6),
            textvariable=self.t0)
        self.label_t0.pack(padx=0,side=LEFT,anchor=W)
        self.progress.pack(fill=X,expand=1,padx=4,pady=0,side=LEFT)
        self.t1=StringVar()
        self.label_t1=Label(mid_frame,text='2:35',font=('',6),
            textvariable=self.t1)
        self.label_t1.pack(padx=0,side=LEFT,anchor=E)
        self.progress.bind('<Button-1>',self.on_progress)
        self.progress.bind('<Motion>',self.on_progress_motion)
        self.init_progress()       
        
        bottom_frame=Frame(base_frame,bd=0)
        pack(bottom_frame)
        
        self.status=Text(bottom_frame,height=4,width=55,bd=1,
            bg=self.cget('bg'))
        self.status.pack(side=LEFT,padx=2,pady=5,fill=BOTH,expand=1)
        self.status.config(state=DISABLED)
        
        self.tl_view=None

    # popup menu is dynamic
    def configure_list_popup(self,index=-1):
        self.list_popup.delete(0,END)
        if not self.browser.is_top_level():
            self.list_popup.add_command(label='back',command=self.back) 
            self.list_popup.add_separator()
            
        if self.browser.is_playable(index):
            self.list_popup.add_command(label='play now',command=self.play_now) 
            self.list_popup.add_command(label='play next',command=self.play_next) 
            self.list_popup.add_command(label='add to queue',
                command=self.add_to_tracks)
            self.list_popup.add_command(label='loop this',
                command=self.loop_now)     
            self.list_popup.add_separator()
            if not self.browser.is_favourites():
                self.list_popup.add_command(label='add to favourites',
                    command=self.add_to_favourites) 
                self.list_popup.add_separator()
            else:        
                self.list_popup.add_command(label='remove from favourites',
                    command=self.remove_from_favourites) 
                self.list_popup.add_separator()

        if not self.browser.is_queue():     
            self.list_popup.add_command(label='show queue',
                command=self.show_queue)
        if not self.browser.is_subscriptions():     
            self.list_popup.add_command(label='show subscriptions',
                command=self.show_subscriptions) 
        if not self.browser.is_favourites():
            self.list_popup.add_command(label='show favourites',
                command=self.show_favourites) 
        if not self.browser.is_history():     
            self.list_popup.add_command(label='show history',
                command=self.show_history)
                
        if index==-1: return
        if self.browser.is_channel(index):
            self.list_popup.add_separator()
            if self.browser.is_subscribed(index):
                self.list_popup.add_command(label='unsubscribe',
                    command=self.unsubscribe)
                self.list_popup.add_command(label='update now',
                    command=self.update_subscription)
            else:
                self.list_popup.add_command(label='subscribe',
                    command=self.subscribe)
        if self.browser.is_podcast(index):
            self.list_popup.add_separator()
            if self.browser.is_podcast_on_disk(index):
                self.list_popup.add_command(label='delete',
                    command=self.delete_podcasts)    
            else:
                self.list_popup.add_command(label='download',
                    command=self.download_podcasts)
            self.list_popup.add_command(label='keep',
                command=self.keep_podcasts)
        if self.browser.is_queue():
            self.list_popup.add_separator()
            self.list_popup.add_command(label='remove from queue',
                command=self.remove_from_queue)
            self.list_popup.add_command(label='clear queue',
                command=self.clear_queue)
            self.list_popup.add_checkbutton(label='loop',
                variable=self.loop, command = self.on_loop)
            self.loop.set(self.browser.is_looping())    
            
        self.list_popup.add_separator()
        self.list_popup.add_command(label='select all',
            command=self.select_all) 
        self.list_popup.add_command(label='clear selection',
            command=self.deselect_all) 

    def on_list_popup_focus_out(self,evt):
        self.list_popup.unpost()    
    
    def on_list_popup(self,evt):
        nearest=self.the_list.nearest(evt.y)
        self.the_list.select_set(nearest)
        if not self.browser.is_top_level():
            nearest-=1
        self.configure_list_popup(nearest)
        self.list_popup.post(evt.x_root,evt.y_root)

    # handling tracks queue
    def remove_from_queue(self):
        self.browser.remove_tracks(self.__curindices())
        self.update_list()
        
    def clear_queue(self):
        self.browser.clear_tracks()
        self.update_list()
    
    def on_loop(self):
        self.browser.flip_loop()
        self.loop.set(self.loop.get())
    
    # podcasts
    def subscribe(self):
        self.browser.subscribe(self.__curindices())

    def unsubscribe(self):
        self.browser.unsubscribe(self.__curindices())

    def update_subscription(self):
        self.browser.update(self.__curindices())
    
    def download_podcasts(self):
        self.browser.download_podcasts(self.__curindices())

    def delete_podcasts(self):
        y=tkMessageBox.askquestion('Deleting files',
            'Selected podcasts will be deleted,\nare you sure about this?',
            icon='warning')
        if y=='yes':            
            self.browser.delete_podcasts(self.__curindices())

    def keep_podcasts(self):
        y=tkMessageBox.askquestion('Keeping podcasts',
            'Selected podcasts will not be auto-deleted,\nare you sure about this?',
            icon='warning')
        if y=='yes':            
            self.browser.keep_podcasts(self.__curindices())
       
    # showing special lists   
    def show_subscriptions(self):
        self.browser.select_subscriptions()
        self.update_list()

    def show_favourites(self):
        self.browser.select_favourites()
        self.update_list()

    def show_history(self):
        self.browser.select_history()
        self.update_list()

    def show_queue(self):
        self.browser.select_queue()
        self.update_list()
        curr=self.browser.get_current_tl_index()
        self.deselect_all()
        if curr is not None:
            self.the_list.select_set(curr+1)

    # handling tooltips
    def the_list_tooltip(self,event):
        if event is None: return None
        if self.browser.is_top_level():
            idx=self.the_list.nearest(event.y)
        else:    
            idx=self.the_list.nearest(event.y)-1
        return enc(delint(self.browser.format_track_info_by_idx(idx)))

    # cursor
    def _waiting(self):
        self.config(cursor='watch')
        self.update()

    def _normal(self):
        self.config(cursor='')
        self.update()

    # progress bar
    def to_time_string(self,ss):
        ssi=int(ss)
        h=ss/(60*60)
        m=(ss-h*60*60)/60
        s=(ss-h*60*60-m*60)
        if h!=0:
            return '{}:{:02d}:{:02d}'.format(h,m,s)
        else:
            return '{:02d}:{:02d}'.format(m,s)
    
    def init_progress(self):
        self.t0.set('00:00')
        self.t1.set('00:00')
        self.progress['maximum']=0
        self.progress['value']=0

    def stop_progress(self):
        self.init_progress()  
  
    def start_progress(self,ms):
        r=self.to_time_string(ms/1000)
        self.t0.set('00:00')
        self.t1.set(r)
        self.progress['maximum']=ms/1000
        self.progress['value']=0
        if self.progress_update is not None:
            self.after_cancel(self.progress_update)
        self.update_progress()

    def update_progress(self):
        if self.browser.is_playing() and self.progress['maximum']!=0:
            tm=self.browser.get_current_tm()
            if tm:
                self.set_progress_val(tm/1000)
        self.after(1000,self.update_progress)

    def set_progress_val(self,v,move_to=True):
        m=self.progress['maximum']
        l=self.to_time_string(v)
        r=self.to_time_string(m-v)
        self.t0.set(l)
        self.t1.set(r)
        if move_to and self.progress['value']!=v:
            self.progress['value']=v

    def on_progress_motion(self,event):
        m=self.progress['maximum']
        wx =self.progress.winfo_x()
        ex=event.x
        w=self.progress.winfo_width()
        pos=(ex+2)*m/w
        self.set_progress_val(pos,False)
 
    def on_progress(self,event):
        m=self.progress['maximum']
        wx =self.progress.winfo_x()
        ex=event.x
        w=self.progress.winfo_width()

        new_tm=((ex+2)*m)/w
        self.browser.seek(new_tm*1000)
    
    # volume slider
    def on_vol_slide_after(self):
        vol=self.volume.get()
        self.browser.set_volume(vol)

    def on_vol_slide(self,event):
        if self._ignore_vol_slide: 
            self._ignore_vol_slide=False
            return
        if self._vol_delay is not None:
            self.after_cancel(self._vol_delay)
        self._vol_delay=self.after(500, self.on_vol_slide_after)        
        
    # other events
    def on_backspace(self,event):
        self.back()
        
    def on_select_all(self,event):
        self.select_all()

    def on_deselect_all(self,event):
        self.deselect_all()

    def select_all(self):
        if self.browser.is_top_level():
            self.the_list.select_set(0,END)
        else:
            self.the_list.select_set(1,END)

    def deselect_all(self):
        self.the_list.select_clear(0,END)

    def on_close(self):
        os.system('pkill mopidy')
        self.destroy()
        self.quit()
    
    # start the loop that checks out queue and tk main loop
    def startloops(self):
        self.q_loop()
        self.update_list()
        self.mainloop()

    # queue loop
    # handles messages from other threads    
    def q_loop(self):
        def current_info(self):
            self.status_message(self.browser.format_current_track_info())
    
        while not self.q.empty():
            msg=self.q.get()
            (evnt, args)=msg
            
            if evnt!='status' and 'Downloading' not in args:
                self.logger.info('event: {}, args: {}'.format(evnt,args))   
            
            if evnt=='deselect-list':
                self.deselect_all()
            elif evnt=='stop':
                self.on_close()
            elif evnt=='stream_title_changed':
                self.current_info()
            elif evnt=='volume_changed':
                v=args['volume']
                self.volume.set(v)
            elif evnt=='play_state_changed':
                if args['new_state']=='playing':
                    self.play_pause_btn['text']='pause'
                elif args['new_state']=='stopped':
                    self.init_progress()
                    self.play_pause_btn['text']='play'
                else:
                    self.play_pause_btn['text']='play'
                self._normal()
            elif evnt=='track_playback_started':
                self.play_pause_btn['text']='pause'
                track=args['tl_track'].track
                if track.length:
                    self.start_progress(track.length)
                else:
                    self.stop_progress()
                status = self.browser.format_current_track_info()
                if status is None:
                    status=self.browser.format_track_info(track)
                    self.after(15000,self.current_info)
                self.status_message(status)
                if self.browser.is_queue():
                    self.update_list()
                self._normal()
            elif evnt=='track_playback_ended':
                self.play_pause_btn['text']='play'
                self.clear_status()
                self.stop_progress()
                if self.browser.is_queue():
                    self.update_list()
            elif evnt=='tracklist_changed':
                if self.browser.is_queue():
                    self.update_list()
            elif evnt=='status':
                if args=='Updated': 
                    self.update_list()
                    self.current_info()    
                elif args is None:
                    self.current_info()
                else:
                    self.status_message(args)
    
        self.after(100,self.q_loop)
   
    # updates the main list
    def update_list(self):
        if self.browser is None: return
        self.browser.refresh_list()
        curr=self.browser.current_names()
        curr=[enc(c) for c in curr]
        top=self.browser.is_top_level()
        if top:
            curr_list=self.the_list.get(0,END)
            if curr_list==tuple(curr): return
            self.the_list.delete(0,END)
        else:
            curr_list=self.the_list.get(1,END)
            if curr_list==tuple(curr): return
            self.the_list.delete(0,END)
            self.the_list.insert(0,'<--')
        self.the_list.insert(END,*curr)
        self.ignore_next_select=True
    
    # list navigation
    def browse_list(self,i):
        if self.browser is None: return
        sel=self.the_list.get(i)
        if sel=='<--':
            self.browser.back()
        else:
            if not self.browser.is_top_level(): i-=1
            self.browser.select(i)
        self.update_list()
    
    def back(self):
        self.browser.back()
        self.update_list()

    def on_list_select(self,event):
        if self.ignore_next_select:
            self.deselect_all()
            self.ignore_next_select=False
        
    def on_list_click(self,event):
        self._waiting()
        i=self.the_list.nearest(event.y)
        self.browse_list(i)
        self._normal()
  
    def on_list_dbl_clk(self,event):
        self._waiting()
        i=self.the_list.nearest(event.y)
        if not self.browser.is_top_level(): i-=1
        if self.browser.is_playable(i):
            self.play_now()
        self._normal()    
 
    def __curindices(self):
        if self.browser.is_top_level():
            return self.the_list.curselection()
        else:
            return [i-1 for i in self.the_list.curselection()]
   
    # playing and tracks
    def play_now(self):
        self._waiting()
        self.browser.play_now(self.__curindices())
        self._normal()
 
    def loop_now(self):
        self._waiting()
        self.browser.loop_now(self.__curindices())
        self._normal()
 
    def play_next(self):
        self._waiting()
        self.browser.play_next(self.__curindices())
        self._normal()

    def add_to_tracks(self):
        self._waiting()
        self.browser.add_to_tracks(self.__curindices())
        self._normal()
  
    def on_prev(self):
        self.browser.prev()
    
    def on_next(self):
        self.browser.next()
    
    def on_play_pause(self):
        if self.browser.is_stopped():
            if len(self.browser.tracks())==0:
                self.play_now()
            else:    
                self.browser.play_current()
        else:
            self.browser.play_pause()
        
        if self.play_pause_btn['text']=='play': 
            self.play_pause_btn['text']='pause'
        else:
            self.play_pause_btn['text']='play'

    # favourites
    def add_to_favourites(self):
        self._waiting()
        self.browser.add_to_favourites(self.__curindices())
        self._normal()
  
    def remove_from_favourites(self):
        self._waiting()
        self.browser.remove_from_favourites(self.__curindices())
        self._normal()

    # searching
    def on_search(self):
        self._waiting()
        d=Search(self)
        if d.searchtext!='':
            self.browser.search(d.searchtext)
            self.update_list()
        self._normal()
 
    # status messages
    def clear_status(self):
        self.status.config(state=NORMAL)
        self.status.delete(1.0,END)
        self.status.config(state=DISABLED)

    def send_status(self,status):
        self.q.put(("status",status))
    
    def send_deselect(self):
        self.q.put(('deselect-list',''))
            
    def status_message(self,msg):
        self.clear_status()
        if msg is not None:
            self.status.config(state=NORMAL)
            self.status.insert(END,enc(delint(msg)))
            self.status.config(state=DISABLED)

# GuiThread controls the thread that runs the tk inter frame
class GuiThread:
    def __init__(self, core):
        self.q=Queue()
        self.core=core
        self.browser=None
        self.thread=threading.Thread(target=self.run_gui)
    
    def run_gui(self):
        gui=RadioRough(self.q, self.core)
        self.browser=gui.browser
        gui.startloops()
    
    def start(self):
        self.thread.start()
    
    def send_to_gui(self,msg,**kwargs):
        if self.browser:
            self.browser.mopidy_event(msg,**kwargs)
        self.q.put((msg,kwargs))
    
    def stop(self):
        self.send_to_gui('stop')

# once radio rough is installed launching mopidy automatically starts it       
if __name__=='__main__':
    from subprocess import call
    call('mopidy')
    rough=RadioRough(Queue(),None)
    rough.startloops()
