
import glob
from setuptools import setup, find_packages
from pytunes import __version__

setup(
    name='pytunes',
    author='Ilkka Tuohela',
    author_email='hile@iki.fi',
    version=__version__,
    keywords='iTunes Music control management playlist export',
    description='iTunes / Music CLI control and python API',
    url='https://github.com/hile/pytunes',
    license='PSF',
    scripts=glob.glob('bin/*'),
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pytunes=pytunes.bin.pytunes:main',
            'pytunes-playlists=pytunes.bin.pytunes_playlists:main',
            'pytunes-db=pytunes.bin.pytunes_db:main',
            'pytunesd=pytunes.bin.pytunesd:main',
        ],
    },
    setup_requires=['pytest-runner'],
    tests_require=(
        'pytest',
        'pytest-runner',
        'pytest-datafiles',
    ),
    install_requires=(
        'soundforest>=4.2.4',
        'systematic>=4.8.0',
        'appscript',
        'configobj',
        'darwinist',
        'redis',
        'zeroconf',
    ),
)
