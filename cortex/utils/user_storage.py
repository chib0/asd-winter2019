from __future__ import annotations
from pathlib import Path
import datetime
from urlpath import URL

from cortex import configuration
from cortex.utils.decorators import cache_res


class UserStorage:
    @classmethod
    def get_for(cls, user):
        return cls(configuration.get_config()[configuration.CONFIG_USER_STORAGE_BASE], user)

    def __init__(self, base, user):
        self.base = Path(base)
        self.user = user

    def generate_file_uri_with_suffix(self, data_type: (str, URL, Path), suffix):
        return self.generate_file_uri(data_type, f'{datetime.datetime.now():%b-%d-%Y_%H:%M:%S_%f}{suffix}')

    def generate_file_uri(self, data_type: (str, URL, Path), file_name):
        if not file_name:
            raise ValueError(" filename must exist ")
        return self.uri_for(data_type) / file_name

    def uri_for(self, data_type : (str, URL, Path)):
        return self.get_base_uri() / data_type

    @cache_res
    def get_base_uri(self):
        return URL(str(self.base / str(self.user))).with_scheme('file')

    def open(self, uri, mode='r'):
        if not uri.scheme == 'file':
            raise ValueError(f"uri type {uri.scheme} not supported")
        print(uri.path)
        return open(uri.path, mode)

    def create(self, uri, mode):
        if not uri.scheme == 'file':
            raise ValueError(f"uri type {uri.scheme} not supported")
        Path(uri.path).absolute().parent.mkdir(parents=True, exist_ok=True)
        return self.open(uri, mode)

