"""
Python wrapper for iTunes using appscript APIs

Example usage:

from pytunes.client import iTunes
client = iTunes()

"""

__version__ = '12.6.1.25.1'

class iTunesError(Exception):
    pass

