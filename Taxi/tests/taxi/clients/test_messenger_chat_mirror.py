# pylint: disable=redefined-outer-name, protected-access
import datetime

import aiohttp
import pytest

from taxi import config
from taxi import discovery
from taxi.clients import messenger_chat_mirror
from taxi.util import dates

NOW = datetime.datetime(2018, 5, 7, 12, 44, 56)


@pytest.fixture
def mock_uuid(patch):
    @patch('uuid.uuid4')
    def _dummy_uuid():
        return 'dummy_uuid'

    return _dummy_uuid


@pytest.fixture
def test_app(test_taxi_app):
    class Config(config.Config):
        MESSENGER_CHAT_API_CLIENT_QOS = {
            '__default__': {'attempts': 3, 'timeout-ms': 3000},
        }

    messenger_chat_mirror_service = discovery.find_service(
        'messenger_chat_mirror',
    )
    test_taxi_app.messenger = (
        messenger_chat_mirror.MessengerChatMirrorApiClient(
            session=test_taxi_app.session,
            service=messenger_chat_mirror_service,
            tvm_client=test_taxi_app.tvm,
            suffix='/api/chatterbox',
            config=Config(test_taxi_app.db),
        )
    )
    return test_taxi_app


@pytest.fixture
def mock_request(patch):
    @patch(
        'taxi.clients.messenger_chat_mirror.'
        'MessengerChatMirrorApiClient._request',
    )
    async def _dummy_request(*args, **kwargs):
        return 'dummy result'

    return _dummy_request


# pylint: disable=too-many-arguments
@pytest.mark.parametrize(
    'method, url, kwargs, aiohttp_kwargs, expected_response, '
    'expected_exception, expected_exception_code, retries',
    [
        (
            'get',
            '/some_url',
            {},
            {'data': None, 'headers': {}, 'json': None, 'params': None},
            {'some': 'response'},
            None,
            None,
            1,
        ),
        (
            'post',
            '/other_url',
            {
                'params': {'some': 'params'},
                'json': {'some': 'json'},
                'user_guid': '123',
            },
            {
                'data': None,
                'headers': {
                    'Content-Type': 'application/json',
                    'X-User-Guid': '123',
                },
                'json': {'some': 'json'},
                'params': {'some': 'params'},
            },
            {'some': 'response'},
            None,
            None,
            1,
        ),
        (
            'post',
            '/binary_url',
            {},
            {'data': None, 'headers': {}, 'json': None, 'params': None},
            b'some response',
            None,
            None,
            1,
        ),
        (
            'post',
            '/error_url',
            {},
            {'data': None, 'headers': {}, 'json': None, 'params': None},
            messenger_chat_mirror.Response.error(
                code='bad_response', text='some_text',
            ),
            messenger_chat_mirror.BadRequestError,
            'bad_response',
            1,
        ),
        (
            'post',
            '/forbidden_url',
            {},
            {'data': None, 'headers': {}, 'json': None, 'params': None},
            messenger_chat_mirror.Response.error(code='forbidden', text=''),
            messenger_chat_mirror.PermissionsError,
            'forbidden',
            1,
        ),
        (
            'post',
            '/server_error_url',
            {},
            {'data': None, 'headers': {}, 'json': None, 'params': None},
            None,
            messenger_chat_mirror.RequestRetriesExceeded,
            None,
            3,
        ),
        (
            'post',
            '/disconnect_url',
            {},
            {'data': None, 'headers': {}, 'json': None, 'params': None},
            None,
            messenger_chat_mirror.RequestRetriesExceeded,
            None,
            3,
        ),
        (
            'post',
            '/parse_error_url',
            {},
            {'data': None, 'headers': {}, 'json': None, 'params': None},
            None,
            messenger_chat_mirror.ParseError,
            None,
            1,
        ),
    ],
)
async def test_request(
        test_app,
        patch_aiohttp_session,
        response_mock,
        method,
        url,
        kwargs,
        aiohttp_kwargs,
        expected_response,
        expected_exception,
        expected_exception_code,
        retries,
):
    @patch_aiohttp_session(
        discovery.find_service('messenger_chat_mirror').url, method,
    )
    def _dummy_request(expected_method, expected_url, **kwargs):
        assert method == expected_method
        assert expected_url == test_app.messenger.baseurl + url
        kwargs.pop('timeout')
        assert kwargs == aiohttp_kwargs

        headers = {'Content-Type': 'application/json'}

        if url == '/binary_url':
            return response_mock(
                headers={'Content-Type': 'application/octet-stream'},
                status=200,
                read=b'some response',
            )
        if url == '/error_url':
            return response_mock(
                headers=headers,
                status=400,
                text='{"status": "error",'
                ' "data": {"code": "bad_response", "text": "some_text"}}',
            )
        if url == '/forbidden_url':
            return response_mock(
                headers=headers,
                status=403,
                text='{"status": "error", "data": {"code": "forbidden"}}',
            )
        if url == '/server_error_url':
            return response_mock(headers=headers, status=500, text='')
        if url == '/disconnect_url':
            raise aiohttp.ClientConnectionError('Connection closed')
        if url == '/parse_error_url':
            return response_mock(
                headers=headers, status=200, json={'some': 'response'},
            )
        return response_mock(
            headers=headers,
            status=200,
            json={'status': 'ok', 'data': {'some': 'response'}},
        )

    exception = None
    exception_type = None
    response = None
    try:
        response = await test_app.messenger._request(
            url, method=method, **kwargs,
        )
    except messenger_chat_mirror.BaseError as _e:
        exception = _e
        exception_type = type(_e)

    assert exception_type == expected_exception
    if expected_exception_code is not None:
        assert exception.error_code == expected_exception_code

    if expected_response is not None:
        if exception is not None:
            assert exception.response == expected_response
        else:
            assert response == expected_response
    assert len(_dummy_request.calls) == retries


