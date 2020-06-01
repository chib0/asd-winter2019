"""
implements a simple interface for getting a file opened for a specific user
"""
from __future__ import annotations
from pathlib import Path
import datetime
from urlpath import URL

from cortex import configuration
from cortex.utils.filesystem import open_file
from cortex.utils.decorators import cache_res


class UserStorage:
    @classmethod
    def get_for(cls, user):
        """
        opens the storage of a specific user
        :param user:
        :return:
        """
        return cls(configuration.get_config()[configuration.CONFIG_USER_STORAGE_BASE], user)

    def __init__(self, base, user):
        self.base = Path(base)
        self.user = user

    def generate_file_uri_with_suffix(self, data_type: (str, URL, Path), suffix):
        """creates a new file with the given suffix"""
        return self.generate_file_uri(data_type, f'{datetime.datetime.now():%b-%d-%Y_%H:%M:%S_%f}{suffix}')

    def generate_file_uri(self, data_type: (str, URL, Path), file_name):
        """
        creates a uri for the filename of a certain data-type in the storage, does not create the file itself
        :param data_type:
        :param file_name:
        :return:
        """
        if not file_name:
            raise ValueError(" filename must exist ")
        return self.uri_for(data_type) / file_name

    def uri_for(self, data_type : (str, URL, Path)):
        """
        creates a uri for a specific datatype of file (i.e color_image)
        :param data_type:
        :return:
        """
        return self.get_base_uri() / data_type

    @cache_res
    def get_base_uri(self):
        """
        returns the base url for the user
        :return:
        """
        return URL(str(self.base / str(self.user))).with_scheme('file')

    @classmethod
    def open(cls, uri, mode='r'):
        """
        opens a file from the uri, with the mode
        :param uri:
        :param mode:
        :return:
        """
        uri = URL(uri)
        if not uri.scheme == 'file':
            raise ValueError(f"uri type {uri} not supported")
        return open_file(uri.path, mode)

    def create(self, uri, mode):
        """
        creates the file at the uri, regardless of the user or if it is out of bounds.
        :param uri:
        :param mode:
        :return:
        """
        if not uri.scheme == 'file':
            raise ValueError(f"uri type {uri.scheme} not supported")
        Path(uri.path).absolute().parent.mkdir(parents=True, exist_ok=True)
        return self.open(uri, mode)

