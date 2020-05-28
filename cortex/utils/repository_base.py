
import re
from pathlib import Path
import abc
from cortex import configuration
from cortex.utils import aop_gatherer
from cortex.utils.decorators import cache_res
from cortex.utils.logging import log_exception


class HandlerRecord(abc.ABC):
    FirstCamelSub = re.compile('(.)([A-Z][a-z]+)')
    SecondCamelSub = re.compile('([a-z0-9])([A-Z])')
    def __init__(self, prop):
        self.handler = prop

    @staticmethod
    def _toplevel_prop_name(prop):
        return  prop.__name__.rsplit('.', 1)[-1]

    @classmethod
    def _camel_to_snake(cls, prop):
        #from https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
        name = cls.FirstCamelSub.sub(r'\1_\2', prop)
        return cls.SecondCamelSub.sub(r'\1_\2', name).lower()

    @abc.abstractmethod
    def format_target_name(self):
        raise NotImplementedError()

    @property
    @cache_res
    def target(self):
        if hasattr(self.handler, 'target'):
            return self.handler.target
        return self.format_target_name()

    def __str__(self):
        return f"{self.__class__.__name__} for {self.target}"

    def __repr__(self):
        return f"<{self.__class__.__name__} for {self.target} using {self.handler} >"


class RepositoryBase(aop_gatherer.Repository, abc.ABC):
    class __GetChecker: pass

    def __init__(self, through_get_checker, *args, **kwargs):
        """
        do not call directly. use 'get'
        :param args:
        :param kwargs:
        """
        if not isinstance(through_get_checker, self.__GetChecker):
            raise RuntimeError(f"{__class__} instantiated directly. use 'get' instead")
        super().__init__(*args, **kwargs)


    @property
    @abc.abstractmethod
    def record_maker(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def specialize_props(self):
        """
        This has to be implemented in order for the Repository to know what to import.
        This hook is called as part of the Repository.get function.
        :return:
        """
        raise NotImplementedError()

    @classmethod
    @cache_res
    def _class_file(cls):
        import sys
        return Path(sys.modules[cls.__module__].__file__).parent

    @classmethod
    def get(cls, paths=()):
        repository = cls(cls.__GetChecker(), paths=paths or configuration.get_config()[configuration.CONFIG_PARSER_DIR]
                         or [cls._class_file()])
        repository.specialize_props()
        return repository

    def handlers(self):
        """
        returns a new list of the parsers that the repository knows of
        :return:
        """
        return [self.record_maker(i) for i in self.properties()]

    def get_handler(self, target):
        """
        returns a single parser whose target matches the request
        """
        with log_exception(self._logger, to_suppress=(IndexError, ), format=f"No hadnler for target {target}"):
            target_parsers = ( [i for i in self.handlers() if i.target == target])
            out = target_parsers.pop(0)
            self._logger.debug(f"got handler {out} for {target}")
            return out


