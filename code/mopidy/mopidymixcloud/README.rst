****************************
Mopidy-Mixcloud
****************************


Installation
============

If you already have `mopidy installed <https://docs.mopidy.com/en/latest/installation/>`_ and running, you can install just by running on a command line:
::
    sudo pip install Mopidy-Mixcloud


Use
===

Once installed the addin behaves much like the rest of mopidy addins, with a couple of special tweaks. 
In the browsing section there are directories for Categories, Popular, New and Hot cloudcasts as well as a User directory.
*User* directory is used for browsing users' cloudcasts, playlists, favorites etc. By default it is populated from the config file (see below). 

Searching for users can be done by adding 'user:' in front of a search string (without quotes), for example:  user:factionmix. 
Once the search is completed the users's cloudcasts will be listed as abums.
Additional user information for all dicovered users wil lbe automatically added to *User* section in the browsing screen.
To clear this search for string 'refresh:'. This will also clear internal caches so you will be able to get updated data from mixcloud. Caches are cleared automatically about every 10 minutes. 


Configuration
=============

Once installed it will work, you can disable it by setting enabled=false in [mixcloud] section of `mopidy.conf <https://docs.mopidy.com/en/latest/config/>`_.
You can also list your favorite users (including yourself) in a comma separated list under *users* setting  in [mixcloud] section of `mopidy.conf <https://docs.mopidy.com/en/latest/config/>`_. 
These users will then appear in Mixcloud/Users section in Mopidy and you will be able to browse their cloudcasts, playlists, followers etc

Project resources
=================

- `Source code <https://github.com/unusualcomputers/unusualcomputers/tree/master/code/mopidy/mopidymixcloud>`_


Credits
=======

- Original author: `unusual computers <http://unusualcomputerscollective.org>`__ (also on `github <https://github.com/unusualcomputers/unusualcomputers/blob/master/README.md#unusual-computers-collective>`__)

I have learned a lot from `jackyNIX's <https://github.com/jackyNIX/xbmc-mixcloud-plugin>`__ code for kodi mopidy plugin. 

