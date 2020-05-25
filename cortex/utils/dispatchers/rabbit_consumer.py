# -*- coding: utf-8 -*-
# pylint: disable=C0111,C0103,R0205

import functools
import json
import random
import string
import threading
from dataclasses import make_dataclass

import pika
import urlpath

from cortex.utils.logging import get_logger, get_module_logger, log_exception

LOGGER = get_module_logger(__file__)

SCHEME = 'rabbitmq'

def get_consumer(url, handlers=None, auto_start=False ):
    url = urlpath.URL(url)
    if not url.scheme == SCHEME:
        return None

    handlers = handlers or {}
    cons  = RabbitQueueConsumer(pika.ConnectionParameters(host=url.hostname, port=url.port), handlers)
    if auto_start:
        cons.start()
    return cons


class RabbitQueueConsumer:
    HandlerRecord = make_dataclass ("HandlerRecord", ['callback', ('thread', 'str'), 'channel'])

    def __init__(self, params, handlers=None):
        """
        creates a new consumer. a consumer is a threaded entity that can handle many channels at once.
        :param params: the pika connection params to the server
        :param handlers: topic -> (lambda message, decoder) map, as would be passed individually to self.register
        """
        self._logger = get_logger(self.__class__.__name__)
        self._connection_params = params
        self._connection = pika.BlockingConnection(self._connection_params)
        self.handlers = handlers or {}
        self.thread_prefix = f"rabbitmq-consumer-{''.join(random.sample(string.ascii_lowercase, 5))}"
        self._running = False
        self._io_list_lock = threading.Lock()

    def start(self):
        self.assert_all_handlers_registered()
        with self._io_list_lock:
            for i in filter(lambda x: not x.thread.is_alive(), self.handlers.values()):
                i.thread.start()
        self._running = True

    def stop(self):
        if not self._running:
            return
        with self._io_list_lock:
            for i in filter(lambda x: not x.thread.is_alive(), self.handlers.values()):
                i.channel.close()


    def _run_consumer(self, topic):
        with self._io_list_lock:
            record = self.handlers.get(topic, None)
        if record is None:
            self._logger.error(f"handler for {topic} is none")

        else:
            with log_exception(self._logger, to_suppress=(Exception, RuntimeError),
                           format=lambda e: f"thread {threading.current_thread()} exception while consuming: {e}"):
                record.channel.start_consuming()
        with self._io_list_lock:
            self.handlers.pop(topic)
            if not len(self.handlers):
                self._running = False

    def _make_consumer(self, topic, auto_start):
        """
        creates a new thread for the channel associated with the topic to consume on.
        caller is responsible to insert the created thread into the handler io list.
        if specifying auto-start, a partial (no thread, just channel&callback) HandlerRecord must be inserted prior to calling this method
        :param topic: topic for which to lookup a handler function when starting the thread
        :param auto_start: should the thread start immediately
        :return:
        """
        t = threading.Thread(target=self._run_consumer,
                             args=(topic,),
                             name=f"{self.thread_prefix}-{len(self.handlers.keys()) + 1}",
                             daemon=True)
        if auto_start:
            self._logger.debug(f"starting thread {t.name}")
            t.start()
        return t

    def on_message(self, topic, b, c, body, message_decoder=None, cb=None):
        self._logger.debug(f"{threading.current_thread().name} receiving: {body} with {topic}, passing to {cb.__name__}")
        if cb and message_decoder:
            cb(message_decoder(body))
        else:
            raise RuntimeError(f"could not parse because bad 'decoder :' {message_decoder!r} or callback: {cb!r}")

    def register_handler(self, topic, handler, auto_start=False, message_decoder=json.loads):
        """
        registers a new handler to the consumer. each handler is running in a separate thread.
        This is called behind the scenes when an instance is used as a decorator
        :param topic: what should it listen for
        :param handler: function to execute with message
        :param auto_start: should the thread start immediately
        :param message_decoder: decoder for messages coming over the handler
        :return: the handler argument
        """
        channel = self._connection.channel()
        channel.queue_declare(topic)
        channel.basic_consume(queue=topic,
                              on_message_callback=functools.partial(self.on_message,
                                                                    cb=handler,
                                                                    message_decoder=message_decoder),
                              auto_ack=True)
        with self._io_list_lock:
            self.handlers[topic] = record = self.HandlerRecord(callback=handler, thread=None, channel=channel)
        t = self._make_consumer(topic, auto_start)
        record.thread = t
        return handler

    def register_handlers(self, handlers, auto_start=False):
        """
        registers the given handlers as consumers
        the handlers is a topic => (callback, message_decoder) map, but can also map to a (callback, ) or to a callback
        in the 2 latter cases, a json.dumps decoder is used
        :param handlers: the topic map
        :param auto_start:
        :return: None
        """
        for topic, handler_decoder in handlers.items():
            if not callable(handler_decoder) and len(handler_decoder) > 1:
                register = functools.partial(self.register_handler, message_decoder=handler_decoder[1])
            else:
                if callable(handler_decoder):
                    handler_decoder = (handler_decoder,)
                register = self.register_handler
            if not all(callable(i) for i in handler_decoder):
                raise TypeError("Expecting handler_decoder to have callable members")
            register(topic, handler_decoder[0], auto_start)

    def __call__(self, topic, auto_start=False, message_decoder=json.loads):
        """
        used to decorate a function to use as a handler given a topic.
        calls register_handler behind the scenes
        :param topic: the topic to listen for
        :param auto_start: should a thread start immediatly or later
        :param message_decoder: the decoder to use for the message
        :return:
        """
        return lambda f: self.register_handler(topic, f, auto_start, message_decoder) or f

    def assert_all_handlers_registered(self):
        """
        esures all the registered handlers have had a record created
        :return:
        """
        to_be_added = tuple(filter(lambda x: not isinstance(x[1], self.HandlerRecord), self.handlers.items()))
        with self._io_list_lock:
            for key in to_be_added:
                self._logger.error(f"popping {key} to be added)")
                self.handlers.pop(key)
        for topic, values in to_be_added:
                self._logger.error(f"registering: {topic} -> {values}")
                self.register_handler(topic, values)

    @property
    def running(self):
        return self._running
