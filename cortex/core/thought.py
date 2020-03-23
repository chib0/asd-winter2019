import inspect
import struct
import datetime

def snapshot_protobuf_serializer(thought):
    return thought.snapshot.SerializeToString()


class Thought:
    """
    Encapsulates everything about a mindshot,
    The client and the server agree on this as the de-facto data-model of a thought.1
    The brain sample may contain more, or less data than the client and the server are feeling comfortable sharing.
    If the sample contains more info - it shall be gracefully ignored.
    If the sample contains less info - Empty fields shall be created.
    """
    TimeReprFormat = "%Y,%m,%d,%H,%M,%S"
    TimeStrFormat = "%Y-%m-%d %H:%M:%S"

    def __init__(self, metadata, snapshot):
        """
        Constructs a Thought descriptor, which is a snapshot taken by a user
        The underlying data is opaque, but should expose the following:
            user: user_id, username
            snapshot: datetime (unix timestamp)
        :param metadata: the user info. should expose a user_id,
        :param snapshot: the snapshot data
        """
        self.metadata = metadata
        self.snapshot = snapshot

    @property
    def user_id(self):
        return self.snapshot.user_id

    @property
    def username(self):
        return self.metadata.username

    @property
    def timestamp(self):
        return self.snapshot.datetime  # I should have copied this but I chose not to.

    def _format_timestamp(self, fmt):
        return f"{datetime.datetime.fromtimestamp(self.snapshot.datetime):{fmt}}"

    def __repr__(self):
        return f'Thought(user_id={self.user_id!r}, timestamp={self.timestamp!r})'

    def __str__(self):
        return f"[{self._format_timestamp(self.TimeStrFormat)}] user {self.username}"

    def __eq__(self, other):
        if not isinstance(other, Thought):
            return False
        return all(self.__getattribute__(x) == other.__getattribute__(x) for x in self.__slots__)

    def serialize(self, serializer):
        """"
        Returns a string representation of the thought.
        The default assumes we want the snapshot in a Protobuf format.
        """
        if not inspect.isfunction(serializer):
            return serializer.serialize(self)
        return serializer(self)




