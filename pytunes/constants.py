"""
Field and order specs
"""

import appscript

TRACK_SYS_FIELDS = (
    'id', # integer -- the id of the item
    'index', # integer -- The index of the item in internal application order.
    'persistent_ID', # string -- the id of the item as a hexidecimal string.
)

TRACK_FIELDS = (
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
 'duration',
 'bookmark',
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
