#thanks aleax: http://www.aleax.it/Python/5ep.html

#borg ensures that the state is shared between all instances of a class
#   derive from it and call borg.__init__(self) from __init__
#   be careful, the rest of your __init__ method still gets executed every time
class borg:
    _shared_state = {}
    def __init__(self):
        self.__dict__ = self._shared_state

#a variant that ensures all initialisation code is only executed once
#   derive from it, call borg_init_once.__init__(self) from __init__
#   and implement all initialisation in a method init_once
class borg_init_once:
    _shared_state = {}
    def __init__(self):
        self.__dict__ = self._shared_state
        if len(self._shared_state)==0:
            self.init_once()
