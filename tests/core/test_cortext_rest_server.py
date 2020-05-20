from unittest.mock import MagicMock

import pytest

from cortex.core import cortex_rest_server
from utils import configuration


@pytest.fixture
def mock_publish():
    return MagicMock()

@pytest.fixture
def mock_server(mock_publish, monkeypatch):
    monkeypatch.setattr(cortex_rest_server, 'MessageRecord', MagicMock(name='MessageRecord'))
    return cortex_rest_server.get_server(mock_publish)


@pytest.fixture
def client(mock_server):
    mock_server.config['TESTING'] = True

    with mock_server.test_client() as client:
        yield client


def test_get_server_runnable(mock_publish):
    assert callable(cortex_rest_server.get_server(mock_publish).run)


def test_server_returns_ok_on_post(client):
    user_id=1234
    test_data = "testdatatestdata"
    rv = client.post(
        f'/user/{user_id}',
        data=test_data
    )
    assert "OK" in rv.data.decode("utf-8")


def test_server_publishes_thought(mock_publish, client):
    user_id = 1234
    test_data = "testdatatestdata"
    rv = client.post(
        f'/user/{user_id}',
        data=test_data
    )
    mock_publish.assert_called_once()
    publish_args = mock_publish.call_args[0]

    assert configuration.topics.snapshot == publish_args[0]
    assert int(publish_args[1]['user']) == user_id
    assert all(i in publish_args[1]['snapshot']._extract_mock_name() for i in ['MessageRecord.create', 'uri'])


def test_server_retrieves_configuration(client, monkeypatch):
    config_mock = MagicMock()
    monkeypatch.setattr(cortex_rest_server.configuration, 'get_config', config_mock)
    test_data = "testdatatestdata"
    config_mock.return_value = {configuration.CONFIG_CLIENT_CONFIG: test_data}
    rv = client.get("/configuration")
    assert rv.data.decode("utf-8")  == test_data


