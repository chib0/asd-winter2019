from .connection import ProtobufConnection, Connection, BrokenConnectionError
from .listener import Listener

from functools import wraps
def call_once(f):
    """
    enforces that a function is called once and only once.
    if the function/method were to return a value, it shall return None on all subsequent calls
    to avoid this, use a cache decorator.
    :param f: the decoratee
    """
    @wraps(f)
    def decorator(*args, **kwargs):
        return f(*args, **kwargs) if decorator.should_call else None

    decorator.should_call = True
    return decorator

def read_all(stream, size):
    message_parts = []
    while size:
        part = stream.read(size)
        size -= len(part)
        message_parts.append(part)
    return b''.join(message_parts)
