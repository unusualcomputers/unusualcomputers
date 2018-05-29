from mopidy_json_client import MopidyClient

class MopidyUpdates:
    def __init__(self,updates_func):
        self.update=updates_func
        self._mopidy=MopidyClient()
        self._mopidy.bind_event('track_playback_started', self.playback_started)
        self._mopidy.bind_event('stream_title_changed', self.title_changed)

    # mopidy updates
    def playback_started(tl_track):
        try:
            track=tl_track.get('track') if tl_track else None
            if not track:
                return
            trackinfo={
                'name' : track.get('name'),
                'artists': ', '.join(\
                    [artist.get('name') for artist in track.get('artists')])
            }
            txt = u'{artists}\n{name}'.format(**trackinfo)
            self.update(txt)
        except: 
            pass

    def title_changed(title):
        try:
            self.update(title)
        except:
            pass

