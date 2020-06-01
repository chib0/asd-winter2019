import json

import urlpath
from funcy import once_per
from google.protobuf.json_format import MessageToDict

from . import sample_reader, protobuf_parser
from cortex.core import cortex_pb2
from cortex import configuration
from cortex.utils import filesystem

class ClientHTTPSession:
    """
    Implements an HTTPSession with a Cortex host.
    The session is meant to work with a snapshots from a single user.
    """
    SCHEME = 'http'
    @classmethod
    def start(cls, host, port):
        url = urlpath.URL().with_scheme(cls.SCHEME).with_hostinfo(host, port)
        out = cls(url)
        out.get_config()
        return out

    def __init__(self, url, server_config=None):
        self._server_config = server_config
        self.url = urlpath.URL(url)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def get_config(self):
        """ retrieves configuration from the server, if necessary"""
        config_url = self.url / configuration.get_config()[configuration.CONFIG_SERVER_CONFIG_ENDPOINT]
        resp = config_url.get()
        if not resp.ok or resp.status_code != 200:
            raise Exception(f"Couldn't get server config: {resp.status_code}, {resp.text}")
        self._server_config = resp.json()

    def serialize_thought(self, thought, serializer):
        """
        a hook that serializes the thought, doing taking action according to the configuration.
        :param thought:
        :param serializer:
        :return:
        """
        #TODO: add configuration filtering? here?
        return thought.serialize(serializer)

    def send_thought(self, thought, serializer, metadata_serializer):
        """
        sends the thoughts as the current user
        :param thought: the thought to send
        :param serializer: the thought serializer
        :param metadata_serializer: the user metadata serializer
        :return:
        """
        self.ensure_user(thought,  metadata_serializer)
        data = self.serialize_thought(thought, serializer)
        content_type =  'application/octet-stream' if isinstance(data, bytes) else ''
        return self.post_with_content_type(f'user/{thought.user_id}', data, content_type= content_type)

    @once_per('self')
    def ensure_user(self, thought, serializer):
        """ensures that the user is indeed registered on the server"""
        data = thought.serialize_user(serializer)
        return self.post_with_content_type('users', data, 'application/json')

    def post_with_content_type(self, path, data, content_type=None):
        url = self.url / path
        headers = {'Content-Type': content_type} if content_type else {}
        resp = url.post(data=data, headers=headers)
        return resp.ok


ClientSession = ClientHTTPSession

def _upload_sample(thought_collection, session):
    for thought in thought_collection:
            session.send_thought(thought, cortex_pb2.Snapshot.SerializeToString, lambda x: json.dumps(MessageToDict(x)))

def upload_sample(host, port, sample_path):
    """
    uploads the sample at the given path to a cortex host at the given host/port.
    :param host: hostname
    :param port: port
    :param sample_path: path the the samplefile
    :return:
    """
    with filesystem.open_file(sample_path) as sample, ClientSession.start(host, port) as session:
        reader = sample_reader.SampleReader(sample, protobuf_parser.ProtobufSampleParser())
        _upload_sample(reader, session)
