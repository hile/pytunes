"""
Simple abstraction to MacOS music library from python with appscript
"""

import appscript
import mactypes
import os

from systematic.process import Processes

from oodi.library.tree import Tree

from . import MusicPlayerError
from . import terminology
from .constants import (
    REPEAT_VALUES,
    PLAYER_STATE_NAMES,
    SKIPPED_PLAYLISTS
)
from .database import TrackIndexDB
from .playlist import Playlist
from .track import Track


APPS = {
    'iTunes': {
        'binary': '/Applications/iTunes.app/Contents/MacOS/iTunes',
        'data_directory': os.path.join(os.getenv('HOME'), 'Music/Tunes'),
        'music_directory': os.path.join(os.getenv('HOME'), 'Music/Tunes/iTunes Media/Music'),
        'library_path_filename': 'library_path.txt',
        'index_database': 'iTunes Track Index.sqlite'
    },
    'Music': {
        'binary': '/System/Applications/Music.app/Contents/MacOS/Music',
        'data_directory': os.path.join(os.getenv('HOME'), 'Music/Music/Music Library.musiclibrary'),
        'music_directory': os.path.join(os.getenv('HOME'), 'Music/Music/Media/Music'),
        'library_path_filename': 'library_path.txt',
        'index_database': 'Tracks.sqlite'
    }
}


def detect_app():
    """
    Detect application (iTunes or Music)
    """
    for app, config in APPS.items():
        if os.path.isfile(config['binary']):
            return app, config
    raise MusicPlayerError('Error detecting music player application')


class MusicTree(Tree):
    """
    MacOS music tree, representing one folder on disk configured as music player library path
    """
    def __init__(self, tree_path=None):
        app, config = detect_app()

        if tree_path is None:
            tree_path_file = os.path.join(config['data_directory'], config['library_path_filename'])
            if os.path.isfile(tree_path_file):
                try:
                    tree_path = open(tree_path_file, 'r').read().strip()
                except IOError as e:
                    raise MusicPlayerError('Error opening {}: {}'.format(tree_path, e))
                except OSError as e:
                    raise MusicPlayerError('Error opening {}: {}'.format(tree_path, e))

            else:
                tree_path = config['music_directory']

        Tree.__init__(self, path=tree_path)


