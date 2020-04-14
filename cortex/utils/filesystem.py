import pathlib
from contextlib import suppress
from datetime import datetime

from utils import configuration


class MessageRecord:
    @classmethod
    def create(cls):
        path = pathlib.Path(configuration.get_config()[configuration.RAW_MESSAGE_REPO]) / f'snapshot_{datetime.now()}'
        return cls(open(path, 'wb'))

    @classmethod
    def open(cls, path, mode='rb'):
        return cls(open(path, mode))

    def __init__(self, fd, path=None):
        self.handle = fd

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def write(self, data):
        return self.handle.write(data)

    def read(self, size=None):
        return self.read(size)

    def uri(self):
        return f"file://{self.path}"

    @property
    def path(self):
        with suppress():
            return self.handle.name

    def close(self):
        self.handle.close()