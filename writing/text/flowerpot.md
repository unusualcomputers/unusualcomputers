# Kodi in a flower pot

  ![pot](../pics/clay1_done2_m.jpg)

> A fully functional kodi machine built into a fully functional flower pot.
> The computer is Raspberry Pi Zero running OpenElec, the pot is made of clay.


There is intrinsic beauty in rough unpolished shapes and there is humanity and deep thought in shaping mud, philosophers know this.

Technologists, on the other hand, know that it is neither hard nor expensive to build small computers and there is immense joy in thinking through the wiring and software to see it light up a screen in the end.

Everyone knows that putting together a useful thing of beauty is what we are for, even at times when taking pride in it is considered naïve.

So here goes a flower pot with the best entertainment centre there is built into it, made for about £17/€20.


### The computer

Pretty much any Raspberry would have worked, so would any of the knock offs (Orange Pi, Banana Pi ... ). Pi Zero is ideal, smallest and the cheapest of the lot. The newer Pi Zero W has a WiFi chip on board, but it would have been wasted here - the machine will be under layers of clay, earth and silicone, reception would be rubbish that deep.

#### Software
Setting up software was as easy as it gets, a straightforward OpenElec installation. 

> To do this yourself:
> If you have access to a computer with an SD card reader, download the OpenElec disk image from [here](http://openelec.tv/get-openelec)  and follow instructions [here](https://www.raspberrypi.org/documentation/installation/installing-images/) to copy in onto SD card. If you don't, by far the best option is to ask someone who does, anyone with a soul should do it for a smile (if they don't have an SD card reader you can buy one for a couple of euros, pounds, dollars).
> The choice of SD cards is permanently a topic on enthusiasts forums, in short, anything with 4Gb or more will work. SanDisk ones are fastest, Kingston probably slowest. Get what you can afford and don't worry.
> Similarly, OpenElec is not the only option, there are at least two more systems just as popular, LibreElec and OSMC - in both set up and usage there is no real difference between them, if you can't make your mind up say their names out loud and choose one you like the best, it will help when you are explaining someone what you did.


#### USB hub

For internet, cable is always faster then WiFi; it can only be used when the TV is close enough to the router but it's good to have this as an option. 
Simplest and probably cheapest is to provide an empty USB port and get hold of a USB-ethernet converter (£2 on ebay). 

For everything else there is a WiFi connection, again a USB WiFi dongle works. 

> The choice of a WiFi dongle is another hot topic in Raspberry Pi community. You can buy them for anything between £2 and £25 and spend a lifetime researching this. If you are buying them in the shop, chances are you can return broken one, so start low and try them. If buying online, anything that mentions raspberry on ebay, aliexpress, amazon etc will do.

We also need some kind of remote control. Kodi works well with remote controls that come with some TV sets, always worth checking [here](http://kodi.wiki/view/CEC) if you know where the machine will be used, if the TV set is listed there, you don't need anything else. I went for a small hand-held keyboard like this: 

![keyboard](../pics/kbd.jpg)

Got it of ebay for a fiver,it took a couple of weeks to arrive and it worked. These keyboards come with a dongle that you plug into USB and just work, a mouse pad and all the keys are there. And it's rechargeable. Can't ask for more.

All in all, three USB ports. The hub used was a 3 eur anonymous ebay special, so had to work a bit to make it work but it does (and in honesty, not worked that hard on it - see [LINK], a small change to autostart.sh file on the sd card and it was up and running).

At this point I put it all together, connected the hub using a mini usb shim (a small adapter that goes inside a usb plug), a TV using a mini HDMI to HDMI cable and powered it up through a USB port on the TV. All was looking great except that I could not install any add-ons no matter what I tried. The next day I re-installed OpenElec and it just worked. Not sure what went wrong, nor if this was a problem with my installation or kodi servers, but the fix was ten minutes of work, so not really sure I care.

Pi zero is tiny, the hub with a plastic box and even the USB plug looked unjustifiably big, so took that apart and soldered it onto the pi board (details [here](https://github.com/unusualcomputers/unusualcomputers/blob/master/writing/text/usbnotes.md#hack-one-software)).

Finally, a flower pot should be round and USB ports should be on its sides, so that dongles stick out for better reception, and the usb hub is rectangular :unamused: 
I had some loose usb ports from before (can't quite remember, but about a couple of pennies each, I ordered them ages ago when buying something else, felt good that I found the use for them). If I didn't I would have desoldered the ones already on the hub and used them. I soldered the ports onto wires, then those onto the hub where existing ports were and had the backbone of the machine ready. Pi and the hub can now be buried in clay and the ports laid near the edge of the pot. I also had to make a connection between the id and ground pins on the micro usb port at this point to make pi recognize the hub, details [here](https://github.com/unusualcomputers/unusualcomputers/blob/master/writing/text/usbnotes.md#soldering-the-hub-to-pi-zero).

And it was beautiful.

![wired](../pics/clay1_wired2_s.jpg)

Tested it all again, and it worked.

#### Insulation

It might not have mattered, but I have no idea how porous or conductive clay is, so had to insulate all this. One option was wrapping it all tightly into a plastic bag, which would likely be fine, but wanted to try [home-made sugru](https://github.com/unusualcomputers/unusualcomputers/blob/master/writing/text/silicone_dough.md#notes-on-silicone-doughoogoohome-made-sugru) for a while, and it worked a charm.

![silicone](../pics/clay1_silicone_s.jpg)

> note to self: it looks alien and feels weird to touch, need to use this for something visible in the future


Tested again. Worked again.


#### The pot

I never even touched clay before, preparations involved reading up a bit and watching youtube while at work in the week before. The plan was to build the computer into the base. Pots need holes in the bottom - the computer is made of two boards, a straw should fit in between them and leave a hole when removed. The bottom will have two layers - I was making a sandwich, clay, computer, clay. And I will use air-drying clay, can't bake this.

Apparently you make a bottom of the pot by rolling clay out into a long sausage and then making a tight swirly circle, so the first layer:

![base](../pics/clay1_base_s.jpg)

Then the machine, cables together, usb ports on the edges, straw through the middle:

![layer](../pics/clay1_layer_s.jpg)

And a layer on top:

![closed](../pics/clay1_closed_s.jpg)

Finally, the walls - again a long sausage of clay layered in a widening spiral, squeezed lightly as I built it up, and there it was :)

  ![pot](../pics/clay1_done_s.jpg)
  ![pot](../pics/clay1_done2_s.jpg)
  ![pot](../pics/clay1_done3_s.jpg)

#### Epilogue:

While drying, which takes days, a crack appeared in the base. Not really a problem, the structure is sound, the electronics well insulated and it wont be visible once the flowers are in. Will fill it up with leftover silicone just so that the pot is not too leaky. The layers of the base need to be thinner - my bad for not trusting clay would harden and easily carry the stuff inside. In hindsight, the usb hackery i did was largely because it was fun - I could easily see all of this working with just a hub plugged in and a bit of a plastic wrapper. The pot may need to be square but nothing wrong with that.  More so, for most other containers this would not matter.


