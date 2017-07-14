# Notes on editing raspberry configuration files

### 101

All operating systems that matter on pi use text files for various bits of software and hardware configuration, running things at launch and so on and so on. In most cases there are no other ways to tweak things. 

They are always in plain text format, as universal as it gets so you can edit them on pretty much any computer you can get hold of. If you are doing this on the pi itself they will be easily accessible through the file system there. Sometimes you won't because you will need to fix things in order to make pi run in the first place. 
Raspberry uses sd cards in place of hard drives and all files are there so in these situations you need an sd card reader (well, reader/writer, but they all are). Many machines come with this, a thin flat slot, about 2cm wide, if not, you have to borrow or buy one (don't pay more than a couple of euros/dollars/pounds). 

Once you plug the sd card in, things will appear as folders or drives (depending on the system) on your computer. Raspberry sd cards are split into two parts, called partitions, each like a separate drive. First one is used by raspberry during booting to read various configuration details from, load drivers etc. When are working on the raspberry, this is accessible as folder `/boot`, the other (main) partition is the root of your file system, you would see it as the only drive on the machine. On windows the boot partition will appear as a separate drive, like when you plug in a usb memory stick. The second partition is not always visible on windows, if it is, it will appear as yet another drive. On linux, both partitions should appear as new folders, probably somewhere under `/media`, one will be called 'boot', the other will most often have a weird name made of letters, numbers and dashes - in Ubuntu they pop up on the screen in file manager.

Now that you have a way to access the files you will need a text editor, a program used for changing text files. Anything will do, on most systems if you right-click the file it will offer to open it for you. On windows notepad works a charm. On linux there are many, if you have time to learn about 'nano' it is well worth it. It is a command line editor, so you work in a terminal window, but easy to use and a favourite in the community so many blogs and examples use it. (someone please tell us what to use on apple boxes).

Some of these files are protected, you won't be able to save them by default. On windows, this is mostly ignored so you are fine, if not, right click and make them writeable. On unix, run your editor with 'sudo' (e.g. type `sudo nano` instead of just `nano`). 

Always, always, always unmount/eject the card before you take it out (most systems let you do this by right clicking on the icon that is your card) - some systems will quietly just not write your changes if you don't even if you clicked save. On linux you can also type `sudo sync` to make sure all is written before removing the card.

And always make a copy of the file before you change it, most of the time you will not need it but when you do it is a desperate need.

## config.txt

This is by far the most important configuration file on any raspberry pi. It is read and applied very early during the booting and lets you configure the machine hardware and the operating system itself. This is where you would play with video resolution, audio options, usb power and much more. It is very well documented:  https://www.raspberrypi.org/documentation/configuration/config-txt/ 

From the documentation:


> The config.txt file is read by the early-stage boot firmware, so it has a very simple file format. The format is a single property=value statement on each line, where value is either an integer or a string. Comments may be added, or existing config values may be commented out and disabled, by starting a line with the # character.


It lives in the boot partition of the sd card (see above).
On linux the file needs to be edited with root privileges, so if using nano, open a terminal and type something like: `sudo nano /boot/config.txt` (if on raspberry, on other linux boxes the path to the file will be different - open the partition in whatever file manager you are using and copy the path from there, in most terminals you paste text by right-click).

## rc.local

This contains commands to run just after the system has booted. You will use it to get raspberry to automatically launch programs or perform various initialisation hacks. 
The format is a bit more complicated, but this is documented well (https://www.raspberrypi.org/documentation/linux/usage/rc-local.md), and in practice you will be mostly copy-pasting stuff from the web into it.

It lives on the main partition (not the boot one, the other one :)) in `/etc/rc.local`. If it is not there, create it when you need it. It is easiest to edit on pi itself,  something like `sudo nano /etc/rc.local`. Similarly on any linux box, except that the entire path is different (see config.txt section).

## OpenElec/LibreElec autostart.sh

OpenElec/LibreElec are very popular for running kodi. They don't have rc.local, they have autostart.sh instead. It lives in `/storage/.config/autostart.sh` (the path will likely be different on machines other than pi running it, you'll find .configure folder on the main partition and if the file is not there, create it). Other than that, it works just like rc.local, and has some of its own documentation (http://wiki.openelec.tv/index.php/Autostart.sh)
