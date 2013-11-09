#!/usr/bin/env python

import sys
import glob
from setuptools import setup, find_packages

if sys.platform != 'darwin':
    print 'ERROR: this module uses applescript and only works in OS/X'
    sys.exit(1)

VERSION='3.0.0'
setup(
    name = 'pytunes',
    version = VERSION,
    zip_safe = False,
    scripts = glob.glob('bin/*'),
    packages = ('pytunes',),
    install_requires = (
        'appscript',
        'configobj',
        'darwinist',
        'soundforest',
    ),
    author = 'Ilkka Tuohela',
    author_email = 'hile@iki.fi',
    url = 'http://tuohela.net/packages/pytunes',
    description = 'Module for itunes library management and remote control',
    license = 'PSF',
    keywords = 'iTunes control management playlist export',
)

