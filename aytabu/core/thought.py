import struct
import datetime
from PIL import Image
from . import net_messages_pb2

class Thought:
    """
    encapsu
    """
    TimeReprFormat = "%Y,%m,%d,%H,%M,%S"
    TimeStrFormat = "%Y-%m-%d %H:%M:%S"
    MetadataPacker = struct.Struct("<QQI")

    def __init__(self, user_id, timestamp, translation=(0,0,0), emotion=None, color_image=None, depth_image=None):
        self._uid = user_id
        self._timestamp = timestamp
        self.translation = translation,
        self.emotion = emotion
        self.color_image = Image.Image() if not color_image else color_image
        self.depth_image = Image.Image() if not depth_image else color_image

    @property
    def user_id(self):
        return self._uid

    @property
    def timestamp(self):
        return self._timestamp  # I should have copied this but I chose not to.

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

    def to_snapshot(self, fields=None):
        """
        creates a UserSnapshot from the thought
        :param fields: the fields to include in the snapshot. default: all fields are included
        :return: a UserMessage as defined in net_messages.proto
        """

        return net_messages_pb2.UserSnapshot()