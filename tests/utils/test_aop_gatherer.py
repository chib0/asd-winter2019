import re
import sys
from unittest.mock import MagicMock

import pytest
from pathlib import Path
from types import ModuleType, SimpleNamespace

from cortex.utils import aop_gatherer


@pytest.fixture(scope='session')
def file_properties():
    return dict(properties=('test_thing1', 'ThingTester'), file_content="""
def test_thing1(): 
    pass
    
class ThingTester: 
    pass
    
def _inner_test_thing():
    pass
    
test_stuff = 1
""")

@pytest.fixture(scope='session')
def special_module_matcher_filename():
    return 'abcdefg.py'

@pytest.fixture(scope='session')
def dir_prop_list(special_module_matcher_filename, file_properties):
    return {
        Path('test_file_1.py'): file_properties,
        Path('test_file_2.py'): dict(properties=(), file_content=""),
        Path(special_module_matcher_filename): dict(properties=(), file_content=""),
        Path('recursion/test_recursion.py'): file_properties,
        Path('recursion/test_empty_recursion.py'): dict(properties=(), file_content=""),
        Path('recursion/more_recursion/test_recursion.py'): file_properties,
        Path('recursion/more_recursion/test_empty_recursion.py'): dict(properties=(), file_content=""),
    }

@pytest.fixture(scope='session')
def dir_prop_list_with_privates(dir_prop_list):
    out = dict(dir_prop_list)
    out[Path('_private.py')] = dict(properties=(), file_content='')
    out[Path('recursion/_private.py')] = dict(properties=(), file_content='')
    out[Path('recursion/more_recursion/_private.py')] = dict(properties=(), file_content='')
    return out

def _make_dirs_for(path, tmpdir_factory):
    for p in list(path.parents)[::-1]:
        if not p.exists():
            tmpdir_factory.mktemp(str(p))

def _make_dir_with_dir_properties(tmpdir_factory, dir_prop_list):
    d = tmpdir_factory.mktemp('dir')
    for path, record in dir_prop_list.items():
        f = d.join(str(path))
        f.write(record['file_content'], ensure=True)
    return d

def _reset_sys_modules(rel_paths_to_remove):
    mod_names = [str(i).replace("/", ".").replace(".py", "") for i in rel_paths_to_remove]

    for n, mod in list(sys.modules.items()):  # avoid changing while iterating
        if n in mod_names:
            del sys.modules[n]


@pytest.fixture(scope='session')
def load_dir(tmpdir_factory, dir_prop_list):
    return _make_dir_with_dir_properties(tmpdir_factory, dir_prop_list)

@pytest.fixture(scope='session')
def load_dir_with_privates(tmpdir_factory, dir_prop_list_with_privates):
    return _make_dir_with_dir_properties(tmpdir_factory, dir_prop_list_with_privates)

def test_module_loader_loads_everything_on_empty_filters_no_recursion(load_dir, dir_prop_list):
    mg = aop_gatherer.ModuleGatherer(recursive=False)
    all_paths = [load_dir.join(k) for k in dir_prop_list.keys()]
    required_paths = [str(i) for i in all_paths if i.dirname == load_dir.realpath()]
    modules = mg.load_modules(str(load_dir))
    module_files = [m.__file__ for m in modules]
    assert sorted(required_paths) == sorted(module_files)

def test_module_loader_loads_everything_on_empty_filters_with_recursion(load_dir, dir_prop_list):
    mg = aop_gatherer.ModuleGatherer(recursive=True)
    required_paths = [str(load_dir.join(k)) for k in dir_prop_list.keys()]
    modules = mg.load_modules(str(load_dir))
    module_files = [m.__file__ for m in modules]
    assert sorted(required_paths) == sorted(module_files)


def test_module_loader_loads_according_to_name_filter(load_dir, dir_prop_list, special_module_matcher_filename):
    mg = aop_gatherer.ModuleGatherer((lambda x: x.name == special_module_matcher_filename,), recursive=True)
    a = mg.load_modules(str(load_dir))
    assert [i.__file__ for i in a] == [load_dir.join(special_module_matcher_filename).realpath()]


