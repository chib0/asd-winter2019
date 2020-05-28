"""
The server frame is the framework for creating different types of servers.
different types of servers allow the usage of different client listeners, as well as different publishers.
"""

class ThoughtServer:
    def __init__(self, listener, publisher):
        """
        :param listener: this listens to new connections and defers them to a handler.
        :param publisher: this takes the received message and defers it to various parsers.
        """
        self.listener = listener
        self.publisher = publisher
