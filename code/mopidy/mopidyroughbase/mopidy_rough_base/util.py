import re
import os
import pathlib
from mopidy.models import Ref

# a bunch of smaller utility functions used all over
_not_allowed='<>:"/|\?* \t\n'

def defined(x): return x is not None

def enc(s):
    if s is None: return 'None'
    try:
        return s.encode('ascii','replace').strip()
    except:
        try:
            return s.encode('ascii','ignore').strip()
        except:
            return '?'*len(s)
               
def enc_for_file(s):#encodes a string to be used for a filename
    s=enc(s)
    for c in _not_allowed:
       s=s.replace(c,'_')
    s2=s.replace('__','_')
    while s2!=s:
        s=s2
        s2=s.replace('__','_')
    return s[:128]

def path_to_uri(path):
    return pathlib.Path(path).as_uri()

def file_exists(path):
        try:
            os.stat(path)
            return True
        except:
            return False

__ignore_delint=False

def set_delint(d=True):
    global __ignore_delint
    __ignore_delint=d
    
def delint(s):
    if __ignore_delint: return s
    if s is None: return ''
    try:
        enc = s.replace(u'\u2019', u'\'').replace(u'\u2010',u'-').\
           replace(u'\u2011', u'\'').replace(u'\u2012',u'-').\
           replace(u'\u2013', u'\'').replace(u'\u2014',u'-').\
           replace(u'%20', u' ')
        enc=re.sub('<br[^<]+?>','\n',enc)
        enc=re.sub('</p[^<]+?>','\n',enc)
        
        enc=re.sub('<[^<]+?>','',enc).replace("&nbsp;"," ").strip()
        return enc
    except:    
        return s
        
def createRef(refType, name, uri):
    if refType == Ref.TRACK:
        return Ref.track(name=name, uri=uri)
    elif refType == Ref.ALBUM:
        return Ref.album(name=name, uri=uri)
    elif refType == Ref.ARTIST:
        return Ref.artist(name=name, uri=uri)
    elif refType == Ref.DIRECTORY:
        return Ref.directory(name=name, uri=uri)
    elif refType == Ref.PLAYLIST:
        return Ref.album(name=name, uri=uri)
    else:
        return None
        
def is_sound_file(s):        
    hl=s.lower()
    return hl.endswith('mp3') or hl.endswith('wav') or \
        hl.endswith('ogg') or hl.endswith('wma')

yt_default=[Ref.track(name=u'Dave Brubeck - Take Five', uri='youtube:video/Dave Brubeck - Take Five.vmDDOFXSgAs'),
    Ref.track(name=u'Dave Brubeck - Take Five ( Original Video)', uri='youtube:video/Dave Brubeck - Take Five ( Original Video).PHdU5sHigYQ'),
    Ref.track( name=u'The Dave Brubeck Quartet - Take Five (Not Now Music) [Full Album]', uri='youtube:video/The Dave Brubeck Quartet - Take Five (Not Now Music) Full Album.pcE-m7ntESQ'),
    Ref.track(name=u'Dave Brubeck - Take Five', uri='youtube:video/Dave Brubeck - Take Five.tT9Eh8wNMkw')]
