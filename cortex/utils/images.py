import io
import json
import struct
import bson
import numpy
from matplotlib import pyplot
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
        """
        creates a new DepthImage from widht, height, and array of floats.
        :param width:
        :param height:
        :param data:
        :return:
        """
        parsed_data = list(data[width *i: width*(i+1)] for i in range(height))
        return cls(parsed_data)

    Header = struct.Struct("II")
    @classmethod
    def from_uri(cls, uri):
        """
        returns a new depth image from the URI. the uri should be a bson file
        :param uri:
        :return:
        """
        uri =  URL(uri)
        if uri.scheme not in cls.SupportedSchemes:
            raise ValueError(f"currently not supporting {uri.scheme} uris")
        with open(uri.path, "rb") as f:
            return cls.from_file(f)

    @classmethod
    def from_file(cls, f):
        """
        creates a depth image from a bson file
        :param f:
        :return:
        """
        data = bson.decode_all(f.read())
        return cls(data[0]['raw']['data'])

    def __init__(self, data):
        self.data = data

    @property
    def width(self):
        return len(self.data[0]) if len(self.data) else 0

    @property
    def height(self):
        return len(self.data)

    @property
    def size(self):
        return self.width * self.height

    def _img_data(self):
        fig = pyplot.Figure()
        axes = fig.add_subplot(1,1,1)
        axes.imshow(numpy.array(self.data))
        img_data = io.BytesIO()
        fig.savefig(img_data)
        return bytes(img_data.getbuffer())

    def save(self, fp):
        """
        writes the image as bson
        :param fp:
        :return:
        """
        fp.write(self.bson())

    def bson(self):
        """
        returns the bson encoded image
        :return:
        """
        return bson.encode(dict(
            raw=dict(width=self.width, height=self.height, data=self.data), image=self._img_data()))

    @classmethod
    def from_bson_data(cls, data):
        """
        :param data:
        :return:
        """
        return cls.from_file(io.BytesIO(data))

