from . import logging
from .connection import ProtobufConnection, Connection, BrokenConnectionError
from .listener import Listener
from . import configuration
from . import decorators


def read_all(stream, size):
    message_parts = []
    while size:
        part = stream.read(size)
        size -= len(part)
        message_parts.append(part)
    return b''.join(message_parts)


def netloc_to_host_port(netloc):
    host, port = netloc.split(":")
    port = int(port) if port else None

    return host, port