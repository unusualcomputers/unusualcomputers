****************************
Mopidy-Mixcloud
****************************


Installation
============

If you already have [mopidy installed](<https://docs.mopidy.com/en/latest/installation/>) and running, you can install just by running on a command line.

If you are using Mopidy 3:

    sudo python3 -m pip install Mopidy-Mixcloud

and for Mopidy 2:

    sudo pip install Mopidy-Mixcloud

 

Use
===

Once installed the addin behaves much like the rest of mopidy addins, with a couple of special tweaks. 
In the browsing section there are directories for Categories, Users and Tags.
*User* directory is used for browsing users' cloudcasts, playlists, favorites etc. By default it is populated from the config file (see below). 
*Tags* directory is used for exploring mixcloud tags, this is like "discover" groups on Mixcloud website. Like users, this is by default populated from the config file (see below). 

Searching for users can be done by adding 'user:' in front of a search string (without quotes), for example:  user:factionmix. 
Once the search is completed the users's cloudcasts will be listed as abums.
Additional user information for all dicovered users wil lbe automatically added to *User* section in the browsing screen.

Similarly you can search for tags (for example tag:jazz) or cities (city:budapest).
The results of these searches will also appear under *Tags* top menu.

To clear this search for string 'refresh:'. This will also clear internal caches so you will be able to get updated data from mixcloud. Caches are cleared automatically about every 10 minutes. 


Configuration
=============

Once installed it will work, you can disable it by setting enabled=false in [mixcloud] section of [mopidy.conf](<https://docs.mopidy.com/en/latest/config/>).
You can also list your favorite users (including yourself) in a comma separated list under *users* setting  in [mixcloud] section. 
These users will then appear in Mixcloud/Users section in Mopidy and you will be able to browse their cloudcasts, playlists, followers etc

Similarly, you can add your favorite tags under *tags* setting, this also works with cities, so you can have something like *tags=city:budapest,jazz* and in your *Tags* section you will have two entries, *city:budapest" and *jazz*. 

Sometimes (often) Mixcloud serches return many, many, many results and this is slow to load and displaybut also not really relevant for the most of it. So the plugin limits the number of results it displays. Default is 20, but this can be changed in configuration file, under *serch_max*.

The plugin caches all of its results, then refreshes the cache about every 10 minutes. This makes it feel faster :) The refresh period can be configured with setting *refresh_period*.

It is, sadly, impossible to play "select exclusive" mixcloud tracks outside their website, even if you are subscribed to them. To reduce the clutter these are ignored and not displayed by the plugin. You can switch that back on and see them, though still not play them, by setting *ignore_exclusive* to False.


Project resources
=================

- [Source code](<https://github.com/unusualcomputers/unusualcomputers/tree/master/code/mopidy/mopidymixcloud>)


Credits
=======

- Original author: [unusual computers](<http://unusualcomputerscollective.org>) (also on [github](<https://github.com/unusualcomputers/unusualcomputers/blob/master/README.md#unusual-computers-collective>))

I have learned a lot from [jackyNIX's](<https://github.com/jackyNIX/xbmc-mixcloud-plugin>) code for kodi MixCloud plugin. 

