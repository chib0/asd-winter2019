from unittest.mock import MagicMock
import sys
import pytest

from cortex.parser import repository
from utils.repository_base import RepositoryBase, HandlerRecord

def test_parser_record_parse_target_name():
    def parse_something():
        pass
    def parse_something_something():
        pass

    parse_something.target = 'something'
    parse_something_something.target = 'something_something'
    class SomethingParser:
        def parse_inner(self):
            pass
        target = 'something'
        parse_inner.target = 'inner'


    class SomethingSomethingParser:
        target = 'something_something'

    suite = [repository.ParserRecord(parse_something),
                 repository.ParserRecord(SomethingParser),
                 repository.ParserRecord(SomethingSomethingParser),
                 repository.ParserRecord(parse_something_something),
                 repository.ParserRecord(SomethingParser().parse_inner)]

    assert all([i.format_target_name() == i.handler.target for i in suite])

def test_parser_record_is_repository_record():
    assert isinstance(repository.ParserRecord(MagicMock()), repository.HandlerRecord)


def test_repository_is_base_repository():
    assert isinstance(repository.Repository.get(MagicMock()), repository.RepositoryBase)

@pytest.fixture
def temp_parser_dir(tmpdir):
    PARSER_CONTENT = """
def parse_test():
    pass

class TestParser:
    pass

def nothing():
    pass
 
"""
    p = tmpdir.mkdtemp()
    tests = [p.join('test_parser.py'), p.join('parse_tests.py')]

    for i in tests:
        i.write(PARSER_CONTENT)
    p.join("nothing.py").write("")
    return p

@pytest.fixture
def clear_modules():
    return [sys.modules.pop(i, None) for i in ['test_parser', 'parse_tests']]

def test_repository_aggregates_right_functions(temp_parser_dir, clear_modules):
    rep = repository.Repository.get((str(temp_parser_dir),))
    modules = rep.modules(recursive=False)

    assert [i.__file__  for i in modules] == list(map(str, (temp_parser_dir.join('test_parser.py'), temp_parser_dir.join('parse_tests.py'))))


def test_repository_aggregates_only_right_modules(temp_parser_dir, clear_modules):
    rep = repository.Repository.get((str(temp_parser_dir),))
    modules = rep.modules(recursive=False)

    assert sorted([i.__file__  for i in modules]) == \
           sorted(list(map(str, (temp_parser_dir.join('test_parser.py'), temp_parser_dir.join('parse_tests.py')))))


def test_repository_aggregates_only_right_properties(temp_parser_dir):
    rep = repository.Repository.get((str(temp_parser_dir),))
    props = rep.properties(recursive=False)
    assert sorted([i.__name__ for i in props]) == sorted(['TestParser', 'parse_test',
                                                          'parse_test', 'TestParser'])
