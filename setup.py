#!/usr/bin/env python

import sys,glob
from setuptools import setup,find_packages

if sys.platform != 'darwin':
    print 'ERROR: this module uses applescript and only works in OS/X, your system is %s' % sys.platform
    sys.exit(1)

VERSION='2.0.0'

setup(
    name = 'pytunes',
    version = VERSION,
    zip_safe = False,
    install_requires = [
        'musa','soundforest','appscript','configobj','systematic','darwinist'
    ],

    scripts = glob.glob('bin/*'),
    packages = ['pytunes'],

    author = 'Ilkka Tuohela', 
    author_email = 'hile@iki.fi',
    url = 'http://tuohela.net/packages/pytunes',
    description = 'Module for itunes library management and remote control',
    license = 'PSF',
    keywords = 'iTunes control management playlist export',

)   

