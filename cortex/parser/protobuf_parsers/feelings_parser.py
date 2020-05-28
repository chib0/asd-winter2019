from google.protobuf.json_format import MessageToDict

from cortex.core import cortex_pb2
from . import  parser_decorators as decos


@decos.with_protobuf_snapshot(cortex_pb2.Snapshot)
@decos.with_user(type=int)
def parse_feelings(user, snapshot, rest):
    out = {'user': user, 'timestamp': snapshot.datetime,
           'result': {'feelings': MessageToDict(snapshot.feelings)}}
    return out
