from functools import wraps

def call_once(f):
    """
    enforces that a function is called once and only once.
    if the function/method were to return a value, it shall return None on all subsequent calls
    to avoid this, use a cache decorator.
    :param f: the decoratee
    """
    @wraps(f)
    def decorator(*args, **kwargs):
        if decorator.should_call:
            decorator.should_call = False
            return f(*args, **kwargs)

    decorator.should_call = True
    return decorator


def cache_res(f):
    """
    A simple decorator that simply caches the return value of a function, and returns it again and again.
    :param f: the function to decorate
    :return: lol
    """
    result, called = None, False
    @wraps(f)
    def decorator(*args, **kwargs):
        global result
        if not called:  # can't just check if result isn't none because it could be return value could be falsy, or None.
            result = f(*args, **kwargs)
        return result
    return decorator