def test_module_loader_loads_according_to_all_module_filters(load_dir, dir_prop_list, file_properties):
    mg = aop_gatherer.ModuleGatherer(module_filters=tuple(lambda m: hasattr(m, i) for i in file_properties['properties']),
        recursive=True)
    required_paths = [str(load_dir.join(p)) for p, props in dir_prop_list.items() if props == file_properties]

    assert sorted(required_paths) == sorted(m.__file__ for m in mg.load_modules(str(load_dir)))


def test_module_loader_default_does_not_load_privates(load_dir_with_privates, dir_prop_list_with_privates):
    #TODO: this consistently fails when run in a group, consistently works when running on its own.
    #       This seems to be caused by the tests running in the same environemnt.
    #       The directory creation creates a new tempdir for load_dir_with_privates, but most imported libs have the
    #       same name, therefore exist in sys.modules and are therefore brought from the old files.
    _reset_sys_modules(dir_prop_list_with_privates.keys())
    mg = aop_gatherer.ModuleGatherer(recursive=True)
    required_paths = [str(load_dir_with_privates.join(k)) for k in dir_prop_list_with_privates.keys()
                      if 'private' not in str(k)]
    modules = mg.load_modules(str(load_dir_with_privates))

    module_files = [m.__file__ for m in modules]
    assert sorted(required_paths) == sorted(module_files)


def test_repository_property_matcher_decorator_adds_to_list():
    rep = aop_gatherer.Repository()
    @rep.add_prop_matcher
    def matcher(x, y):
        pass
    assert matcher in rep.prop_matchers #  this is the only one that could work this way


def test_repository_module_name_filter_decorator_adds_to_gatherer():
    rep = aop_gatherer.Repository()
    @rep.module_name_filter
    def thing(y):
        pass
    assert thing in rep.gatherer.module_name_filters


def test_repository_module_filter_decorator_adds_to_gatherer():
    rep = aop_gatherer.Repository()
    @rep.module_filter
    def thing(y):
        pass
    assert thing in rep.gatherer.module_filters


def test_repository_property_name_matcher_decorator_adds_to_list():
    rep = aop_gatherer.Repository()
    m = MagicMock()
    rep.prop_name_matcher(m)
    a = list(i('x', 'y') for i in rep.prop_matchers)
    print(a)
    m.assert_called_once_with('x')

def test_repository_property_value_matcher_decorator_adds_to_list():
    rep = aop_gatherer.Repository()
    m = MagicMock()
    rep.prop_value_matcher(m)
    a = list(i('x', 'y') for i in rep.prop_matchers)
    m.assert_called_once_with('y')

@pytest.fixture()
def mock_modules(file_properties):
    m1 = SimpleNamespace(**{k:k for k in file_properties['properties']})
    m2 = SimpleNamespace(**{k: i for i, k in enumerate(file_properties['properties'])})
    return (m1, m2)


def test_repository_property_name_regex_adds_regex_to_list():
    rep = aop_gatherer.Repository()
    rep.prop_name_matches(re.compile("test_prop.*"))
    assert any(i('test_propabcdersggsdfhg', None) for i in rep.prop_matchers)


def test_repository_property_name_regex_adds_regex_string_to_list():
        rep = aop_gatherer.Repository()
        rep.prop_name_matches("test_prop.*")
        assert any(i('test_propabcdersggsdfhg', None) for i in rep.prop_matchers)


def test_repository_hasnt_properties_without_matchers(mock_modules):
    # this is meant to ensure that all the previous tests are valid.
    gatherer_mock = MagicMock(spec=aop_gatherer.ModuleGatherer)
    gatherer_mock.load_modules.return_value = mock_modules
    rep = aop_gatherer.Repository()
    rep.gatherer = gatherer_mock
    assert not rep.properties(True)


def test_repository_properties_incremental_with_matchers(mock_modules):
    # this is meant to ensure that all the previous tests are valid.
    gatherer_mock = MagicMock(spec=aop_gatherer.ModuleGatherer)
    gatherer_mock.load_modules.return_value = mock_modules
    rep = aop_gatherer.Repository(paths=(MagicMock(),)) # adding a single 'path' so that modules are 'loaded'
    rep.gatherer = gatherer_mock
    rep.prop_name_ends_with('Tester')
    assert all([i.endswith('Tester') if isinstance(i, str) else i == 1 for i in rep.properties()])
    rep.prop_name_starts_with('test_')
    print(list(rep.modules()))
    assert all( [i in rep.properties() for i in [1, 0, 'ThingTester', 'test_thing1']]) and len(rep.properties() ) == 4



