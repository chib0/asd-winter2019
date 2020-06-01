"""
This weird thing is meant to accept a repository and run a plugin from it by name.
it passes a message encoder and decoder in so that the plugin itself can have an easy life just accepting the data.


"""

import contextlib
from time import sleep

from cortex import configuration
from cortex.utils import dispatchers

class PluginRunner:
    def __init__(self, repo, message_decoder, message_encoder=None):
        """
        creates a new parser runner with a message encoder and decoder to pass to the parser once it starts running.
        :param message_decoder:
        :param message_encoder:
        """
        self.repo = repo
        if not message_decoder or not callable(message_decoder):
            raise ValueError(f"Can't create runner with {type(message_decoder)}. Must be callable")
        self.message_decoder = message_decoder
        self.message_encoder = message_encoder

    def _run_with_tee(self, handler, tee, blocking):
        tee.bind(handler, message_decoder=self.message_decoder,
                 message_encoder=self.message_encoder)
        with contextlib.suppress(KeyboardInterrupt):
            tee.start()
            while blocking:
                if not (tee.consumer.running and tee.publisher.running):
                    sleep(1)
        if blocking:
            tee.stop()

    def run_with_tee(self, name, tee, blocking=False):
        """
        running the plugin with a pre-created tee.
        this will get the plugin by name, bind it's handler to the tee with the plugin target, and either block or not.
        :param name: name of the plugin to run
        :param tee: the Tee to run this with.
        :param blocking: whether or not to wait for the tee to finish. note that if this is non-blocking the user would have to make sure the tee is stopped correctly.
        :return:
        """
        handler = self.repo.get_handler(name)
        if not handler:
            raise RuntimeError(f"No entry for {name} in {self.repo}")
        self._run_with_tee(handler.handler, tee, blocking)

    def _run_with_uri(self, handler, uri, blocking, publisher_uri=None):
        tee = dispatchers.tee.get_topic_tee(in_topic=configuration.get_raw_data_topic_name() + str(handler.target),
                                            out_topic=configuration.get_parsed_data_topic_name(handler.target),
                                            consumer_uri=uri,
                                            publisher_uri=publisher_uri or uri)
        parser = handler.handler
        parser = parser if callable(parser) else parser.parse

        self._run_with_tee(parser, tee, blocking=blocking)


    def run_with_uri(self, name, uri, publisher_uri=None, blocking=True):
        """
        running the plugin with a given uri.
        This will get the plugin by name, get a consumer from the given uri and a dispatcher on (publisher_uri or uri).
        This pair will then be bound to a Tee, and then start and block if required.
        :param publisher_uri: in case the publisher is on a different server, or a different beast, we allow it to have a different uri.
        :param name: name of the plugin to run
        :param uri: the consumer uri, i.e where to read data from
        :param blocking: whether or not to wait for the tee to finish. note that if this is non-blocking the user would have to make sure the tee is stopped correctly.
        :return:
        """
        handler = self.repo.get_handler(name)
        if not handler:
            raise RuntimeError(f"No entry for {name} in {self.repo}")
        self._run_with_uri(handler, uri, blocking, publisher_uri=publisher_uri)


    def run(self, name, data):
        """
        simply execute the plugin by name on the given data without running it through the pipeline.
        :param name:
        :param data:
        :return:
        """
        handler = self.repo.get_handler(name)
        if not handler:
            raise RuntimeError(f"No entry for {name} in  in {self.repo}")
        marshaled_data = self.message_decoder(data)
        callee = handler.handler
        return callee(marshaled_data)

