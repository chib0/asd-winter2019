import pathlib
import contextlib
import sys
# from .connection import ProtobufConnection, Connection, BrokenConnectionError
# from .listener import Listener
# from . import configuration
# from . import decorators
# from . import dispatchers
from . import logging


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


@contextlib.contextmanager
def tweak_path(which, where=0, logger=None):  #TODO: mock the logger with something empty
    """
    inserts the given path/s to the required index in the system path, then removes it when exiting.
    :param which: paths to add. string or list.
    :param where: index to insert into in the list
    :return: nothing
    """
    old = sys.path
    new = list(sys.path)

    if isinstance(which, (pathlib.Path, str, bytes)):
        new.insert(where, str(which))
    else:
        new[where:where] = which
    if logger: logger.debug(f"adding {which} to path")
    sys.path = new
    yield
    if logger: logger.debug("restoring path")
    sys.path = old

def list_queue(_list):
    """
    allows iteration over a list, while also adding/removing elements during iteration.
    :param _list: list to iter over. must support the 'pop(index)' method
    :return: an element
    """
    while _list:
        yield _list.pop(0)