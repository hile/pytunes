
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
    url='https://github.com/hile/pytunes/',
    license='PSF',
    packages=find_packages(),
    python_requires='>3.6.0',
    entry_points={
        'console_scripts': [
            'pytunes=pytunes.bin.pytunes:main',
            'pytunes-playlists=pytunes.bin.pytunes_playlists:main',
            'pytunes-update=pytunes.bin.pytunes_update:main',
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
        'oodi',
        'systematic>=4.8.0',
        'appscript',
        'configobj',
        'darwinist',
        'redis',
        'zeroconf',
    ),
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3',
        'Topic :: System',
        'Topic :: System :: Systems Administration',
    ],
)
