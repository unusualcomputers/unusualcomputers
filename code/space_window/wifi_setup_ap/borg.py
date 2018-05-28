#thanks aleax: http://www.aleax.it/Python/5ep.html

class borg:
    _shared_state = {}
    def __init__(self):
        self.__dict__ = self._shared_state

class borg_init_once:
    _shared_state = {}
    def __init__(self):
        self.__dict__ = self._shared_state
        if len(self._shared_state)==0:
            self.init_once()
