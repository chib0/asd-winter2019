"""
this file implements functionality that takes data from one queue, yields it to someone, than sends it on another queue.
"""
from cortex.utils.dispatchers.topic_consumer import get_topic_consumer
from cortex.utils.dispatchers.topic_dispatcher import get_topic_dispatcher
from cortex.utils.logging import get_logger

def get_topic_tee(topic, consumer_uri, publisher_uri):
    """
    returns a tee over the topic. consumer and publisher are unbounded and not started
    :param topic: topic to tee on
    :param consumer_uri: uri to the consumer
    :param publisher_uri: uri to the publisher
    :return: a Tee
    """
    cons = get_topic_consumer(topic, consumer_uri)
    if not cons:
        raise ValueError(f"Could not find consumer impl for {consumer_uri}")
    pub = get_topic_dispatcher(None, publisher_uri)
    if not pub:
        raise ValueError(f"Could not find consumer impl for {publisher_uri}")

    return Tee(consumer=cons, publisher=pub)


class Tee:
    def __init__(self, consumer, publisher):
        """
        the consumer and dispatchers to tee
        in case the publisher is None, the message will not be forwarded onwards
        :param consumer: any unbound TopicConsumer
        :param publisher: any unbound TopicPublisher
        """
        if consumer is None:
            raise ValueError("consumer can't be None")
        self.consumer = consumer
        self.publisher = publisher
        self.running = False
        self._callback = None
        self._logger = get_logger(self.__class__.__name__)

    def __call__(self, f=None, /, message_decoder=None, message_encoder=None):
        """
        wraps `self.bind` with a decorator.
        arguments are the same
        :return: f
        """
        if f is None:
            return lambda f: self(f, message_decoder=message_decoder, message_encoder=message_encoder)
        self._logger.debug(f"Tee over {self.publisher.topic} decorating {f.__name__}")
        self.bind(f, message_decoder=message_decoder, message_encoder=message_encoder)
        return f

    @property
    def callback(self):
        return self._callback

    def bind(self, f, message_decoder=None, message_encoder=None):
        """
        binds the given function to receive messages from the consumer, and publish its return value
        :param f: callback to bind
        :param message_decoder: decoder to be used by the consumer
        :param message_encoder: encoder to be used by the publisher (if applicable)
        :return:
        """
        if f is None:
            self.stop()
            self._callback = f
            return
        if not callable(f):
            raise TypeError("callback must be either callable or None")
        self._callback = f
        publish_func = f
        if self.publisher:
            publisher_kwargs = {} if not message_encoder else {"message_encoder": message_encoder}
            publish_func = self.publisher.results_publisher(self._callback, **publisher_kwargs)
        self.consumer.bind(publish_func, message_decoder=message_decoder)

    def stop(self):
        """
        stops the consumer and publisher.
        :return:
        """
        self._logger.info("stopping...")
        try:
            self.consumer.stop()
            self.publisher.stop()
            self.running = False
        except Exception as x:
            self._logger.exception(f"Failed to stop: {x}")

    def start(self):
        """
        starts both the consumer and the publisher (in the correct order)
        if any exception happens, stops self
        :return:
        """
        if not self.callback:
            raise ValueError("Can't start unbound tee")
        self._logger.info("starting...")
        component = "publisher"
        try:
            self.publisher.start()
            component = "consumer"
            self.consumer.start()
            self.running = True
        except Exception as x:
            self._logger.exception(f"Failed to start {component}: {x}")
            self.stop()

