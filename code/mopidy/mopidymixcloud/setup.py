from __future__ import unicode_literals

import re

from setuptools import find_packages, setup


def get_version(filename):
    with open(filename) as fh:
        metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", fh.read()))
        return metadata['version']

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='Mopidy-Mixcloud',
    version=get_version('mopidy_mixcloud/__init__.py'),
    url='https://github.com/unusualcomputers/unusualcomputers/tree/master/code/mopidy/mopidymixcloud',
    license='Apache License, Version 2.0',
    author='Unusual Computers',
    author_email='unusual.computers@gmail.com',
    description='Mopidy Mixcloud extension',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'setuptools',
        'Mopidy >= 1.0',
        'Pykka >= 1.1',
        'yt_dlp >= 2023.9.24'
    ],
    entry_points={
        'mopidy.ext': [
            'mixcloud = mopidy_mixcloud:Extension',
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
