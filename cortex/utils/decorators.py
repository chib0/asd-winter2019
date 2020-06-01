"""
just a cool meeting place for all sorts of decorators to hang
"""
from functools import wraps, lru_cache
from funcy import once_per_args, once


def cache_res(f=None, / , maxsize=None):
    """
    A simple decorator that simply caches the return value of a function, and returns it again and again.
    :param f: the function to decorate
    :return: lol
    """
    if f is None:
        return lambda func: cache_res(func, maxsize=maxsize)
    return lru_cache(maxsize=maxsize)(f)

