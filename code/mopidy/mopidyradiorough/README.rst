****************************
Radio Rough
****************************

Radio rough is a computer program for listening to internet. 

For those who care, it is based on the excellent `Mopidy <https://www.mopidy.com/>`_ framework, written in python 2.7, using tk inter for the front end. It has only been tested on linux based machines, would love to hear from anyone who gets it working on Windows or OIS.

Once installed it will let you search YouTube, browse thousands of internet radio streams (via TuneIn) or podcasts published on iTunes. It will also support any additional Mopidy extensions you care to install (look `here <https://docs.mopidy.com/en/latest/ext/backends/>`_ for what's available, much interesting stuff like internet archive, spotify, soma fm ... ). 
It's lightweight and perfect for Raspberry Pi and runs happily even on Pi Zero :) (tested extensively under Ubuntu too)

The look and feel are based on the principles of rough design. It serves its purpose without trying to sell anything, including itself.


Installation
============

On Raspbian machines download `installation script from here  <https://raw.githubusercontent.com/unusualcomputers/unusualcomputers/master/code/mopidy/mopidyradiorough/rr.desktop>`_ (right click on the link and choose 'save as') and place it on the desktop (has to be on the desktop), then double click it. It will install all sorts of dependencies and will ask you if that's ok a couple of times along the way. 
This will create an entry in the start menu in "Audio & Video" section, click on it and enjoy.

To download the above script from the command line run:
::
    wget https://goo.gl/gBdWGw -O ~/Desktop/rr.desktop

This should work on all debian based machines. It downloads and runs this `shell script <https://github.com/unusualcomputers/unusualcomputers/blob/master/code/mopidy/mopidyradiorough/rasp_radio_rough_install.sh>`_


If you already have `mopidy installed <https://docs.mopidy.com/en/latest/installation/>`_ and running, you can install just by running on a command line:
::
    sudo pip install Mopidy-Radio-Rough


Configuration
=============

Once installed it will work, you can disable it by setting enabled=false in [radio_rough] section of `mopidy.conf <https://docs.mopidy.com/en/latest/config/>`_.


How to use radio rough
======================

Radio rough looks like this 

.. image:: https://github.com/unusualcomputers/unusualcomputers/blob/master/writing/pics/radio_rough_start.png

The most interesting part is the list. By double-clicking on it you navigate through sources of sound. Directories of things have square brackets around the name, albums have round brackets, files on your local disk have a star in front of them. 

Right click opens up a menu that tells you what you can do, it changes a bit depending on where you are in the lists. 
All this can be done using keyboard too, see the list of shortcuts below.

.. image:: https://github.com/unusualcomputers/unusualcomputers/blob/master/writing/pics/radio_rough_menu.png

Double click plays the stream or the file (give it a couple of seconds, it needs to be fetched from somewhere on the internet). 
If what you are listening to has a start and an end, once a playback starts the pretty orange line will show you where you are. You can click on it to skip or rewind. Buttons on the right do what you think they do, the small slider changes volume. 

When you float the mouse pointer over something in the list radio rough will get what information it can about it and show it in a tool tip. Very handy when choosing podcasts.

.. image:: https://github.com/unusualcomputers/unusualcomputers/blob/master/writing/pics/radio_rough_tooltip.png

While playing tracks this information will also be shown in the bottom part of the screen. 


.. image:: https://github.com/unusualcomputers/unusualcomputers/blob/master/writing/pics/radio_rough_podcast.png

As long as it is connected to the internet it will happily stream content directly. 
For when you are not it can download podcasts for you. 
If you subscribe to a podcast channel it will check for new episodes daily and download the latest one. It may also delete some old ones, unless you choose to keep them, there is a 'keep' option in the menu for this. (Mind you, if you will always be online when using radio rough it is much better to just mark them as favourites.)

You can also mark things as favourites and you can queue tracks to be played in order and play good stuff in loops. 

Radio rough does not support playlists yet, mostly because I don't ever use them. If you would like to have them drop me a line on unusual.computers(at)gmail.com, we can design them together and I will implement them - or you can if you like. 

Finally, there is a few keyboard shortcuts:

================    ========================
Return              Select item in the list
Backspace           Back one level
Space               Play/Pause
Control-a           Select all in the list
Control-Shift-a     Deselect all in the list
Control-s           Search
Up/Down             Move up/down in the list
Left/Right          Volume up/down
Menu button         Same as right-click
================    ========================

Data
====

Radio rough will keep history of played tracks only for the duration of a session, once you switch it off it will all be gone. It will never create or emit any information on the internet other than what is required by providers it gets tracks from - the usual metadata that sites like YouTube, iTunes etc hoover up. It will keep track of your favourites and subscriptions on the disk even when switched off - the files are saved in ~/.rough folder. 

Feedback
========

We love to hear about bugs, poor solutions and missing features, write to us: unusual.computers(at)gmail.com. 
It is also nice to hear about how well it works, just saying.

`unusual computers collective <https://unusualcomputerscollective.org/>`_
