from . import  parser_decorators as decos
from core import cortex_pb2


@decos.with_protobuf_snapshot(cortex_pb2.Snapshot)
def parse_color_image(snapshot, rest):
    pass

@decos.with_protobuf_snapshot(cortex_pb2.Snapshot)
def parse_depth_image(snapshot, rest):
    pass

