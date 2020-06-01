"""
See rabbit_dispatcher.py to understand the lifecycle of the instance.
This test suite assumes function names and attempts to mock a RabbitMq server.
while this is not fully achieved (since I don't want part of the requirements for the project be a
RabbitMQ docker or instance), the flow as documented by RabbitMQ is emulated.

If RabbitMQ ever changes their callbacks or anything like that, this (& the dispatcher itself) is going to break.
Once it breaks, we will reconsider the test implementation.

"""
from itertools import chain

import pika
from unittest.mock import MagicMock

import pytest

from cortex.utils.dispatchers import rabbit_dispatcher


def test_get_consumer_connects_to_right_place(monkeypatch):
    m = MagicMock()
    monkeypatch.setattr(rabbit_dispatcher.pika, "SelectConnection", m)
    rabbit_dispatcher.get_dispatcher('rabbitmq://testdomainname:1234/', [])
    m.assert_called_once()
    assert pika.ConnectionParameters(host='testdomainname', port=1234) in m.call_args[0]


def test_get_consumer_does_not_accept_non_rabbitmq_urls(monkeypatch):
    assert rabbit_dispatcher.get_dispatcher('testdomainname:1234/', []) is None
    assert rabbit_dispatcher.get_dispatcher('file://testdomainname:1234/', []) is None
    assert rabbit_dispatcher.get_dispatcher('http://testdomainname:1234/', []) is None
    assert rabbit_dispatcher.get_dispatcher('https://testdomainname:1234/', []) is None
    assert rabbit_dispatcher.get_dispatcher('acmq://testdomainname:1234/', []) is None
    # could add more but this shows the point

def test_get_consumer_starts_dispatcher(monkeypatch):
    m = MagicMock()
    monkeypatch.setattr(rabbit_dispatcher, 'RabbitQueueDispatcher', m)
    rabbit_dispatcher.get_dispatcher('rabbitmq://testdomainname:1234/', [])
    m.assert_called_once()

def test_get_consumer_passes_list_topics_to_queue_dispatcher(monkeypatch):
    m = MagicMock()
    monkeypatch.setattr(rabbit_dispatcher.RabbitQueueDispatcher, 'start', m)
    test_topics = ['topic1', 'topic2']
    disp = rabbit_dispatcher.get_dispatcher('rabbitmq://testdomainname:1234/', test_topics)
    assert disp._topics == test_topics

def test_queue_dispatcher_publish_is_dispatch(monkeypatch):
    disp_mock = MagicMock()
    monkeypatch.setattr(rabbit_dispatcher.RabbitQueueDispatcher, 'dispatch', MagicMock)
    args = [1,2,3,4,5]
    kwargs={'test1': 1}
    rabbit_dispatcher.RabbitQueueDispatcher(None, None).publish(*args, **kwargs)
    assert disp_mock.called_once_with(*args, **kwargs)


@pytest.fixture()
def dispatcher():
    return rabbit_dispatcher.RabbitQueueDispatcher(None, None)


@pytest.fixture()
def dispatcher_with_channel(dispatcher):
    dispatcher._connection = MagicMock()
    dispatcher._channel = MagicMock()
    return dispatcher


def test_dispatch_sends_with_existing_channel(dispatcher_with_channel):
    test_topic, test_data = 'test_topic', 'test_data'
    dispatcher_with_channel.dispatch(test_topic, test_data)
    dispatcher_with_channel._channel.basic_publish.assert_called_once_with(None, test_topic, test_data)


def test_dispatch_creates_new_channel_on_bad_existing_channel(dispatcher_with_channel):
    dispatcher_with_channel._channel.basic_publish.side_effect=ValueError()
    test_topic, test_data = 'test_topic', 'test_data'
    dispatcher_with_channel.dispatch(test_topic, test_data)
    dispatcher_with_channel._connection.channel.assert_called_once_with(
        on_open_callback=dispatcher_with_channel._on_channel_opened)


