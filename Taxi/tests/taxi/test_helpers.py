from aiohttp import test_utils
import pytest

from taxi.util import helpers


@pytest.mark.parametrize(
    'headers, expected_result',
    [
        ({'X-Real-IP': '1', 'remote_addr': '2', 'X-Forwarded-For': '3'}, '1'),
        ({'remote_addr': '2', 'X-Forwarded-For': '3'}, '2'),
        ({'X-Forwarded-For': '3'}, '3'),
        ({'X-Forwarded-For': ' 1 , 2, 3 '}, '1'),
        ({'X-Forwarded-For': ' 1 , 2 '}, '1'),
        ({'X-Forwarded-For': ' 1, '}, '1'),
        ({'X-Forwarded-For': ','}, None),
        ({'X-Real-IP': '', 'remote_addr': '', 'X-Forwarded-For': '3'}, '3'),
        ({'X-Real-IP': ''}, None),
        ({}, None),
    ],
)
@pytest.mark.nofilldb()
def test_get_user_ip(headers, expected_result):
    request = test_utils.make_mocked_request('GET', '/', headers=headers)
    assert helpers.get_user_ip(request) == expected_result
