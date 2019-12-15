from socket import socket
from struct import pack
import datetime
import sys
from .thought import Thought
from .utils import Connection
from .cli import CommandLineInterface

_HEADER_FORMAT = "<QQI"

cli = CommandLineInterface()

@cli.command
def upload(address, user, thought):
    message = Thought(user, datetime.datetime.now(), thought)
    # print(f"sending: {message}")
    s = socket()
    s.connect(tuple(address))
    con = Connection(s)
    s.send(thought.serialize())
    con.close()


def main():
    return cli.main()

if __name__ == '__main__':
    sys.exit(main())
