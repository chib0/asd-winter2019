import json
import pytest
import pika
from unittest.mock import MagicMock

from cortex.utils.dispatchers import rabbit_consumer


@pytest.fixture()
def rabbit_consumer_patched(monkeypatch):
    pik, threading, thread = MagicMock(), MagicMock(spec=rabbit_consumer.threading), MagicMock(spec=rabbit_consumer.threading.Thread)
    monkeypatch.setattr(rabbit_consumer.pika, "BlockingConnection", pik)
    monkeypatch.setattr(rabbit_consumer, "threading", threading)
    threading.Thread.return_value = thread
    thread.is_alive.return_value = True
    thread.isAlive.return_value = True
    return rabbit_consumer

def test_get_consumer_connects_to_right_place(monkeypatch):
    m = MagicMock()
    monkeypatch.setattr(rabbit_consumer.pika, "BlockingConnection", m)
    rabbit_consumer.get_consumer('rabbitmq://testdomainname:1234/')
    m.assert_called_once_with(pika.ConnectionParameters(host='testdomainname', port=1234))


def test_get_consumer_does_not_accept_non_rabbitmq_urls(monkeypatch):
    assert rabbit_consumer.get_consumer('testdomainname:1234/') is None
    assert rabbit_consumer.get_consumer('file://testdomainname:1234/') is None
    assert rabbit_consumer.get_consumer('http://testdomainname:1234/') is None
    assert rabbit_consumer.get_consumer('https://testdomainname:1234/') is None
    assert rabbit_consumer.get_consumer('acmq://testdomainname:1234/') is None
    # could add more but this shows the point


def test_get_consumer_registers_handlers(rabbit_consumer_patched):
    c = rabbit_consumer_patched.get_consumer('rabbitmq://testdomainname:1234/',
                                             {'topic': lambda x:None, 'topic2':(lambda x:None, lambda y: None)})
    assert 'topic' in c.handlers
    assert 'topic2' in c.handlers

def test_consumer_decorator_registers_handler(rabbit_consumer_patched, monkeypatch):
    registerer = MagicMock(return_value=None)  # this is so that the decorator will return the original function
    monkeypatch.setattr(rabbit_consumer.RabbitQueueConsumer, 'register_handler', registerer)
    c = rabbit_consumer_patched.RabbitQueueConsumer(None, None)

    @c("topic1")
    def something(x):
        pass
    registerer.assert_called_once_with('topic1', something, False, json.loads)

def test_consumer_decorator_starts_thread_automatically_on_request(rabbit_consumer_patched, monkeypatch):
    registerer = MagicMock(return_value=None)  # this is so that the decorator will return the original function
    monkeypatch.setattr(rabbit_consumer.RabbitQueueConsumer, 'register_handler', registerer)
    c = rabbit_consumer.RabbitQueueConsumer(None, None)
    @c('topic1', auto_start=True)
    def something(x):
        pass
    registerer.assert_called_once_with('topic1', something, True, json.loads)


def test_consumer_register_handlers_works_for_callback(rabbit_consumer_patched):
    cb = lambda x: None
    c = rabbit_consumer_patched.RabbitQueueConsumer(None, None)
    c.register_handlers({'topic': cb})
    assert 'topic' in c.handlers
    rec = c.handlers['topic']
    assert isinstance(rec, rabbit_consumer.RabbitQueueConsumer.HandlerRecord)
    assert rec.callback == cb
    assert isinstance(rec.thread, MagicMock)




def test_consumer_register_handlers_works_for_callback_only_list(rabbit_consumer_patched):
    cb = lambda x: None
    c = rabbit_consumer_patched.RabbitQueueConsumer(None, None)
    c.register_handlers({'topic': [cb]})
    assert 'topic' in c.handlers
    rec = c.handlers['topic']
    assert isinstance(rec, rabbit_consumer.RabbitQueueConsumer.HandlerRecord)
    assert rec.callback == cb
    assert isinstance(rec.thread, MagicMock)


def test_consumer_register_handlers_works_for_callback_decoder_pair(rabbit_consumer_patched):
    cb = lambda x: None
    c = rabbit_consumer_patched.RabbitQueueConsumer(None, None)
    c.register_handlers({'topic': [cb, cb]})
    assert 'topic' in c.handlers
    rec = c.handlers['topic']
    # No way to test that the decoder is also cb, since it's binded to the on_message function rather than saved as state
    assert isinstance(rec, rabbit_consumer.RabbitQueueConsumer.HandlerRecord)
    assert rec.callback == cb
    assert isinstance(rec.thread, MagicMock)

def test_consumer_register_handlers_raises_on_non_callables(rabbit_consumer_patched):
    c = rabbit_consumer_patched.RabbitQueueConsumer(None, None)
    with pytest.raises(TypeError):
        c.register_handlers({'topic': ['s']})
    with pytest.raises(TypeError):
        c.register_handlers({'topic': 's'})
    with pytest.raises(TypeError):
        c.register_handlers({'topic': ['s', lambda x: None]})
    with pytest.raises(TypeError):
        c.register_handlers({'topic': [ lambda x: None, 's']})


def test_consumer_register_handler_starts_consuming_on_topic(rabbit_consumer_patched):
    c = rabbit_consumer_patched.RabbitQueueConsumer(None, None)
    c.register_handler('topic', lambda x: None)
    rec = c.handlers['topic']
    rec.channel.basic_consume.assert_called_once()
    assert rec.channel.basic_consume.call_args.kwargs['queue'] == 'topic'

def test_consumer_register_handler_with_auto_start_starts_thread(rabbit_consumer_patched):
    c = rabbit_consumer_patched.RabbitQueueConsumer(None, None)
    c.register_handler('topic', lambda x: None, auto_start=True)
    rec = c.handlers['topic']
    rec.thread.start.assert_called_once()

## TODO:
def test_consumer_decoder_handles_message(rabbit_consumer_patched):
    pass

def test_consumer_handler_gets_decoded_message(rabbit_consumer_patched):
    pass
