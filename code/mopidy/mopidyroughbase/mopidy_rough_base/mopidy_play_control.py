from mopidy.core import PlaybackState
from mopidy.models import Ref

# controls for playback
class MopidyPlayControl:

    def __init__(self, core):
        self.core = core

    def get_title(self):
        t = self.core.playback.get_stream_title().get()
        if t is None:
            t = self.get_current_track()
            if t is None: return ''
            else: return t.name
        else:
            return t

    def get_state(self):
        return self.core.playback.get_state().get()

    def get_current_tl_track(self):
        return self.core.playback.get_current_tl_track().get()
    
    def get_current_track(self):
        return self.core.playback.get_current_track().get()
    
    def get_current_tm(self):
        return self.core.playback.time_position.get()

    def is_playing(self):
        state = self.get_state()
        return state == PlaybackState.PLAYING
    
    def is_paused(self):
        state = self.get_state()
        return state == PlaybackState.PAUSED
    
    def is_stopped(self):
        state = self.get_state()
        return state == PlaybackState.STOPPED

    def play(self):
        self.core.playback.play()

    def stop(self):
        self.core.playback.stop()

    def pause(self):
        self.core.playback.pause()
    
    def resume(self):
        self.core.playback.resume()
    
    def play_pause(self):
        if self.is_paused():
            self.resume()
        elif self.is_stopped():
            self.play()
        else:
            self.pause()
        return self.get_state()
 
    def next(self):
        self.core.playback.next()

    def prev(self):
        self.core.playback.previous()

    def seek(self, tm):
        self.core.playback.seek(tm)

    def restart(self):
        self.seek(0)

    def skip_fwd(self, tm = 10000):
        track = self.get_current_track()
        if track is None: return
        track_tm = track.length
        current_tm = self.get_current_tm()
        
        if current_tm+tm > track_tm:
            new_tm = track_tm - 1000
        else:
            new_tm = current_tm + tm
        self.seek(new_tm)

    def skip_back(self, tm = 10000):
        track = self.get_current_track()
        if track is None: return
        current_tm = self.get_current_tm()
        if current_tm - tm < 1:
            new_tm = 0
        else:
            new_tm = current_tm - tm
        self.seek(new_tm)

    def flip_mute(self):
        self.core.mixer.set_mute( not self.is_mute )

    def is_mute(self):
        m = self.core.mixer.get_mute()
        if m is None:
            return False
        else:
            return m

    def volume(self):
        v = self.core.mixer.get_volume().get()
        if v is None:
            return 0
        else:
            return v

    def set_volume(self, v):
        if v > 100:
            self.core.mixer.set_volume(100)
        elif v < 0:
            self.core.mixer.set_volume(0)
        else:
            self.core.mixer.set_volume(v)

    def volume_up(self, step = 5):
        v = self.volume()
        self.set_volume(v+step)
        return v+step
    
    def volume_down(self, step = 5):
        v = self.volume()
        self.set_volume(v-step)
        return v-step

