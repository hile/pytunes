"""
ITC Albumart files
"""

import os
from struct import pack, unpack
from PIL import ImageFile

class ITCArtworkFile(object):
    """ITC Albumart

    ITC Albumart file parser
    """
    def __init__(self, path):
        self.path = path

        self.library_id, self.track_id = os.path.splitext(
            os.path.basename(path)
        )[0].split('-')

        data = open(self.path, 'r').read()

        hdr_len = unpack('>i', data[0:4])[0]
        hdr_id  = data[0:8]
        data_len = unpack('>i', data[hdr_len:hdr_len + 4])[0]

        self.itc_type = data[hdr_len + 44:hdr_len + 48]
        imagedata = data[hdr_len + 208:]
        parser = ImageFile.Parser()
        parser.feed(imagedata)
        self.image = parser.close()

    def __str__(self):
        return '{0} track {1} {2}'.format(
            self.itc_type,
            self.track_id,
            self.image.format.lower(),
        )

    def write(self, outputdir, filename=None):
        """Write ITC to file

        Write ITC image output file specified directory
        """
        if not filename:
            filename = os.path.join(
                outputdir, '{0}.{1}'.format(
                    self.track_id,
                    self.image.format.lower(),
                )
            )

        if self.image.mode != "RGB":
            self.image = self.image.convert('RGB')

        self.image.save(filename)
