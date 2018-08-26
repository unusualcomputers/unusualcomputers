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
sudo apt-get install -y mopidy
echo Installing gstreamer stuff
sudo apt-get install -y gstreamer1-devel gstreamer1-plugins-base-tools gstreamer1-devel-docs gstreamer1-plugins-base-devel gstreamer1-plugins-base-devel-docs gstreamer1-plugins-good gstreamer1-plugins-good-extras gstreamer1-plugins-ugly gstreamer1-plugins-ugly-devel-docs  gstreamer1-plugins-bad-free gstreamer1-plugins-bad-free-devel gstreamer1-plugins-bad-free-extras
echo Installing pip
sudo apt-get install -y python-pip

## Then radio rough
echo Installing radio rough
sudo pip install -y uritools
sudo pip install -y -U Mopidy-Radio-Rough-HTML

## Install a version of youtube-dl that doesn't have 'unknown url type' bug
echo Installing youtube-dl
sudo pip install -y -U youtube-dl

echo
echo **********************************************************************
echo * radio rough is installed                                           *
echo * run it from the start menu or type sudo mopidy on the command line *
echo **********************************************************************
echo
