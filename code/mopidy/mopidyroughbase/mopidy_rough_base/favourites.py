from podcasts import Jsonable,_base_path
from util import file_exists
import os
import pdb

# file name for saving favourites
_favourites_data='.rough.favourites'

# favourites handling
# simple dictionary of mopidy uris saved to a file
class Favourites(Jsonable):
    @classmethod
    def _config_path(cls):
        return os.path.join(_base_path,_favourites_data)
    
    @classmethod
    def load(cls):
        if not file_exists(_base_path):
            os.mkdir(_base_path)
        path=cls._config_path()
        if file_exists(path):
            return cls.from_file(path)
        s=cls()
        s.save()
        return s        

    def save(self):
        full_path=os.path.join(_base_path,_favourites_data)        
        self.to_file(full_path)
    
    def __init__(self,favourites=[]):
        self.favourites=favourites
        
    def add(self,name,uri):
        e=next((x for x in self.favourites if x[0]==name),None)
        if e is None:
            self.favourites.append([name,uri])
        else:
            e[1]=uri
        self.save()
            
    def remove(self,name):
        self.favourites=[x for x in self.favourites if x[0]!=name]
        self.save()
