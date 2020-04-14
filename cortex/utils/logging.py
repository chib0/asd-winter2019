import contextlib
import itertools
import logging
import sys

from cortex.utils import configuration


def get_logger(name, custom_handlers=()):
    """
    gets a uniformally configured logger for the project.
    adds a default handler that is defined by the configuration.

    :param name: the name of the logger
    :param custom_handlers: an iterable of handlers to add to the logger. all handlers are normat python logging ones.
    """
    # create logger with 'spam_application'
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    config = configuration.get_config()
    # create file handler which logs even debug messages
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    default_handler = logging.FileHandler(config['log_file']) if config.get('log_file', None) else \
        logging.StreamHandler(sys.stdout)

    for handler in itertools.chain(custom_handlers, [default_handler]):
        handler.setLevel(config[configuration.CONFIG_DEBUG_LEVEL])
        # create console handler with a higher log level
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

def get_instance_logger(instance):
    return get_logger(instance.__class__.__name__)

class log_exception(contextlib.suppress):
    def __init__(self, logger, to_suppress=(), to_ignore=(), format=None):
        """
        will log exceptions that happen in its block. will suppress exceptions *if explicitly listed*
        :param logger: the logger to log with.
        :param to_suppress: exceptions to suppress but still log
        :param to_ignore: exceptions that will not be logged
        :param formatter: the message to log, or a function that gets the exception instance and returns a message
        """
        super().__init__(to_suppress)
        self._try_suppress = not to_suppress == ()
        self._logger = logger
        self._ignore = to_ignore
        self._formatter = format

    def get_message(self, e):
        if not self._formatter:
            return f"{e}"
        elif callable(self._formatter):
            return self._formatter(e)
        return self._formatter

    def __exit__(self, exctype, excinst, exctb):
        if exctype is not None and not issubclass(exctype, self._ignore):  # shamelessly stolen from supress's __exit__
            self._logger.exception(self.get_message(excinst))

        return self._try_suppress and super().__exit__(exctype, excinst, exctb)


def get_module_logger(name):
    return get_logger(name)