import functools
import json

from cortex.utils.dispatchers import get_dispatcher

def get_topic_dispatcher(topic, uri):
    disp = get_dispatcher(uri, topic)
    return TopicDispatcher.wrap_dispatcher(disp, topic)

class TopicDispatcher:
    """
    An instance of this class uses a dispatcher to post messages about a particular topic.
    it allows direct publishing, as well as binding a function to publish its results.
    """
    @classmethod
    def wrap_dispatcher(cls, topic, dispatcher):
        """
        returns a TopicDispatcher wrapping the original dispatcher.
        :param topic: the topic to publish on
        :param dispatcher: the dispatcher to wrap
        :return: a TopicDispatcher
        """
        wrap = cls(topic, dispatcher)
        return wrap

    def __init__(self, topic, dispatcher):
        self.topic = topic
        self.dispatcher = dispatcher

    def publish(self, data):
        """
        see `TopicDispatcher.dispatch`
        :param data:
        :return:
        """
        self.dispatch(data)

    def dispatch(self, data):
        """
        sends the given data over the original dispatcher with the specified topic
        :param data: the data to send. The data is sent as-is, make sure it matches the underlying dispatcher
        :return:
        """
        if not self.dispatcher.running:
            raise RuntimeError("Could not publish to non-running publisher")
        self.dispatcher.publish(self.topic, data)


    def result_publisher(self, f=None, /, message_encoder=json.dumps):
        """
        returns a function that publishes the results of the given function over the given topic.
        :param f: function to publish results of
        :param message_encoder: encoder to use to publish results. if nothing given, json.dumps used
        :return:
        """
        if f is None:
            return lambda f: self.result_publisher(f, message_encoder=message_encoder)

        @functools.wraps(f)
        def decorator(*args, **kwargs):
            res = f(*args, **kwargs)
            self.publish(message_encoder(res))

        if not (callable(message_encoder) or callable(f)):
            raise TypeError("message_encoder and f must be callable")
        return decorator


    def start(self):
        self.dispatcher.start()

    def stop(self):
        self.dispatcher.stop()