class Client(object):
    """Music client application

    Singleton access to music player appscript API.

    Raises MusicPlayerError if music player was not running when initialized.
    """
    __instance__ = None

    def __init__(self):
        self.__app_name__ = None
        self.__binary__ = None
        self.__index_database__ = None
        self.__detect_application__()

        if Client.__instance__ is None:
            Client.__instance__ = Client.Instance(self.__app_name__, self.__binary__)

        self.__dict__['_Client__instance__'] = Client.__instance__
        self.indexdb = TrackIndexDB(self, self.__index_database__)

    def __detect_application__(self):
        """
        Detect which application we have
        """
        app, config = detect_app()
        self.__app_name__ = app
        self.__binary__ = config['binary']
        self.__index_database__ = os.path.join(config['data_directory'], config['index_database'])

    @property
    def application(self):
        """MacOS music player appscript Instance

        Returns instance of appscript client
        """
        return self.__instance__.application

    def __getattr__(self, attr):
        try:
            return getattr(self.__instance__, attr)
        except AttributeError as e:
            raise AttributeError(e)

    class Instance(object):
        """MacOS music player appscript app instance

        Singleton instance of MacOS music player appscript app

        """
        def __init__(self, app_name, binary):
            self.__app_name__ = app_name
            self.__binary__ = binary
            self.application = None

        def __connect__(self):
            if self.is_running:
                self.application = appscript.app(self.__app_name__, terms=terminology)
            else:
                self.application = None
                raise MusicPlayerError('{} is not running'.format(self.__app_name__))

        def __getattr__(self, attr):
            if self.application is None:
                self.__connect__()
            try:
                return getattr(self.application, attr)
            except AttributeError as e:
                raise AttributeError('No such client attribute: {}: {}'.format(attr, e))

        @property
        def path(self):
            if self.application is not None:
                return '{}'.format(self.application).replace("""app(u'""", '').replace("""')""", '')
            else:
                return ''

        @property
        def is_running(self):
            """Check if user has music player open

            Check if music player process exists for this user
            """
            for process in Processes().filter(command=self.__binary__):
                if process.userid == os.geteuid():
                    return True
            return False

    @property
    def status(self):
        """Music player play status

        Returns current music player play status string from PLAYER_STATE_NAMES
        """
        if self.application is None:
            self.__connect__()
        s = self.application.player_state.get()
        try:
            return PLAYER_STATE_NAMES[s]
        except KeyError:
            return 'Unknown ({}'.format(s)

    @property
    def current_track(self):
        """Current track

        Returns currently selected music player track or None
        """
        if self.application is None:
            self.__connect__()
        try:
            return Track(self, self.application.current_track())

        except appscript.reference.CommandError:
            return None

    @property
    def repeat(self):
        """Get repeat

        """
        if self.application is None:
            self.__connect__()
        try:
            value = self.application.current_playlist.song_repeat.get()
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
        if self.application is None:
            self.__connect__()
        try:
            self.application.current_playlist.song_repeat.set(to=REPEAT_VALUES[value])
        except KeyError:
            raise MusicPlayerError('Invalid repeat value {}'.format(value))

    @property
    def shuffle(self):
        """Get shuffle mode

        """
        if self.application is None:
            self.__connect__()
        try:
            return self.application.shuffle_enabled.get()
        except appscript.reference.CommandError:
            return None

    @shuffle.setter
    def shuffle(self, value):
        """Set shuffle

        Set shuffle mode
        """
        if self.application is None:
            self.__connect__()
        value = value and True or False
        self.application.shuffle_enabled.set(to=value)

    @property
    def volume(self):
        """Get volume

        """
        if self.application is None:
            self.__connect__()
        return self.application.sound_volume.get()

    @volume.setter
    def volume(self, value):
        """Set volume level

        Must be a integer in range 0-100
        """
        if self.application is None:
            self.__connect__()
        if not isinstance(value, int):
            raise MusicPlayerError('Volume adjustment must be integer value')
        if value < 0 or value > 100:
            raise MusicPlayerError('Volume adjustment must be in range 0-100')
        self.application.sound_volume.set(to=value)

    @property
    def library(self):
        """Music player library

        Return configured music player library
        """
        return Playlist(self)

    @property
    def smart_playlists(self):
        """Return user smart playlists

        """
        playlists = []
        if self.application is None:
            self.__connect__()
        for pl in self.application.user_playlists.get():
            name = pl.name.get()
            if name not in SKIPPED_PLAYLISTS and pl.smart.get():
                playlists.append(Playlist(self, name))
        return playlists

    @property
    def playlists(self):
        """Return user playlists

        Skips smart playlists and playlists in pytunes.constants.SKIPPED_PLAYLISTS
        """
        playlists = []
        if self.application is None:
            self.__connect__()
        for pl in self.application.user_playlists.get():
            name = pl.name.get()
            if name in SKIPPED_PLAYLISTS or pl.smart.get():
                continue
            playlists.append(Playlist(self, name))
        return playlists

    def create_playlist(self, name):
        """Create playlist

        Returns created playlist as Playlist object
        """
        if self.application is None:
            self.__connect__()
        self.application.make(
            new=appscript.k.user_playlist,
            at='Playlists',
            with_properties={appscript.k.name: name},
        )
        return Playlist(self, name)

    def delete_playlist(self, name):
        """Delete playlist

        Note: if there are multiple lists with same name, ALL are removed.
        """
        if self.application is None:
            self.__connect__()
        for pl in self.application.user_playlists.get():
            if pl.name.get() == name:
                pl.delete()

    def get_playlist(self, name):
        """Get playlist by name

        """
        if self.application is None:
            self.__connect__()
        for pl in self.application.user_playlists.get():
            if pl.name.get() == name:
                return Playlist(self, name)
        raise MusicPlayerError('No such playlist: {}'.format(name))

    def get_playlist_track(self, playlist, index):
        """Get playlist track by index

        Playlist must be a reference to internal playlist object: this is used
        from Playlist class.
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
        if self.application is None:
            self.__connect__()
        try:
            self.application.play(self.library.playlist.file_tracks[index])
        except appscript.reference.CommandError:
            raise MusicPlayerError('Invalid library index: {}'.format(index))
        return self.current_track

    def play(self, path=None):
        """Play track by path

        """
        if self.application is None:
            self.__connect__()
        if path is not None:
            if os.path.isdir(path):
                path = os.path.join(path, os.listdir(path)[0])
            try:
                self.jump(self.indexdb.lookup_index(path))
            except MusicPlayerError:
                pass
            self.application.play(mactypes.Alias(path))
        else:
            self.application.play()
        return self.current_track
