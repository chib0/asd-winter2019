import struct
import datetime



class Thought:
    TimeReprFormat = "%Y,%m,%d,%H,%M,%S"
    TimeStrFormat = "%Y-%m-%d %H:%M:%S"
    MetadataPacker = struct.Struct("<QQI")

    __slots__ = ('_uid', '_timestamp', '_thought')
    def __init__(self, user_id, timestamp, thought):
        self._uid = user_id
        self._timestamp = timestamp
        self._thought = thought

    @property
    def user_id(self):
        return self._uid

    @property
    def timestamp(self):
        return self._timestamp  # I should have copied this but I chose not to.

    @property
    def thought(self):
        return self._thought

    def _format_timestamp(self, fmt):
        return f"{self._timestamp:{fmt}}"

    def __repr__(self):
        return f'Thought(user_id={self._uid!r}, timestamp={self.timestamp!r}, thought={self._thought!r})'

    def __str__(self):
        return f"[{self._format_timestamp(self.TimeStrFormat)}] user {self._uid}: {self._thought}"

    def __eq__(self, other):
        if not isinstance(other, Thought):
            return False
        return all(self.__getattribute__(x) == other.__getattribute__(x) for x in self.__slots__)

    def serialize(self):
        return self.MetadataPacker.pack(self._uid, int(self._timestamp.timestamp()), len(self._thought)) + \
                    bytearray(self._thought, "utf-8")

    @classmethod
    def deserialize(cls, thought_bytes):  # though thought_bites is both a better pun and a better name
        header, payload = thought_bytes[:cls.MetadataPacker.size], thought_bytes[cls.MetadataPacker.size:]
        uid, timestamp, data_len = cls.MetadataPacker.unpack(header)
        return cls(uid,
                   datetime.datetime.fromtimestamp(timestamp),
                   payload[:data_len].decode("utf-8"))




