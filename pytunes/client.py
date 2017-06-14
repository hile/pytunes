"""
Simple abstraction to itunes library from python with appscript
"""

import appscript
import logging
import mactypes
import os
import pwd
import re
import sys
import sys

from datetime import datetime
from systematic.process import Processes

from soundforest.tags import TagError
from soundforest.tree import Tree, Album, Track

from pytunes import iTunesError
from pytunes import terminology as itunes_terminology
from pytunes.constants import TRACK_FIELDS, TRACK_SYS_FIELDS, \
                              TRACK_INT_FIELDS, TRACK_FLOAT_FIELDS, \
                              TRACK_DATE_FORMAT, TRACK_DATE_FIELDS, \
                              REPEAT_VALUES, ITUNES_PLAYER_STATE_NAMES, \
                              SKIPPED_PLAYLISTS
from pytunes.indexdb import iTunesIndexDB
from pytunes.playlist import iTunesPlaylist

ITUNES_DIR = os.path.join(os.getenv('HOME'), 'Music', 'iTunes')
ITUNES_MUSIC = os.path.join(ITUNES_DIR, 'iTunes Media', 'Music')
ITUNES_PATH_FILE = os.path.join(ITUNES_DIR, 'library_path.txt')
ITUNES_INDEX_DB = os.path.join(ITUNES_DIR, 'iTunes Track Index.sqlite')

ITUNES_BINARY_PATH = '/Applications/iTunes.app/Contents/MacOS/iTunes'


class iTunesMusicTree(Tree):
    """iTunes music tree

    iTunes music tree, representing one folder on disk configured as
    iTunes library path.
    """
    def __init__(self, itunes_path=None, codec='m4a', tree_path=ITUNES_PATH_FILE):
        self.itunes_path = itunes_path is not None and itunes_path or ITUNES_DIR
        if not os.path.isdir(self.itunes_path):
            raise iTunesError('No such directory: {0}'.format(self.itunes_path))

        if tree_path is None:
            if os.path.isfile(ITUNES_PATH_FILE):

              try:
                  tree_path = open(ITUNES_PATH_FILE, 'r').read().strip()
              except IOError as e:
                  raise iTunesError('Error opening {0}: {1}'.format(tree_path, e))

              except OSError as e:
                  raise iTunesError('Error opening {0}: {1}'.format(tree_path, e))

            else:
                tree_path = ITUNES_MUSIC

        if not os.path.isdir(tree_path):
                raise iTunesError('No such directory: {0}'.format(tree_path))

        Tree.__init__(self, path=tree_path)


