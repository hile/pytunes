#!/usr/bin/env python

import os
import sys
import re
import appscript
import mactypes

from pytunes.client import iTunes, Track
from soundforest.playlist import m3uPlaylist

SKIP_PLAYLISTS = (
    'Music',
    'Movies',
    'TV Shows',
    'Purchased'
)

def AlliTunesPlaylists(client=None, skipDefaultLists=True, include_smart_playlists=False):
    client = client is not None and client or iTunes()
    playlists = []
    for pl in client.user_playlists.get():
        name = pl.name.get()
        if skipDefaultLists and name in SKIP_PLAYLISTS:
            continue
        if pl.smart.get() and not include_smart_playlists:
            continue
        playlists.append(iTunesPlaylist(name, client))
    return playlists

class iTunesPlaylist(object):
    def __init__(self, name='library', app=None):
        self.itunes = app is not None and app or iTunes()
        self.__next = 0
        try:
            if name == 'library':
                self.playlist = self.itunes.get(self.itunes.library_playlists[name])
            else:
                self.playlist = self.itunes.get(self.itunes.user_playlists[name])
        except appscript.reference.CommandError:
            self.playlist = self.itunes.make(
                new=appscript.k.user_playlist,  at='Playlists',
                with_properties={appscript.k.name: name},
            )
        self.name = name
        self.__update_len()

    def __update_len(self):
        try:
            self.__len_cached = self.itunes.get(self.playlist.file_tracks[-1].index)
        except appscript.reference.CommandError:
            self.__len_cached = 0

    def __repr__(self):
        return 'playlist:%s' % self.name

    def __len__(self):
        return self.__len_cached

    def __str__(self):
        return self.name

    @property
    def parent(self):
        try:
            return self.playlist.parent.get().name.get()
        except appscript.reference.CommandError:
            return None

    @property
    def path(self):
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

    @property
    def smart(self):
        return self.playlist.smart.get() and True or False

    def __getattr__(self, attr):
        try:
            ref = getattr(self.playlist, attr)
            return self.itunes.get(ref)

        except AttributeError:
            pass

        except appscript.reference.CommandError:
            pass

        raise AttributeError('No such iTunesPlaylist item: %s' % attr)

    def __getitem__(self, item):
        try:
            item = int(item)+1
            return Track(self.itunes.get(self.playlist.file_tracks[item]))

        except ValueError:
            self.__update_len()
            raise ValueError('Invalid playlist index: %s' % item)

        except appscript.reference.CommandError:
            self.__update_len()
            raise ValueError('Out of playlist: %d' % item)

    def __iter__(self):
        try:
            return self
        except ValueError:
            raise StopIteration

    def next(self):
        try:
            if self.__next > len(self):
                raise ValueError
            track = self[self.__next]
            self.__next += 1
        except ValueError:
            self.__next = 0
            raise StopIteration

        return track

    def jump(self, index):
        if index < 0 or index > len(self):
            raise ValueError
        self.__next = index + 1

    def add(self, files):
        entries = []
        if type(files) == list:
            entries = map(lambda x: mactypes.Alias(x), files)
        else:
            entries = [mactypes.Alias(files)]
        self.itunes.add(entries, to=self.playlist)
        self.__update_len()

    def delete(self, entry):
        self.itunes.delete(entry.track)
        if self.__next > 0:
            self.__next -= 1
        self.__update_len()

