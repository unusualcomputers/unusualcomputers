from threading import Lock

class Cache:
    def __init__(self):
        self.data=[]
        self.max_size=2000
        self.lock=Lock()
        
    def clear(self):
        with self.lock:
            self.data=[]
        
    def add(self, uri, item):
        i = self.get(uri)
        with self.lock:
            if i is None:
                if len(self.data) >= self.max_size: 
                    self.data=self.data[(self.max_size/2):]
                self.data.append((uri,item))

    def get(self,uri):
        with self.lock:
            item = next((i for i in self.data if i[0]==uri),None)
        if item is not None: return item[1]
        else: return None
