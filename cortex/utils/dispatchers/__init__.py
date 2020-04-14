from cortex import utils
from . import *

module_logger = utils.logging.get_module_logger(__name__)



def get_dispatcher(url, topics, *args, **kwargs):
    with utils.logging.log_exception(module_logger,
                                     format="URL Scheme does not match rabbitmq://host:port"):



