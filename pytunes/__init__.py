"""
Python wrapper for iTunes using appscript APIs
"""

import sys

__all__ = ( 'client', 'constants', 'itc', 'playlist', 'status', 'terminology' )

class iTunesError(Exception):
    pass

