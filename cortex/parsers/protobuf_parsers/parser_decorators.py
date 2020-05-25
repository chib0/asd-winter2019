import functools


def with_protobuf_snapshot(pb_type, snapshot_key=None):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(data, *args, **kwargs):
            container = pb_type()
            pb_type.ParseFromString(container, data[snapshot_key or 'snapshot'])
            return f(container, data)
        return wrapper
    return decorator

def parser_target(f=None, /, target=None):
    if f is None:
        return lambda x: parser_target(x, target=target)
    f.target=target
    return f