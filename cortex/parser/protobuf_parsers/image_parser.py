
from . import  parser_decorators as decos
from cortex.core import cortex_pb2
from cortex.utils import images, user_storage



@decos.with_protobuf_snapshot(cortex_pb2.Snapshot,
                              user_key='user',
                              user_type=int)
def parse_color_image(user, snapshot, rest):
    ci = snapshot.color_image
    im = images.ColorImage.from_bytes(ci.width, ci.height, ci.data)
    store = user_storage.UserStorage.get_for(user)
    uri = store.generate_file_uri_with_suffix('color_image', '.png')
    im.save(store.create(uri, 'wb'))
    return {'user': user, 'timestamp': snapshot.datetime, 'result': {'color_image' : str(uri)}}


@decos.with_protobuf_snapshot(cortex_pb2.Snapshot,
                              user_key='user',
                              user_type=int)
def parse_depth_image(user, snapshot, rest):
    di = snapshot.depth_image
    im = images.DepthImage.from_bytes(di.width, di.height, list(di.data))
    store = user_storage.UserStorage.get_for(user)
    uri = store.generate_file_uri_with_suffix('depth_image', '.depth')
    im.save(store.create(uri, 'wb'))
    return {'user': user, 'timestamp': snapshot.datetime, 'result': {'depth_image' : str(uri)}}


