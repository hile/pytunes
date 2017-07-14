
iTunes command line and python API
==================================

This module implements a wrapper for itunes appscript control and allows updating
library and playlists from command line.

There used to be a notification agent with itunesd but this has now been removed, as
itunes has it's own notifications.

This module uses apple script bridge and only works on OS X. No windows support is planned.

iTunes index database
---------------------

There is a custom sqlite database for itunes track indexes. This database is used when
playing tracks by path from shell, like:

```
itunes play 'Music/Library/ACDC/Back in Black/01 Hells Bells.m4a'
```

The command works without the database, but can be very slow, because there is no direct
way to lookup track ID from itunes and itunes.play(path) actually imports track, not just
plays it.

Creating index of itunes tracks to sqlite is thus recommended and can be done with:

```
itunes update-index
```

iTunes status daemon
--------------------

The itunesd daemon currently does very little. Currently it's only purpose is to log any
played tracks with timestamp to ~/Library/Logs/itunes.log file.

You can extend the pytunes.daemon.iTunesDaemon class process_track_change method to do
something else. This method is called whenever itunes track changes or playback status
is changed, and receives playback status and track details as arguments.

There is example example launch agent file in examples/com.tuohela.net.itunesd.plist
that can be used to load itunesd with launchctl. This example expects you use homebrew's
python2.7 from /usr/local/bin.
