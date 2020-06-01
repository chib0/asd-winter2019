from unittest.mock import MagicMock

import pytest

from cortex.core import cortex_rest_server
from cortex import configuration


@pytest.fixture
def mock_publish():
    return MagicMock()

@pytest.fixture()
def mock_encoder():
    return MagicMock()

@pytest.fixture
def mock_server(mock_publish, mock_encoder, monkeypatch):
    return cortex_rest_server.get_server(mock_publish, mock_encoder)


@pytest.fixture
def client(mock_server):
    mock_server.config['TESTING'] = True

    with mock_server.test_client() as client:
        yield client


def test_get_server_runnable(mock_publish, mock_encoder):
    assert callable(cortex_rest_server.get_server(mock_publish, mock_encoder).run)


def test_server_returns_ok_on_post(client):
    user_id=1234
    test_data = "testdatatestdata"
    rv = client.post(
        f'/user/{user_id}',
        data=test_data
    )
    assert "OK" in rv.data.decode("utf-8")


def test_server_publishes_thought(mock_publish, mock_encoder, client):
    user_id = 1234
    test_data = "testdatatestdata"
    rv = client.post(
        f'/user/{user_id}',
        data=test_data
    )
    mock_publish.assert_called_once()
    mock_encoder.assert_called_once()
    publish_args = mock_publish.call_args[0]
    encoder_args = mock_encoder.call_args

    assert configuration.topics.snapshot == publish_args[0]
    print(encoder_args)
    assert int(encoder_args.kwargs['user']) == user_id
    assert encoder_args[0][0].decode("utf-8") == test_data




def test_server_retrieves_configuration(client, monkeypatch):
    config_mock = MagicMock()
    monkeypatch.setattr(cortex_rest_server.configuration, 'get_config', config_mock)
    test_data = "testdatatestdata"
    config_mock.return_value = {configuration.CONFIG_CLIENT_CONFIG: test_data}
    rv = client.get("/configuration")
    assert rv.data.decode("utf-8")  == test_data


