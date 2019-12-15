from connection import Connection
import socket

class Listener:
    def __init__(self, port, host='0.0.0.0', backlog=1000, reuseaddr=True):
        self._port = port
        self._host = host
        self.backlog = backlog
        self.reuseaddr = reuseaddr
        self._server = None
        #socket not created here because best-practices don't instantiate anything in ctor

    @property
    def port(self):
        if self._server:  # this means the server was created
            _, port = self._server.getsockname()
            return port
        return self._port

    @property
    def host(self):
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
        :return:
        """
        self._server = self._make_server()

    def stop(self):
        if self._server:
            self._server.close()
        self._server = None

    def accept(self):
        client, info = self._server.accept()
        return Connection(client)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc_info):
        self.stop()

    @classmethod
    def Listen(cls, port):
        return cls(port)
