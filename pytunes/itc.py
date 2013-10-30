#!/usr/bin/env python

import os
from struct import pack, unpack
from PIL import ImageFile

class ITCArtworkFile(object):
    def __init__(self, path):
        self.path = path
        (self.library_id, self.track_id) = \
            os.path.splitext(os.path.basename(path))[0].split('-')

        data = open(self.path, 'r').read()

        hdr_len = unpack('>i', data[0:4])[0]
        hdr_id  = data[0:8]
        data_len = unpack('>i', data[hdr_len:hdr_len+4])[0]

        self.itc_type = data[hdr_len+44:hdr_len+48]
        imagedata = data[hdr_len+208:]
        parser = ImageFile.Parser()
        parser.feed(imagedata)
        self.image = parser.close()

    def __str__(self):
        return '%s track %s %s' % (
            self.itc_type, self.track_id, self.image.format.lower()
        )

    def write(self, outputdir, filename=None):
        if not filename:
            filename = os.path.join(
                outputdir,
                '%s.%s' % (self.track_id, self.image.format.lower())
            )

        if self.image.mode != "RGB":
            self.image = self.image.convert('RGB')

        self.image.save(filename)

# Example use for this module
if __name__ == '__main__':
    import sys

    try:
        outdir = sys.argv[1]
    except IndexError:
        outdir = '/tmp'

    artwork_dir = os.path.join(os.getenv('HOME'), 'Music/iTunes/Album Artwork')
    if not os.path.isdir(artwork_dir):
        print 'No such directory: %s' % artwork_dir
        sys.exit(1)

    print 'Writing downloaded artwork files to %s' % outdir
    for root, dirs, files in os.walk(artwork_dir):
        for f in files:
            f = os.path.join(root, f)
            if os.path.splitext(f)[1] != '.itc': continue
            itcfile = ITCArtworkFile(f)
            if itcfile.itc_type == 'locl':
                continue
            print '%s.%s' % (itcfile.track_id, itcfile.image.format.lower())
            itcfile.write(outdir)

