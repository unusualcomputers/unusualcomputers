from __future__ import unicode_literals

import re

from setuptools import find_packages, setup


def get_version(filename):
    with open(filename) as fh:
        metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", fh.read()))
        return metadata['version']


setup(
    name='Mopidy-Rough-Base',
    version=get_version('mopidy_rough_base/__init__.py'),
    url='https://github.com/unusualcomputers/unusualcomputers/tree/master/code/mopidy/mopidyroughbase',
    license='Apache License, Version 2.0',
    author='Unusual Computers',
    author_email='unusual.computers@gmail.com',
    description='Shared classes for building radio rough guis.',
    long_description=open('README.rst').read(),
    packages=find_packages(),
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
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
)
