from pathlib import Path
from cortex import utils
from cortex.utils.decorators import cache_res
from cortex.utils import aop_gatherer

module_logger = utils.logging.get_module_logger(__name__)
def _get_modules_with_gatherer( gatherer, paths=()):
    all_modules = []
    paths = map(Path, paths) or (Path(__file__).parent,)
    for p in paths:
        all_modules.append(gatherer.load_modules(p))

    return all_modules


@cache_res
def gather_dispatchers(paths=()):
    mod_gatherer = aop_gatherer.ModuleGatherer(module_name_filters=[lambda x: x.endswith('_dispatcher.py')],
                                               module_filters= [lambda x: 'get_dispatcher' in x
                                                          and callable(x.get_dispatcher)],
                                               recursive=False)

    return _get_modules_with_gatherer(mod_gatherer, paths)

@cache_res
def gather_consumers(paths=()):
    mod_gatherer = aop_gatherer.ModuleGatherer(module_name_filters=[lambda x: x.endswith('_consumer.py')],
                                               module_filters=[lambda x: 'get_consumer' in x
                                                                         and callable(x.get_dispatcher)],
                                               recursive=False)
    return _get_modules_with_gatherer(mod_gatherer, paths)


def get_dispatcher(url, topics, *args, **kwargs):
    with utils.logging.log_exception(module_logger,
                                     format="URL Scheme does not match any scheme"):
        for i in gather_dispatchers():
            candidate = i.get_dispatcher(url, topics, *args, **kwargs)
            if candidate:
                return candidate
        return None

def get_consumer(url, handlers, *args, **kwargs):
    with utils.logging.log_exception(module_logger,
                                     format="URL Scheme does not match any scheme"):
        for i in gather_consumers():
            candidate = i.get_dispatcher(url, handlers, *args, **kwargs)
            if candidate:
                return candidate
        return None
