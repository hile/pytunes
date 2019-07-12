#!/usr/bin/env python
"""
Daemon process to log songs played by MacOS music player
"""

from soundforest.cli import Script
from pytunes import MusicPlayerError
from pytunes.daemon import Daemon, DaemonConfiguration, DEFAULT_CONFIGURATION_PATH

DEFAULT_LOGFILE = '~/Library/Logs/pytunes.log'


def main():

    script = Script()
    script.add_argument('-f', '--log-file', default=DEFAULT_LOGFILE, help='Log file')
    script.add_argument('-c', '--configuration-file', default=DEFAULT_CONFIGURATION_PATH, help='Log file')
    script.add_argument('-h', '--redis-host', help='Redis host')
    script.add_argument('-r', '--redis-auth', help='Redis auth')
    args = script.parse_args()

    try:
        configuration = DaemonConfiguration(
            args.configuration_file,
            args.log_file,
            args.redis_host,
            args.redis_auth,
        )
    except Exception as e:
        script.exit(1, e)

    try:
        Daemon(**configuration).run()
    except MusicPlayerError as e:
        script.exit(1, e)
