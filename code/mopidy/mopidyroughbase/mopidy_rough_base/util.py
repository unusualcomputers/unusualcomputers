import re
import os
import pathlib
from mopidy.models import Ref

# a bunch of smaller utility functions used all over
_not_allowed='<>:"/|\?* \t\n'

def defined(x): return x is not None

def enc(s):
    if s is None: return 'None'
    return s.encode('ascii','replace').strip()
    
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
    enc = s.replace(u'\u2019', u'\'').replace(u'\u2010',u'-').\
       replace(u'\u2011', u'\'').replace(u'\u2012',u'-').\
       replace(u'\u2013', u'\'').replace(u'\u2014',u'-').\
       replace(u'%20', u' ')
    enc=re.sub('<br[^<]+?>','\n',enc)
    enc=re.sub('</p[^<]+?>','\n',enc)
    
    return re.sub('<[^<]+?>','',enc).replace("&nbsp;"," ").strip()

def is_sound_file(s):        
    hl=s.lower()
    return hl.endswith('mp3') or hl.endswith('wav') or \
        hl.endswith('ogg') or hl.endswith('wma')

yt_default=[Ref.track(name=u'Dave Brubeck - Take Five', uri='youtube:video/Dave Brubeck - Take Five.vmDDOFXSgAs'),
    Ref.track(name=u'Dave Brubeck - Take Five ( Original Video)', uri='youtube:video/Dave Brubeck - Take Five ( Original Video).PHdU5sHigYQ'),
    Ref.track( name=u'The Dave Brubeck Quartet - Take Five (Not Now Music) [Full Album]', uri='youtube:video/The Dave Brubeck Quartet - Take Five (Not Now Music) Full Album.pcE-m7ntESQ'),
    Ref.track(name=u'Dave Brubeck - Take Five', uri='youtube:video/Dave Brubeck - Take Five.tT9Eh8wNMkw'),
    Ref.track(name=u'Take/Five - Tell Me', uri='youtube:video/TakeFive - Tell Me.Kx1QIlGmhPo'),
    Ref.track(name=u'Al Jarreau 1976 -Take Five', uri='youtube:video/Al Jarreau 1976 -Take Five.hhq7fSrXn0c'),
    Ref.track(name=u'Dave Brubeck, The Dave Brubeck Quartet - Take Five', uri='youtube:video/Dave Brubeck The Dave Brubeck Quartet - Take Five.-DHuW1h1wHw'),
    Ref.track(name=u'North East Ska*Jazz Orchestra - "Take Five"', uri='youtube:video/North East SkaJazz Orchestra - Take Five.wJl0fpUc4U8'),
    Ref.track(name=u'Take/Five - Requiem', uri='youtube:video/TakeFive - Requiem.d-1csddl0VU'),
    Ref.track(name=u'george benson  - Take Five 1976 Montreux 1986', uri='youtube:video/george benson - Take Five 1976 Montreux 1986.Tn27IcAapPI'),
    Ref.track(name=u'MICHEL CAMILO - TAKE FIVE', uri='youtube:video/MICHEL CAMILO - TAKE FIVE.ezkrkxg536o'),
    Ref.track(name=u'Take/Five - Dagger', uri='youtube:video/TakeFive - Dagger.cUmK2-HjyaM'),
    Ref.track(name=u'Take/Five - Hertz', uri='youtube:video/TakeFive - Hertz.n49eiTXEghA'),
    Ref.track(name=u'Take Five - The Dave Brubeck Quartet (1959)', uri='youtube:video/Take Five - The Dave Brubeck Quartet (1959).nzpnWuk3RjU'),
    Ref.track(name=u'Carmen McRae - Take Five', uri='youtube:video/Carmen McRae - Take Five.uEMzWuvUX44'),
    Ref.track(name=u'Dave Brubeck - Take Five', uri='youtube:video/Dave Brubeck - Take Five.vmDDOFXSgAs'),
    Ref.track(name=u'Dave Brubeck - Take Five ( Original Video)', uri='youtube:video/Dave Brubeck - Take Five ( Original Video).PHdU5sHigYQ'),
    Ref.track( name=u'The Dave Brubeck Quartet - Take Five (Not Now Music) [Full Album]', uri='youtube:video/The Dave Brubeck Quartet - Take Five (Not Now Music) Full Album.pcE-m7ntESQ'),
    Ref.track(name=u'Dave Brubeck - Take Five', uri='youtube:video/Dave Brubeck - Take Five.tT9Eh8wNMkw'),
    Ref.track(name=u'Take/Five - Tell Me', uri='youtube:video/TakeFive - Tell Me.Kx1QIlGmhPo'),
    Ref.track(name=u'Al Jarreau 1976 -Take Five', uri='youtube:video/Al Jarreau 1976 -Take Five.hhq7fSrXn0c'),
    Ref.track(name=u'Dave Brubeck, The Dave Brubeck Quartet - Take Five', uri='youtube:video/Dave Brubeck The Dave Brubeck Quartet - Take Five.-DHuW1h1wHw'),
    Ref.track(name=u'North East Ska*Jazz Orchestra - "Take Five"', uri='youtube:video/North East SkaJazz Orchestra - Take Five.wJl0fpUc4U8'),
    Ref.track(name=u'Take/Five - Requiem', uri='youtube:video/TakeFive - Requiem.d-1csddl0VU'),
    Ref.track(name=u'george benson  - Take Five 1976 Montreux 1986', uri='youtube:video/george benson - Take Five 1976 Montreux 1986.Tn27IcAapPI'),
    Ref.track(name=u'MICHEL CAMILO - TAKE FIVE', uri='youtube:video/MICHEL CAMILO - TAKE FIVE.ezkrkxg536o'),
    Ref.track(name=u'Take/Five - Dagger', uri='youtube:video/TakeFive - Dagger.cUmK2-HjyaM'),
    Ref.track(name=u'Take/Five - Hertz', uri='youtube:video/TakeFive - Hertz.n49eiTXEghA'),
    Ref.track(name=u'Take Five - The Dave Brubeck Quartet (1959)', uri='youtube:video/Take Five - The Dave Brubeck Quartet (1959).nzpnWuk3RjU'),
    Ref.track(name=u'Carmen McRae - Take Five', uri='youtube:video/Carmen McRae - Take Five.uEMzWuvUX44'),
    Ref.track(name=u'Dave Brubeck - Take Five', uri='youtube:video/Dave Brubeck - Take Five.vmDDOFXSgAs'),
    Ref.track(name=u'Dave Brubeck - Take Five ( Original Video)', uri='youtube:video/Dave Brubeck - Take Five ( Original Video).PHdU5sHigYQ'),
    Ref.track( name=u'The Dave Brubeck Quartet - Take Five (Not Now Music) [Full Album]', uri='youtube:video/The Dave Brubeck Quartet - Take Five (Not Now Music) Full Album.pcE-m7ntESQ'),
    Ref.track(name=u'Dave Brubeck - Take Five', uri='youtube:video/Dave Brubeck - Take Five.tT9Eh8wNMkw'),
    Ref.track(name=u'Take/Five - Tell Me', uri='youtube:video/TakeFive - Tell Me.Kx1QIlGmhPo'),
    Ref.track(name=u'Al Jarreau 1976 -Take Five', uri='youtube:video/Al Jarreau 1976 -Take Five.hhq7fSrXn0c'),
    Ref.track(name=u'Dave Brubeck, The Dave Brubeck Quartet - Take Five', uri='youtube:video/Dave Brubeck The Dave Brubeck Quartet - Take Five.-DHuW1h1wHw'),
    Ref.track(name=u'North East Ska*Jazz Orchestra - "Take Five"', uri='youtube:video/North East SkaJazz Orchestra - Take Five.wJl0fpUc4U8'),
    Ref.track(name=u'Take/Five - Requiem', uri='youtube:video/TakeFive - Requiem.d-1csddl0VU'),
    Ref.track(name=u'george benson  - Take Five 1976 Montreux 1986', uri='youtube:video/george benson - Take Five 1976 Montreux 1986.Tn27IcAapPI'),
    Ref.track(name=u'MICHEL CAMILO - TAKE FIVE', uri='youtube:video/MICHEL CAMILO - TAKE FIVE.ezkrkxg536o'),
    Ref.track(name=u'Take/Five - Dagger', uri='youtube:video/TakeFive - Dagger.cUmK2-HjyaM'),
    Ref.track(name=u'Take/Five - Hertz', uri='youtube:video/TakeFive - Hertz.n49eiTXEghA'),
    Ref.track(name=u'Take Five - The Dave Brubeck Quartet (1959)', uri='youtube:video/Take Five - The Dave Brubeck Quartet (1959).nzpnWuk3RjU'),
    Ref.track(name=u'Carmen McRae - Take Five', uri='youtube:video/Carmen McRae - Take Five.uEMzWuvUX44')]
