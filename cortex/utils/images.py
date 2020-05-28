import struct

import urlpath
from PIL import Image
from urlpath import URL

from cortex.utils import read_all


class ColorImage:
    SupportedSchemes = ['file']

    @classmethod
    def from_bytes(cls, width, height, data):
        return cls(Image.frombytes("RGB", (width, height), data))

    @classmethod
    def from_uri(cls, uri):
        uri =  URL(uri)
        if uri.scheme not in cls.SupportedSchemes:
            raise ValueError(f"currently not supporting {uri.scheme} uris")
        return cls(Image.open(uri.path))

    def __init__(self, impl):
        self._impl = impl


    def save(self, fp):
        self._impl.save(fp)


class DepthImage:
    SupportedSchemes = ['file']

    @classmethod
    def from_bytes(cls, width, height, data):
        return cls(Image.frombytes("RGB", (width, height), data))

    Header = struct.Struct("II")
    @classmethod
    def from_uri(cls, uri):
        uri =  URL(uri)
        if uri.scheme not in cls.SupportedSchemes:
            raise ValueError(f"currently not supporting {uri.scheme} uris")
        with open(uri.path, "rb") as f:
            width, height = cls.Header.unpack(read_all(f, cls.Header.size))
            data = struct.unpack(f"{width*height}f", f.read())

        return cls(width, height, data)

    def __init__(self, width, height, data):
        self.width = width
        self.height = height
        self.data = data

    @property
    def size(self):
        return self.width * self.height

    def save(self, fp):
        fp.write(self.Header.pack(self.width, self.height))
        fp.write(struct.pack(f'{self.size}f', self.data))

