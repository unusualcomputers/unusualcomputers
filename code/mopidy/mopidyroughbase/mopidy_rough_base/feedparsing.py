import urlparse
import urllib2
import xml.etree.ElementTree as et
from dateutil.parser import parse as parse_date
import datetime
import podcasts
import feedparser
from util import *
import sys
import traceback

# parsing of podcast feeds
# for rss 2 elements tree is used, it is faster
# for everything else we fall back to feedparser
ITUNES_PREFIX = '{http://www.itunes.com/dtds/podcast-1.0.dtd}'

def _i_tag(tag):#format i tunes tag
    return ITUNES_PREFIX+tag

def _get_e(el,n):#get element text if there
    e=el.find(n)
    if e is not None: return e.text.strip()
    return None

def _get_attrib(el,n,a):#get nodes attribute value if there
    e=el.find(n)
    if e is None: return None
    else: return e.attrib.get(a).strip()

# parsed feeds are cached
class CachedFeedParser():

    def __init__(self):
        self.cache={}
        self.channel_desc_cache={}
        
    def parse_etree(self,channel_uri):
        try:
            rss=urllib2.urlopen(channel_uri).read()
            root=et.fromstring(rss)
            #channel info
            channel_e=root.find('channel')
            channel_name=_get_e(channel_e,'title')
            channel_desc=_get_e(channel_e,'description')
            channel_img=_get_attrib(channel_e,_i_tag('image'),'href')
            channel_auth=_get_e(channel_e,_i_tag('author'))
            #podcats
            parsed_podcasts=[]
            podcast_es=channel_e.findall('item')
            
            for p in podcast_es:
                name=_get_e(p,'title')
                guid=_get_e(p,'guid')
                enclosures=p.findall('enclosure')
                image_uri=None
                p_uri=None
                for e in enclosures:
                    e_uri=e.attrib['url']
                    t=e.attrib['type']
                    if t.startswith('audio'): p_uri=e_uri
                    elif t.startswith('image'):image_uri=e_uri
                    elif is_sound_file(e_uri): p_uri=e_uri
                if (p_uri is None) and len(enclosures)>0:
                    p_uri=enclosures[0].attrib['url']
                if image_uri is None:
                    image_uri=channel_img
                artist=_get_e(p,_i_tag('author'))
                if artist is None: artist=_get_e(p,'author')
                if artist is None: artist=channel_auth
                description=_get_e(p,'description')
                if description is None:
                    description=_get_e(p,_i_tag('summary'))
                date=_get_e(p,'pubDate')
                if date is not None:        
                    date=parse_date(date).isoformat()
                else:
                    date=datetime.date.today().isoformat()
                length=_get_e(p,_i_tag('duration'))
                podcast=podcasts.Podcast(name,p_uri,guid,artist,description,
                    date,length,image_uri,channel_uri,channel_name)
                parsed_podcasts.append(podcast)

            parsed_podcasts=sorted(parsed_podcasts,key=lambda p: p.date,reverse=True)    

            channel=podcasts.Channel(channel_name,channel_desc,channel_uri,
                channel_img,parsed_podcasts)
            return channel
        except:
            e = sys.exc_info()
            traceback.print_exception(*e)
            return None
    
    def parse_feedparser(self,channel_uri):
        feed=feedparser.parse(channel_uri)
        channel_name=feed.feed['title']
        loaded=[]
        for p in feed.entries:
            uri=None
            image_uri=None
            for e in p.enclosures:
                if e.type.startswith('audio'):
                    uri=e.href
                elif e.type.startswith('image'):
                    image_uri=e.href
                elif is_sound_file(e.href): uri=e.href
            if uri is None and len(p.enclosures)==1:
                uri=p.enclosures[0].href
            title=p.get('title')
            guid=p.get('guid')
            if (uri is None) or (title is None):
                continue#need at least these
            pub=p.get('pubDate')
            if pub is None:
                date=datetime.date.today().isoformat()
            else:
                date=parse_date(date).isoformat()
            podcast=podcasts.Podcast( name=title,
                uri=uri,
                guid=guid,
                artist=p.get('author',p.get('authors')),
                description=p.get('summary'),
                date=date,
                length=p.get('itunes_duration'),
                image_uri=image_uri,
                channel_uri=channel_uri,
                channel_name=channel_name)
            loaded.append(podcast)
        feed=feed.feed
        description=feed.get('description')
        if feed.get('image') is None:
            img=None
        else:
            img=feed.get('image').get('href')
        loaded=sorted(loaded,key=lambda p: p.date,reverse=True)    
        c = podcasts.Channel(channel_name,description,channel_uri,img,loaded)
        return c
            
    def parse(self,uri):
        channel=self.cache.get(uri)
        if channel is not None: return channel
        return self.update(uri)

    def parse_channel_desc(self,uri):
        desc=self.channel_desc_cache.get(uri)
        if desc is not None: return desc
        else:
            rss=urllib2.urlopen(uri).read()
            root=et.fromstring(rss)
            channel_e=root.find('channel')
            desc=_get_e(channel_e,'description')
            self.channel_desc_cache[uri]=desc
            return desc
            
    def update(self,uri):
        c=self.parse_etree(uri)
        if c is None:
            c=self.parse_feedparser(uri)
        self.cache[uri]=c
        return c

    def clear(self):
        self.cache.clear()
