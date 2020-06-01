import gzip
import pathlib

import urlpath

from .message_record import MessageRecord
from .. import images
file_ext_handlers = {'.gz': gzip.open,
                   }

def open_file(path, mode=None):
    uri = urlpath.URL(path)
    if not uri.scheme or uri.scheme == 'file://':
        path = pathlib.Path(uri.path)
    else:
        raise NotImplementedError("Cannot open non-local file")
    return file_ext_handlers.get(path.suffix, open)(str(path), mode) if mode else file_ext_handlers[path.suffix](str(path))
