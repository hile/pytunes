"""
iTunes background daemon
"""

import configobj
import os
import redis

from pytunes import iTunesError
from pytunes.status import iTunesStatus

DEFAULT_CONFIGURATION_PATH = '~/Library/Application Support/Pytunes/itunesd.conf'

# Max songs to keep in redis queue
MAX_REDIS_LIST_ITEMS = 8000

class iTunesDaemonConfiguration(dict):
    """Configuration for iTunesDaemon

    """

    def __init__(self,
                 path=DEFAULT_CONFIGURATION_PATH,
                 logfile=None, redis_host=None, redis_auth=None, redis_key='itunesd'):

        self['logfile'] = logfile
        self['redis_host'] = redis_host
        self['redis_auth'] = redis_auth
        self['redis_key'] = redis_key

        path = os.path.expandvars(os.path.expanduser(path))
        if os.path.isfile(path):
            self.update(configobj.ConfigObj(path).items())


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

        if self.redis:
            try:
                self.redis.ping()
            except Exception as e:
                print(e)

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
            self.redis.ltrim(self.redis_key, MAX_REDIS_LIST_ITEMS)

    def process_track_change(self, status, details):
        """Process track changes

        Receives current status and track details as arguments. By default logs
        track changes, override to do something else.
        """
        if status == 'playing' and details:
            self.log_track_change(details)
