from socket import socket

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

    def send(self, data):
        return self._sock.sendall(data)

    def receive(self, size):
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
