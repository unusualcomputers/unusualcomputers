# it helps dynamic browsing and menus to know what we are looking at
# in mopidy this is most easily found by looking at uri schemes

youtube_scheme = 'youtube:'
spotify_scheme = 'spotify:'
file_scheme = 'file:'
tunein_scheme = 'tunein:'
itunes_podcast_scheme = 'podcast+itunes:'
podcast_scheme = 'podcast+'
internet_archive_scheme = 'internetarchive:'
soundcloud_scheme = 'soundcloud:'

known_schemes = {
    'YouTube' : youtube_scheme,
    'Spotify' : spotify_scheme,
    'Files' : file_scheme,
    'Podcasts' : podcast_scheme,
    'TuneIn' : tunein_scheme,
    'iTunes Store: Podcasts' : itunes_podcast_scheme,
    'Internet Archive' : internet_archive_scheme,
    'SoundCloud' : soundcloud_scheme
}


def get_scheme(uri,dirName):
    for v in known_schemes.values():
        if uri.startswith(v): return v
    if known_schemes.has_key(dirName):
        return known_schemes[dirName]
    else:
        return None

def name_from_scheme(uri):
    for k,v in known_schemes.items():
        if uri.startswith(v): return k
    return None
    
