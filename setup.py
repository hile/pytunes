
import glob
from setuptools import setup, find_packages
from pytunes import __version__

setup(
    name = 'pytunes',
    author = 'Ilkka Tuohela',
    author_email = 'hile@iki.fi',
    version = __version__,
    keywords = 'iTunes control management playlist export',
    description = 'iTunes CLI control and python API',
    url = 'https://github.com/hile/pytunes',
    license = 'PSF',
    scripts = glob.glob('bin/*'),
    packages = find_packages(),
    install_requires = (
        'soundforest>=4.1.1',
        'systematic>=4.7.8',
        'appscript',
        'configobj',
        'darwinist',
        'zeroconf',
    ),
)
