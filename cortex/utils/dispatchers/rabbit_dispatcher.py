import functools

import pika
from threading import Thread

import urlpath

from cortex import utils

SCHEME = "rabbitmq"

module_logger = utils.logging.get_module_logger(__file__)

def get_dispatcher(url, topics, **kwargs):
    """
    creates a dispatcher and connects to the given url
    :param url: where to connect
    :param topics: topics that could be published
    :param kwargs: anything to pass on to the dispatcher implementation (TODO)
    :return: a dispatcher if the url scheme matches, None otherwise
    """
    url = urlpath.URL(url)
    if not url.scheme == SCHEME:
        return None

    topics = topics if not isinstance(topics, str) else (topics, )
    dispatcher = RabbitQueueDispatcher(pika.ConnectionParameters(host=url.hostname, port=url.port), topics)
    dispatcher.start()
    return dispatcher


class RabbitQueueDispatcher:
    def __init__(self, endpoints, topics):
        self._logger = utils.logging.get_instance_logger(self.__class__.__name__)
        self._connection = None
        self._channel = None
        self._endpoints = endpoints
        self._topics = topics
        self._ioloop = None
        self._queue = []

    def dispatch(self, topic, data, again=False):
        if not self._send_with_existing_channel(topic, data):
            self._logger.debug("creating new channel to dispatch with")
            self._queue.insert(0 if again else len(self._queue), (topic, data))
            self._connection.channel(on_open_callback=self._on_channel_opened)

    def publish(self, *args, **kwargs):
        """
        this is a pure forward to `self.dispatch`
        :param args:
        :param kwargs:
        :return:
        """
        return self.dispatch(*args, **kwargs)

    def _send_with_existing_channel(self, topic, data):
        if not self._channel:
            return False

        with utils.logging.log_exception(self._logger, to_suppress=Exception, format=lambda e: f"had error sending {e}"):
            self._channel.basic_publish('', topic, data)
            return True

        return False

    def _on_channel_opened(self, channel):
        self._channel = channel
        self._flush_messages()

    def _flush_messages(self):
        """
        flushes all the messages that were to be dispatched by the queue.
        :return:
        """
        while self._queue:
            topic, data = self._queue.pop(0)
            try:
                self._channel.basic_publish('', topic, data)
            except Exception:
                # there is an issue with this channel, we're trying to reconnect.
                self.dispatch(topic, data, again=True)
                break


    def _declare_topics(self, connection):
        """
        Creates a channel, declares the topics that this dispatcher should be handling on the client.
        :param connection: The connection to declare topics for
        :return:
        """
        self._logger.info("opening channel...")
        def has_channel(channel):
            self._logger.info("declaring topics...")
            for i in self._topics:
                channel.queue_declare(i)

            self._channel = channel

        ch = connection.channel(on_open_callback=has_channel)

    def _connection_closed(self, something, reason):
        """
        logs that the connection was closed
        :param something:
        :param reason:
        :return:
        """
        self._logger.info(f"connection closed: {reason}")
        self._connection.ioloop.stop()

    def _create_and_start_conn(self):
        """
        thread entry method. Creates and starts ioloop for a rabbitmq connection
        :return: Nothing
        """
        self._connection = pika.SelectConnection(self._endpoints, on_open_callback=self._declare_topics,
                                                 on_close_callback=self._connection_closed)
        self._connection.ioloop.start()


    def start(self):
        """
        Creates a connection and starts its ioloop in a different thread
        :return:
        """
        self._ioloop = Thread(target=self._create_and_start_conn, daemon=True)
        self._ioloop.start()


    def stop(self):
        """
        closes the connection; blocks until it's closed
        """
        self._connection.close()
        self._ioloop.join()

    @property
    def running(self):
        return self._ioloop.is_alive()