# pylint: disable=too-many-arguments
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'method, kwargs, http_method, path, expected_request',
    [
        (
            'get_chat',
            {'chat_id': 'some_chat_id', 'user_guid': '123'},
            'POST',
            '/get_chat',
            {'chat_id': 'some_chat_id'},
        ),
        (
            'get_history',
            {
                'chat_id': 'some_chat_id',
                'include_participants': False,
                'include_metadata': True,
                'message_ids_newer_than': dates.timestring(NOW),
                'user_guid': '123',
            },
            'POST',
            '/get_history',
            {
                'chat_id': 'some_chat_id',
                'include_participants': False,
                'include_metadata': True,
                'newer_than': dates.timestring(NOW),
            },
        ),
        (
            'add_update',
            {
                'chat_id': 'some_chat_id',
                'message_text': 'some message text',
                'message_sender_id': 'some_sender_id',
                'message_sender_role': 'client',
                'user_guid': '123',
            },
            'POST',
            '/add_update',
            {
                'chat_id': 'some_chat_id',
                'request_id': 'dummy_uuid',
                'message': {
                    'sender': {'id': 'some_sender_id', 'role': 'client'},
                    'text': 'some message text',
                },
                'created_date': dates.timestring(NOW),
            },
        ),
        (
            'add_update',
            {
                'chat_id': 'some_chat_id',
                'update_metadata': {'some': 'metadata'},
            },
            'POST',
            '/add_update',
            {
                'chat_id': 'some_chat_id',
                'request_id': 'dummy_uuid',
                'created_date': dates.timestring(NOW),
                'update_metadata': {'some': 'metadata'},
            },
        ),
        (
            'mark_processed',
            {'chat_id': 'some_chat_id', 'user_guid': '123'},
            'POST',
            '/mark_processed',
            {'chat_id': 'some_chat_id'},
        ),
        (
            'search_by_text',
            {'text': 'qqq', 'limit': 10, 'user_guid': '123'},
            'POST',
            '/search_by_text',
            {'text': 'qqq', 'limit': 10},
        ),
        (
            'attach_file',
            {
                'chat_id': 'some_chat_id',
                'sender_id': 'some_sender_id',
                'filename': 'name',
                'file': b'some-binary',
                'content_type': (
                    '{\'Content-Type\': \'application/octet-stream\'}'
                ),
                'user_guid': '123',
            },
            'POST',
            '/upload_attachment'
            '?chat_id=some_chat_id&sender_id=some_sender_id&filename=name',
            b'some-binary',
        ),
        (
            'download_attachment',
            {
                'chat_id': 'some_chat_id',
                'attachment_id': 'some_file_id',
                'user_guid': '123',
            },
            'GET',
            '/download_attachment?chat_id=some_chat_id&'
            'file_id=some_file_id',
            None,
        ),
    ],
)
async def test_methods(
        test_app,
        mock_request,
        mock_uuid,
        method,
        kwargs,
        http_method,
        path,
        expected_request,
):
    result = await getattr(test_app.messenger, method)(**kwargs)
    assert result == 'dummy result'
    request_call = mock_request.calls[0]
    assert request_call['args'] == (path,)
    assert request_call['kwargs']['method'] == http_method
    if 'user_guid' in kwargs:
        assert request_call['kwargs']['user_guid'] == kwargs['user_guid']
    if isinstance(expected_request, dict):
        assert request_call['kwargs']['json'] == expected_request
    elif isinstance(expected_request, bytes):
        assert request_call['kwargs']['data'] == expected_request
    else:
        assert all([v not in request_call['kwargs'] for v in ('json', 'data')])
