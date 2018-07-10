"""
Python wrapper for iTunes using appscript APIs

Example usage:

from pytunes.client import iTunes
client = iTunes()

"""

__version__ = '12.7.5.9'


class iTunesError(Exception):
    pass
