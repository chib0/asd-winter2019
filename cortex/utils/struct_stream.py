# import struct
# from itertools import chain
#
# def _build_cache_structs():
#     """
#     :return: a map of all simple types in all endianities to their respective struct parser.
#     """
#
#     simple_types = ("?", "i", "q", "c", "b", "u", "l")
#     simple_types = simple_types + (i.upper() for i in simple_types) + ("f", "d")
#     endianess_types = ("", "!", ">", "<")
#     combinations = ((j + i) for j in endianess_types for i in simple_types)
#     return {i: struct.Struct(i) for i in combinations}
#
#
# class StructStream:
#     """
#     This utility allows us to what use Struct on a stream, but in a neater style than just reading according to size
#     this does not have a context manager because it's simply a wrapper.
#     """
#     CHACED_STRUCTS = _build_cache_structs()
#
#     def __init__(self, stream):
#         self._stream = stream
#
#     def close(self):
#         self._stream.close()
#
#     def read_value(self, value_str):
#         reader =
#
#     def read(self, struct_str):
#         """
#         reads the requested struct from the stream. may raise any exception that is usually raised from struct or the
#         stream used.
#
#         :param struct_str: the struct to read
#         :return: the value if reading
#         """
#         reader = self.CHACED_STRUCTS.get(struct_str, None)
#         if reader:
#             return reader.read()
#         return reader.unpack(self._stream.read(reader.size))
#
