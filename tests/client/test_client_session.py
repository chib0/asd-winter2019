import pytest
import urlpath
from pytest_httpserver import HTTPServer

from cortex.client import cortex_pb2
from cortex.client.client import ClientHTTPSession
from cortex import Thought
from cortex import configuration

@pytest.fixture()
def config_dict():
    return {'one': 2}

@pytest.yield_fixture()
def sessionserver(config_dict):
    config_path = configuration.get_config()[configuration.CONFIG_SERVER_CONFIG_ENDPOINT]
    with HTTPServer()as httpserver:
        httpserver.expect_request(config_path).respond_with_json(config_dict)
        yield httpserver

def test_start_requests_conf(sessionserver, config_dict):
    out = ClientHTTPSession.start(sessionserver.host, sessionserver.port)
    assert out._server_config == config_dict

def test_get_config_sets_configuration(sessionserver, config_dict):
    ses = ClientHTTPSession(urlpath.URL(sessionserver.url_for("/")))
    ses.get_config()
    assert ses._server_config == config_dict

def test_send_thought_to_correct_url(sessionserver):
    client_session = ClientHTTPSession.start(sessionserver.host, sessionserver.port)
    USER_ID = 12345
    sessionserver.expect_oneshot_request(f'/user/{USER_ID}').respond_with_json({})
    with sessionserver.wait(raise_assertions=True, timeout=2):
        import json
        client_session.send_thought(Thought.from_snapshot(cortex_pb2.User(user_id=USER_ID), cortex_pb2.Snapshot()),
                                     lambda x: b'string')

def test_get_config_sets_config(httpserver, config_dict):
    client = ClientHTTPSession(httpserver.url_for("/"))
    httpserver.expect_oneshot_request(f'/configuration').respond_with_json(config_dict)
    with httpserver.wait(raise_assertions=True, timeout=2):
        client.get_config()
    assert client._server_config == config_dict






