
import appscript
import os
import re

from . import MusicPlayerError

from .constants import (
    TRACK_FIELDS,
    TRACK_SYS_FIELDS,
    TRACK_INT_FIELDS,
    TRACK_FLOAT_FIELDS,
    TRACK_DATE_FIELDS,
    MUSIC_APP_IGNORED_FIELDS
)


class Track(object):
    """
    Track in music player library
    """

    def __init__(self, client, track):
        self.client = client
        self.track = track

        try:
            self.path = self.client.get(self.track.location).path
        except AttributeError:
            self.path = None
        except appscript.reference.CommandError:
            self.path = None

    def __repr__(self):
        return '{} - {} - {}'.format(
            self.artist,
            self.album,
            self.title,
        )

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            pass
        raise AttributeError('Invalid Track attribute: {}'.format(attr))

    def __getitem__(self, item):
        if item == 'path':
            return self.path

        if item == 'extension':
            return os.path.splitext(self.path)[1][1:]

        if item in ('id', 'ID'):
            item = 'id'

        if item in ('date', 'year'):
            item = 'year'

        if item in ('title', 'name'):
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
                return str(value)

            except AttributeError:
                return value

        except AttributeError:
            pass

        except appscript.reference.CommandError:
            return None

        raise KeyError('Invalid Track item: {}'.format(item))

    def __setattr__(self, item, value):
        if item in ('date', 'year'):
            item = 'year'
            if type(value) != int:
                try:
                    value = int(value.split('-')[0])
                except ValueError:
                    raise AttributeError('tag {} invalid value: {}'.format(item, value))
                except IndexError:
                    value = int(value)

        if item in TRACK_FIELDS:
            try:
                entry = self.track.__getattr__(item)
                self.client.set(entry, to=value)
            except appscript.reference.CommandError as e:
                raise ValueError('ERROR setting {} to {}: {}'.format(item, value, e))

        elif item in TRACK_SYS_FIELDS:
            raise ValueError('Track attribute {} is read-only'.format(item))

        elif item in ('client', 'track', 'path', 'log'):
            self.__dict__[item] = value

        else:
            raise AttributeError('Invalid Track attribute: {}'.format(item))

    def updateTracknumber(self):
        """Update tracknumber

        Update tracknumber in player. Sets album total tracks to number of files with same extension
        in same directory.
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
        """Set tag in player metadata

        Set tag to value in player metadata for track
        """
        try:
            current_value = self.__getattr__(tag)
            if tag in ('year', 'date'):
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

        Sync tags from file metadata to player metadata
        """
        modified = False
        try:
            for tag in ('artist', 'album', 'title', 'genre', 'date', 'bpm'):
                if tag not in song.tags:
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

        except Exception as e:
            raise MusicPlayerError('Error updating tags: {} {}'.format(self.path, e))

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
        if self.client.__app_name__ == 'Music':
            keys.extend(field for field in TRACK_FIELDS if field not in MUSIC_APP_IGNORED_FIELDS)
        else:
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
