from unittest.mock import MagicMock
import sys
import pytest

from cortex.saver import repository

def test_saver_record_parse_target_name():
    def save_something():
        pass
    def save_something_something():
        pass

    save_something.target = 'something'
    save_something_something.target = 'something_something'
    class SomethingSaver:
        def save_inner(self):
            pass
        target = 'something'
        save_inner.target = 'inner'


    class SomethingSomethingSaver:
        target = 'something_something'

    suite = [repository.SaverRecord(save_something),
                 repository.SaverRecord(SomethingSaver),
                 repository.SaverRecord(SomethingSomethingSaver),
                 repository.SaverRecord(save_something_something),
                 repository.SaverRecord(SomethingSaver().save_inner)]

    assert all([i.format_target_name() == i.handler.target for i in suite])

def test_saver_record_is_repository_record():
    assert isinstance(repository.SaverRecord(MagicMock()), repository.HandlerRecord)


def test_repository_is_base_repository():
    assert isinstance(repository.Repository.get(MagicMock()), repository.RepositoryBase)

@pytest.fixture
def temp_saver_dir(tmpdir):
    SAVER_CONTENT = """
def save_test():
    pass

class TestSaver:
    pass

def nothing():
    pass
 
"""
    p = tmpdir.mkdtemp()
    tests = [p.join('test_saver.py'), p.join('save_tests.py')]

    for i in tests:
        i.write(SAVER_CONTENT)
    p.join("nothing.py").write("")
    return p

@pytest.fixture
def clear_modules():
    return [sys.modules.pop(i, None) for i in ['test_saver', 'save_tests']]

def test_repository_aggregates_right_functions(temp_saver_dir, clear_modules):
    rep = repository.Repository.get((str(temp_saver_dir),))
    modules = rep.modules(recursive=False)

    assert [i.__file__  for i in modules] == list(map(str, (temp_saver_dir.join('test_saver.py'), temp_saver_dir.join('save_tests.py'))))


def test_repository_aggregates_only_right_modules(temp_saver_dir, clear_modules):
    rep = repository.Repository.get((str(temp_saver_dir),))
    modules = rep.modules(recursive=False)

    assert sorted([i.__file__  for i in modules]) == \
           sorted(list(map(str, (temp_saver_dir.join('test_saver.py'), temp_saver_dir.join('save_tests.py')))))


def test_repository_aggregates_only_right_properties(temp_saver_dir):
    rep = repository.Repository.get((str(temp_saver_dir),))
    props = rep.properties(recursive=False)
    assert sorted([i.__name__ for i in props]) == sorted(['TestSaver', 'save_test',
                                                          'save_test', 'TestSaver'])
