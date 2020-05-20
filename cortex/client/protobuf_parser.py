from struct import Struct
from cortex import utils, Thought
from . import cortex_pb2

class ProtobufParseError(Exception): pass

class ProtobufSampleParser:
    MESSAGE_SIZE_PARSER = Struct("I")

    def __init__(self):
        self._user = None

    def read_message_size(self, stream):
        data = stream.read(self.MESSAGE_SIZE_PARSER.size)
        if not data:
            return None
        read_size , = self.MESSAGE_SIZE_PARSER.unpack(data)

        if not read_size:
            raise ProtobufParseError(f"Invalid message size {read_size}")
        return read_size


    def read_message(self, stream, into):
        """
        reads a single message into the given thing from the stream
        :param stream: stream to read from.
        :param into: the message type that is being parsed
        :return: Nothing, the message is in into. raises on error
        """
        message_size = self.read_message_size(stream)
        if not message_size:
            return False
        message = utils.read_all(stream, message_size)
        if not message:  # this would happen if read_all fails to read all the data from the stream
            raise ProtobufParseError("Could not read message from stream")
        into.ParseFromString(message)
        return True

    @property
    def user(self):
        return self._user or self.parse_user()

    @utils.decorators.call_once
    def parse_user(self, stream):
        self._user = cortex_pb2.User()
        ok = self.read_message(stream, self._user)
        return self._user if ok else None

    def parse_thought(self, stream):
        """
        reads the next thought from the stream, returns a Thought object with all needed info
        :param stream: the stream to parse the thought from
        :return:
        """
        thought_data = cortex_pb2.Snapshot()
        ok = self.read_message(stream, thought_data)
        return Thought.from_snapshot(self._user, thought_data) if ok else None

    def next(self, stream):
        self.parse_user(stream)
        return self.parse_thought(stream)

