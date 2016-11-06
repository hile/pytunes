"""
Simple abstraction to itunes library from python with appscript
"""

import sys
import os
import re
import logging
import appscript
import mactypes

from soundforest.tags import TagError
from soundforest.tree import Tree, Album, Track

from pytunes import iTunesError
from pytunes import terminology as itunes_terminology
from pytunes.constants import TRACK_FIELDS, TRACK_SYS_FIELDS, \
                              TRACK_INT_FIELDS, TRACK_FLOAT_FIELDS, \
                              REPEAT_VALUES, ITUNES_PLAYER_STATE_NAMES

ITUNES_DIR = os.path.join(os.getenv('HOME'), 'Music', 'iTunes')
ITUNES_MUSIC = os.path.join(ITUNES_DIR, 'iTunes Media', 'Music')
ITUNES_PATH_FILE = os.path.join(ITUNES_DIR, 'library_path.txt')


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

    Singleton access to iTunes appscript API

    """
    __instance__ = None

    def __init__(self):
        if iTunes.__instance__ is None:
            iTunes.__instance__ = iTunes.Instance()
        self.__dict__['_iTunes__instance__'] = iTunes.__instance__

    @property
    def itunes(self):
        """iTunes appscript Instance

        Returns instance of itunes appscript client

        """
        return self.__instance__.itunes

    def __getattr__(self, attr):
        try:
            return getattr(self.__instance__, attr)
        except AttributeError:
            raise AttributeError('No such iTunes attribute: {0}'.format(attr))

    class Instance(object):
        """iTunes appscript app

        Singleton instance of iTunes appscript app

        """
        def __init__(self):
            self.itunes = appscript.app('iTunes', terms=itunes_terminology)

        def __getattr__(self, attr):
            try:
                return getattr(self.itunes, attr)

            except AttributeError:
                raise AttributeError('No such iTunes attribute: {0}'.format(attr))

    @property
    def library(self):
        """iTunes library

        Return configured iTunes library

        """
        for src in self.itunes.sources.get():
            if src.kind.get() == appscript.k.library:
                return src

        return None

    @property
    def status(self):
        """iTunes play status

        Returns current iTunes play status string from
        ITUNES_PLAYER_STATE_NAMES

        """
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
        try:
            return Track(self.itunes.current_track())

        except appscript.reference.CommandError:
            return None

    @property
    def repeat(self):
        try:
            return filter(lambda k:
                REPEAT_VALUES[k]==self.itunes.current_playlist.song_repeat.get(),
                REPEAT_VALUES.keys()
            )[0]

        except appscript.reference.CommandError:
            return None

    @repeat.setter
    def repeat(self, value):
        try:
            self.itunes.current_playlist.song_repeat.set(to=REPEAT_VALUES[value])

        except KeyError:
            raise iTunesError('Invalid repeat value {0}'.format(value))

    @property
    def shuffle(self):
        try:
            return self.itunes.current_playlist.shuffle.get()

        except appscript.reference.CommandError:
            return None

    @shuffle.setter
    def shuffle(self, value):
        value = value and True or False
        self.itunes.current_playlist.shuffle.set(to=value)

    @property
    def volume(self):
        return self.itunes.sound_volume.get()

    @volume.setter
    def volume(self, value):
        if not isinstance(value, int):
            raise iTunesError('Volume adjustment must be integer value')

        if value < 0 or value > 100:
            raise iTunesError('Volume adjustment must be in range 0-100')

        self.itunes.sound_volume.set(to=value)

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


class Track(object):
    """Track accessor

    Track in itunes library

    """

    def __init__(self, track):
        self.itunes = iTunes()
        self.track = track

        try:
            self.path = self.itunes.get(self.track.location).path
        except AttributeError:
            self.path = None

    def __repr__(self):
        return '{0} - {1} - {2}'.format(self.artist, self.album, self.title)

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

        if item in ['id', 'ID']:
            item = 'id'

        if item in ['date', 'year']:
            item = 'year'

        if item in ['title', 'name']:
            item = 'name'

        try:
            value = self.itunes.get(self.track.__getattr__(item))
            if value == appscript.k.missing_value:
                value = None

            try:
                if item in TRACK_INT_FIELDS:
                    return int(value)
                elif item in TRACK_FLOAT_FIELDS:
                    return float(value)
                return unicode(value)

            except AttributeError:
                return value

        except AttributeError:
            pass

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
                self.itunes.set(entry, to=value)
            except appscript.reference.CommandError as e:
                raise ValueError('ERROR setting {0} to {1}: {2}'.format(item, value, e))

        elif item in TRACK_SYS_FIELDS:
            raise ValueError('Track attribute {0} is read-only'.format(item))

        elif item in ['itunes', 'track', 'path', 'log']:
            self.__dict__[item] = value

        else:
            raise AttributeError('Invalid Track attribute: {0}'.format(item))

    def updateTracknumber(self):
        m = re.match('^([0-9]+) .*', os.path.basename(self.path))
        if not m:
            return False

        track = int(m.group(1))
        name, ext = os.path.splitext(os.path.basename(self.path))
        total = len(filter(lambda x:
            os.path.splitext(x)[1]==ext,
            os.listdir(os.path.dirname(self.path))
        ))

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
        try:
            current_value = self.__getattr__(tag)
            if tag in ['year', 'date']:
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
        modified = False
        try:
            for tag in ('artist', 'album', 'title', 'genre', 'date', 'bpm'):
                if not song.tags.has_key(tag):
                    continue

                if tag in ('bpm', 'date'):
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
        self.itunes.refresh(self.track)

    def keys(self):
        keys = ['path']
        keys.extend(TRACK_SYS_FIELDS)
        keys.extend(TRACK_FIELDS)

        return keys

    def items(self):
        items = []
        for k in self.keys():
            items.append([k, self.__getattr__(k)])

        return items

