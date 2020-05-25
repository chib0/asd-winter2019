import contextlib
from time import sleep

from . import repository
from cortex import configuration
from cortex.utils import dispatchers

class ParserRunner:
    def __init__(self, message_decoder, message_encoder=None):
        """
        creates a new parser runner with a message encoder and decoder to pass to the parser once it starts running.
        :param message_decoder:
        :param message_encoder:
        """
        if not message_decoder or not callable(message_decoder):
            raise ValueError(f"Can't create runner with {type(message_decoder)}. Must be callable")
        self.message_decoder = message_decoder
        self.message_encoder = message_encoder

    def _run_parser_with_uri(self, parser, uri, publisher_uri=None):
        tee = dispatchers.tee.get_topic_tee(in_topic=configuration.get_raw_data_topic_name(),
                                            out_topic=configuration.get_parsed_data_topic_name(parser.target),
                                            consumer_uri=uri,
                                            publisher_uri=publisher_uri or uri)
        parser = parser.parser
        assert callable(parser) or hasattr(parser, 'parse')
        tee.bind(parser if callable(parser) else parser.parse, message_decoder=self.message_decoder,
                                                                message_encoder=self.message_encoder)
        with contextlib.suppress(KeyboardInterrupt):
            tee.start()
            while True:
                if not tee.consumer.running or not tee.publisher.running:
                    sleep(1)
        tee.stop()


    def run_parser_with_uri(self, name, uri, publisher_uri=None):
        parser = repository.get_parser(name)
        if not parser:
            raise RuntimeError(f"No parser for {name}")
        self._run_parser_with_uri(parser, uri, publisher_uri=publisher_uri)


    def run_parser(self, name, data):
        parser = repository.get_parser(name)
        if not parser:
            raise RuntimeError(f"No parser for {name}")
        marshaled_data = self.message_decoder(data)
        callee = parser if callable(parser) else  parser.parse
        return callee(marshaled_data)

