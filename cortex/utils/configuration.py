from .decorators import cache_res
import logging

CONFIG_DEBUG_LEVEL = 'debug_level'
CONFIG_CLIENT_CONFIG = 'client_config'
RAW_MESSAGE_REPO = '/tmp/raw_message_repo'

@cache_res
def get_config():
    return {
        CONFIG_DEBUG_LEVEL: logging.DEBUG,
        CONFIG_CLIENT_CONFIG: {},

    }


class topics:
    snapshot = 'snapshot'