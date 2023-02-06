import asyncio

import pytest

from rida.stq import send_notifications


TRANSLATIONS = dict(
    rida={
        'notifications.user.add_bid.title': {'en': 'Added bid'},
        'notifications.user.add_bid.body': {
            'en': 'Suggested price: {price} {currency}',
        },
    },
)

OAUTH_200_RESPONSE = {
    # access_token returned by google is padded with a bunch of dots, idk why
    'access_token': (
        'ya29.c.0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcd'
        'ef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef012'
        '3456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef01234567'
        '89abcdef0123456789abcdef0............................................'
        '.....................................................................'
        '.....................................................................'
        '.....................................................................'
        '.....................................................................'
        '.....................................................................'
        '.....................................................................'
        '.....................................................................'
        '.....................................................................'
        '.....................................................................'
        '.....................................................................'
        '........................'
    ),
    'expires_in': 3599,
    'token_type': 'Bearer',
}

EXPECTED_OAUTH_REQUEST_DATA = {
    'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
    'assertion': (
        'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6InNvbWVfcHJpdmF0ZV9rZXkif'
        'Q.eyJpc3MiOiJzb21lZW1haWxAeWFuZGV4LXRlYW0ucnUiLCJzdWIiOiJzb21lZW1haWx'
        'AeWFuZGV4LXRlYW0ucnUiLCJhdWQiOiJodHRwczovL29hdXRoMi5nb29nbGVhcGlzLmNv'
        'bS90b2tlbiIsInNjb3BlIjoiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vYXV0aC9ma'
        'XJlYmFzZS5tZXNzYWdpbmciLCJpYXQiOjE1ODI3MjUwMDAuMCwiZXhwIjoxNTgyNzI4Nj'
        'AwLjB9.EObuM69telv5IdhyLGE0gqnZby7l2Z9-xqy9BXysmN5-PWdqAYxYcR6Ua9fyOl'
        'Vqyuk2fdDrC5p8DIjYlDDvkgDFyYeeKv8fFZLEl2QzpphKu---V8xVfjAPuuF5jGSAUh'
        '_qcmy_c9BlgyDRAQxG5_t73-jqQmjjZV0PPwMFGXU'
    ),
}

