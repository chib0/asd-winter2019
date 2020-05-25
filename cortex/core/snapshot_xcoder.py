from json import loads, dumps

from cortex.utils.filesystem import MessageRecord
from cortex.utils.logging import log_exception, get_module_logger

logger = get_module_logger(__file__)


def snapshot_encoder(snapshot, **kwargs):
    with MessageRecord.create() as mr:
        mr.write(snapshot)
    to_encode = {k: v for k, v in kwargs.items()}
    to_encode['snapshot'] = mr.uri()
    return dumps(to_encode)


def snapshot_decoder(message_string):
    d = loads(message_string)
    with log_exception(logger, to_suppress=(FileNotFoundError,),
                       format=lambda x: f"Could not read MessageRecord: {x}"):
        with MessageRecord.open(d['snapshot']) as mr:
            d['snapshot'] = mr.read()
            return d

    return None

