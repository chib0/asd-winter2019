"""
This file contains everything related to introspective aspect oriented programming as shown in class.
I mainly chose this to learn, but having not been able to find stuff on google on how pytest searches for modules,
I decided to write a thing of my own that should be 'good enough'
"""

import os
import pathlib
from contextlib import suppress
import importlib
from itertools import chain
import re

import typing

from cortex.utils import logging, tweak_path, list_queue
from cortex.utils.decorators import cache_res


def default_module_name_filter(path):
    return path.is_file() and path.suffix == '.py' and not path.name.startswith("_")


class ModuleGatherer:
    def __init__(self, module_name_filters=(default_module_name_filter,), module_filters=(), recursive=True):
        self._module_name_filters=list(module_name_filters)
        self._module_fiters = list(module_filters)
        self._recursive = recursive
        self._logger = logging.get_logger(self.__class__.__name__)

    @staticmethod
    @cache_res
    def _load_from_dir(root, d, module_name_filters, module_filters, logger):
        """
        loads from a dir relative to the root.
        this is a staticmethod so we can cache the result according to the filters required.
        :param root: the root of the loading process
        :param d: the currnet path in the heirarch
        :param module_name_filters: filters to run on file names prior to loading
        :param module_filters: filters to run on loaded modules
        :param logger: the logger to use to log the process
        :return:
        """
        dir_loaded = list()
        for path in d.iterdir():
            if all(name_filter(path) for name_filter in module_name_filters):
                module_name = f"{(str(d.relative_to(root)).replace(os.sep, '.') + '.' if root != d else '')}{path.stem}"
                logger.debug(f"loading {module_name}")
                try:
                    module = importlib.import_module(module_name, package=root.name)
                    if all(module_filter(module) for module_filter in module_filters):
                        dir_loaded.append(module)
                except Exception as e:
                    logger.error(f"could not load {module_name} from {root}: {e}")

        return dir_loaded

    def load_modules(self, root, recursive=False):
        """
        loads the modules in the given root.
        if no name_filter is given, *files* with a '.py' extension without a '_' suffix will be collected.
        this name filter is exposed as 'default_module_filter', add it when specifying custom filters
        :param root:
        :return: the lsit of modules
        """
        recursive = recursive or self._recursive

        root = pathlib.Path(root).absolute()
        dirs = [root]
        all_loaded = []
        seen = set()
        with tweak_path(root,logger=self._logger), suppress(IndexError):
            for path in list_queue(dirs):
                #this is called with a tuple cause that is a hashable type
                all_loaded.extend(self._load_from_dir(root,
                                                      path,
                                                      tuple(self.module_name_filters),
                                                      tuple(self.module_filters),
                                                      self._logger))
                for item in path.iterdir():
                    if recursive and item.is_dir() and not item.resolve() in seen:
                        self._logger.debug(f"adding {item} as directory")
                        dirs.append(item)
                        seen.add(item.resolve())  # make sure we're not dumbed by links
        return all_loaded

#TODO: remove properties, they are handled in the repository.
    @cache_res
    def get_properties(self, root, prop_matchers, recursive=False):
        """
        returns properties in modules located in root
        :param root: the location of all the modules
        :param prop_matchers: list of lambda (name, property): predicate. if any returns true, the property will be returned
        :return: a list of properties from the loaded modules.
        """
        modules = self.load_modules(root, recursive=recursive)
        out = [getattr(module, prop) for module in modules for prop in dir(module)
               if any(prop_matcher(prop, getattr(module, prop)) for prop_matcher in prop_matchers)]
        return out

    def properties_by_name(self, roots, prop_names, recursive=False):
        """
        returns all properties in roots that match any of the names in the list/iterable
        :param roots: where to look at.
        :param prop_names: list of names to try and match
        :return: a list of properties
        """
        name_matcher = [lambda name, _: re.compile(f"({'|'.join(prop_names)})").match(name)]
        out = list(chain(self.get_properties(root, name_matcher, recursive=recursive) for root in roots))
        return out

    def properties_by_type(self, roots, types, recursive=False):
        """
        returns all properties in roots that are an instanceof the given types
        :param roots: where to look at.
        :param types: types to look for
        :return: a list of properties
        """
        name_matcher = [lambda _, t: isinstance(t, types)]
        out = list(chain(self.get_properties(root, name_matcher, recursive=recursive) for root in roots))
        return out

    @property
    def module_filters(self):
        return self._module_fiters

    @property
    def module_name_filters(self):
        return self._module_name_filters

# TODO: make repository work with several module gatherers instead of one per multiple paths
class Repository:
    def __init__(self, paths=(), module_name_filters=(), module_filters=(), prop_matchers=(), default_filters=True):
        self.paths = list(paths)
        self.gatherer = ModuleGatherer(module_name_filters, module_filters)
        self.prop_matchers = list(prop_matchers)
        self._generation = 0
        self._logger = logging.get_instance_logger(self)
        if default_filters:
            self._add_default_filters()

    def _add_default_filters(self):
        self.gatherer.module_name_filters.append(default_module_name_filter)

    def add_prop_matcher(self, f):
        """
        adds a property matcher to the list
        :param f: lambda name, property_value ->bool
        :return: f
       """
        self.prop_matchers.append(f)
        self._generation += 1
        return f

    def prop_name_matches(self, regex):
        if not isinstance(regex, (str, bytes, typing.Pattern)):
            raise TypeError("regex must be string or pattern")
        r = re.compile(regex) if  isinstance(regex, (str, bytes)) else regex
        self.add_prop_matcher(lambda name, prop: r.match(name))


    def prop_name_matcher(self,f):
        """
         registers a matcher that takes only the name of a property
        :param f: lambda name -> Bool
        :return: f
        """
        self.add_prop_matcher(lambda name, prop: f(name))
        return f

    def prop_value_matcher(self, f):
        """
        registers a matcher that takes only the property
        :param f: lambda something->bool
        :return: f
        """
        self.add_prop_matcher(lambda name, prop: f(prop))
        return f

    def module_name_filter(self, f):
        """
        registers a filter that takes a name per every possible module
        :param f: lambda name -> bool
        :return: f
        """
        self.gatherer.module_name_filters.append(f)
        self._generation += 1
        return f

    def module_filter(self, f):
        """
        registers a filter that takes a module_instance per every possible module\
        a module is kept iff all filters return true
        :param f: lambda name -> bool
        :return: f
        """
        self.gatherer.module_filters.append(f)
        self._generation += 1
        return f

    def modules(self, recursive=False):
        return chain(*(self.gatherer.load_modules(path, recursive=recursive) for path in self.paths))

    @cache_res(maxsize=32)
    def _ensure_properties(self, recursive, generation):
        """
        returns the currently lo
        :param recursive:
        :param generation: this argument makes sure that the lru cache loads correctly it changes when the matchers change.
        :return:
        """
        out = []
        for module in self.modules(recursive=recursive):
            self._logger.info(f'looking at module: {module}')
            out.extend(getattr(module, prop) for prop in dir(module)
                        if any(prop_matcher(prop, getattr(module, prop)) for prop_matcher in self.prop_matchers))
        return out

    def properties(self, recursive=False):
        return self._ensure_properties(recursive, self._generation)

    def prop_name_starts_with(self, param):
        self.prop_name_matches(f"^{param}.*")

    def prop_name_ends_with(self, param):
        self.prop_name_matches(f".*{param}$")
        