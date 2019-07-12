"""
Python wrapper for MacOS music players (iTunes / Music) using appscript

Example usage:

from pytunes.client import Client
client = Client()

"""

__version__ = '15.0.1'


class MusicPlayerError(Exception):
    pass