EXPECTED_MESSAGES_SEND_JSON = {
    'message': {
        'android': {
            'notification': {
                'body': 'Suggested price: ' '1000 ',
                'tag': '00000000000000000000000000000000',
                'title': 'Added bid',
            },
            'priority': 'high',
            'ttl': '0s',
        },
        'apns': {
            'headers': {
                'apns-collapse-id': '00000000000000000000000000000000',
                'apns-expiration': '1582725000',
                'apns-priority': '10',
                'apns-topic': 'rida',
            },
            'payload': {
                'aps': {
                    'alert': {
                        'body': 'Suggested ' 'price: ' '1000 ',
                        'title': 'Added ' 'bid',
                    },
                    'badge': 1,
                    'sound': 'default',
                },
            },
        },
        'token': 'firebase_token0',
    },
}


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.now('2020-02-26T13:50:00.000')
async def test_happy_path(stq3_context, patch, mock_handle, response_mock):
    notification_id_counter = 0
    oauth_request_data = None
    messages_send_json = None

    @patch('rida.logic.notifications.models._gen_notification_template_id')
    def _patched_gen_notification_template_id():
        nonlocal notification_id_counter
        template_id = str(notification_id_counter).rjust(32, '0')
        notification_id_counter += 1
        return template_id

    @mock_handle('https://oauth2.googleapis.com/token')
    def _patched_get_access_token(*args, **kwargs):
        nonlocal oauth_request_data
        oauth_request_data = kwargs['data']
        return response_mock(json=OAUTH_200_RESPONSE)

    @mock_handle(
        'https://fcm.googleapis.com/v1/projects/project_id/messages:send',
    )
    def _patched_messages_send(*args, **kwargs):
        nonlocal messages_send_json
        messages_send_json = kwargs['json']
        return response_mock(
            json={'name': 'projects/project_id/messages/message_id'},
        )

    await send_notifications.task(
        stq3_context,
        intent='add_bid',
        user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
        price=1000.3,
    )
    assert _patched_get_access_token.times_called == 1
    assert oauth_request_data == EXPECTED_OAUTH_REQUEST_DATA
    assert _patched_messages_send.times_called == 1
    assert messages_send_json == EXPECTED_MESSAGES_SEND_JSON


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.parametrize(
    'expected_get_access_token_calls',
    [
        pytest.param(
            1,
            marks=[
                pytest.mark.config(
                    RIDA_FIREBASE_SETTINGS={
                        'access_token_ttl': 3600,
                        'access_token_ttl_offset': 60,
                        'http_request_timeout': 10,
                        'http_request_retries': 3,
                    },
                ),
            ],
            id='access_token_cached',
        ),
        pytest.param(
            2,
            marks=[
                pytest.mark.config(
                    RIDA_FIREBASE_SETTINGS={
                        'access_token_ttl': 3600,
                        'access_token_ttl_offset': 3700,
                        'http_request_timeout': 10,
                        'http_request_retries': 3,
                    },
                ),
            ],
            id='access_token_renewed',
        ),
    ],
)
async def test_access_token_renewal(
        stq3_context,
        mock_handle,
        response_mock,
        expected_get_access_token_calls: int,
):
    @mock_handle('https://oauth2.googleapis.com/token')
    def _patched_get_access_token(*args, **kwargs):
        return response_mock(json=OAUTH_200_RESPONSE)

    @mock_handle(
        'https://fcm.googleapis.com/v1/projects/project_id/messages:send',
    )
    def _patched_messages_send(*args, **kwargs):
        return response_mock(
            json={'name': 'projects/project_id/messages/message_id'},
        )

    # no cached access_token, creating new one
    await send_notifications.task(
        stq3_context,
        intent='add_bid',
        user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
        price=1000.3,
    )
    assert _patched_get_access_token.times_called == 1
    assert _patched_messages_send.times_called == 1

    # access_token is cached, update only if need to renew
    await send_notifications.task(
        stq3_context,
        intent='add_bid',
        user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
        price=1000.3,
    )
    assert (
        _patched_get_access_token.times_called
        == expected_get_access_token_calls
    )
    assert _patched_messages_send.times_called == 2


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.parametrize('is_error_during_access_token', [True, False])
@pytest.mark.parametrize('is_error_during_messages_send', [True, False])
async def test_unexpected_error(
        stq3_context,
        mock_handle,
        response_mock,
        is_error_during_access_token: bool,
        is_error_during_messages_send: bool,
):
    @mock_handle('https://oauth2.googleapis.com/token')
    def _patched_get_access_token(*args, **kwargs):
        if is_error_during_access_token:
            return response_mock(status=500)
        return response_mock(json=OAUTH_200_RESPONSE)

    @mock_handle(
        'https://fcm.googleapis.com/v1/projects/project_id/messages:send',
    )
    def _patched_messages_send(*args, **kwargs):
        if is_error_during_messages_send:
            return response_mock(status=500)
        return response_mock(
            json={'name': 'projects/project_id/messages/message_id'},
        )

    await send_notifications.task(
        stq3_context,
        intent='add_bid',
        user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
        price=1000.3,
    )
    if is_error_during_access_token:
        assert _patched_get_access_token.times_called == 3
        assert _patched_messages_send.times_called == 0
    elif is_error_during_messages_send:
        assert _patched_get_access_token.times_called == 1
        assert _patched_messages_send.times_called == 3
    else:
        assert _patched_get_access_token.times_called == 1
        assert _patched_messages_send.times_called == 1


@pytest.mark.translations(**TRANSLATIONS)
async def test_messages_send_404(stq3_context, mock_handle, response_mock):
    @mock_handle('https://oauth2.googleapis.com/token')
    def _patched_get_access_token(*args, **kwargs):
        return response_mock(json=OAUTH_200_RESPONSE)

    @mock_handle(
        'https://fcm.googleapis.com/v1/projects/project_id/messages:send',
    )
    def _patched_messages_send(*args, **kwargs):
        return response_mock(json={'error': 'user not found, duh'}, status=404)

    await send_notifications.task(
        stq3_context,
        intent='add_bid',
        user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
        price=1000.3,
    )
    assert _patched_get_access_token.times_called == 1
    assert _patched_messages_send.times_called == 1


@pytest.mark.translations(**TRANSLATIONS)
async def test_firebase_timeout(
        stq3_context, mock_handle, response_mock, get_stats_by_label_values,
):
    @mock_handle('https://oauth2.googleapis.com/token')
    def _patched_get_access_token(*args, **kwargs):
        return response_mock(json=OAUTH_200_RESPONSE)

    @mock_handle(
        'https://fcm.googleapis.com/v1/projects/project_id/messages:send',
    )
    def _patched_messages_send(*args, **kwargs):
        raise asyncio.TimeoutError

    await send_notifications.task(
        stq3_context,
        intent='add_bid',
        user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
        price=1000.3,
    )
    assert _patched_get_access_token.times_called == 1
    assert _patched_messages_send.times_called == 3
    stats = get_stats_by_label_values(
        stq3_context, {'sensor': 'notifications.sent'},
    )
    assert stats == [
        {
            'kind': 'IGAUGE',
            'labels': {
                'sensor': 'notifications.sent',
                'intent': 'add_bid',
                'is_success': 'timeout',
            },
            'value': 1,
            'timestamp': None,
        },
    ]
