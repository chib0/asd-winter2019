import os
import pathlib
import socket
import datetime
import threading
from cortex.utils import Listener
from .thought import Thought


class ThoughtServer:
    Coders = tuple()
    @classmethod
    def open(cls, port, db, addr='0.0.0.0'):
        listener = Listener(port, addr)
        listener.start()
        return cls(listener, cls.Coders, db)

    def __init__(self, listener, coders, db):
        self.coders = coders
        self.listener = listener
        self.db = db 



class ClientHandler(threading.Thread):
    UserLocksLock = threading.Lock()
    UserLocks = {}
    def __init__(self,  connection, data_dir):
        threading.Thread.__init__(self)
        self._connection= connection
        self._out_dir = data_dir
        self.result = None

    def run(self):
        uid, timestamp, payload_len = recv_format(self._sock, _HEADER_FORMAT)
        thought = recv_all(self._sock, payload_len)
        self._ensure_user_lock(uid)
        self._write_data(uid, datetime.datetime.fromtimestamp(timestamp), thought.decode())

    def _ensure_user_lock(self, uid):
        """
        ensure we have a lock for the user id
        :param uid: the uid
        """

        # To be able to avoid write collisions to the file from 2 concurrent user sessions, we can do one of 2 things:
        # first: keep a lock for every user that logs in (which we do), which we can discard after all user_id sessions end (although we dont)
        # second: keep a queue to which the handler would pour new messages,
        #   synchronize the enqueue operations, and have another thread write to files synchronously.
        # I chose the lock version because it seems like the general case is that many different users log in at the same time
        # thus having only one thread write to one file at a time didn't sound right.
        self.UserLocksLock.acquire()
        if uid not in self.UserLocks:
            self.UserLocks[uid] = threading.Lock()
        self.UserLocksLock.release()

    def _write_data(self, uid, timestamp, payload):
        dir_path = pathlib.Path(self._out_dir).absolute() / str(uid)
        if not dir_path.exists():
            dir_path.mkdir()
        file_path = dir_path / f'{timestamp:%Y-%m-%d_%H-%M-%S}.txt'
        out_text = ("\n" if file_path.exists() else "") + payload
        file_path.touch()
        #  not locking on a specific file because I couldn't figure out a simple enough data structure to hold the locks
        #  and it seemed like locking per user is just the same as per file, because they only access the same file
        #  if there are 2 concurrent sessions.
        self.UserLocks[uid].acquire()
        with open(str(file_path), "a") as f:
            f.write(out_text)
        self.UserLocks[uid].release()


def create_server_socket(address):
    s = socket.socket()
    s.bind(tuple(address))
    s.listen(1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return s

def run_server(address, data_path):
    """ 
    Starts a server gathering thoughts storing them in `data_path` to the addresses specified by `address`
    @param address - a socket bind tuple
    @para data_path - path to the thought storage
    @returns nothing
    """
    
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    with create_server_socket(address) as s:
        while True:
            client, origin = s.accept()
            handler = ClientHandler(client, data_path)
            handler.start()
            # I'd like to detach the threads but the .detach function isn't there anymore :(
            # I'm not joining the threads in the end because if a thread is blocking, it'll block the ctrl+c