class iTunes(object):
    """iTunes application

    Singleton access to iTunes appscript API.

    Raises iTunesError if iTunes was not running when initialized.
    """
    __instance__ = None

    def __init__(self):
        if iTunes.__instance__ is None:
            iTunes.__instance__ = iTunes.Instance()

        reload(sys)
        sys.setdefaultencoding('utf-8')

        self.__dict__['_iTunes__instance__'] = iTunes.__instance__
        self.indexdb = iTunesIndexDB(self, ITUNES_INDEX_DB)

    @property
    def itunes(self):
        """iTunes appscript Instance

        Returns instance of itunes appscript client
        """
        return self.__instance__.itunes

    def __getattr__(self, attr):
        try:
            return getattr(self.__instance__, attr)
        except AttributeError as e:
            raise AttributeError(e)

    class Instance(object):
        """iTunes appscript app

        Singleton instance of iTunes appscript app

        """
        def __init__(self):
            self.itunes = None

        def __connect__(self):
            if self.is_running:
                self.itunes = appscript.app('iTunes', terms=itunes_terminology)
            else:
                self.itunes = None
                raise iTunesError('iTunes is not running')

        def __getattr__(self, attr):
            if self.itunes is None:
                self.__connect__()
            try:
                return getattr(self.itunes, attr)
            except AttributeError as e:
                raise AttributeError('No such iTunes attribute: {0}: {1}'.format(attr, e))

        @property
        def path(self):
            if self.itunes is not None:
                return '{0}'.format(self.itunes).replace("app(u'", "").replace("')", "")
            else:
                return ''

        @property
        def is_running(self):
            """Check if user has itunes open

            Check if iTunes process exists for this user
            """
            for process in  Processes().filter(command=ITUNES_BINARY_PATH):
                if process.userid == os.geteuid():
                    return True
            return False

    @property
    def status(self):
        """iTunes play status

        Returns current iTunes play status string from
        ITUNES_PLAYER_STATE_NAMES
        """
        if self.itunes is None:
            self.__connect__()
        s = self.itunes.player_state.get()
        try:
            return ITUNES_PLAYER_STATE_NAMES[s]
        except KeyError:
            return 'Unknown ({0}'.format(s)

    @property
    def current_track(self):
        """Current track

        Returns currently selected iTunes track or None
        """
        if self.itunes is None:
            self.__connect__()
        try:
            return Track(self, self.itunes.current_track())

        except appscript.reference.CommandError:
            return None

    @property
    def repeat(self):
        """Get repeat

        """
        if self.itunes is None:
            self.__connect__()
        try:
            value = self.itunes.current_playlist.song_repeat.get()
            for key in REPEAT_VALUES:
                if value == REPEAT_VALUES[key]:
                    return REPEAT_VALUES[key]
        except appscript.reference.CommandError:
            return None

    @repeat.setter
    def repeat(self, value):
        """Set repeat

        Set repeat mode. Valid values are in pytunes.constants.REPEAT_VALUES
        """
        if self.itunes is None:
            self.__connect__()
        try:
            self.itunes.current_playlist.song_repeat.set(to=REPEAT_VALUES[value])
        except KeyError:
            raise iTunesError('Invalid repeat value {0}'.format(value))

    @property
    def shuffle(self):
        """Get shuffle mode

        """
        if self.itunes is None:
            self.__connect__()
        try:
            return self.itunes.shuffle_enabled.get()
        except appscript.reference.CommandError:
            return None

    @shuffle.setter
    def shuffle(self, value):
        """Set shuffle

        Set shuffle mode
        """
        if self.itunes is None:
            self.__connect__()
        value = value and True or False
        self.itunes.shuffle_enabled.set(to=value)

    @property
    def volume(self):
        """Get volume

        """
        if self.itunes is None:
            self.__connect__()
        return self.itunes.sound_volume.get()

    @volume.setter
    def volume(self, value):
        """Set volume level

        Must be a integer in range 0-100
        """
        if self.itunes is None:
            self.__connect__()
        if not isinstance(value, int):
            raise iTunesError('Volume adjustment must be integer value')
        if value < 0 or value > 100:
            raise iTunesError('Volume adjustment must be in range 0-100')
        self.itunes.sound_volume.set(to=value)

    @property
    def library(self):
        """iTunes library

        Return configured iTunes library
        """
        return iTunesPlaylist(self)

    @property
    def smart_playlists(self):
        """Return user smart playlists

        """
        playlists = []
        if self.itunes is None:
            self.__connect__()
        for pl in self.itunes.user_playlists.get():
            name = pl.name.get()
            if name not in SKIPPED_PLAYLISTS and pl.smart.get():
                playlists.append(iTunesPlaylist(self, name))
        return playlists

    @property
    def playlists(self):
        """Return user playlists

        Skips smart playlists and playlists in pytunes.constants.SKIPPED_PLAYLISTS
        """
        playlists = []
        if self.itunes is None:
            self.__connect__()
        for pl in self.itunes.user_playlists.get():
            name = pl.name.get()
            if name in SKIPPED_PLAYLISTS or pl.smart.get():
                continue
            playlists.append(iTunesPlaylist(self, name))
        return playlists

    @property
    def library(self):
        """Return iTunes library

        Returns main library as iTunesPlaylist
        """
        return iTunesPlaylist(self)

    def create_playlist(self, name):
        """Create playlist

        Returns created playlist as iTunesPlaylist object
        """
        if self.itunes is None:
            self.__connect__()
        self.itunes.make(
            new=appscript.k.user_playlist,
            at='Playlists',
            with_properties={appscript.k.name: name},
        )
        return iTunesPlaylist(self, name)

    def delete_playlist(self, name):
        """Delete playlist

        Note: if there are multiple lists with same name, ALL are removed.
        """
        if self.itunes is None:
            self.__connect__()
        for pl in self.itunes.user_playlists.get():
            if pl.name.get() == name:
                pl.delete()

    def get_playlist(self, name):
        """Get playlist by name

        """
        if self.itunes is None:
            self.__connect__()
        for pl in self.itunes.user_playlists.get():
            if pl.name.get() == name:
                return iTunesPlaylist(self, name)
        raise iTunesError('No such playlist: {0}'.format(name))

    def get_playlist_track(self, playlist, index):
        """Get playlist track by index

        Playlist must be a reference to internal playlist object: this is used
        from iTunesPlaylist class.
        """
        return Track(self, playlist.file_tracks[index])

    def previous(self):
        """Previous track

        Jump to previous track
        """
        return self.previous_track()

    def next(self):
        """Next track

        Jump to next track

        """
        return self.next_track()

    def jump(self, index):
        """Play track by index

        """
        if self.itunes is None:
            self.__connect__()
        try:
            self.itunes.play(self.library.playlist.file_tracks[index])
        except appscript.reference.CommandError:
            raise iTunesError('Invalid library index: {0}'.format(index))
        return self.current_track

    def play(self, path=None):
        """Play track by path

        """
        if self.itunes is None:
            self.__connect__()
        if path is not None:
            path = path.decode('utf-8')
            if os.path.isdir(path):
                path = os.path.join(path, os.listdir(path)[0])
            try:
                self.jump(self.indexdb.lookup_index(path))
            except iTunesError:
                pass
            self.itunes.play(mactypes.Alias(path))
        else:
            self.itunes.play()
        return self.current_track


