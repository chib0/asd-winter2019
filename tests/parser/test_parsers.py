import time
from unittest.mock import MagicMock

import pytest
from cortex.parser.protobuf_parsers import parser_decorators
#from cortex.parser.protobuf_parsers import feelings_parser, image_parser, pose_parser
#from cortex.core import cortex_pb2


""" not testing the parsers themselves because, well I can't undecorate them and they are REALLY simple."""

def test_with_user_calls_decoree_with_user_value():
    f = MagicMock()
    callee = parser_decorators.with_user(f)
    data = {'user': '55'}
    callee(data)
    f.assert_called_once_with('55', data)

def test_with_user_calls_decoree_with_correct_type():
    f = MagicMock()
    callee = parser_decorators.with_user(f, type=int)
    data = {'user': '55'}
    callee(data)
    f.assert_called_once_with(55, data)

def test_with_protobuf_snapshot_unpacks_message():
    f = MagicMock()
    mock_protobuf = MagicMock()
    callee = parser_decorators.with_protobuf_snapshot(mock_protobuf)(f)
    passed_message = {'snapshot': 'some_string'}
    callee(passed_message)

    mock_protobuf.ParseFromString.assert_called_once_with(mock_protobuf.return_value, 'some_string')
    f.assert_called_once_with(mock_protobuf.return_value, passed_message)


def test_with_protobuf_snapshot_unpacks_message_according_to_key():
    f = MagicMock()
    mock_protobuf = MagicMock()
    callee = parser_decorators.with_protobuf_snapshot(mock_protobuf, 'key')(f)
    passed_message = {'key': 'some_string'}
    callee(passed_message)

    mock_protobuf.ParseFromString.assert_called_once_with(mock_protobuf.return_value, 'some_string')
    f.assert_called_once_with(mock_protobuf.return_value, passed_message)


# @pytest.fixture()
# def modules():
#     return feelings_parser, image_parser, pose_parser
# @pytest.fixture
# def mock_snapshot():
#     s = MagicMock()
#     s.timestamp = int(time.time())
#     return s
#
# def _build_message_with(user, snapshot):
#     return {'user': user, 'snapshot': snapshot}
# @pytest.fixture
# def negate_parser_decorators(modules, monkeypatch):
#     """
#     this will allow us to call the actual parser functions without their decorators extracting data for them.
#     the decorators will be separately tested
#     :param monkeypatch:
#     :return:
#     """
#     mock_decorator = MagicMock()
#     mock_decorator.return_value = lambda *args, **kwargs: lambda f, *args, **kwargs: f
#     for module in modules:
#         monkeypatch.setattr(module.decos, 'with_protobuf_snapshot', mock_decorator)
#         monkeypatch.setattr(module.decos, 'with_user', mock_decorator)
#     return mock_decorator
#
#
# def test_feelings_parser_formats_dict_correctly(negate_parser_decorators, mock_snapshot):
#     mock_snapshot = MagicMock()
#     feelings = dict(hunger=1., thirst=2., exhaustion=3.,happiness=4.)
#     mock_snapshot.feelings = cortex_pb2.Feelings(**feelings)
#     res = feelings_parser.parse_feelings(1, mock_snapshot)
#     assert res['user'] == 1
#     assert res['result'] == {'feelings': feelings}
#     assert res['timestamp'] == mock_snapshot.timestamp
#



def test_feelings_parser():
    pass