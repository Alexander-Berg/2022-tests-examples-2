# pylint: disable=redefined-outer-name, protected-access
import datetime

import pytest

from taxi import discovery
from taxi.clients import support_chat
from taxi.util import dates

NOW = datetime.datetime(2018, 5, 7, 12, 44, 56)


@pytest.fixture
def mock_uuid(patch):
    @patch('uuid.uuid4')
    def _dummy_uuid():
        return 'dummy_uuid'

    return _dummy_uuid


@pytest.fixture
def mock_request(patch):
    @patch('taxi.clients.support_chat.SupportChatApiClient._request')
    async def _dummy_request(*args, **kwargs):
        return 'dummy result'

    return _dummy_request


@pytest.mark.parametrize(
    'method, url, kwargs, aiohttp_kwargs, status, expected_response',
    [
        (
            'get',
            '/some_url',
            {},
            {'data': None, 'headers': {}, 'json': None, 'params': None},
            200,
            {'some': 'response'},
        ),
        (
            'post',
            '/other_url',
            {'params': {'some': 'params'}, 'json': {'some': 'json'}},
            {
                'data': None,
                'headers': {'Content-Type': 'application/json'},
                'json': {'some': 'json'},
                'params': {'some': 'params'},
            },
            200,
            {'some': 'response'},
        ),
        (
            'post',
            '/third_url',
            {'data': b'some data', 'content_type': 'application/octet-stream'},
            {
                'data': b'some data',
                'headers': {'Content-Type': 'application/octet-stream'},
                'json': None,
                'params': None,
            },
            200,
            b'some response',
        ),
        (
            'post',
            '/error_url',
            {},
            {'data': None, 'headers': {}, 'json': None, 'params': None},
            400,
            {'some': 'response'},
        ),
    ],
)
async def test_request(
        test_taxi_app,
        patch_aiohttp_session,
        response_mock,
        method,
        url,
        kwargs,
        aiohttp_kwargs,
        status,
        expected_response,
):
    support_chat_service = discovery.find_service('support_chat')

    @patch_aiohttp_session(support_chat_service.url, method)
    def _dummy_request(expected_method, expected_url, **kwargs):
        assert method == expected_method
        assert expected_url == support_chat_service.url + url
        assert kwargs == aiohttp_kwargs
        if kwargs['data']:
            return response_mock(
                read=b'some response',
                headers={'Content-Type': 'application/octet-stream'},
            )
        return response_mock(json={'some': 'response'})

    client = support_chat.SupportChatApiClient(
        support_chat_service,
        session=test_taxi_app.session,
        tvm_client=test_taxi_app.tvm,
    )
    response = await client._request(url, method=method, **kwargs)
    assert response == expected_response
    assert _dummy_request.calls


# pylint: disable=too-many-arguments
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'chat_id,message_text,message_sender_id,message_sender_role,'
    'message_metadata,update_metadata,created_date,expected_request',
    [
        (
            'some_chat_id',
            'some message text',
            'some_sender_id',
            'client',
            None,
            None,
            None,
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
            'some_chat_id',
            None,
            'some_sender_id',
            'system',
            {'some': {'message': 'metadata'}},
            None,
            None,
            {
                'chat_id': 'some_chat_id',
                'request_id': 'dummy_uuid',
                'message': {
                    'sender': {'id': 'some_sender_id', 'role': 'system'},
                    'metadata': {'some': {'message': 'metadata'}},
                },
                'created_date': dates.timestring(NOW),
            },
        ),
        (
            'some_chat_id',
            None,
            None,
            None,
            None,
            {'some': 'metadata'},
            None,
            {
                'chat_id': 'some_chat_id',
                'request_id': 'dummy_uuid',
                'created_date': dates.timestring(NOW),
                'update_metadata': {'some': 'metadata'},
            },
        ),
        (
            'some_chat_id',
            'some message text',
            'some_sender_id',
            'support',
            {'some': {'message': 'metadata'}},
            {'some': 'metadata'},
            datetime.datetime(2018, 5, 1, 12, 34, 56),
            {
                'chat_id': 'some_chat_id',
                'request_id': 'dummy_uuid',
                'message': {
                    'sender': {'id': 'some_sender_id', 'role': 'support'},
                    'metadata': {'some': {'message': 'metadata'}},
                    'text': 'some message text',
                },
                'created_date': dates.timestring(
                    datetime.datetime(2018, 5, 1, 12, 34, 56),
                ),
                'update_metadata': {'some': 'metadata'},
            },
        ),
    ],
)
async def test_add_update(
        db,
        aiohttp_client,
        simple_secdist,
        mock_request,
        mock_uuid,
        chat_id,
        message_text,
        message_sender_id,
        message_sender_role,
        message_metadata,
        update_metadata,
        created_date,
        expected_request,
):

    client = support_chat.SupportChatApiClient(
        discovery.find_service('support_chat'),
        session=aiohttp_client,
        tvm_client=None,
    )
    result = await client.add_update(
        chat_id=chat_id,
        message_text=message_text,
        message_sender_id=message_sender_id,
        message_sender_role=message_sender_role,
        message_metadata=message_metadata,
        update_metadata=update_metadata,
        created_date=created_date,
    )
    assert result == 'dummy result'
    request_call = mock_request.calls[0]
    assert request_call['args'] == ('/v1/chat/{}/add_update'.format(chat_id),)
    assert request_call['kwargs']['method'] == 'POST'
    assert request_call['kwargs']['json'] == expected_request


