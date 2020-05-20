from socket import socket
import struct

class BrokenConnectionError(Exception):
    pass


class Connection:
    # I decided to implement the object itself as a context manager instead of using @contextlib.contextmanager.
    # This decision comes from the idea that the functoinality is the same but this way, a user may still call the 
    # constructor directly and be able to enjoy context management.
    @classmethod
    def connect(cls, addr, port):
        """opens a connection to the target and and returns it"""
        s = socket() # the object itself handles closing the socket.
        s.connect((addr, port))
        return cls(s)

    def __init__(self, sock):
        self._sock = sock

    def __repr__(self):
        peer = self._sock.getpeername()
        me = self._sock.getsockname()
        return f'<{self.__class__.__name__} from {me[0]}:{me[1]} to {peer[0]}:{peer[1]}>'

    def send(self, *data_parts):
        """
        sends all data passed.
        all parts should be convertible to bytes.
        :param *data_parts a list of byte strings to send
        :return the amount of bytes sent
        """
        return self._sock.sendall(b"".join(data_parts) if len(data_parts) > 1 else data_parts[0])

    def receive(self, size):
        """
        receives the exact amount of bytes required.
        :param size: # of bytes to wait for
        :return: the byte string received.
        """
        parts = []
        while size:
            recved = self._sock.recv(size)
            if not recved:
                raise BrokenConnectionError("Broken socket~!")
            size -= len(recved)
            parts.append(recved)
        return b''.join(parts)

    def close(self):
        """ closes underlying socket """
        self._sock.close()

    def __enter__(self):
        return self

    def __exit__(self, *exception_data):
        self.close()

class ProtobufConnection(Connection):
    """
    Wraps the original Connection functionality with the ability to send and receive messages encoded with protobuf
    """
    MessageHeaderFormat = struct.Struct("I")
    def send(self, message):
        """
        This is an overload.
        sends a protobuf message in its entirety. on error, acts like Connection.send
        :param message: any protobuf message compliant objects
        :return # of bytes sent
        """
        buffer = message.SerialzeToString()
        return super().send(self.MessageHeaderFormat.pack(len(buffer)), buffer)

    def receive(self, message_type):
        """
        This is an overload.
        receives an entire protobuf message
        :param message_type: the protobuf message to construct from the received data
        :return: a constructed protobuf message
        """
        mlength = self.MessageHeaderFormat.unpack(super().receive(self.MessageHeaderFormat.size))
        return message_type.FromString(super().receive(mlength))

