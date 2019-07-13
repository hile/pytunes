"""
Python wrapper for MacOS music players (iTunes / Music) using appscript

Example usage:

from pytunes.client import Client
client = Client()

"""

__version__ = '13.0.2'


class MusicPlayerError(Exception):
    pass
