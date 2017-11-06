from __future__ import unicode_literals

import re

from setuptools import find_packages, setup


def get_version(filename):
    with open(filename) as fh:
        metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", fh.read()))
        return metadata['version']


setup(
    name='MopidyRoughRadio',
    version=get_version('mopidy_rough_radio/__init__.py'),
    url='https://github.com/unusual.computers/mopidyroughradio',
    license='Apache License, Version 2.0',
    author='Unusual Computers',
    author_email='unusual.computers@gmail.com',
    description='Mopidy extension for Foobar mechanics',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'setuptools',
        'Mopidy >= 1.0',
        'Mopidy-Podcast-iTunes',
        'Mopidy-Youtube',
        'Pykka >= 1.1',
        'psutil',
        'feedparser',
        'jsonpickle',
        'mutagen',
    ],
    entry_points={
        'mopidy.ext': [
            'rough_radio = mopidy_rough_radio:Extension',
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
)
