# pylint: disable=redefined-outer-name
import json

import aiohttp
import pytest

from taxi.clients import http_client
from taxi.clients import sender


@pytest.fixture
async def mock_session(loop):
    session = http_client.HTTPClient(loop=loop)
    yield session
    await session.close()


MOCK_HOST = 'http://kinda_sender_host.x'


@pytest.mark.parametrize(
    'attachments,',
    [
        [
            {
                'filename': 'Test filename',
                'mime_type': 'text/plain',
                'data': 'dGVzdCBhdHRhY2htZW50',
            },
        ],
        [],
        None,
    ],
)
@pytest.mark.parametrize(
    [
        'account_slug',
        'user',
        'campaign_slug',
        'to_email',
        'template_vars',
        'is_async',
    ],
    [
        (
            'account1',
            'user1',
            'campaign1',
            'sender_test@ya.ru',
            {'lol': 'kek'},
            True,
        ),
        ('account1', 'user1', 'campaign1', 'sender_test@ya.ru', None, True),
    ],
)
async def test_transactional_email(
        db,
        aiohttp_client,
        patch,
        account_slug,
        user,
        campaign_slug,
        to_email,
        template_vars,
        is_async,
        attachments,
):
    @patch('taxi.clients.sender.SenderClient._request')
    async def _dummy_request(*args, **kwargs):
        return {'result': {'status': 'OK'}}

    sender_client = sender.SenderClient(
        MOCK_HOST, account_slug, user, aiohttp_client,
    )
    result = await sender_client.send_transactional_email(
        campaign_slug,
        to_email,
        attachments=attachments,
        template_vars=template_vars,
    )
    params = {'to_email': to_email}
    pathname = '/api/0/{}/transactional/{}/send'.format(
        account_slug, campaign_slug,
    )
    send_data = {'async': is_async}

    if template_vars is not None:
        send_data['args'] = json.dumps(template_vars)
    if attachments:
        send_data['attachments'] = attachments
    expected_args = (pathname, params, send_data)

    assert result == {'result': {'status': 'OK'}}
    request_call = _dummy_request.calls[0]
    assert request_call['args'] == expected_args


@pytest.mark.parametrize(
    [
        'account_slug',
        'user',
        'campaign_slug',
        'to_email',
        'send_data',
        'server_error_status',
        'exception',
    ],
    [
        (
            'account1',
            'user1',
            'campaign1',
            'sender_test@ya.ru',
            None,
            401,
            sender.SenderAuthError,
        ),
        (
            'account1',
            'user1',
            'campaign1',
            'sender_test@ya.ru',
            None,
            404,
            sender.SenderNotFoundError,
        ),
        (
            'account1',
            'user1',
            'campaign1',
            'sender_test@ya.ru',
            None,
            500,
            aiohttp.ClientResponseError,
        ),
    ],
)
async def test_sender_fail(
        mock_session,
        response_mock,
        patch,
        account_slug,
        user,
        campaign_slug,
        to_email,
        send_data,
        server_error_status,
        exception,
):
    @patch('aiohttp.ClientSession.post')
    async def _patch_request(*args, **kwargs):
        return response_mock(status=server_error_status)

    sender_client = sender.SenderClient(
        MOCK_HOST, account_slug, user, session=mock_session,
    )
    with pytest.raises(exception):
        await sender_client.send_transactional_email(
            campaign_slug, to_email, send_data,
        )
