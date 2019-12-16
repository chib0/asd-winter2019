import struct


class ThoughtXCoder:
    def __init__(self, name, format):
        self.name = name
        self.format = struct.Struct(format)

    def encode(self, thing):
        return self.format.pack(thing)

    def decode(self, bytearr):
        return self.format.unpack(bytearr)
