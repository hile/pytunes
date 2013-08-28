#!/usr/bin/env python
"""
Very basic class to abstract access to itunes library from python.
"""

import sys,os,re,logging
import appscript,mactypes

from musa.tags import TagError
from musa.tree import Tree,Album,Track

from pytunes import iTunesError
from pytunes import terminology as itunes_terminology

TRACK_SYS_FIELDS = [
    'id', # integer -- the id of the item
    'index', # integer -- The index of the item in internal application order.
    'persistent_ID', # string -- the id of the item as a hexidecimal string.
]

TRACK_FIELDS = [
    'name', # unicode_text -- the name of the item This id does not change over time.
    'album', # unicode_text -- the album name of the track
    'album_artist', # unicode_text -- the album artist of the track
    'album_rating', # integer -- the rating of the album for this track (0 to 100)
    'album_rating_kind', # k.user / k.computed -- the rating kind of the album rating for this track
    'artist', # unicode_text -- the artist/source of the track
    'bit_rate', # integer -- the bit rate of the track (in kbps)
    'bookmark', # short_float -- the bookmark time of the track in seconds
    'bookmarkable', # boolean -- is the playback position for this track remembered?
    'bpm', # integer -- the tempo of this track in beats per minute
    'category', # unicode_text -- the category of the track
    'comment', # unicode_text -- freeform notes about the track
    'compilation', # boolean -- is this track from a compilation album?
    'composer', # unicode_text -- the composer of the track
    'database_ID', # integer -- the common, unique ID for this track. If two tracks in different playlists have the same database ID, they are sharing the same data.
    'date_added', # date -- the date the track was added to the playlist
    'description', # unicode_text -- the description of the track
    'disc_count', # integer -- the total number of discs in the source album
    'disc_number', # integer -- the index of the disc containing this track on the source album
    'duration', # short_float -- the length of the track in seconds
    'enabled', # boolean -- is this track checked for playback?
    'episode_ID', # unicode_text -- the episode ID of the track
    'episode_number', # integer -- the episode number of the track
    'EQ', # unicode_text -- the name of the EQ preset of the track
    'finish', # short_float -- the stop time of the track in seconds
    'gapless', # boolean -- is this track from a gapless album?
    'genre', # unicode_text -- the music/audio genre (category) of the track
    'grouping', # unicode_text -- the grouping (piece) of the track. Generally used to denote movements within a classical work.
    'kind', # unicode_text -- a text description of the track long_description : unicode_text
    'lyrics', # unicode_text -- the lyrics of the track
    'modification_date', # date -- the modification date of the content of this track
    'played_count', # integer -- number of times this track has been played
    'played_date', # date -- the date and time this track was last played
    'podcast', # boolean -- is this track a podcast episode?
    'rating', # integer -- the rating of this track (0 to 100)
    'rating_kind', # k.user / k.computed -- the rating kind of this track
    'release_date', # date -- the release date of this track
    'sample_rate', # integer -- the sample rate of the track (in Hz)
    'season_number', # integer -- the season number of the track
    'shufflable', # boolean -- is this track included when shuffling?
    'skipped_count', # integer -- number of times this track has been skipped
    'skipped_date', # date -- the date and time this track was last skipped
    'show', # unicode_text -- the show name of the track
    'sort_album', # unicode_text -- override string to use for the track when sorting by album
    'sort_artist', # unicode_text -- override string to use for the track when sorting by artist
    'sort_album_artist', # unicode_text -- override string to use for the track when sorting by album artist
    'sort_name', # unicode_text -- override string to use for the track when sorting by name
    'sort_composer', # unicode_text -- override string to use for the track when sorting by composer
    'sort_show', # unicode_text -- override string to use for the track when sorting by show name
    'size', # integer -- the size of the track (in bytes)
    'start', # short_float -- the start time of the track in seconds
    'time', # unicode_text -- the length of the track in MM:SS format
    'track_count', # integer -- the total number of tracks on the source album
    'track_number', # integer -- the index of the track on the source album
    'unplayed', # boolean -- is this track unplayed?
    'video_kind', # k.none / k.movie / k.music_video / k.TV_show -- kind of video track
    'volume_adjustment', # integer -- relative volume adjustment of the track (-100% to 100%)
    'year', # integer -- the year the track was recorded/released
    'location', # alias -- the location of the file represented by this track
]

TRACK_INT_FIELDS = [
    'year','id','index','album_rating','rating',
    'disc_count','disc_number','episode_number','season_number',
    'sample_rate','size','track_count','track_number',
    'volume_adjustment'
]
TRACK_FLOAT_FIELDS = [ 'bpm','bitrate','duration','bookmark',]

REPEAT_VALUES = {
    'off': appscript.k.off,
    'one': appscript.k.one,
    'all': appscript.k.all,
}

ITUNES_PLAYER_STATE_NAMES = {
    appscript.k.playing: 'playing',
    appscript.k.paused:  'paused',
    appscript.k.stopped: 'stopped',
    appscript.k.off: False,
    appscript.k.off: False,
}

# Default settings for 'normal' itunes on OS/X. Does not work on windows
ITUNES_DIR = os.path.join(os.getenv('HOME'),'Music','iTunes')
ITUNES_MUSIC = os.path.join(ITUNES_DIR,'iTunes Media','Music')
ITUNES_PATH_FILE = os.path.join(ITUNES_DIR,'library_path.txt')

