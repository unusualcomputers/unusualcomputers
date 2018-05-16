import ConfigParser
from os.path import *

class Config:
    def __init__(self, filename, caller_file=None):
        if caller_file is None:
            path=dirname(abspath(__file__))+'/conf/'+filename
        else:
            path=dirname(abspath(caller_file))+'/conf/'+filename
        self.config=ConfigParser.ConfigParser()
        self.config.read(path)

    def has(self, section, option):
        return self.config.has_section(section) and \
            self.config.has_option(section,option)

    def get(self, section, option, default=None):
        if self.has(section,option):
            return self.config.get(section,option)
        return default

    def getint(self, section, option, default=None):
        if self.has(section,option):
            return self.config.getint(section,option)
        return default

    def getfloat(self, section, option, default=None):
        if self.has(section,option):
            return self.config.getfloat(section,option)
        return default

    def getbool(self, section, option, default=None):
        if self.has(section,option):
            return self.config.getboolean(section,option)
        return default

    def getcolor(self, section, option, default = None):
        if self.has(section,option):
            s=self.config.get(section,option)
            rgba=[int(i) for i in s.split(',')]
            if len(rgba) not in [3,4]: 
                raise 'colors must have 3 or 4 members,'+\
                     '%s in section %s is wrong' % (option, section) 
            return rgba
        return default
