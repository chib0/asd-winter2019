from __future__ import annotations

import functools

from cortex.utils.dispatchers import repository

def get_topic_consumer(topic, uri, auto_start=False):
    consumer = repository.ConsumerRepository.get_repo().get_consumer(uri, {}, auto_start=auto_start)
    return TopicConsumer.wrap_consumer(topic, consumer)

class TopicConsumer:
    @classmethod
    def wrap_consumer(cls, topic : str, consumer, callback=None, message_decoder=None, auto_start=False):
        if consumer.running:
            # TODO: I should probably be able to support that, but it creates clutter.
            raise RuntimeError("cant wrap running consumer")
        wrapped = cls(topic, consumer)
        if callback:
            wrapped.bind(callback, message_decoder, auto_start)
        return wrapped

    def __init__(self, topic : str, consumer):
        """
        gets a topic string and a consumer to later bind to that.
        :param topic: the topic to bind to
        :param consumer: the consumer that will be bound to that
        """
        self._topic = topic
        self._consumer = consumer
        self._callback = None
        self._decoder = None
        self.started = False

    def bind(self, callback, message_decoder=None, auto_start=False):
        if not all(i is not None and i is not callable(callback) for i in [callback, message_decoder]):
            raise TypeError("expected callable callback")
        register = self._consumer.register_handler
        if message_decoder:
            register = functools.partial(register, message_decoder=message_decoder)
        register(self.topic, callback, auto_start=auto_start)
        self._callback = callback

    def __call__(self, callback=None, /,  message_decoder=None, auto_start=False):
        """
        decorator bo bind function to the consumer
        :param callback: callback to bind
        :param message_decoder: the message decoder to use, if any
        :param auto_start: should it autostart
        :return: the callback
        """
        if message_decoder is not None and callback is None:
            return lambda f: self(f, message_decoder=message_decoder)
        self.bind(callback, message_decoder=message_decoder, auto_start=auto_start)
        return callback

    @property
    def running(self):
        return self._consumer.running

    @property
    def bound(self):
        """True if this was bound"""
        return self.callback is not None

    @property
    def callback(self):
        """ the callback this was bound to"""
        return self._callback

    @property
    def topic(self):
        return self._topic

    def start(self):
        if not self.bound:
            raise RuntimeError("Cannot start unbound TopicConsumer")
        self._consumer.start()
        self.started = True

    def stop(self):
        self._consumer.stop()
        self.started = False



