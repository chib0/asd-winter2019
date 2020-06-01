from collections import namedtuple

from cortex.client.sample_reader import SampleReader


def test_sample_reader_user():
    """
    the user is received from the parser, let's supply one in which the user is set
    :return:
    """
    parser = namedtuple("mock", ("user",))
    reader = SampleReader(None, parser("david"))
    assert reader.user == 'david'


def test_sample_reader_iteration():
    class mock_parser:
        def next(self, stream):
            return next(stream)
    thoughts = ["these", "are", "insightful", "words"]
    reader = SampleReader(iter(thoughts), mock_parser())
    assert list(reader) == thoughts




