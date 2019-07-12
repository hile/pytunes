#!/usr/bin/env python


import os
import fnmatch
import shutil

from operator import attrgetter

from soundforest.cli import Script, ScriptCommand
from soundforest.playlist import m3uPlaylist, m3uPlaylistDirectory, PlaylistError

from pytunes import MusicPlayerError
from pytunes.client import Client

DEFAULT_DIRECTORY = os.path.expanduser('~/Music/Playlists')


class PlaylistProcessorCommand(ScriptCommand):
    def setup(self, args):
        self.client = Client()
        self.playlists = []

        if 'playlists' in args and args.playlists:
            for playlist in self.client.playlists:
                path = playlist.path
                for match in args.playlists:
                    if fnmatch.fnmatch(match, path):
                        self.playlists.append(playlist)

            if 'smart_playlists' in args and args.smart_playlists:
                for playlist in self.client.smart_playlists:
                    path = playlist.path
                    for match in args.playlists:
                        if fnmatch.fnmatch(match, path):
                            self.playlists.append(playlist)
        else:
            self.playlists.extend(self.client.playlists)
            if 'smart_playlists' in args and args.smart_playlists:
                self.playlists.extend(self.client.smart_playlists)


class ListCommand(PlaylistProcessorCommand):
    def run(self, args):
        super(ListCommand, self).setup(args)

        if not args.playlists:
            for playlist in self.playlists:
                self.message(playlist.path)

        else:
            for playlist in self.playlists:

                years = {}
                for track in playlist:
                    if args.yearly:
                        if track.year not in years:
                            years[track.year] = []

                        years[track.year].append(track)

                    elif args.format:
                        try:
                            self.message(args.format % track)
                        except KeyError as e:
                            self.exit(1, 'Error formatting track {}: {}'.format(track.path, e))

                    else:
                        self.message(track)

                if args.yearly:
                    for year in sorted(years.keys()):
                        years[year].sort(key=attrgetter('artist'))

                        first = True
                        for track in years[year]:
                            if args.format:
                                try:
                                    self.message(args.format % track)
                                except KeyError as e:
                                    self.exit(1, 'Error formatting track {}: {}'.format(track.path, e))
                            elif first:
                                self.message('%(year)4s\t%(artist)s\t%(name)s' % track)
                                first = False
                            else:
                                self.message('\t%(artist)s\t%(name)s' % track)


class ExportFilesCommand(PlaylistProcessorCommand):
    def run(self, args):
        super(ExportFilesCommand, self).setup(args)

        for playlist in self.playlists:
            self.script.log.debug('Processing: {}'.format(playlist))

            path = os.path.join(args.directory, playlist.path)

            if not os.path.isdir(path):
                try:
                    os.makedirs(path)
                except OSError as e:
                    self.exit(1, 'Error creating playlist folder {}: {}'.format(path, e))

            tracks = []
            if args.yearly:
                years = {}
                for track in playlist:
                    if track.year not in years:
                        years[track.year] = []
                    years[track.year].append(track)

                for year in sorted(years.keys()):
                    years[year].sort(key=attrgetter('artist'))
                    for track in years[year]:
                        name = '{} - {}.{}'.format(track.artist, track.name, track.extension)
                        filename = os.path.join('{}'.format(year, name.replace(os.sep, '')))
                        tracks.append((filename, track))

            elif args.format:
                index = 1
                for track in playlist:
                    try:
                        name = '{}'.format(args.format % track)
                        filename = '{:03d} {}.{}'.format(
                            index,
                            os.path.join(path, name.replace(os.sep, '')),
                            track.extension
                        )
                        tracks.append((filename, track))
                    except KeyError as e:
                        self.exit(1, 'Error formatting track {}: {}'.format(track.path, e))
                    index += 1

            else:
                index = 1
                for track in playlist:
                    filename = '{:03d} {}'.format(index, track.path)
                    tracks.append((filename, track))

            for filename, original in tracks:
                filename = os.path.join(path, filename)
                self.script.log.debug('Processing {}'.format(filename))
                if os.path.isfile(filename):
                    continue

                file_dir = os.path.dirname(filename)
                if not os.path.isdir(file_dir):
                    try:
                        os.makedirs(file_dir)
                    except OSError as e:
                        self.exit(1, 'Error creating directory {}: {}'.format(filename, e))

                try:
                    self.message('Writing {}'.format(filename))
                    shutil.copyfile(original.path, filename)
                except OSError as e:
                    self.exit(1, 'Error writing file {}: {}'.format(filename, e))


