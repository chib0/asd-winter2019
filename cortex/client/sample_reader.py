import gzip
import struct
from contextlib import contextmanager

# from cortex.utils.struct_stream import StructStream
from ..core import thought
"""
The thing we are trying to achieve here is the following:
1. We get a means of reading the Sample file 
2. The reader is format agnostic
3. Format changes are PnP into the reader. 
    3.1 There has to be a class that reads the thoughts correctly, and couples them with user info.
    3.2 There has to be a very clear api to the format reader and the sample reader
4. The Sample 'provider' may change. today it's a gzip file, tomorrow it's read from a dedicated buffer in the kernel.
    4.1 The formatter has to get it's bytes from a stream that knows exactly what it's reading, and it has to be PnP.
    4.2 There has to be a clear api that allows the formatter to get bytes from the stream and handle that.
    
    
What I chose to do is have a SampleThoughtReader which:
 1. Implements the logic of reading thoughts one by another
 2. Can be decorated with a stream type (for context manager 'open' functions) and a format parser.
"""


class SampleReader:
    def __init__(self, stream, parser):
        """
        gets a stream and spits out a SampleReader, which outputs thoughts one by one from the file.
        @:param stream - should support the normative pythonic stream functions (like file or BytesIO)
        @:param formatter - should read thoughts from a stream.
        """
        self._stream = stream
        self._parser = parser

    def __iter__(self):
        return iter(self._parser)

    def next(self):
        next_thought = self._parser.next(self._stream)
        while next_thought:
            yield next_thought
        raise StopIteration

    def __repr__(self):
        return f"{self.__class__.__name__} over {self._stream!r} with formatter {self._parser!r}"

    def __str__(self):
        return f"Sample Reader over {self._stream} with {self._parser}"

