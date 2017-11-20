****************************
Mopidy Radio Rough
****************************

Rough gui for listening to internet. 

Installation
============

On Raspbian machines download `installation script from here  <https://raw.githubusercontent.com/unusualcomputers/unusualcomputers/master/code/mopidy/mopidyradiorough/rr.desktop>`_ (right click on the link and choose 'save as') and place it on the desktop (has to be on the desktop), then double click it. It will install all sorts of dependencies and will ask you if that's ok a couple of times along the way.

To download the above scritp from the command line run:
::
    wget https://goo.gl/gBdWGw -O ~/Desktop/rr.desktop

This should work on all debian based machines. It downloads and runs this `shell script <https://github.com/unusualcomputers/unusualcomputers/blob/master/code/mopidy/mopidyradiorough/rasp_radio_rough_install.sh>`_


If you already have mopidy installed and running, you can install just by running on a command line:
::
    sudo pip install Mopidy-Radio-Rough


Configuration
=============

Once installed it will work, you ca disable it by setting enabled=false in [radio_rough] section of mopidy.conf.

Project resources
=================

- `Source code <https://github.com/unusual.computers/mopidyroughradio>`_
- `Issue tracker <https://github.com/unusual.computers/mopidyroughradio/issues>`_


Credits
=======

- Original author: `Unusual Computers <https://github.com/unusual.computers`__
- Current maintainer: `Unusual Computers <https://github.com/unusual.computers`__
- `Contributors <https://github.com/unusual.computers/mopidyroughradio/graphs/contributors>`_


Changelog
=========

v0.1.0 (UNRELEASED)
----------------------------------------

- Initial release.
