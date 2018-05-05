****************************
Radio Rough HTML
****************************

Radio rough HTML is a rough and simple interface for Mopidy. It is intended to provide a usable interface to excellent Mopidy via simpler devices and browsers that do not support fanciness that is java script.
Or you can use it if you like things simple and as fast as can be. It will work on pretty much anything with any sort of browser - tried it on an old IPod, pi zero with dillo, a ubuntu box ...

Once installed it will let you search YouTube, browse thousands of internet radio streams (via TuneIn) or podcasts published on iTunes. It will also support any additional Mopidy extensions you care to install (look `here <https://docs.mopidy.com/en/latest/ext/backends/>`_ for what's available, much interesting stuff like internet archive, spotify, soma fm ... ). 

The look and feel are based on the principles of rough design. It serves its purpose without trying to sell anything, including itself.


Installation
============

If you already have `mopidy installed <https://docs.mopidy.com/en/latest/installation/>`_ and running, you can install just by running on a command line:
::
    sudo pip install Mopidy-Radio-Rough-HTML

On Raspberries, probably the ideal setup is to run it with Pi Music Box. It will run just fine even on a pi zero and once installed you will find in at musicbox.local/radiorough.

Alternatively, on debian based machines (including Raspbian) download `installation script from here  <https://github.com/unusualcomputers/unusualcomputers/blob/master/code/mopidy/mopidyradioroughhtml/rr.desktop>`_ (right click on the link and choose 'save as') and place it on the desktop (has to be on the desktop), then double click it. It will install all sorts of dependencies and will ask you if that's ok a couple of times along the way. 
This will create an entry in the start menu in "Audio & Video" section, click on it and enjoy. Otherwise, once installed just run modpidy, e.g. sudo mopidy on the command line.

To download the above script from the command line run:
::
    wget https://goo.gl/qjGZeG -O ~/Desktop/rr.desktop

It downloads and runs this `shell script <https://github.com/unusualcomputers/unusualcomputers/blob/master/code/mopidy/mopidyradioroughhtml/rasp_radio_rough_install.sh>`_


If you don't have Music Box set up it will be wherever your mopidy is in your browser, by default localhost:6680/radiorough or 127.0.0.1:6680/radiorough. 
You can quite easily make it accessible from any computer on your local network at home: find the file mopidy.conf on your computer. For example by typing sudo find / -name mopidy.conf on the command line.
There may be more than one, just change them all as follows: open the file, any text editor will do,for example: sudo nano /root/.config/mopidy/mopidy.conf. I the file, find section [http] and in it the line that mentions 'hostname'. Change this line to be exactly: hostname=0.0.0.0 (make sure there is no # in front of it).
Then you can access radiorough from any computer on your network using the ip adress of the machine you are running it on, e.g. http://192.168.0.1:6680/radiorough. You can do even better by naming your host and making sure mopidy runs always, drop me a line if you need help with this.


Use
===

At the start Radio Rough will present you with the list of browsable Mopidy addins that you can explore by clicking on them. 
Once you select one, a search box will appear at the top. 
In addition, via the home page or buttons at the bottom of every page you can access Favorites, Playlists, Queue and History of tracks played (favorites and history are internal to radio rough, not the same ones you have in your browser and history is kept for a single session only).

The rest of the navigation is via buttons at the top of the screen and next to each item in lists, this should be quite intuitive and there are tooltips to help.

Since there are no dynamic features used (i.e. no JavaScript and such) to  display track progress the page needs to be refreshed, you can make this happen automatically ever ten seconds or so using auto-refresh button at the bottom of every page.


Configuration
=============

Once installed it will work, you can disable it by setting enabled=false in [radio_rough_html] section of `mopidy.conf <https://docs.mopidy.com/en/latest/config/>`_.

Credits
=======

I used icons downloaded from `flaticon universal interface <https://www.flaticon.com/packs/universal-interface>`_.
