import json
import pathlib
import tempfile
from pathlib import Path

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

CONFIG_DISPATCHER_CONSUMER_DIR = 'server-dispatcher-consumer-dir'
CONFIG_PARSER_DIR = 'server-parser-dir'
CONFIG_SAVER_DIR = 'server-saver-dir'

CONFIG_SERVICE_DOCKER_IMAGES = 'server-docker-image-data'


CONFIG_USER_STORAGE_BASE = 'server-user-shared-storage'


def _shard_storage_base():
    return pathlib.Path(tempfile.mkdtemp(prefix='cortex_tests') if testing() else '/var')


def shared_storage_path():
    out = _shard_storage_base() / "cortex" / "server"
    out.mkdir(parents=True, exist_ok=True)
    return out


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
        CONFIG_PARSER_DIR : (),
        CONFIG_SAVER_DIR: (),
        CONFIG_SERVICE_DOCKER_IMAGES: {'db': MONGO_DB_DOCKER_INFO, 'mq': RABBIT_MQ_DOCKER_INFO},
        CONFIG_USER_STORAGE_BASE: shared_storage_path() / 'users'
    }


def _make_docker_port_list(tcp_ports, udp_ports=()):
    ports = {f"{port}/tcp": port for port in tcp_ports}
    ports.update({f"{port}/upd": port for port in udp_ports})
    return ports

MONGO_DB_DOCKER_INFO = dict(image='mongo:4', ports=_make_docker_port_list([27017]), hostname='some-mongo')
RABBIT_MQ_DOCKER_INFO = dict(image='rabbitmq:3', ports=_make_docker_port_list([5672, 5671, 15672]),
                             hostname='some-rabbit')


class topics:
    snapshot = 'snapshot'
    user_info = 'user_info'


def testing():
    import sys
    return 'test' in sys.argv[0]

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