class iTunesMusicTree(Tree):
    def __init__(self,itunes_path=None,codec='m4a',tree_path=ITUNES_PATH_FILE):
        self.itunes_path = itunes_path is not None and itunes_path or ITUNES_DIR
        if not os.path.isdir(self.itunes_path):
            raise iTunesError('No such directory: %s' % self.itunes_path)

        if tree_path is None:
            if os.path.isfile(ITUNES_PATH_FILE):
              try:
                  tree_path = open(ITUNES_PATH_FILE,'r').read().strip()
              except IOError,(ecode,emsg):
                  raise iTunesError('Error opening %s: %s' % (tree_path, emsg))
              except OSError,(ecode,emsg):
                  raise iTunesError('Error opening %s: %s' % (tree_path, emsg))
            else:
                tree_path = ITUNES_MUSIC

        if not os.path.isdir(tree_path):
                raise iTunesError('No such directory: %s' % tree_path)
        Tree.__init__(self,path=tree_path)

class iTunes(object):
    """iTunes application

    Wrap iTunes application nicely

    """

    def __init__(self):
        self.itunes = appscript.app('iTunes',terms=itunes_terminology)
        self.log = logging.getLogger('modules')

    def __getattr__(self,attr):
        try:
            return self.itunes.__getattr__(attr)
        except AttributeError:
            raise AttributeError('No such iTunes attribute: %s' % attr)

    @property
    def library(self):
        for src in self.itunes.sources.get():
            if src.kind.get() == appscript.k.library:
                return src
        return None

    @property
    def status(self):
        s = self.itunes.player_state.get()
        try:
            return ITUNES_PLAYER_STATE_NAMES[s]
        except KeyError:
            return 'Unknown (%s' % (s)

    @property
    def current_track(self):
        try:
            return Track(self.itunes.current_track(),self.itunes)
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
            raise iTunesError('Invalid repeat value %s' % value)

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
        if not isinstance(value,int):
            raise iTunesError('Volume adjustment must be integer value')
        if value<0 or value>100:
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
    def __init__(self,track,app=None):
        self.itunes = app
        if not self.itunes:
            self.itunes = iTunes()
        self.track = track
        try:
            self.path = self.itunes.get(self.track.location).path
        except AttributeError:
            self.path = None
        self.log = logging.getLogger('modules')

    def __repr__(self):
        return '%s - %s - %s' % (self.artist,self.album,self.title)

    def __getattr__(self,attr):
        try:
            return self[attr]
        except KeyError:
            pass
        raise AttributeError('Invalid Track attribute: %s' % attr)

    def __getitem__(self,item):
        if item == 'path':
            return self.path
        if item == 'extension':
            return os.path.splitext(self.path)[1][1:]
        if item in ['id','ID']:
            item = 'id'
        if item in ['date','year']:
            item = 'year'
        if item in ['title','name']:
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
        raise KeyError('Invalid Track item: %s' % item)

    def __setattr__(self,item,value):
        if item in ['date','year']:
            item = 'year'
            if type(value) != int:
                try:
                    value = int(value.split('-')[0])
                except ValueError:
                    raise AttributeError('tag %s invalid value: %s' % (item,value))
                except IndexError:
                    value = int(value)
        if item in TRACK_FIELDS:
            try:
                entry = self.track.__getattr__(item)
                self.itunes.set(entry,to=value)
            except appscript.reference.CommandError,e:
                raise ValueError('ERROR setting %s to %s: %s' % (item,value,e))
        elif item in TRACK_SYS_FIELDS:
            raise ValueError('Track attribute %s is read-only' % item)
        elif item in ['itunes','track','path','log']:
            self.__dict__[item] = value
        else:
            raise AttributeError('Invalid Track attribute: %s' % item)

    def updateTracknumber(self):
        m = re.match('^([0-9]+) .*',os.path.basename(self.path))
        if not m:
            return False
        track = int(m.group(1))
        name,ext = os.path.splitext(os.path.basename(self.path))
        total = len(filter(lambda x: os.path.splitext(x)[1]==ext,os.listdir(os.path.dirname(self.path))))
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

    def updateTag(self,tag,value):
        try:
            current_value = self.__getattr__(tag)
            if tag in ['year','date']:
                if type(value) != int:
                    try:
                        value = value.split('-')[0]
                    except IndexError:
                        value = str(value)
            if current_value == value:
                return
        except AttributeError,e:
            self.log.debug('Error checking current value: %s' % e)
            pass
        if value == '' or value == None:
            return
        self.log.debug('%s set %s: %s' % (self.path.encode('utf-8'),tag,value))
        self.__setattr__(tag,value)

    def syncTags(self,song):
        modified = False
        try:
            for tag in ['artist','album','title','genre','date','bpm']:
                if not song.tags.has_key(tag):
                    continue
                if tag in ['bpm','date']:
                    value = int(song.tags[tag])
                else:
                    value = song.tags[tag]
                if tag == 'bpm' and value == 0:
                    continue
                if tag == 'title':
                    tag = 'name'
                self.updateTag(tag,value)
                modified = True
        except TagError,e:
            raise iTunesError('Error updating tags: %s %s' % (self.path,e))
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
            items.append([k,self.__getattr__(k)])
        return items

