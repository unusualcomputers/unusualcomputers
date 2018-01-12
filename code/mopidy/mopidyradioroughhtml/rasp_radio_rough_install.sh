#!/bin/sh


## Mopidy installation first
## copied from https://docs.mopidy.com/en/latest/installation/debian/

# 1. Add the archive’s GPG key:
echo Adding mopidy GPG key
sudo wget -q -O - https://apt.mopidy.com/mopidy.gpg | sudo apt-key add -

# 2. Add the APT repo to your package sources:
echo Adding mopidy repo
sudo wget -q -O /etc/apt/sources.list.d/mopidy.list https://apt.mopidy.com/jessie.list

# 3. Install Mopidy and all dependencies:
echo Updating repos
sudo apt-get update
echo Installing mopidy
sudo apt-get install mopidy

## Then radio rough
echo Installing radio rough
sudo pip install -U Mopidy-Radio-Rough-HTML

## Install a version of youtube-dl that doesn't have 'unknown url type' bug
echo Installing youtube-dl
sudo pip install git+https://github.com/Khang-NT/youtube-dl.git
 
## Setup the start menu
echo Copying desktop and icon files
sudo wget https://raw.githubusercontent.com/unusualcomputers/unusualcomputers/master/code/mopidy/mopidyradioroughhtml/mopidy_radio_rough_html/radio_rough.desktop -O /usr/share/applications/radio_rough.desktop

sudo wget https://github.com/unusualcomputers/unusualcomputers/raw/master/code/mopidy/mopidyradioroughhtml/mopidy_radio_rough_html/icons/ucc.png -O /usr/share/pixmaps/ucc.png

sudo wget https://github.com/unusualcomputers/unusualcomputers/raw/master/code/mopidy/mopidyradioroughhtml/mopidy_radio_rough_html/icons/ucc.gif -O /usr/share/pixmaps/ucc.gif

## Update the start menu
sudo lxpanelctl restart

echo
echo **********************************************************************
echo * radio rough is installed                                           *
echo * run it from the start menu or type sudo mopidy on the command line *
echo **********************************************************************
echo
