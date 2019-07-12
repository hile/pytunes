#!/usr/bin/env python
"""
Example script to view and control macos music player playback status
"""

import time

from soundforest.cli import Script, ScriptCommand

from pytunes import MusicPlayerError
from pytunes.client import Client

INFO_FORMAT = """
Artist  %(artist)s
Album   %(album)s
Title   %(title)s
Genre   %(genre)s
Track   %(track_number)s/%(track_count)s
Length  %(time)s
Year    %(year)s
BPM     %(bpm)s
Comment %(comment)s
"""


class CLICommand(ScriptCommand):
    """
    Base class for CLI commands
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.client = Client()
        except MusicPlayerError as e:
            self.exit(1, 'Error connecting to music player: {}'.format(e))


class InfoCommand(CLICommand):
    """Show info

    Show info about playing track
    """
    def run(self, args):
        if self.client.current_track:
            track = self.client.current_track
            if args.verbose:
                self.message(track.path)
            self.message(INFO_FORMAT % (track))
        else:
            self.message('No song playing')


class PlayCommand(CLICommand):
    """Play track or start playback

    """
    def run(self, args):
        if args.track:
            self.client.play(args.track)
        else:
            if self.client.status == 'playing':
                self.client.pause()
            else:
                self.client.play()


class StopCommand(CLICommand):
    """Stop playback

    """
    def run(self, args):
        if self.client.status in ('playing', 'paused',):
            self.client.stop()


class PreviousTrackCommand(CLICommand):
    """Jump to previous tack

    """
    def run(self, args):
        self.client.previous()


class NextTrackCommand(CLICommand):
    """Jump to next tack

    """
    def run(self, args):
        self.client.next() # noqa B305


class ShuffleModeCommand(CLICommand):
    """Show or set shuffle mode

    """
    def run(self, args):
        if args.mode == 'enable':
            self.client.shuffle = True
        elif args.mode == 'disable':
            self.client.shuffle = False
        else:
            self.message('Shuffle {}'.format(self.client.shuffle and 'enabled' or 'disabled'))


class VolumeCommand(CLICommand):
    """Show or set volume

    """
    def run(self, args):
        if args.volume is None:
            self.message('volume {:d}%'.format(self.client.volume))
            return

        fade = True
        try:
            if args.volume.startswith('+'):
                volume = self.client.volume + int(args.volume[1:])
                if volume > 100:
                    volume = 100
            elif args.volume.startswith('-'):
                volume = self.client.volume - int(args.volume[1:])
                if volume < 0:
                    volume = 0
            else:
                volume = int(args.volume)
                fade = False
        except ValueError:
            self.exit(1, 'Invalid volume value {}'.format(args.volume))

        try:
            if fade:
                if self.client.volume < volume:
                    while self.client.volume < volume:
                        self.client.volume = self.client.volume + 1
                        time.sleep(0.01)
                if self.client.volume > volume:
                    while self.client.volume > volume:
                        self.client.volume = self.client.volume - 1
                        time.sleep(0.01)
            else:
                self.client.volume = volume
        except MusicPlayerError as e:
            self.exit(1, e)


class UpdateIndexCommand(CLICommand):
    """Update index database

    Update music player track index database
    """
    def run(self, args):
        try:
            self.message('Update: {}'.format(self.client.indexdb))
            self.client.indexdb.update()
        except MusicPlayerError as e:
            self.error('Error updating {}: {}'.format(self.client.indexdb, e))


class LookupDBCommand(CLICommand):
    """Lookup track index

    Lookup track index by path from database
    """
    def run(self, args):
        for path in args.paths:
            try:
                index = self.client.indexdb.lookup_index(path)
                if index:
                    self.message('{:6} {}'.format(index, path))
            except MusicPlayerError as e:
                self.error('{}'.format(e))


def main():

    script = Script()

    c = script.add_subcommand(InfoCommand('info', 'Show playing track information'))
    c.add_argument('-v', '--verbose', action='store_true', help='Verbose messages')

    c = script.add_subcommand(PlayCommand('play', 'Play/pause/jump to file'))
    c.add_argument('track', nargs='?', help='Track to play')

    c = script.add_subcommand(StopCommand('stop', 'Stop playback'))

    c = script.add_subcommand(PreviousTrackCommand('previous', 'Play previous tracks'))
    c = script.add_subcommand(NextTrackCommand('next', 'Play next tracks'))

    c = script.add_subcommand(ShuffleModeCommand('shuffle', 'Toggle or show suffle mode'))
    c.add_argument('mode',  nargs='?', choices=('enable', 'disable', ), help='Enable or disable shuffle mode')

    c = script.add_subcommand(VolumeCommand('volume', 'Adjust or show playback volume'))
    c.add_argument('volume',  nargs='?', help='Value to set')

    c = script.add_subcommand(UpdateIndexCommand('update-index', 'Update track index database'))

    c = script.add_subcommand(LookupDBCommand('lookup-index', 'Lookup track index from database'))
    c.add_argument('paths', nargs='*', help='Track paths to lookup')

    script.run()
