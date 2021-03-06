#!/usr/bin/env python
"""
Update music player library metadata against a music tree from command line
"""

import os
import time

from systematic.shell import Script, normalized
from oodi.library.track import Track

from pytunes import MusicPlayerError
from pytunes.client import Client, MusicTree

# How often we report something
PROGRESS_INTERVAL = 1000


def main():

    script = Script(description='Update music player library metadata')
    script.add_argument('-c', '--codec', help='Music library default codec')
    script.add_argument('-l', '--music-path', help='Music library path')
    script.add_argument('-p', '--position', type=int, help='Start from given position in library')
    script.add_argument('-m', '--metadata', action='store_true', help='Update metadata')
    args = script.parse_args()

    client = Client()

    script.log.info('Loading music player library playlist')

    if args.position:
        try:
            client.library.jump(args.position)
        except ValueError:
            script.exit(1, 'Invalid position: {0} ({1:d} entries)'.format((
                args.position,
                len(client.library)
            )))

    try:
        tree = MusicTree(tree_path=args.music_path)
        tree.load()
        tree_paths = tree.realpaths
    except Exception as e:
        script.exit(1, e)

    processed = 0
    progress_interval = PROGRESS_INTERVAL
    progress_start = time.time()
    start = time.time()
    app_files = {}

    script.log.info('Checking library files against music player database')

    for entry in client.library:
        processed += 1
        if processed % progress_interval == 0:
            progress_time = float(time.time() - progress_start)
            progress_rate = int(progress_interval / progress_time)
            script.log.info('Index {0:d} ({1:d} entries per second)'.format(processed, progress_rate))
            progress_start = time.time()

        try:
            if entry.path is None:
                try:
                    client.library.delete(entry)
                except MusicPlayerError as e:
                    print(e)
                continue
        except TypeError as e:
            print('Error processing entry {0}: {1}'.format(entry, e))
            continue

        try:
            path = normalized(os.path.realpath(entry.path))
        except AttributeError:
            script.log.info('Removing invalid entry (no path defined)')
            try:
                client.library.delete(entry)
            except MusicPlayerError as e:
                print(e)
            continue

        if path not in tree_paths:
            if not os.path.isfile(path):
                script.log.info('Removing non-existing: "}0}"'.format(path))
                try:
                    client.library.delete(entry)
                except MusicPlayerError as e:
                    print(e)
            else:
                script.log.info('File outside tree: {0}'.format(path))

        elif path not in app_files:
            app_files[path] = entry
            if args.metadata:
                mtime = os.stat(path).st_mtime
                if int(entry.modification_date.strftime('%s')) >= mtime:
                    continue

                song = Track(entry.path)
                if entry.syncTags(song):
                    client.library.__next = entry.index

        else:
            script.log.info('Removing duplicate: {0}'.format(entry.path))
            try:
                client.library.delete(entry)
            except MusicPlayerError as e:
                print(e)

    loadtime = float(time.time() - start)
    script.log.info('Checked {0:d} files in {1:4.2f} seconds'.format(processed, loadtime))

    start = time.time()
    processed = 0

    script.log.info('Checking music player database against tree files')

    if args.position is None:

        for path in sorted(tree_paths.keys()):

            if path not in app_files:
                script.log.info('Adding: {0}'.format(path))
                try:
                    client.library.add(path)
                except ValueError as e:
                    print(e)

            processed += 1
            if processed % 1000 == 0:
                script.log.debug('Processed: {0:d} entries'.format(processed))

    loadtime = float(time.time() - start)
    script.log.info('Checked {0:d} files in {1:2.2f} seconds'.format(processed, loadtime))
