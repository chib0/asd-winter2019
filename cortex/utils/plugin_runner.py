import contextlib
from time import sleep

import funcy

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
                if not tee.consumer.running or not tee.publisher.running:
                    sleep(1)
        if blocking:
            tee.stop()

    def run_with_tee(self, name, tee, blocking=False):
        handler = self.repo.get_handler(name)
        if not handler:
            raise RuntimeError(f"No entry for {name} in {self.repo}")
        self._run_with_tee(handler.handler, tee, blocking)

    def _run_with_uri(self, handler, uri, blocking, publisher_uri=None):
        tee = dispatchers.tee.get_topic_tee(in_topic=configuration.get_raw_data_topic_name(),
                                            out_topic=configuration.get_parsed_data_topic_name(handler.target),
                                            consumer_uri=uri,
                                            publisher_uri=publisher_uri or uri)
        parser = handler.handler
        parser = funcy.silent(parser if callable(parser) else parser.parse)

        self._run_with_tee(parser, tee, blocking=blocking)


    def run_with_uri(self, name, uri, publisher_uri=None, blocking=True):
        handler = self.repo.get_handler(name)
        if not handler:
            raise RuntimeError(f"No entry for {name} in {self.repo}")
        self._run_with_uri(handler, uri, blocking, publisher_uri=publisher_uri)


    def run(self, name, data):
        handler = self.repo.get_handler(name)
        if not handler:
            raise RuntimeError(f"No entry for {name} in  in {self.repo}")
        marshaled_data = self.message_decoder(data)
        callee = handler.handler
        return callee(marshaled_data)

