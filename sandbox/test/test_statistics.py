from os import remove
from sandbox.projects.common.yabs.server.requestlog import get_statistics
from tempfile import NamedTemporaryFile
import pytest

REQUEST_LOG = '''
44	2021-02-08 15:01:18.271 +0300	::1:36796	200	7	29
GET /count/tre HTTP/1.1
asdeasdeasdeasdeasde

80	2021-02-08 15:01:18.271 +0300	::1:36796	200	5	29
GET /count/avc HTTP/1.1
76547654765476547654765476547654765476547654765476547654

80	2021-02-08 15:01:18.271 +0300	::1:36796	200	5	29
GET /count/avc HTTP/1.1
76547654765476547654765476547654765476547654765476547654

48	2021-02-08 15:01:18.271 +0300	::1:36796	200	19	29
GET /skip2 HTTP/1.1
8756875687568756875687568756

48	2021-02-08 15:01:18.271 +0300	::1:36796	200	19	29
GET /skip2 HTTP/1.1
8756875687568756875687568756

48	2021-02-08 15:01:18.271 +0300	::1:36796	200	19	29
GET /skip2 HTTP/1.1
8756875687568756875687568756

59	2021-02-08 15:01:18.271 +0300	::1:36796	200	5	29
GET /skip1 HTTP/1.1
123123123123123123123123123123123123123

59	2021-02-08 15:01:18.271 +0300	::1:36796	200	5	29
GET /skip1 HTTP/1.1
123123123123123123123123123123123123123

29	2021-02-08 15:01:18.271 +0300	::1:36796	200	3	29
GET /ping HTTP/1.1
1111111111

29	2021-02-08 15:01:18.271 +0300	::1:36796	200	3	29
GET /ping HTTP/1.1
1111111111
'''

UNEXPECTED_FIELDS = ['/count/tre', '/count/avc', '/skip2', '/skip1', '/ping']
EXPECTED_FIELDS = {
    'count': {
        'count': 3,
        'request_size': 204,
        'response_size': 17
    },
    'skip2': {
        'count': 3,
        'request_size': 144,
        'response_size': 57
    },
    'skip1': {
        'count': 2,
        'request_size': 118,
        'response_size': 10
    },
    'ping': {
        'count': 2,
        'request_size': 58,
        'response_size': 6
    }
}


@pytest.fixture
def request_path():
    request_log = NamedTemporaryFile(mode='w', delete=False)
    request_log.file.write(REQUEST_LOG)
    request_log.close()
    yield request_log.name
    remove(request_log.name)


@pytest.mark.parametrize('ignore_handlers', [
    [],
    ['skip1'],
    ['skip2'],
    ['skip1', 'skip2'],
])
def test_statistics(ignore_handlers, request_path):
    statistics = get_statistics(request_path, ignore_handlers=ignore_handlers)

    for field in UNEXPECTED_FIELDS + ignore_handlers:
        assert field not in statistics

    for k, v in EXPECTED_FIELDS.iteritems():
        if k in ignore_handlers:
            continue
        assert k in statistics
        assert statistics[k] == v
