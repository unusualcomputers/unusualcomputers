from mopidy.models import Ref,Track,Album,Artist,Playlist

# searching is slow compared to other things
# we cache the results in object that look like mopidy references

class RefWithData:
    def __init__(self, ref, data):
        self.uri = ref.uri
        self.name = ref.name
        self.type = ref.type
        self.data = data
    
    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return self.__str__()

def make_ref(data): 
    if isinstance(data, Track):
        ref = Ref.track(uri = data.uri, name = data.name)
    elif isinstance(data, Album):
        ref = Ref.album(uri = data.uri, name = data.name)
    elif isinstance(data, Artist):
        ref = Ref.artist(uri = data.uri, name = data.name)
    elif isinstance(data, Playlist):
        ref = Ref.playlist(uri = data.uri, name = data.name)
    elif isinstance(data, Directory):
        ref = Ref.directory(uri = data.uri, name = data.name)
        
    return RefWithData(ref,data)

# cached mopidy search
class MopidySearch:

    def __init__(self,core):
        self.core = core
        self.last_res = None
        self.last_query=None
        
    def flat_res(self):
        tmp = [[ make_ref(t) for t in s.tracks]
             + [ make_ref(a) for a in s.albums]
             + [ make_ref(a) for a in s.artists]
                 for s in self.last_res]
        return reduce( lambda x,y : x+y, tmp)

    # search with a simple string that matches a given field
    def search_single_field( self, q, field, uris = None):
        query = { field : [q] }
        self.last_query=q
        self.last_res = self.core.library.search(query, uris).get()
        if len(self.last_res) == 0: return []
        
        return self.flat_res() 
    
    def search_any( self, q, uris = None):
        return self.search_single_field(q, 'any', uris)

    def search_track( self, q, uris = None):
        return self.search_single_field(q, 'track_name', uris)

    def search_artist( self, q, uris = None):
        return self.search_single_field(q, 'artist', uris)

    def search_album( self, q, uris = None):
        return self.search_single_field(q, 'album', uris)

