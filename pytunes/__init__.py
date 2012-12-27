
import sys

__all__ = [ 'client', 'itc', 'playlist', 'status', 'terminology' ]

class iTunesError(Exception):
    def __str__(self):
        return self.args[0]

