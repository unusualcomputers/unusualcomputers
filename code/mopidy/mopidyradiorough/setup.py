from __future__ import unicode_literals

import re

from setuptools import find_packages, setup
from setuptools.command.install import install

gstreamer_cmd='sudo apt-get install python-gst-1.0 \
    gir1.2-gstreamer-1.0 gir1.2-gst-plugins-base-1.0 \
    gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly \
    gstreamer1.0-tools'.split()

class InstallGstreamerStuff(install):
    def run(self):
        from subprocess import call
        print 'Installing gstreamer dependencies'
        call(gstreamer_cmd)
        install.run(self)
    
def get_version(filename):
    with open(filename) as fh:
        metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", fh.read()))
        return metadata['version']


setup(
    name='Mopidy-Radio-Rough',
    version=get_version('mopidy_radio_rough/__init__.py'),
    url='https://github.com/unusualcomputers/unusualcomputers/tree/master/code/mopidy/mopidyradiorough',
    license='Apache License, Version 2.0',
    author='Unusual Computers',
    author_email='unusual.computers@gmail.com',
    description='Rough gui for listening to internet',
    long_description=open('README.rst').read(),
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'setuptools',
        'Mopidy >= 1.0',
        'Mopidy-Podcast-iTunes',
        'Mopidy-Youtube',
        'Mopidy-Rough-Base',
        'Pykka >= 1.1',
        'feedparser',
        'jsonpickle',
        'mutagen',
    ],
    entry_points={
        'mopidy.ext': [
            'radio_rough = mopidy_radio_rough:Extension',
        ],
    },
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
    data_files=[
        ('/usr/share/applications',['mopidy_radio_rough/radio_rough.desktop']),
        ('/usr/share/pixmaps',['mopidy_radio_rough/ucc.gif','mopidy_radio_rough/ucc.png','mopidy_radio_rough/ucc_64.png']),
    ],
    cmdclass={
        'install': InstallGstreamerStuff,
    },
)
