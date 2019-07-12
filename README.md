
MacOS iTunes / Music command line and python API
================================================

Note: these scripts work both with iTunes 12.x and MacOS Catalina Music app. These apps share
same appscript bridge internally.

This module implements a wrapper for macos music player appscript control and allows updating
library and playlists from command line.

This module uses apple script bridge and only works on OS X. No windows support is planned.

Library track index database
============================

There is a custom sqlite database for music player track indexes. This database is used when
playing tracks by path from shell, like:

```
pytunes play 'Music/Library/ACDC/Back in Black/01 Hells Bells.m4a'
```

The command works without the database, but can be very slow, because there is no direct
way to lookup track ID and client.play(path) actually imports track, not just plays it.

Creating index of itunes tracks to sqlite is thus recommended and can be done with:

```
pytunes update-index
```

Player status daemon
====================

The pytunesd daemon currently does very little. Currently it's only purpose is to log any
played tracks with timestamp to ~/Library/Logs/pytunes.log file, or if a configuration file
exists and redis is configured, publish the track details to redis.

You can extend the pytunes.daemon.MusicPlayerDaemon class process_track_change method to do
something else. This method is called whenever the player track changes or playback status
is changed, and receives playback status and track details as arguments.

Status daemon configuration file
--------------------------------

Configuration file can be used to publish played tracks to a list in redis. The configuration
file default path is ~/Library/Application Support/Pytunes/pytunesd.conf and can contain all
arguments given to pytunes.daemon.iTunesDaemon class, example:


```
redis_host = 'localhost'
redis_auth = 'password-to-local-redis'
```

Maximum list length is now set to 8000 entries in hard coded variable.
