****************************
Radio Rough HTML
****************************

Radio rough HTML is a rough and simple interface for Mopidy. It is intended to provide a usable interface to excellent Mopidy via simpler devices and browsers that do not support fanciness that is java script.
Or you can use it if you like things simple and as fast as can be. I will work on pretty much anything with any sort of browser - tried it on an old IPod, pi zero with dillo, a ubuntu box ...

Once installed it will let you search YouTube, browse thousands of internet radio streams (via TuneIn) or podcasts published on iTunes. It will also support any additional Mopidy extensions you care to install (look `here <https://docs.mopidy.com/en/latest/ext/backends/>`_ for what's available, much interesting stuff like internet archive, spotify, soma fm ... ). 

The look and feel are based on the principles of rough design. It serves its purpose without trying to sell anything, including itself.


Installation
============

If you already have `mopidy installed <https://docs.mopidy.com/en/latest/installation/>`_ and running, you can install just by running on a command line:
::
    sudo pip install Mopidy-Radio-Rough-HTML

On Raspberries, probably the ideal setup is to run it with Pi Music Box. It will run just fine even on a pi zero and once installed you will find in at musicbox.local/radiorough.

Configuration
=============

Once installed it will work, you can disable it by setting enabled=false in [radio_rough_html] section of `mopidy.conf <https://docs.mopidy.com/en/latest/config/>`_.
