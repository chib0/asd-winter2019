import pytest

from cortex.utils.dispatchers import tee
from unittest.mock import MagicMock, NonCallableMock


@pytest.fixture()
def cons_mock():
    return MagicMock()
@pytest.fixture()
def pub_mock():
    return MagicMock()

@pytest.fixture()
def patched_tee(monkeypatch, cons_mock, pub_mock):
    monkeypatch.setattr(tee, 'get_topic_consumer', cons_mock)
    monkeypatch.setattr(tee, 'get_topic_dispatcher', pub_mock)
    return tee

@pytest.fixture()
def mocked_Tee(monkeypatch, cons_mock, pub_mock):
    monkeypatch.setattr(tee, 'get_logger', MagicMock())
    t = tee.Tee(cons_mock, pub_mock)
    return t

@pytest.fixture()
def bound_Tee(monkeypatch, cons_mock, pub_mock):
    monkeypatch.setattr(tee, 'get_logger', MagicMock())
    t = tee.Tee(cons_mock, pub_mock)
    t.bind(MagicMock)
    return t

# Test Creation #
def test_get_tee_looks_lookups_according_to_uri(monkeypatch, patched_tee, cons_mock, pub_mock):
    cons_uri = "test://domain:123/cons"
    pub_uri = "test://domain:123/pub"
    t = patched_tee.get_topic_tee('test_topic', cons_uri, pub_uri)
    assert t.consumer == cons_mock.return_value
    assert t.publisher == pub_mock.return_value
    assert cons_mock.called_once_with(None, cons_uri)
    assert pub_mock.called_once_with('test_topic', pub_uri)

def test_get_tee_raises_if_consumer_not_found(monkeypatch, patched_tee, cons_mock, pub_mock):
    cons_mock.return_value = None
    cons_uri = "test://domain:123/cons"
    pub_uri = "test://domain:123/pub"
    with pytest.raises(ValueError):
        t = tee.get_topic_tee('test_topic', cons_uri, pub_uri)


def test_get_tee_raises_if_publisher_not_found(monkeypatch, patched_tee, cons_mock, pub_mock):
    pub_mock.return_value = None
    cons_uri = "test://domain:123/cons"
    pub_uri = "test://domain:123/pub"
    with pytest.raises(ValueError):
        t = tee.get_topic_tee('test_topic', cons_uri, pub_uri)

def test_tee_raises_on_none_consumer():
    with pytest.raises(ValueError):
        tee.Tee(None, MagicMock())


# Test Starting and stoping
def test_tees_start_starts_everything(bound_Tee, cons_mock, pub_mock):
    bound_Tee.start()
    cons_mock.start.assert_called_once()
    pub_mock.start.assert_called_once()
    assert bound_Tee.running is True

def test_tee_stop_stops_everything(mocked_Tee, cons_mock, pub_mock):
    mocked_Tee.stop()
    cons_mock.stop.assert_called_once()
    pub_mock.stop.assert_called_once()
    assert mocked_Tee.running is False

def test_tee_raises_if_start_unbound(mocked_Tee, cons_mock, pub_mock):
    with pytest.raises(ValueError):
        mocked_Tee.start()
    assert mocked_Tee.running is False

def test_tee_publisher_start_failure_stops_everything(bound_Tee, cons_mock, pub_mock):
    pub_mock.start.side_effect = TypeError("Test exception")

    bound_Tee.start()
    cons_mock.stop.assert_called_once()
    pub_mock.stop.assert_called_once()
    assert bound_Tee.running is False

def test_tee_consumer_start_failure_stops_everything(bound_Tee, cons_mock, pub_mock):
    cons_mock.start.side_effect = TypeError("Test exception")
    bound_Tee.start()
    cons_mock.stop.assert_called_once()
    pub_mock.stop.assert_called_once()
    assert bound_Tee.running is False

# Test decoration
def test_tee_call_decorator_without_args(mocked_Tee):
    @mocked_Tee
    def thing():
        pass

    assert mocked_Tee.callback == thing

def test_tee_call_decorator_with_empty_args(mocked_Tee):
    @mocked_Tee()
    def thing():
        pass

    assert mocked_Tee.callback == thing

def test_tee_binds_with_encoder_and_decoder(mocked_Tee, monkeypatch):
    enc, dec = MagicMock(), MagicMock()
    monkeypatch.setattr(mocked_Tee, 'bind', MagicMock())
    @mocked_Tee(message_encoder=enc, message_decoder=dec)
    def thing():
        pass
    mocked_Tee.bind.assert_called_once_with(thing, message_encoder=enc, message_decoder=dec)

def test_tee_bind_stops_on_none_callback(monkeypatch, mocked_Tee):
    monkeypatch.setattr(mocked_Tee, 'stop', MagicMock())
    mocked_Tee.bind(None)
    mocked_Tee.stop.assert_called_once()

def test_tee_with_publisher_binds_result_publisher(bound_Tee, monkeypatch):
    bound_Tee.consumer.bind.assert_called_once_with(bound_Tee.publisher.results_publisher.return_value,
                                                     message_decoder=None)

def test_tee_without_publisher_binds_callback(pub_mock, monkeypatch):
    t = tee.Tee(pub_mock, None)
    def func(): pass
    t.bind(func)
    t.consumer.bind.assert_called_once_with(func, message_decoder=None)

def test_tee_bind_fails_on_non_callable(mocked_Tee):
    with pytest.raises(TypeError):
        mocked_Tee.bind(NonCallableMock())
