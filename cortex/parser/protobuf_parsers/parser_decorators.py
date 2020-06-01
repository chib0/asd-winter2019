import functools


def with_protobuf_snapshot(pb_type, snapshot_key=None, user_key=None, user_type=int):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(data, *args, **kwargs):
            container = pb_type()
            pb_type.ParseFromString(container, data[snapshot_key or 'snapshot'])
            user = user_type(data[user_key or 'user'])
            return f(user, container, data, *args, **kwargs)
        return wrapper
    return decorator

def with_target(f=None, /, target=None):
    if f is None:
        return lambda x: with_target(x, target=target)
    f.target=target
    return f


def with_user(f=None, /, type=None):
    if not callable(f):
        return lambda x: with_user(x, type=f)
    @functools.wraps(f)
    def deco(data, *args, **kwargs):
        return f(type(data['user']) if type else data['user'], data, *args, **kwargs)
    return deco
