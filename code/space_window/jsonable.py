import jsonpickle
import io
import os

class Jsonable(object):
    # base class for object that can be serialised to Json

    @classmethod
    def file_exists(self, path):
        try:
            os.stat(path)
            return True
        except:
            return False
            
    def to_json(self):
        return jsonpickle.encode(self)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.__class__) + ': ' + str(self.__dict__)      
    
    def __eq__(self,other):
        return self.__dict__==other.__dict__
        
    @classmethod
    def from_json(cls,json_string):
        d=jsonpickle.decode(json_string)
        return d
        
    @classmethod
    def from_file(cls,path):
        f=io.open(path,'r',encoding='utf-8')
        return cls.from_json(f.read())

    def to_file(self,path):
        f=io.open(path,'w',encoding='utf8')
        f.write(unicode(self.to_json()))

