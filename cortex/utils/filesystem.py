import pathlib
import urlpath
from contextlib import suppress
from datetime import datetime

from cortex import configuration
from cortex.utils import logging
module_logger = logging.get_module_logger(__file__)
class MessageRecord:

    @classmethod
    def create(cls):
        repo = pathlib.Path(configuration.get_config()[configuration.CONFIG_RAW_MESSAGE_REPO])
        repo.mkdir(parents=True, exist_ok=True)
        path = repo / str(f"snapshot_{datetime.now():%b-%d-%Y_%H:%M:%S_%f}")
        module_logger.info(f"creating {path}")
        return cls(path.open('wb'), path)

    @classmethod
    def open(cls, path, mode='rb'):
        path = pathlib.Path(urlpath.URL(path).path)
        return cls(path.open(mode), path)

    def __init__(self, fd, path=None):
        self.handle = fd
        self._path = path

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def write(self, data):
        return self.handle.write(data)

    def read(self, size=None):
        if not size:
            return self.handle.read()
        return self.handle.read(size)

    def uri(self):
        return str(urlpath.URL().with_scheme(f"file://").with_netloc(str(self.path)))

    @property
    def path(self):
        with suppress():
            return self.handle.name
        return self._path

    def close(self):
        self.handle.close()
