from socket import socket
import datetime
from .thought import Thought
from aytabu.utils import Connection

_HEADER_FORMAT = "<QQI"

def upload_thought(address, user, thought, timestamp=None):
    message = Thought(user, timestamp or datetime.datetime.now(), thought)
    s = socket()
    s.connect(tuple(address))
    con = Connection(s)
    s.send(thought.serialize())
    con.close()
