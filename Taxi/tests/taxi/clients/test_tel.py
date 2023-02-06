# pylint: disable=redefined-outer-name
# pylint: disable=protected-access


import json
import typing
from urllib import parse

import aiohttp
import pytest

from taxi import config
from taxi.clients import tel


@pytest.fixture
def client(db, loop, test_taxi_app):
    class Config(config.Config):
        TEL_MAX_RETRIES = 3
        TEL_TIMEOUT = 1
        TEL_RETRY_DELAY = 1.0
        TEL_DELAY_MULTIPLIER = 1.5
        TEL_MAX_RANDOM_DELAY = 1
        TEL_MAX_DELAY = 4

    secdist = {
        'settings_override': {
            'TEL_ROBOT_NAME': 'some_name',
            'TEL_ROBOT_KEY': 'some_key',
        },
    }

    class Settings:
        url = 'https://tel.yandex-team.ru'
        verify_ssl = False

    return tel.TelClient(Settings, Config(db), test_taxi_app.session, secdist)


@pytest.mark.parametrize(
    'exception_type', [aiohttp.ClientError, aiohttp.ServerTimeoutError],
)
@pytest.mark.nofilldb()
async def test_request_try_and_fail(client, patch, exception_type):
    @patch('aiohttp.ClientSession._request')
    async def _request(*args, **kwargs):
        raise exception_type()

    with pytest.raises(tel.RequestRetriesExceeded):
        await client.list_rules_for_number('999', 'op_queue')


@pytest.mark.nofilldb()
async def empty_queue_list_rules(client):
    with pytest.raises(tel.TelephonyEmptyQueues):
        await client.list_rules_for_number('999', 'op_queue')


@pytest.mark.parametrize(
    'exception_type', [aiohttp.ClientError, aiohttp.ServerTimeoutError],
)
@pytest.mark.nofilldb()
async def test_request_retry_and_succeed(
        client, patch, exception_type, response_mock,
):
    count = 0

    @patch('aiohttp.ClientSession._request')
    async def _request(*args, **kwargs):
        nonlocal count
        count += 1
        if count <= 3:
            raise exception_type()
        else:
            return response_mock(
                json={'STATUS': True, 'STATUSCODE': 200, 'DATA': {}},
            )

    await client.list_rules_for_number('999', 'op_queue')


def _ok_response(data: typing.Any = True):
    return {'STATUS': True, 'STATUSCODE': 200, 'DATA': data}


def _error_response(msg: str):
    return {
        'STATUS': False,
        'STATUSCODE': 400,
        'DATA': False,
        'STATUSMSG': msg,
        'STATUSDESC': None,  # imitate null. yep, this happens.
    }


@pytest.mark.parametrize(
    ['method_name', 'args', 'tel_response', 'expected_resp'],
    [
        (
            'set_action',
            ['telnum', 100, None, 'op_queue'],
            _ok_response(),
            True,
        ),
        (
            'set_action',
            ['telnum', 100, None, 'op_queue'],
            _error_response(tel.ErrorCodes.ENTRY_ALREADY_EXISTS),
            {},
        ),
        (
            'set_action',
            ['telnum', 100, None, 'op_queue'],
            _error_response(tel.ErrorCodes.ENTRY_DOES_NOT_EXIST),
            tel.TelInvalidOperation,
        ),
        ('unset_action', ['telnum', 'op_queue'], _ok_response(), True),
        (
            'unset_action',
            ['telnum', 'op_queue'],
            _error_response(tel.ErrorCodes.ENTRY_ALREADY_EXISTS),
            tel.TelInvalidOperation,
        ),
        (
            'unset_action',
            ['telnum', 'op_queue'],
            _error_response(tel.ErrorCodes.ENTRY_DOES_NOT_EXIST),
            {},
        ),
        (
            'set_route',
            ['telnum', 'dstnum', tel.FOREVER, 'op_queue'],
            _ok_response(),
            True,
        ),
        (
            'get_status',
            ['agent_id'],
            _ok_response({'QUEUES': {}, 'CALLCENTERID': '2'}),
            tel.OperatorState(callcenter_id='2', queues=[]),
        ),
        (
            'connect_to_queues',
            ['agent_id', '1', 'queue1'],
            _ok_response(),
            True,
        ),
        (
            'disconnect_from_queues',
            ['agent_id', '1', 'queue1'],
            _ok_response(),
            True,
        ),
        ('set_status', ['agent_id', 'queue_name'], _ok_response(), True),
        ('delete_user', ['username'], _ok_response(), True),
        (
            'register_user',
            [
                'login',
                'РусскоеИмя',
                'РусскаяФамилия',
                '999',
                'yandex',
                None,
                None,
                None,
            ],
            _ok_response(),
            True,
        ),
        ('block_number', ['telnum', 100, 'op_queue'], _ok_response(), True),
    ],
)
@pytest.mark.nofilldb()
async def test_tel_client_methods(
        client,
        patch,
        response_mock,
        method_name,
        args,
        tel_response,
        expected_resp,
):
    @patch('aiohttp.ClientSession._request')
    async def _request(method, url, *args, data=None, **kwargs):
        url = str(url)  # just in case
        assert method.lower() == 'post'
        parsed_url = parse.urlparse(url)
        query_params = parse.parse_qs(parsed_url.query)
        assert '_data' not in query_params
        assert '_DATA' not in query_params
        if data:
            sent_data = data.get('_DATA')
            assert sent_data is not None
            assert json.loads(sent_data)
        return response_mock(json=tel_response)

    method = getattr(client, method_name)
    if isinstance(expected_resp, type) and issubclass(
            expected_resp, Exception,
    ):
        with pytest.raises(expected_resp):
            await method(*args)
    else:
        result = await method(*args)
        assert result == expected_resp


