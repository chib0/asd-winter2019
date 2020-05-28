import pytest
import werkzeug

import cortex.cli.api_consumer as api_consumer


@pytest.fixture()
def consumer(httpserver):
    return api_consumer.Consumer(httpserver.host, httpserver.port)


def test_consumer_base_request_requests_joined_url(consumer, httpserver):
    TEST_JSON  = {'code': 1}
    httpserver.expect_oneshot_request('/').respond_with_json(TEST_JSON)
    assert TEST_JSON == consumer._request()
    httpserver.expect_oneshot_request('/this/is/a/test/url').respond_with_json(TEST_JSON)
    assert TEST_JSON == consumer._request('this', 'is', 'a', 'test', 'url')

def test_consumer_base_request_returns_none_on_error(consumer, httpserver):
    httpserver.expect_oneshot_request('/error').respond_with_response(werkzeug.Response(status=404))
    assert consumer._request('error') is None


def test_requests_request_correct_paths(consumer, httpserver):
    tests = [
       (consumer.get_users, [], '/users'),
       (consumer.get_user, [1], '/users/1'),
       (consumer.get_snapshots, [1], '/users/1/snapshots'),
       (consumer.get_snapshot, [1, 2], '/users/1/snapshots/2'),
       (consumer.get_result, [1, 2, 'pose'], '/users/1/snapshots/2/pose'),
       (consumer.get_result_data, [1, 2, 'pose'], '/users/1/snapshots/2/pose/data')
    ]
    for method, args, expected_url in tests:
        httpserver.expect_oneshot_request(expected_url).respond_with_json({})
        assert {} == method(*args)