class ExportCommand(PlaylistProcessorCommand):
    def run(self, args):
        super(ExportCommand, self).setup(args)

        if not os.path.isdir(args.directory):
            try:
                os.makedirs(args.directory)
            except OSError as e:
                self.exit(1, 'Error creating directory {}: {}'.format(args.directory, e))
            except IOError as e:
                self.exit(1, 'Error creating directory {}: {}'.format(args.directory, e))

        for playlist in self.playlists:

            try:
                folder = os.path.dirname(os.path.join(args.directory, playlist.path))
            except AttributeError:
                folder = None

            m3u = m3uPlaylist(playlist.name, folder=folder)
            for track in playlist:
                m3u.append(track.path)

            if args.ignore_empty and len(m3u) == 0:
                self.script.log.debug('Ignore empty playlist: {}'.format(m3u))
                continue

            try:
                m3u.write()
            except PlaylistError as e:
                self.script.log.info('Error writing playlist {}: {}'.format(m3u.path, e))
                continue

            self.script.log.info('Exported: {} {:d} songs'.format(m3u.path, len(m3u)))


class ImportCommand(PlaylistProcessorCommand):
    def run(self, args):
        from pytunes.playlist import Playlist
        super(ImportCommand, self).setup(args)

        if not os.path.isdir(args.directory):
            self.exit(1, 'No such directory: {}'.format(args.directory))

        for playlist in m3uPlaylistDirectory(path=args.directory):
            playlist.read()
            ipl = Playlist(playlist.name)

            for track in playlist:
                ipl.add(track)

            self.script.log.info('Imported: {} {} songs'.format(playlist.path, len(playlist)))


class CreateCommand(PlaylistProcessorCommand):
    def run(self, args):
        super(CreateCommand, self).setup(args)

        for name in args.names:
            self.client.create_playlist(name)


class RemoveCommand(PlaylistProcessorCommand):
    def run(self, args):
        super(RemoveCommand, self).setup(args)

        for name in args.names:
            try:
                self.client.delete_playlist(name)
            except MusicPlayerError as e:
                self.error('Error removing playlist {}: {}'.format(name, e))


def main():
    script = Script('pytunes-playlists', 'Import and export music player playlists')

    c = script.add_subcommand(ListCommand('list', 'List playlists'))
    c.add_argument('-s', '--smart-playlists', action='store_true', help='Include smart playlists')
    c.add_argument('-y', '--yearly', action='store_true', help='Order listed tracks by year')
    c.add_argument('-f', '--format', help='List formatting string')
    c.add_argument('playlists', nargs='*', help='Playlists to process')

    c = script.add_subcommand(ExportFilesCommand('export-files', 'Export playlists as files'))
    c.add_argument('-s', '--smart-playlists', action='store_true', help='Include smart playlists')
    c.add_argument('-y', '--yearly', action='store_true', help='Order exported tracks by year')
    c.add_argument('-f', '--format', help='Filename formatting string')
    c.add_argument('playlists', nargs='*', help='Playlists to process')

    c = script.add_subcommand(ExportCommand('export', 'Export m3u playlists'))
    script.add_argument('-D', '--directory', default=DEFAULT_DIRECTORY, help='Playlist directory for m3u files')
    c.add_argument('-s', '--smart-playlists', action='store_true', help='Include smart playlists')
    c.add_argument('-E', '--ignore-empty', action='store_true', help='Ignore empty playlists')
    c.add_argument('playlists', nargs='*', help='Playlists to process')

    c = script.add_subcommand(ImportCommand('import', 'Import playlists'))
    c.add_argument('-s', '--smart-playlists', action='store_true', help='Include smart playlists')
    c.add_argument('playlists', nargs='*', help='Playlists to process')

    c = script.add_subcommand(CreateCommand('create', 'Create playlists'))
    c.add_argument('names', nargs='*', help='Names of playlists to create')

    c = script.add_subcommand(RemoveCommand('remove', 'Remove playlists'))
    c.add_argument('names', nargs='*', help='Names of playlists to create')

    script.run()