@pytest.mark.parametrize(
    'owner_id,owner_role,chat_type,include_history,date_newer_than,'
    'date_older_than,date_limit,expected_request_data',
    [
        (
            'some_owner_id',
            'some_owner_role',
            'some_type',
            None,
            None,
            None,
            None,
            {
                'owner': {'id': 'some_owner_id', 'role': 'some_owner_role'},
                'type': 'some_type',
            },
        ),
        (
            'some_owner_id',
            'some_owner_role',
            'some_type',
            True,
            'some_date',
            'another_date',
            123,
            {
                'owner': {'id': 'some_owner_id', 'role': 'some_owner_role'},
                'type': 'some_type',
                'include_history': True,
                'date': {
                    'newer_than': 'some_date',
                    'older_than': 'another_date',
                    'limit': 123,
                },
            },
        ),
    ],
)
async def test_search(
        aiohttp_client,
        mock_request,
        mock_uuid,
        owner_id,
        owner_role,
        chat_type,
        include_history,
        date_newer_than,
        date_older_than,
        date_limit,
        expected_request_data,
):

    client = support_chat.SupportChatApiClient(
        discovery.find_service('support_chat'),
        session=aiohttp_client,
        tvm_client=None,
    )

    result = await client.search(
        owner_id=owner_id,
        owner_role=owner_role,
        chat_type=chat_type,
        include_history=include_history,
        date_newer_than=date_newer_than,
        date_older_than=date_older_than,
        date_limit=date_limit,
    )
    assert result == 'dummy result'
    request_call = mock_request.calls[0]
    assert request_call['args'] == ('/v1/chat/search',)
    assert request_call['kwargs']['method'] == 'POST'
    assert request_call['kwargs']['json'] == expected_request_data


@pytest.mark.parametrize(
    'kwargs,expected_request_data,expected_headers',
    [
        (
            {
                'owner_id': 'some_id',
                'owner_role': 'client',
                'message_text': 'some text',
                'message_sender_id': 'some_id',
                'message_sender_role': 'client',
            },
            {
                'request_id': 'dummy_uuid',
                'owner': {'id': 'some_id', 'role': 'client'},
                'message': {
                    'text': 'some text',
                    'sender': {'id': 'some_id', 'role': 'client'},
                },
            },
            None,
        ),
        (
            {
                'owner_id': 'some_id',
                'owner_role': 'driver',
                'message_text': 'some text',
                'message_sender_id': 'some_id',
                'message_sender_role': 'driver',
                'metadata': {'some': 'meta'},
                'message_metadata': {'message': 'meta'},
                'request_id': 'some_request_id',
                'headers': {'some': 'headers'},
            },
            {
                'request_id': 'some_request_id',
                'owner': {'id': 'some_id', 'role': 'driver'},
                'metadata': {'some': 'meta'},
                'message': {
                    'text': 'some text',
                    'sender': {'id': 'some_id', 'role': 'driver'},
                    'metadata': {'message': 'meta'},
                },
            },
            {'some': 'headers'},
        ),
    ],
)
async def test_create(
        aiohttp_client,
        mock_request,
        mock_uuid,
        kwargs,
        expected_request_data,
        expected_headers,
):

    client = support_chat.SupportChatApiClient(
        discovery.find_service('support_chat'),
        session=aiohttp_client,
        tvm_client=None,
    )

    result = await client.create_chat(**kwargs)
    assert result == 'dummy result'
    request_call = mock_request.calls[0]
    assert request_call['args'] == ('/v1/chat',)
    assert request_call['kwargs']['method'] == 'POST'
    assert request_call['kwargs']['json'] == expected_request_data
    assert request_call['kwargs']['headers'] == expected_headers


@pytest.mark.parametrize(
    'chat_id, attachment_id, sender_id, sender_role, expected_result',
    [
        (
            'chat_id',
            'attachment_id',
            'sender_id',
            'driver',
            '/v1/chat/chat_id/attachment/attachment_id'
            '?sender_id=sender_id&sender_role=driver',
        ),
        (
            'chat_id_1',
            'attachment_id_1',
            'sender_id_1',
            'client',
            '/v1/chat/chat_id_1/attachment/attachment_id_1'
            '?sender_id=sender_id_1&sender_role=client',
        ),
    ],
)
def test_download_url(
        aiohttp_client,
        mock_request,
        chat_id,
        attachment_id,
        sender_id,
        sender_role,
        expected_result,
):

    client = support_chat.SupportChatApiClient(
        discovery.find_service('support_chat'),
        session=aiohttp_client,
        tvm_client=None,
    )
    result = client.download_attach_url(
        chat_id, attachment_id, sender_id, sender_role,
    )
    assert result == expected_result
