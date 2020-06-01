import logging
from unittest.mock import Mock, MagicMock

import pytest

from cortex import server
import cortex.server.cli
from click.testing import CliRunner

from tests import mocks


@pytest.fixture()
def mock_publish():
    return print

@pytest.fixture()
def mock_encoder():
    return MagicMock()

def test_server_get_server_gets_runnable_server(mock_publish, mock_encoder):
    assert callable(server.get_server(mock_publish, mock_encoder).run)


def test_server_threaded(monkeypatch):
    get_server_mock = Mock(sepc=server.get_server)
    dispatcher_mock = MagicMock()
    thread_mock = mocks.mock_threading.DaemonThread
    monkeypatch.setattr(server, 'get_server', get_server_mock)
    monkeypatch.setattr(server.server.dispatchers.repository.DispatcherRepository, 'get_dispatcher', dispatcher_mock)
    monkeypatch.setattr(server.server.threading, "Thread", thread_mock)
    kwargs = dict(host="127.0.0.1", port=1234)

    server.server._run_server(publish=mock_publish, **kwargs, run_threaded=True)
    mock_server = get_server_mock.return_value
    mock_server.run.assert_called_once()
    assert all(mock_server.run.call_args.kwargs[i] == kwargs[i] for i in kwargs)


def test_server_non_threaded(monkeypatch, mock_publish, mock_encoder):
    get_server_mock = Mock(sepc=server.get_server)
    dispatcher_mock = MagicMock()
    monkeypatch.setattr(server, 'get_server', get_server_mock)
    monkeypatch.setattr(server.cli.dispatchers.repository.DispatcherRepository, 'get_dispatcher', dispatcher_mock)
    kwargs = dict(host="127.0.0.1", port=1234)
    server.server._run_server(publish=mock_publish, encoder=mock_encoder, **kwargs, run_threaded=True)
    mock_server = get_server_mock.return_value
    # We are not mocking run_server,
    # so if it were to run on this thread we would have blocked.
    mock_server.run.assert_called_once_with(host='127.0.0.1', port=1234)



def test_server_cli_exposes_command(monkeypatch):
    run_server_mock = Mock()
    dispatcher_mock = MagicMock()
    monkeypatch.setattr(server, '_run_server', run_server_mock)
    monkeypatch.setattr(server.cli.dispatchers.repository.DispatcherRepository, 'get_dispatcher', dispatcher_mock)
    runner = CliRunner()
    runner.invoke(server.cli, ['run-server', '-p', '1234', '-h', '127.0.0.1', 'some_uri'])
    run_server_mock.assert_called_once()

def test_server_runs_server_run_with_args(monkeypatch):
    get_server_mock = Mock(sepc=server.get_server)
    dispatcher_mock = MagicMock()
    monkeypatch.setattr(server, 'get_server', get_server_mock)
    monkeypatch.setattr(server.cli.dispatchers.repository.DispatcherRepository, 'get_dispatcher', dispatcher_mock)
    monkeypatch.setattr(server.server.threading, "Thread", mocks.mock_threading.DaemonThread)
    runner = CliRunner()
    runner.invoke(server.cli, ['run-server', '-p', '1234', '-h', '127.0.0.1', 'some_uri'])
    get_server_mock.return_value.run.assert_called_once_with(host='127.0.0.1', port=1234)
