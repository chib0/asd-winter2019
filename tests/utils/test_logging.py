import contextlib
import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

import tempfile

from cortex.utils import logging
from cortex import configuration


@pytest.fixture()
def patched_config_dict(monkeypatch):
    dic = {
        configuration.CONFIG_DEBUG_LEVEL: logging.logging.INFO,
        'log_file': None
    }
    monkeypatch.setattr(logging.configuration, 'get_config', lambda: dic)
    return dic

def test_get_logger_sets_logger_name():
    assert logging.get_logger('test_name').name == 'test_name'

def test_get_logger_returns_a_console_logger_when_log_file_is_none(capsys, patched_config_dict):
    patched_config_dict['log_file'] = None
    l = logging.get_logger('test_name0')
    test_message = 'this is a test message'
    l.error(test_message)
    capted = capsys.readouterr()
    assert test_message in capted.out

def test_get_logger_returns_a_console_logger_when_log_file_not_in_config(capsys, patched_config_dict):
    with contextlib.suppress():
        patched_config_dict.pop('log_file')
    l = logging.get_logger('test_name1')
    test_message = 'this is a test message'
    l.error(test_message)

    capted = capsys.readouterr()
    assert test_message in capted.out

def test_get_logger_returns_a_file_logger_when_log_file_in_config(patched_config_dict):
    t = tempfile.mktemp()
    patched_config_dict['log_file'] = t
    l = logging.get_logger('test_name2')
    test_message = 'this is a test message'
    l.error(test_message)
    with open(t) as f:
        assert test_message in f.read()
    os.unlink(t)


def test_get_logger_registers_custom_handlers():
    mock = MagicMock(spec=logging.logging.Handler)
    mock.level = logging.logging.INFO
    l = logging.get_logger('test_name3', custom_handlers=(mock,))
    assert mock in l.handlers

def test_get_instance_logger_gets_class_name():
    class TestInstance:
        def __init__(self):
            assert "TestInstance" in logging.get_instance_logger(self).name

def test_get_instance_logger_adds_custom_handlers():
    mock = MagicMock(spec=logging.logging.Handler)
    mock.level = logging.logging.INFO
    class TestInstance:
        def __init__(self):
            assert mock in logging.get_instance_logger(self, (mock,)).handlers


def test_get_module_logger_gets_path_name():
    assert __name__ in logging.get_module_logger(__name__).name
    assert Path(__file__).name in logging.get_module_logger(__file__).name

def test_get_module_logger_adds_custom_handlers():
    mock = MagicMock(spec=logging.logging.Handler)
    mock.level = logging.logging.INFO
    assert mock in logging.get_module_logger(__file__, (mock,)).handlers


def test_log_exception_does_log(capsys):
    logger = logging.get_logger("name")
    exception_message = "This is a message"
    with pytest.raises(Exception):
        with logging.log_exception(logger):
            raise Exception(exception_message)
    output = capsys.readouterr().out
    assert exception_message in output
    assert 'ERROR' in output


def test_log_exception_does_log_and_suppresses(capsys):
    logger = logging.get_logger("name1")
    exception_message = "This is a message"
    with logging.log_exception(logger, to_suppress=(Exception, )):
        raise Exception(exception_message)
    output = capsys.readouterr().out
    assert exception_message in output
    assert 'ERROR' in output

def test_log_exception_does_not_log_on_ignore(capsys):
    logger = logging.get_logger("name2")
    typeerror_message = "this is a TypeError"
    with pytest.raises(TypeError):
        with logging.log_exception(logger, to_ignore=(TypeError,)):
            raise TypeError(typeerror_message)
    output = capsys.readouterr().out
    assert typeerror_message not in output
    assert 'ERROR' not in output

def test_log_exception_does_not_log_on_ignore_but_suppresses(capsys):
        logger = logging.get_logger("name3")
        typeerror_message = "this is a TypeError"
        with logging.log_exception(logger, to_suppress=(TypeError,), to_ignore=(TypeError,)):
            raise TypeError(typeerror_message)

        output = capsys.readouterr().out
        assert typeerror_message not in output
        assert 'ERROR' not in output