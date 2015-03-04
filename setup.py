
import sys
import glob
from setuptools import setup, find_packages

if sys.platform != 'darwin':
    print 'ERROR: this module uses applescript and only works in OS/X'
    sys.exit(1)

VERSION='3.2'

setup(
    name = 'pytunes',
    version = VERSION,
    author = 'Ilkka Tuohela',
    author_email = 'hile@iki.fi',
    keywords = 'iTunes control management playlist export',
    description = 'Module for itunes library management and remote control',
    url = 'https://github.com/hile/pytunes',
    license = 'PSF',
    scripts = glob.glob('bin/*'),
    packages = find_packages(),
    install_requires = (
        'soundforest>=3.1',
        'appscript',
        'configobj',
        'darwinist',
    ),
)

