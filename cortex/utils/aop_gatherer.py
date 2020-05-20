"""
This file contains everything related to introspective aspect oriented programming as shown in class.
I mainly chose this to learn, but having not been able to find stuff on google on how pytest searches for modules,
I decided to write a thing of my own that should be 'good enough'
"""

import os
import sys
import pathlib
from contextlib import contextmanager, suppress
import importlib
from itertools import chain
import re

from cortex.utils import logging, tweak_path, list_queue


def default_module_name_filter(path):
    return path.is_file() and path.suffix == '.py' and not path.name.startswith("_")


class ModuleGatherer:
    def __init__(self, module_name_filters=(default_module_name_filter,), module_filters=(), recursive=True):
        self._module_name_filters=module_name_filters
        self._module_fiters = module_filters
        self._recursive = recursive
        self._logger = logging.get_logger(self.__class__.__name__)

    def load_modules(self, root):
        """
        loads the modules in the given root.
        if no name_filter is given, *files* with a '.py' extension without a '_' suffix will be collected.
        this name filter is exposed as 'default_module_filter', add it when specifying custom filters
        :param root:
        :return: the lsit of modules
        """
        def load_from_dir(d):
            dir_loaded = list()
            for path in d.iterdir():
                if all(name_filter(path) for name_filter in self._module_name_filters):
                    module_name = f"{(str(d.relative_to(root)).replace(os.sep, '.') + '.' if root != d else '') }{path.stem}"
                    self._logger.debug(f"loading {module_name}")
                    try:
                        module = importlib.import_module(module_name, package=root.name)
                        if all(module_filter(module) for module_filter in self._module_name_filters):
                            dir_loaded.append(module)
                    except Exception as e:
                        self._logger.error(f"could not load {module_name} from {root}: {e}")
            return dir_loaded

        root = pathlib.Path(root).absolute()
        dirs = [root]
        all_loaded = []
        seen = set()
        with tweak_path(root,logger=self._logger), suppress(IndexError):
            for path in list_queue(dirs):
                all_loaded.append(load_from_dir(path))
                for item in path.iterdir():
                    if self._recursive and item.is_dir() and not item.resolve() in seen:
                        self._logger.debug(f"adding {item} as directory")
                        dirs.append(item)
                        seen.add(item.resolve())  # make sure we're not dumbed by links
        return all_loaded

    def get_properties(self, root, prop_matchers):
        """
        returns properties in modules located in root
        :param root: the location of all the modules
        :param prop_matchers: list of lambda (name, thing): predicate. if any returns true, the property will be returned
        :return: a list of properties from the loaded modules.
        """
        modules = self.load_modules(root)
        out = [getattr(module, prop) for module in modules for prop in dir(module)
               if any(prop_matcher(prop, getattr(module, prop)) for prop_matcher in prop_matchers)]
        return out

    def properties_by_name(self, roots, prop_names):
        """
        returns all properties in roots that match any of the names in the list/iterable
        :param roots: where to look at.
        :param prop_names: list of names to try and match
        :return: a list of properties
        """
        name_matcher = [lambda name, _: re.compile(f"({'|'.join(prop_names)})").match(name)]
        out = list(chain(self.get_properties(root, name_matcher) for root in roots))
        return out

    def properties_by_type(self, roots, types):
        """
        returns all properties in roots that are an instanceof the given types
        :param roots: where to look at.
        :param types: types to look for
        :return: a list of properties
        """
        name_matcher = [lambda _, t: isinstance(t, types)]
        out = list(chain(self.get_properties(root, name_matcher) for root in roots))
        return out

