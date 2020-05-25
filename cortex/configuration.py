import json

from cortex.utils.decorators import cache_res

import logging

CONFIG_DEBUG_LEVEL = 'debug_level'
CONFIG_CLIENT_CONFIG = 'client_config'
CONFIG_SERVER_THREAD_NAME = 'backend_thread_name'
CONFIG_SERVER_CONFIG_ENDPOINT = 'client_configuration_endpoint'
CONFIG_SERVER_PUBLISH_TOPICS = 'server_publish_topics'
CONFIG_RAW_MESSAGE_REPO = 'server_snapshot_location'
RAW_MESSAGE_REPO = '/tmp/raw_message_repo'
CONFIG_RAW_MESSAGE_DECODER = 'raw-message-decoder'
CONFIG_RAW_MESSAGE_ENCODER = 'raw-message-encoder'
CONFIG_PARSER_DIR = 'server-parser-dir'
CONFIG_DISPATCHER_CONSUMER_DIR = 'server-dispatcher-consumer-dir'


@cache_res
def get_config():
    return {
        CONFIG_DEBUG_LEVEL: logging.DEBUG,
        CONFIG_CLIENT_CONFIG: {},
        CONFIG_SERVER_THREAD_NAME: "cortex_backend_server",
        CONFIG_SERVER_CONFIG_ENDPOINT: '/configuration',
        CONFIG_SERVER_PUBLISH_TOPICS: ['test1'],
        CONFIG_RAW_MESSAGE_REPO: RAW_MESSAGE_REPO,
        CONFIG_DISPATCHER_CONSUMER_DIR: (),
        CONFIG_PARSER_DIR : ()

    }


class topics:
    snapshot = 'snapshot'


def get_raw_data_topic_name():
    return topics.snapshot


def get_parsed_data_topic_name(name):
    return f"{name}.parsed"


def raw_message_decoder():
    from cortex.core.snapshot_xcoder import snapshot_decoder
    return snapshot_decoder


def raw_message_encoder():
    from cortex.core.snapshot_xcoder import snapshot_encoder
    return snapshot_encoder