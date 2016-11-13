# -*- coding: utf-8 -*-
"""
Field and order specs
"""

import appscript

SKIPPED_PLAYLISTS = (
    'iTunes U',
    'Music',
    'Movies',
    'Videos',
    'Home Videos',
    'Films',
    'TV Shows',
    'TV Programmes',
    'Audiobooks',
    'Purchased',
    'Books',
    'PDFs',
    'Genius',
)

TRACK_SYS_FIELDS = (
    'id',
    'index',
    'persistent_ID',
)

TRACK_FIELDS = (
    'name',
    'album',
    'album_artist',
    'album_rating',
    'album_rating_kind',
    'artist',
    'bit_rate',
    'bookmark',
    'bookmarkable',
    'bpm',
    'category',
    'comment',
    'compilation',
    'composer',
    'database_ID',
    'date_added',
    'description',
    'disc_count',
    'disc_number',
    'duration',
    'enabled',
    'episode_ID',
    'episode_number',
    'EQ',
    'finish',
    'gapless',
    'genre',
    'grouping',
    'kind',
    'lyrics',
    'modification_date',
    'played_count',
    'played_date',
    'podcast',
    'rating',
    'rating_kind',
    'release_date',
    'sample_rate',
    'season_number',
    'shufflable',
    'skipped_count',
    'skipped_date',
    'show',
    'sort_album',
    'sort_artist',
    'sort_album_artist',
    'sort_name',
    'sort_composer',
    'sort_show',
    'size',
    'start',
    'time',
    'track_count',
    'track_number',
    'unplayed',
    'video_kind',
    'volume_adjustment',
    'year',
    'location',
)

TRACK_INT_FIELDS = (
    'year',
    'id',
    'index',
    'album_rating',
    'rating',
    'disc_count',
    'disc_number',
    'episode_number',
    'played_count',
    'season_number',
    'sample_rate',
    'size',
    'track_count',
    'track_number',
    'volume_adjustment',
)

TRACK_FLOAT_FIELDS = (
    'bpm',
    'bitrate',
    'bit_rate',
    'duration',
    'bookmark',
    'start',
    'finish',
)

TRACK_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
TRACK_DATE_FIELDS = (
    'date_added',
    'modification_date',
    'played_date',
    'release_date',

)

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