def test_dispatch_appends_message_to_queue_on_send_failure(dispatcher_with_channel):
    dispatcher_with_channel._channel.basic_publish.side_effect = ValueError()
    test_topic, test_data = 'test_topic', 'test_data'
    dispatcher_with_channel.dispatch(test_topic, test_data)
    assert (test_topic, test_data) in dispatcher_with_channel._queue

def test__on_channel_open_replaces_current_channel(dispatcher_with_channel):
    m = MagicMock()
    dispatcher_with_channel._on_channel_opened(m)
    assert dispatcher_with_channel._channel is m


def test__on_channel_open_flushes_messages(dispatcher_with_channel, monkeypatch):
    _flush_messages_mock = MagicMock()
    monkeypatch.setattr(dispatcher_with_channel, '_flush_messages', _flush_messages_mock)
    dispatcher_with_channel._on_channel_opened(None)
    _flush_messages_mock.assert_called_once()

def test__flush_messages_publishes_messages_in_queue_on_good_channel(dispatcher_with_channel):
    test_list = [(None,'test_topic1', 'test_data1'), (None, 'test_topic2', 'test_topic2')]
    dispatcher_with_channel._queue = [i[1:] for i in test_list]
    dispatcher_with_channel._flush_messages()
    for called, expected in zip(dispatcher_with_channel._channel.basic_publish.call_args_list, test_list):
        assert called.args == expected

def test__flush_messages_re_dispatches_on_exception(dispatcher_with_channel, monkeypatch):
    monkeypatch.setattr(dispatcher_with_channel, 'dispatch', MagicMock())
    test_list = [(None, 'test_topic1', 'test_data1'), (None, 'test_topic2', 'test_topic2')]
    dispatcher_with_channel._queue = [i[1:] for i in test_list]
    dispatcher_with_channel._channel.basic_publish.side_effect = (None, Exception)
    dispatcher_with_channel._flush_messages()
    for called, expected in zip(dispatcher_with_channel._channel.basic_publish.call_args_list, test_list):
        assert called.args == expected

    dispatcher_with_channel.dispatch.assert_called_once_with(*test_list[1][1:], again=True)

def test__flush_does_not_lose_messages_on_exception(dispatcher_with_channel):
    test_list = [('','test_topic1', 'test_data1'), ('', 'test_topic2', 'test_topic2')]
    dispatcher_with_channel._queue = [i[1:] for i in test_list]
    dispatcher_with_channel._channel.basic_publish.side_effect = Exception()
    dispatcher_with_channel._flush_messages()

    assert dispatcher_with_channel._queue == [i[1:] for i in test_list]


def test__declare_topics_on_connection_opens_new_channel(dispatcher):
    con = MagicMock()
    dispatcher._declare_topics(con)
    con.channel.assert_called_once()

def test__declare_topics_declares_topics_on_channel(dispatcher):
    con = MagicMock()
    chan = MagicMock()
    test_topics = ['top1', 'top2']
    dispatcher._topics = test_topics[:]
    dispatcher._declare_topics(con)
    con.channel.call_args.kwargs['on_open_callback'](chan)
    for got, expected in zip(chan.queue_declare.call_arg_list, test_topics):
        assert got == expected

def test__connection_closed_stops_loop(dispatcher_with_channel):
    dispatcher_with_channel._connection_closed(None, 'reason')
    dispatcher_with_channel._connection.ioloop.stop.assert_called_once()


def test__create_and_start_conn_starts_con_io_loop(dispatcher, monkeypatch):
    monkeypatch.setattr(rabbit_dispatcher, 'pika', MagicMock())
    dispatcher._create_and_start_conn()
    rabbit_dispatcher.pika.SelectConnection.assert_called_once()
    rabbit_dispatcher.pika.SelectConnection.return_value.ioloop.start.assert_called_once()





