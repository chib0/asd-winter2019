from .connection import Connection
import socket

class Listener:
    """
    Represents a listening socket
    """
    def __init__(self, port, host='0.0.0.0', backlog=1000, reuseaddr=True):
        self._port = port
        self._host = host
        self.backlog = backlog
        self.reuseaddr = reuseaddr
        self._server = None
        #socket not created here because best-practices don't instantiate anything in ctor

    @property
    def port(self):
        """ the port we're listening on """
        if self._server:  # this means the server was created
            _, port = self._server.getsockname()
            return port
        return self._port

    @property
    def host(self):
        """ the ips we're listening for """
        if self._server:  # this means the server was created
            host, _ = self._server.getsockname()
            return host
        return self._host


    def _make_server(self):
        consock = socket.socket()
        if self.reuseaddr:
            consock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        consock.bind((self._host, self._port))
        consock.listen(self.backlog)
        return consock

    def __repr__(self):
        return f'{self.__class__.__name__}(port={self.port!r}, host={self.host!r}, backlog={self.backlog!r}, reuseaddr={self.reuseaddr!r})'

    def start(self):
        """
        creates the socket and starts listening.

        """
        self._server = self._make_server()

    def stop(self):
        """
        closes the socket
        :return:
        """
        if self._server:
            self._server.close()
        self._server = None

    def accept(self):
        """
        returns a new connection to a client
        :return: a socket
        """
        client, info = self._server.accept()
        return Connection(client)

    def __enter__(self):
        """ starts the listener """
        self.start()
        return self

    def __exit__(self, *exc_info):
        """ stops the listener """
        self.stop()

    @classmethod
    def Listen(cls, port):
        """
        use with a `with` statement to start listening on a port
        """
        return cls(port)
