from .decorators import cache_res
import logging

CONFIG_DEBUG_LEVEL = 'debug_level'
CONFIG_CLIENT_CONFIG = 'client_config'
CONFIG_SERVER_THREAD_NAME = 'backend_thread_name'
CONFIG_SERVER_CONFIG_ENDPOINT = 'client_configuration_endpoint'
CONFIG_SERVER_PUBLISH_TOPICS = 'server_publish_topics'
CONFIG_RAW_MESSAGE_REPO = 'server_snapshot_location'
RAW_MESSAGE_REPO = '/tmp/raw_message_repo'

@cache_res
def get_config():
    return {
        CONFIG_DEBUG_LEVEL: logging.ERROR,
        CONFIG_CLIENT_CONFIG: {},
        CONFIG_SERVER_THREAD_NAME: "cortex_backend_server",
        CONFIG_SERVER_CONFIG_ENDPOINT: '/configuration',
        CONFIG_SERVER_PUBLISH_TOPICS: ['test1'],
        CONFIG_RAW_MESSAGE_REPO: RAW_MESSAGE_REPO
    }


class topics:
    snapshot = 'snapshot'