class Track(object):
    """Track accessor

    Track in itunes library
    """

    def __init__(self, client, track):
        self.client = client
        self.track = track

        try:
            self.path = self.client.get(self.track.location).path.decode('utf-8')
        except AttributeError:
            self.path = None
        except appscript.reference.CommandError:
            self.path = None

    def __repr__(self):
        return '{0} - {1} - {2}'.format(
            str(self.artist).encode('utf-8'),
            str(self.album).encode('utf-8'),
            str(self.title).encode('utf-8'),
        )

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            pass
        raise AttributeError('Invalid Track attribute: {0}'.format(attr))

    def __getitem__(self, item):
        if item == 'path':
            return self.path

        if item == 'extension':
            return os.path.splitext(self.path)[1][1:]

        if item in ( 'id', 'ID', ):
            item = 'id'

        if item in ( 'date', 'year', ):
            item = 'year'

        if item in ( 'title', 'name', ):
            item = 'name'

        try:
            value = self.client.get(self.track.__getattr__(item))
            if value == appscript.k.missing_value:
                value = None

            try:
                if item in TRACK_INT_FIELDS:
                    return int(value)
                elif item in TRACK_FLOAT_FIELDS:
                    return float(value)
                elif item in TRACK_DATE_FIELDS:
                    return value
                elif item == 'location':
                    return value.path
                return unicode(value)

            except AttributeError as e:
                return value

        except AttributeError:
            pass

        except appscript.reference.CommandError as e:
            raise iTunesError('Error reading track attribute: {0}'.format(e))

        raise KeyError('Invalid Track item: {0}'.format(item))

    def __setattr__(self, item, value):
        if item in ('date', 'year'):
            item = 'year'
            if type(value) != int:
                try:
                    value = int(value.split('-')[0])
                except ValueError:
                    raise AttributeError('tag {0} invalid value: {1}'.format(item, value))
                except IndexError:
                    value = int(value)

        if item in TRACK_FIELDS:
            try:
                entry = self.track.__getattr__(item)
                self.client.set(entry, to=value)
            except appscript.reference.CommandError as e:
                raise ValueError('ERROR setting {0} to {1}: {2}'.format(item, value, e))

        elif item in TRACK_SYS_FIELDS:
            raise ValueError('Track attribute {0} is read-only'.format(item))

        elif item in ( 'client', 'track', 'path', 'log' ):
            self.__dict__[item] = value

        else:
            raise AttributeError('Invalid Track attribute: {0}'.format(item))

    def updateTracknumber(self):
        """Update tracknumber

        Update itunes tracknumber. Sets album total tracks to number of files
        with same extension in same directory.
        """
        m = re.match('^([0-9]+) .*', os.path.basename(self.path))
        if not m:
            return False

        track = int(m.group(1))
        name, ext = os.path.splitext(os.path.basename(self.path))
        total = len([f for f in os.listdir(os.path.dirname(self.path)) if os.path.splitext(f)[1] == ext])

        try:
            if self.track_count != total:
                self.track_count = total
        except AttributeError:
            self.track_count = total

        try:
            if self.track_number != track:
                self.track_number = track
        except AttributeError:
            self.track_number = track

        return True

    def updateTag(self, tag, value):
        """Set tag in itunes

        Set tag to value in itunes
        """
        try:
            current_value = self.__getattr__(tag)
            if tag in ( 'year', 'date', ):
                if type(value) != int:
                    try:
                        value = value.split('-')[0]
                    except IndexError:
                        value = str(value)

            if current_value == value:
                return

        except AttributeError:
            pass

        if value in ('', None,):
            return

        self.__setattr__(tag, value)

    def syncTags(self, song):
        """Sync file tags

        Sync tags from file metadata to itunes
        """
        modified = False
        try:
            for tag in ('artist', 'album', 'title', 'genre', 'date', 'bpm'):
                if not song.tags.has_key(tag):
                    continue

                if tag in ( 'bpm', 'date', ):
                    value = int(song.tags[tag])
                else:
                    value = song.tags[tag]

                if tag == 'bpm' and value == 0:
                    continue

                if tag == 'title':
                    tag = 'name'

                self.updateTag(tag, value)
                modified = True

        except TagError as e:
            raise iTunesError('Error updating tags: {0} {1}'.format(self.path, e))

        if self.updateTracknumber():
            modified = True

        return modified

    def refresh(self):
        """Refresh trck

        """
        self.client.refresh(self.track)

    def keys(self):
        keys = ['path']
        keys.extend(TRACK_SYS_FIELDS)
        keys.extend(TRACK_FIELDS)
        return keys

    def items(self):
        items = []
        for k in self.keys():
            try:
                items.append([k, self.__getattr__(k)])
            except appscript.reference.CommandError:
                pass
        return items

