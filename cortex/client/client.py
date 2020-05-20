import urlpath

from . import sample_reader, protobuf_parser
from cortex.core import cortex_pb2
from cortex.utils import configuration


class ClientHTTPSession:
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
        #TODO: add configuration filtering
        return thought.serialize(serializer)

    def send_thought(self, thought, serializer):
        thought_url = self.url / 'user' / str(thought.user_id)
        data =self.serialize_thought(thought, serializer)
        headers = {'Content-Type': 'application/octet-stream'} if not isinstance(data, bytes) else {}
        resp = thought_url.post(data=data, headers=headers)
        return resp.ok

ClientSession = ClientHTTPSession

def _upload_sample(thought_collection, session):
    for thought in thought_collection:
            session.send_thought(thought, cortex_pb2.Snapshot.SerializeToString)

def upload_sample(host, port, sample_path):
    with sample_reader.SampleReader(sample_path, protobuf_parser.ProtobufSampleParser()) as reader, \
                     ClientSession.start(host, port) as session:
        _upload_sample(reader, session)






