
import os
import appscript
import mactypes

from . import MusicPlayerError


class Playlist(object):
    """
    Music player playlist

    Abstraction of a single MacOS music player playlist
    """

    def __init__(self, client, name=None):
        self.client = client
        self.__index__ = 0

        try:
            if name is None:
                self.playlist = self.client.get(self.client.library_playlists['library'])
                name = 'library'
            else:
                self.playlist = self.client.get(self.client.user_playlists[name])
        except appscript.reference.CommandError:
            raise MusicPlayerError('No such playlist: {}'.format(name))

        self.name = name
        self.__update_len__()

    def __update_len__(self):
        try:
            self.__len_cached__ = self.client.get(self.playlist.file_tracks[-1].index)
        except appscript.reference.CommandError:
            self.__len_cached__ = 0

    def __repr__(self):
        return 'playlist:{}'.format(self.name)

    def __len__(self):
        return self.__len_cached__

    def __str__(self):
        return self.name

    @property
    def parent(self):
        """
        Parent playlist

        Return parent playlist or playlist folder
        """
        try:
            return self.playlist.parent.get().name.get()
        except appscript.reference.CommandError:
            return None

    @property
    def is_smart(self):
        """Is this smart playlist

        Return true if this is a smart playlist

        """
        return self.playlist.smart.get() and True or False

    @property
    def path(self):
        """Playlist path

        Return relative path for this playlist

        """
        path = [self.name]
        try:
            p = self.playlist.parent.get()
            while True:
                path.append(p.name.get())
                p = p.parent.get()

        except appscript.reference.CommandError:
            pass

        path.reverse()
        return os.sep.join(path)

    def __getattr__(self, attr):
        try:
            ref = getattr(self.playlist, attr)
            return self.client.get(ref)

        except AttributeError:
            pass

        except appscript.reference.CommandError:
            pass

        raise AttributeError('No such playlist item: {}'.format(attr))

    def __getitem__(self, index):
        """Get track by index

        """
        try:
            index = int(index)
        except ValueError:
            raise ValueError('Invalid playlist index: {}'.format(index))

        if index < 0:
            index = len(self) - index

        try:
            index = int(index) + 1
            if index > len(self):
                raise StopIteration
            return self.client.get_playlist_track(self.playlist, index)
        except ValueError:
            self.__update_len__()
            raise ValueError('Invalid playlist index: {}'.format(index))
        except appscript.reference.CommandError:
            self.__update_len__()
            raise IndexError('Out of playlist: {:d}'.format(index))

    def __iter__(self):
        return self

    def __next__(self):
        return self.next() # noqa B305

    def next(self):
        """Iterate playlist

        Iterate tracks on playlist
        """
        try:
            if self.__index__ > len(self):
                raise StopIteration
            try:
                track = self[self.__index__]
                self.__index__ += 1
            except IndexError:
                raise StopIteration
        except StopIteration:
            self.__index__ = 0
            raise StopIteration

        return track

    def jump(self, index):
        """Jump to position

        Jump to playlist position

        """
        if index < 0 or index > len(self):
            raise ValueError
        self.__index__ = index + 1
        return self[self.__index__]

    def add(self, files):
        """Add files to playlist

        Add provided files to the playlist

        """
        if not isinstance(files, list):
            files = [files]
        self.client.add([mactypes.Alias(entry) for entry in files], to=self.playlist)
        self.__update_len__()

    def delete(self, entry):
        """Delete entry from playlist

        Delete provided track entry from playlist (via entry.track)

        """
        try:
            self.client.delete(entry.track)
            if self.__index__ > 0:
                self.__index__ -= 1
            self.__update_len__()
        except appscript.reference.CommandError as e:
            raise MusicPlayerError('Error deleting track {}: {}'.format(entry.track, e))
