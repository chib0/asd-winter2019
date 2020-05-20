import struct

from io import BytesIO

import pytest
from google.protobuf.message import DecodeError

from cortex.client.protobuf_parser import ProtobufSampleParser
from cortex.client import cortex_pb2

@pytest.fixture()
def thought():
    return cortex_pb2.Snapshot( datetime=10000000,
         pose=dict(translation=dict(x=1, y=2, z=3), rotation=dict(x=4, y=5,z=6,w=7)),
         color_image=cortex_pb2.ColorImage(width=1, height=2, data=b"12345"),
         depth_image = cortex_pb2.DepthImage(width=3, height=4, data=[1.2,1.3]),
         feelings=dict(hunger = 1,    thirst = 2,    exhaustion = 3,    happiness = 4))


@pytest.fixture()
def user_info():
    return cortex_pb2.User(user_id=1, username="test_username", birthday=12354, gender=0)

def _build_message_buffer(message):
    m = message.SerializeToString()
    return struct.pack("I", len(m)) + m

def test_read_message_size():
    size = 0xdeadbeef
    assert ProtobufSampleParser().read_message_size(BytesIO(struct.pack("I", size))) == size

def test_parse_thought(thought):
    b = _build_message_buffer(thought)
    p = ProtobufSampleParser().parse_thought(BytesIO(b))
    assert p.snapshot == thought

def test_parse_user( user_info):
    b = _build_message_buffer(user_info)
    assert ProtobufSampleParser().parse_user(BytesIO(b)) == user_info

def test_next_reads_all_thoughts(user_info, thought):
    """
    next should only return the thoughts, not the user.
    :param parser:
    :return:
    """
    parser = ProtobufSampleParser()
    b = BytesIO(b"".join(_build_message_buffer(x) for x in (user_info, thought, thought)))
    out = parser.next(b)
    assert parser.user == user_info
    while out:
        assert out.snapshot == thought
        out = parser.next(b)

def test_next_reads_only_one_user_and_then_thoughts(user_info, thought):
    parser = ProtobufSampleParser()
    b = BytesIO(b"".join(_build_message_buffer(x) for x in (user_info, thought, user_info, thought)))
    out = parser.next(b)
    with pytest.raises(DecodeError):
        out = parser.next(b)


def test_read_message():
    class Dummy:
        def ParseFromString(self, string):
            self.string = string

    test_string = b'this is a test string'
    test_dummy = Dummy()
    assert ProtobufSampleParser().read_message(BytesIO(struct.pack("I", len(test_string)) + test_string), test_dummy),\
                "returns failure on correct string"
    assert test_string == test_dummy.string

def test_next_reads_user_first(user_info):
    parser = ProtobufSampleParser()
    b = _build_message_buffer(user_info)
    assert parser.next(BytesIO(b)) is None
    assert parser.user == user_info