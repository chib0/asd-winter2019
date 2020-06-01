import abc
from pathlib import Path

from cortex import utils, configuration
from cortex.utils.decorators import cache_res
from cortex.utils import aop_gatherer

module_logger = utils.logging.get_module_logger(__name__)

class _BaseRepository(aop_gatherer.Repository, abc.ABC):
    def __init__(self, paths=(), module_name_filters=(), module_filters=(), prop_matchers=(), default_filters=True):
        super().__init__(paths, module_name_filters, module_filters, prop_matchers, default_filters=default_filters)
        self._attr_getter = f'get_{self.type}'

    @classmethod
    @cache_res
    def get_repo(cls, paths=()):
        paths = paths or configuration.get_config()[configuration.CONFIG_DISPATCHER_CONSUMER_DIR] or \
                [Path(__file__).parent]
        rep = cls(paths)
        rep.module_filter(lambda x: hasattr(x, rep._attr_getter) and callable(getattr(x, rep._attr_getter)))
        rep.module_name_filter(lambda x: x.name.endswith(f'_{rep.type}.py'))
        return rep

    @property
    @abc.abstractmethod
    def type(self):
        return None

    def _get(self, url, topic_or_handlers, *args, auto_start=True, **kwargs):
        self._logger.info(f"getting for {url}")
        with utils.logging.log_exception(module_logger,
                                         format="URL Scheme does not match any scheme"):
            for i in self.modules():
                self._logger.info(f"Testing {i} for {url}")
                candidate = getattr(i, self._attr_getter)(url, topic_or_handlers, *args, auto_start=auto_start, **kwargs)

                if candidate:
                    return candidate
            return None

    def _has(self, url):
        return self._get(url, [], auto_start=False) is not None


class DispatcherRepository(_BaseRepository):
    @property
    def type(self):
        return 'dispatcher'

    def get_dispatcher(self, url, topics, *args, auto_start=True, **kwargs):
        return self._get(url, topics, *args, auto_start=auto_start, **kwargs)

    def has_dispatcher(self, url):
        return self._has(url)


class ConsumerRepository(_BaseRepository):
    @property
    def type(self):
        return 'consumer'

    def get_consumer(self, url, handlers, *args, auto_start=True, **kwargs):
        return self._get(url, handlers, *args, auto_start=auto_start, **kwargs)

    def has_consumer(self, url):
        return self._has(url)

