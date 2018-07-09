"""
iTunes background daemon
"""

import os
import redis

from pytunes import iTunesError
from pytunes.status import iTunesStatus


class iTunesDaemon(object):
    """Background daemon for itunes status

    Daemon to monitor itunes status changes. By default just logs tracks played.
    """
    def __init__(self, logfile=None, redis_host=None, redis_auth=None, redis_key='itunesd'):
        self.monitor = iTunesStatus()
        self.logfile = logfile
        if redis_host:
            self.redis = redis.client.StrictRedis(host=redis_host, password=redis_auth)
        else:
            self.redis = None
        self.redis_key = redis_key

    def run(self):
        """Run daemon

        """
        while True:
            status, details = self.monitor.next()
            try:
                self.process_track_change(status, details)
            except iTunesError as e:
                print(e)

    def log_track_change(self, details):
        """Log track changes

        Logs timestamp and path of track played to logfile, if defined.
        """
        if self.logfile is not None:
            path = os.path.expandvars(os.path.expanduser(self.logfile))
            try:
                with open(path, 'a') as f:
                    f.write('{0} {1}\n'.format(
                        details['started'],
                        details['path'],
                    ))
                    f.flush()
            except OSError as e:
                raise iTunesError('Error writing to {0}: {1}'.format(self.log_file, e))
            except IOError as e:
                raise iTunesError('Error writing to {0}: {1}'.format(self.log_file, e))

        if self.redis is not None:
            self.redis.lpush(self.redis_key, details)

    def process_track_change(self, status, details):
        """Process track changes

        Receives current status and track details as arguments. By default logs
        track changes, override to do something else.
        """
        if status == 'playing' and details:
            self.log_track_change(details)