@pytest.mark.parametrize(
    ['method_name', 'args'],
    [
        ('unset_route', ['telnum', None]),
        ('set_route', ['telnum', 'dstnum', tel.FOREVER, None]),
        ('connect_to_queues', ['agent_id', None]),
        ('disconnect_from_queues', ['agent_id', None]),
        ('block_number', ['agent_id', None, tel.FOREVER]),
    ],
)
@pytest.mark.nofilldb()
async def test_tel_client_methods_empty_queues(client, method_name, args):

    method = getattr(client, method_name)
    with pytest.raises(tel.TelephonyEmptyQueues):
        await method(*args)


@pytest.mark.parametrize(
    'string, key, expected_sign',
    [
        ('', '', 'da39a3ee5e6b4b0d3255bfef95601890afd80709'),
        ('hello', 'there', 'f9a4d6c9b146c1e4a8e9ed904e2f9da5564baed6'),
    ],
)
def test_sign(string, key, expected_sign):
    assert tel._get_sign(string, key) == expected_sign


async def test_prepare_blacklist(patch, response_mock, client):
    number = 'special_number_request'

    tel_response = {
        'TYPE': 'REPLY',
        'STATUSCODE': 200,
        'STATUSMSG': '',
        'STATUSDESC': None,
        'STATUS': 'TRUE',
        'PARAM': {},
        'DATA': {
            '0': {
                'ID': '13386437',
                'QUEUE': 'disp_cc',
                'SRCNUMB': '1234567890',
                'ACTIONID': '400',
                'ACTIONDATA': '',
                'STREAMSRC': '',
                'EXPIREDATE': '1588168130',
            },
            '1': {
                'ID': '1659623',
                'QUEUE': 'disp_cc',
                'SRCNUMB': '1234567891',
                'ACTIONID': '400',
                'ACTIONDATA': '',
                'STREAMSRC': '',
                'EXPIREDATE': '1588168130',
            },
            '2': {
                'ID': '1660644',
                'QUEUE': 'disp_cc',
                'SRCNUMB': '37443214852',
                'ACTIONID': '100',
                'ACTIONDATA': '80086',
                'STREAMSRC': '',
                'EXPIREDATE': '0',
            },
        },
    }

    num_tel_response = {
        'TYPE': 'REPLY',
        'STATUSCODE': 200,
        'STATUSMSG': '',
        'STATUSDESC': None,
        'STATUS': 'TRUE',
        'PARAM': {},
        'DATA': {
            '0': {
                'ID': '13386437',
                'QUEUE': 'disp_cc',
                'SRCNUMB': number,
                'ACTIONID': '400',
                'ACTIONDATA': '',
                'STREAMSRC': '',
                'EXPIREDATE': '1588168130',
            },
        },
    }

    @patch('aiohttp.ClientSession._request')
    async def _request(method, url, *args, **kwargs):
        url = str(url).lower()
        if f'list/{number}' in url:
            return response_mock(json=num_tel_response)
        return response_mock(json=tel_response)

    method = getattr(client, 'list_blacklist_rules')
    blacklist = await method('disp_cc')
    assert isinstance(blacklist, list)
    blocked_numbers = {item.telnum for item in blacklist}
    assert blocked_numbers == {'1234567890', '1234567891'}

    num_blacklist = await method('disp_cc', number)
    assert isinstance(num_blacklist, list)
    blocked_numbers = {item.telnum for item in num_blacklist}
    assert blocked_numbers == {number}
