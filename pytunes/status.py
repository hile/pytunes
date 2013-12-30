"""Song status change

Song change monitoring and XML reporting class

"""

import os
import sys
import time
import base64
import appscript

from lxml import etree as ET
from lxml.builder import E

from pytunes.client import iTunes
from soundforest import normalized

INFO_KEY_ORDER = (
    'path',
    'album_artist',
    'artist',
    'album',
    'name',
    'comment',
    'length',
    'genre',
    'year',
    'track_number',
    'track_count'
)

IGNORE_TRACK_FIELDS = (
    'persistent_ID',
    'id',
    'index',
    'start',
    'finish',
    'database_ID',
    'time',
    'album_rating_kind',
    'compilation',
    'date_added',
    'enabled',
    'gapless',
    'modification_date',
    'played_count',
    'podcast',
    'rating_kind',
    'release_date',
    'played_date',
    'skipped_date',
    'skipped_count',
    'bookmarkable',
    'shufflable',
    'unplayed',
    'video_kind',
    'location',
)

class iTunesStatus(object):
    """Song status change monitoring

    This class can monitor status of currently playing iTunes track
    and return track change information with next() iterator, when
    current track changes.

    """

    def __init__(self, interval=1, xml_output=False, export_albumart=False):
        self.client = iTunes()
        self.interval = int(interval)
        self.xml_output = xml_output
        self.export_albumart = export_albumart

        try:
            self.previous = self.client.current
        except appscript.reference.CommandError:
            self.previous = None

        self.status = self.client.status

    def __iter__(self):
        return self

    def next(self):
        """Return song info on song change

        Iterate current object, sleeping self.interval time and returning
        status and XML formatted track information when song is changed.

        """
        while True:
            try:
                n = self.client.current
                if self.client.status != self.status:
                    self.status = self.client.status

                    if self.status == 'playing':
                        return (self.status, self.songinfo(n))
                    else:
                        return (self.status, None)

                if self.previous is None or n.id != self.previous.id:
                    self.previous = n
                    return (self.client.status, self.songinfo(n))

            except appscript.reference.CommandError:
                pass

            time.sleep(self.interval)

    def songinfo(self, track=None, xml_output=False, export_albumart=False):
        """Current playing track info

        Return current playing track information as XML or None if no
        track was selected.

        """
        if self.client.status in ['stopped', 'paused']:
            return None

        if not track:
            track = self.client.current

        started = time.mktime(time.localtime())-self.client.player_position()
        info = {
            'path': track.path,
            'started': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(started)),
            'album_artist':  track.album_artist,
            'artist':  track.artist,
            'album':   track.album,
            'name':    track.name,
            'comment':    track.comment,
            'genre':   track.genre,
            'length':  track.time,
            'track_number':  track.track_number,
            'track_count':  track.track_count,
        }

        if track.year != 0:
            info['year'] = track.year

        albumart = os.path.join(os.path.dirname(normalized(track.path)), 'artwork.jpg')
        if os.path.isfile(albumart):
            info['artwork'] = os.path.realpath(albumart)

        if not self.xml_output and not xml_output:
            return info

        xml = E('itunes',
            persistent_ID=track.persistent_ID,
            started=info['started']
        )

        for k in INFO_KEY_ORDER:
            # Skip node attributes
            if k in ['started']:
                continue

            # Optional fields
            if not info.has_key(k):
                continue

            # Don't export empty fields
            if info[k] is '':
                continue

            v = info[k]
            try:
                if isinstance(v, int):
                    if v==0: continue
                    xml.append(E(k, '%d'%v))
                elif isinstance(v, float):
                    if v==0: continue
                    xml.append(E(k, '%.2f'%v))
                elif v!='':
                    xml.append(E(k, v))

            except ValueError, emsg:
                print emsg
                print 'ERROR encoding key %s type %s: %s' % (k, type(v), v)

        for k in sorted(track.keys()):
            v = track[k]
            if k in INFO_KEY_ORDER or k in IGNORE_TRACK_FIELDS:
                continue

            try:
                if isinstance(v, int):
                    if v==0:
                        continue
                    xml.append(E(k, '%d'%v))
                elif isinstance(v, float):
                    if v==0:
                        continue
                    xml.append(E(k, '%.2f'%v))
                else:
                    if v=='':
                        continue
                    xml.append(E(k, v))

            except TypeError, emsg:
                print emsg
                print 'ERROR encoding key %s type %s: %s' % (k, type(v), v)

            except ValueError, emsg:
                print emsg
                print 'ERROR encoding key %s type %s: %s' % (k, type(v), v)

        if (self.export_albumart or export_albumart) and albumart:
            xml.append(E('albumart',
                base64.b64encode(open(albumart, 'r').read()),
                filename=os.path.basename(albumart)
            ))

        return xml
