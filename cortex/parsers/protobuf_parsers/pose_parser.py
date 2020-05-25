from google.protobuf.json_format  import MessageToDict
from cortex.core import cortex_pb2
from . import  parser_decorators as decos


@decos.with_protobuf_snapshot(cortex_pb2.Snapshot)
def parse_pose(snapshot, rest):
    out = {'user': rest['user'], 'timestamp': snapshot.datetime, 'result': MessageToDict(snapshot.pose)}
    return out

