import logging

from google.protobuf.json_format  import MessageToDict
from cortex.core import cortex_pb2
from . import  parser_decorators as decos


@decos.with_protobuf_snapshot(cortex_pb2.Snapshot,
                              user_key='user',
                              user_type=int)
def parse_pose(user,
               snapshot, rest):
    out = {'user': user, 'timestamp': snapshot.datetime, 'result': {'pose': MessageToDict(snapshot.pose)}}
    return out

