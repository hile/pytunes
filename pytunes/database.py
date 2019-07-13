"""
Sqlite database to cache music player track index / filename mappings
"""

import os

from datetime import datetime
from pytz import timezone
from sqlite3 import OperationalError
from systematic.sqlite import SQLiteDatabase

from pytunes import MusicPlayerError

TABLES_SQL = (
    """
    CREATE TABLE IF NOT EXISTS tracks (
        key INTEGER PRIMARY KEY,
        path STRING,
        mtime INTEGER,
        added DATE
    );
    """,
)


class TrackIndexDB(SQLiteDatabase):
    """
    Track index database

    SQlite index for track paths in MacOS music player
    """
    def __init__(self, client, path):
        super().__init__(path, tables_sql=TABLES_SQL)
        self.client = client

    def __repr__(self):
        return '{}'.format(self.db_path)

    def add_track(self, track):
        """
        Add track to index
        """

        try:
            c = self.cursor
            c.execute("""SELECT key, mtime FROM tracks WHERE key=?""", (track.index,))
            res = c.fetchone()
        except OperationalError as e:
            raise MusicPlayerError(e)

        try:
            mtime = os.stat(track.path).st_mtime
        except OSError:
            mtime = None
        except IOError:
            mtime = None

        if res is not None:
            if mtime:
                if res[1] != mtime:
                    c = self.cursor
                    c.execute("""UPDATE tracks set mtime=? WHERE key=?""", (mtime, res[0],))
                    self.commit()
            else:
                c = self.cursor
                c.execute("""DELETE FROM tracks WHERE key=?""", (res[0],))
                self.commit()

        elif mtime is not None:
            added = datetime.now(timezone('UTC'))
            try:
                c = self.cursor
                c.execute("""INSERT INTO tracks VALUES (?, ?, ?, ?)""", (
                    track.index,
                    track.path,
                    mtime,
                    added
                ))
                self.commit()
            except OperationalError as e:
                raise MusicPlayerError(e)

    def lookup_index(self, path):
        """
        Find index for filename

        Raises MusicPlayerError if path was not in database
        """
        path = os.path.realpath(path)
        try:
            c = self.cursor
            c.execute("""SELECT key FROM tracks WHERE path=?""", (path,))
            res = c.fetchone()
        except OperationalError as e:
            raise MusicPlayerError(e)
        if res:
            return res[0]
        else:
            raise MusicPlayerError('Track not in index database: {}'.format(path))

    def cleanup(self, ids):
        """
        Remove unknown IDs

        Removes tracks with ID not provided in list 'ids'
        """
        try:
            c = self.cursor
            c.execute("""DELETE FROM tracks WHERE key not in (?)""", (','.join(ids),))
            self.commit()
        except OperationalError as e:
            raise MusicPlayerError(e)

    def update(self):
        """
        Update index

        Update tracks track sqlite index
        """
        ids = []
        for _i, track in enumerate(self.client.library):
            if track.path is not None:
                self.add_track(track)
                ids.append('{}'.format(track.index))
        self.cleanup(ids)
