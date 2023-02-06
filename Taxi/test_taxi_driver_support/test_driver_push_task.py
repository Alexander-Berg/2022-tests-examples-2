# pylint: disable=unused-variable
import pytest

from taxi import discovery

from taxi_driver_support import stq_task
from test_taxi_driver_support import conftest


@pytest.mark.now('2019-11-12T12:00:00+00:00')
@pytest.mark.config(DRIVER_SUPPORT_ENABLE_CLIENT_NOTIFY_PUSH=True)
@pytest.mark.parametrize(
    'chat_id, task_id, task_kwargs, driver_uuid, db_id, driver_offline, lang,'
    'expected_action_link, support_chat_response',
    [
        (
            '5bd8249c779fb33f90e2b45a',
            '5b436ca8779fb3302cc784bf',
            {},
            '9dcc7f3a81c94e528176c4aa4a6d22e0',
            'ee6aad2097104bde9a5debbf2d814171',
            True,
            'ru',
            'taximeter://screen/support/chat',
            {
                'id': '5b436ece779fb3302cc784b0',
                'metadata': {
                    'db': 'ee6aad2097104bde9a5debbf2d814171',
                    'driver_uuid': '9dcc7f3a81c94e528176c4aa4a6d22e0',
                    'user_locale': 'ru',
                    'new_messages': 3,
                },
            },
        ),
        (
            '5bd8249c779fb33f90e2b45a',
            '5b436ca8779fb3302cc784bf',
            {},
            '9dcc7f3a81c94e528176c4aa4a6d22e0',
            'ee6aad2097104bde9a5debbf2d814171',
            False,
            'ru',
            'taximeter://screen/support/chat',
            {
                'id': '5b436ece779fb3302cc784b0',
                'participants': [
                    {'role': 'support'},
                    {'author_id': 'support'},
                    {'role': 'driver'},
                ],
                'metadata': {
                    'db': 'ee6aad2097104bde9a5debbf2d814171',
                    'driver_uuid': '9dcc7f3a81c94e528176c4aa4a6d22e0',
                    'user_locale': 'ru',
                    'new_messages': 3,
                    'platform': 'vezet',
                },
            },
        ),
        (
            '5bd8249c779fb33f90e2b45a',
            '5b436ca8779fb3302cc784bf',
            {},
            '9dcc7f3a81c94e528176c4aa4a6d22e0',
            'ee6aad2097104bde9a5debbf2d814171',
            True,
            'en',
            'taximeter://screen/support/chat',
            {
                'id': '5b436ece779fb3302cc784b0',
                'participants': [
                    {'role': 'support'},
                    {'author_id': 'support'},
                ],
                'metadata': {
                    'db': 'ee6aad2097104bde9a5debbf2d814171',
                    'driver_uuid': '9dcc7f3a81c94e528176c4aa4a6d22e0',
                    'user_locale': 'en',
                    'new_messages': 3,
                },
            },
        ),
        (
            '5bd8249c779fb33f90e2b45a',
            '5b436ca8779fb3302cc784bf',
            {},
            '9dcc7f3a81c94e528176c4aa4a6d22e0',
            'ee6aad2097104bde9a5debbf2d814171',
            False,
            'en',
            'taximeter://screen/support/chat',
            {
                'id': '5b436ece779fb3302cc784b0',
                'participants': [
                    {'role': 'support'},
                    {'author_id': 'support'},
                    {'role': 'driver'},
                    {'role': 'driver'},
                ],
                'metadata': {
                    'db': 'ee6aad2097104bde9a5debbf2d814171',
                    'driver_uuid': '9dcc7f3a81c94e528176c4aa4a6d22e0',
                    'user_locale': 'en',
                    'new_messages': 3,
                    'platform': 'taximeter',
                },
            },
        ),
        (
            '5bd8249c779fb33f90e2b45a',
            '5b436ca8779fb3302cc784bf',
            {'message_key': 'user_chat.csat_request'},
            '9dcc7f3a81c94e528176c4aa4a6d22e0',
            'ee6aad2097104bde9a5debbf2d814171',
            False,
            'ru',
            'uber://screen/support/chat',
            {
                'id': '5b436ece779fb3302cc784b0',
                'participants': [
                    {'role': 'support'},
                    {'author_id': 'support'},
                    {'role': 'driver'},
                ],
                'metadata': {
                    'db': 'ee6aad2097104bde9a5debbf2d814171',
                    'driver_uuid': '9dcc7f3a81c94e528176c4aa4a6d22e0',
                    'user_locale': 'ru',
                    'new_messages': 3,
                    'platform': 'uberdriver',
                },
            },
        ),
    ],
)
@pytest.mark.translations(**conftest.TRANSLATIONS)
async def test_driver_push_client_notify(
        taxi_driver_support_app_stq,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        chat_id,
        task_id,
        task_kwargs,
        driver_uuid,
        db_id,
        driver_offline,
        lang,
        expected_action_link,
        support_chat_response,
):
    @patch_aiohttp_session(discovery.find_service('support_chat').url, 'GET')
    def patch_support_chat_request(method, url, **kwargs):
        assert method == 'get'
        return response_mock(json=support_chat_response)

    def _check_notification_action(**kwargs):
        data = kwargs['json']
        message_key = task_kwargs.get('message_key', 'user_chat.new_message')
        message_text = conftest.TRANSLATIONS['notify'][message_key][lang]
        assert data == {
            'intent': 'PersonalOffer',
            'service': 'taximeter',
            'client_id': db_id + '-' + driver_uuid,
            'ttl': 30,
            'data': {
                'id': task_id,
                'action': conftest.TRANSLATIONS['taximeter_messages'][
                    'notification_open_driver_messages'
                ][lang],
                'action_link_need_auth': False,
                'need_notification': False,
            },
            'notification': {
                'text': message_text,
                'link': expected_action_link,
            },
        }

        if driver_offline:
            return mockserver.make_response(
                json={'error': {'text': 'Driver is offline'}}, status=400,
            )
        return mockserver.make_response(json={})

    def _check_unread_messages_action(**kwargs):
        data = kwargs['json']
        assert data == {
            'intent': 'UnreadSupportMessages',
            'service': 'taximeter',
            'client_id': db_id + '-' + driver_uuid,
            'ttl': 30,
            'data': {
                'id': task_id,
                'count': 3,
                'version': '2019-11-12T12:00:00Z',
            },
        }

        if driver_offline:
            return mockserver.make_response(
                json={'error': {'text': 'Driver is offline'}}, status=400,
            )
        return mockserver.make_response(json={})

    @mockserver.json_handler('/client-notify/v2/push')
    def patch_client_notify_request(request):
        assert request.method == 'POST'
        data = request.json
        if data['intent'] == 'PersonalOffer':
            return _check_notification_action(json=data)
        return _check_unread_messages_action(json=data)

    await stq_task.driver_push(
        taxi_driver_support_app_stq, chat_id, task_id, **task_kwargs,
    )


@pytest.mark.now('2019-11-12T12:00:00+00:00')
@pytest.mark.config(DRIVER_SUPPORT_ENABLE_CLIENT_NOTIFY_PUSH=True)
@pytest.mark.parametrize(
    (
        'task_kwargs',
        'push_count',
        'new_messages_count_expected',
        'support_chat_response',
    ),
    [
        (
            {'zero_messages': True},
            1,
            0,
            {
                'id': '5b436ece779fb3302cc784b0',
                'metadata': {
                    'db': 'ee6aad2097104bde9a5debbf2d814171',
                    'driver_uuid': '9dcc7f3a81c94e528176c4aa4a6d22e0',
                    'user_locale': 'ru',
                    'new_messages': 0,
                },
            },
        ),
        (
            {},
            2,
            3,
            {
                'id': '5b436ece779fb3302cc784b0',
                'metadata': {
                    'db': 'ee6aad2097104bde9a5debbf2d814171',
                    'driver_uuid': '9dcc7f3a81c94e528176c4aa4a6d22e0',
                    'user_locale': 'ru',
                    'new_messages': 3,
                },
            },
        ),
        (
            {'message_key': 'user_chat.csat_request'},
            1,
            0,
            {
                'id': '5b436ece779fb3302cc784b0',
                'metadata': {
                    'db': 'ee6aad2097104bde9a5debbf2d814171',
                    'driver_uuid': '9dcc7f3a81c94e528176c4aa4a6d22e0',
                    'user_locale': 'ru',
                    'new_messages': 0,
                },
            },
        ),
        (
            {},
            0,
            0,
            {
                'id': '5b436ece779fb3302cc784b0',
                'metadata': {
                    'db': 'ee6aad2097104bde9a5debbf2d814171',
                    'driver_uuid': '9dcc7f3a81c94e528176c4aa4a6d22e0',
                    'user_locale': 'ru',
                    'new_messages': 0,
                },
            },
        ),
    ],
)
@pytest.mark.translations(**conftest.TRANSLATIONS)
async def test_driver_push_unread_messages_client_notify(
        taxi_driver_support_app_stq,
        patch_aiohttp_session,
        mockserver,
        response_mock,
        task_kwargs,
        push_count,
        new_messages_count_expected,
        support_chat_response,
):
    @patch_aiohttp_session(discovery.find_service('support_chat').url, 'GET')
    def patch_support_chat_request(method, url, **kwargs):
        assert method == 'get'
        return response_mock(json=support_chat_response)

    @mockserver.json_handler('/client-notify/v2/push')
    def patch_client_notify_request(request, **kwargs):
        assert request.method == 'POST'
        data = request.json
        intent = data['intent']
        if not push_count:
            assert intent == 'UnreadSupportMessages'
        else:
            if intent == 'UnreadSupportMessages':
                assert (
                    request.json['data']['count']
                    == new_messages_count_expected
                )
        return mockserver.make_response(json={})

    chat_id = '5bd8249c779fb33f90e2b45a'
    task_id = '5b436ca8779fb3302cc784bf'
    await stq_task.driver_push(
        taxi_driver_support_app_stq, chat_id, task_id, **task_kwargs,
    )
    assert patch_client_notify_request.times_called == push_count


@pytest.mark.now('2019-11-12T12:00:00+00:00')
@pytest.mark.config(DRIVER_SUPPORT_ENABLE_CLIENT_NOTIFY_PUSH=False)
@pytest.mark.parametrize(
    'chat_id, task_id, task_kwargs, driver_uuid, db_id, driver_offline, lang,'
    'expected_action_link, support_chat_response',
    [
        (
            '5bd8249c779fb33f90e2b45a',
            '5b436ca8779fb3302cc784bf',
            {},
            '9dcc7f3a81c94e528176c4aa4a6d22e0',
            'ee6aad2097104bde9a5debbf2d814171',
            True,
            'ru',
            'taximeter://screen/support/chat',
            {
                'id': '5b436ece779fb3302cc784b0',
                'metadata': {
                    'db': 'ee6aad2097104bde9a5debbf2d814171',
                    'driver_uuid': '9dcc7f3a81c94e528176c4aa4a6d22e0',
                    'user_locale': 'ru',
                    'new_messages': 3,
                },
            },
        ),
        (
            '5bd8249c779fb33f90e2b45a',
            '5b436ca8779fb3302cc784bf',
            {},
            '9dcc7f3a81c94e528176c4aa4a6d22e0',
            'ee6aad2097104bde9a5debbf2d814171',
            False,
            'ru',
            'taximeter://screen/support/chat',
            {
                'id': '5b436ece779fb3302cc784b0',
                'participants': [
                    {'role': 'support'},
                    {'author_id': 'support'},
                    {'role': 'driver'},
                ],
                'metadata': {
                    'db': 'ee6aad2097104bde9a5debbf2d814171',
                    'driver_uuid': '9dcc7f3a81c94e528176c4aa4a6d22e0',
                    'user_locale': 'ru',
                    'new_messages': 3,
                    'platform': 'vezet',
                },
            },
        ),
        (
            '5bd8249c779fb33f90e2b45a',
            '5b436ca8779fb3302cc784bf',
            {},
            '9dcc7f3a81c94e528176c4aa4a6d22e0',
            'ee6aad2097104bde9a5debbf2d814171',
            True,
            'en',
            'taximeter://screen/support/chat',
            {
                'id': '5b436ece779fb3302cc784b0',
                'participants': [
                    {'role': 'support'},
                    {'author_id': 'support'},
                ],
                'metadata': {
                    'db': 'ee6aad2097104bde9a5debbf2d814171',
                    'driver_uuid': '9dcc7f3a81c94e528176c4aa4a6d22e0',
                    'user_locale': 'en',
                    'new_messages': 3,
                },
            },
        ),
        (
            '5bd8249c779fb33f90e2b45a',
            '5b436ca8779fb3302cc784bf',
            {},
            '9dcc7f3a81c94e528176c4aa4a6d22e0',
            'ee6aad2097104bde9a5debbf2d814171',
            False,
            'en',
            'taximeter://screen/support/chat',
            {
                'id': '5b436ece779fb3302cc784b0',
                'participants': [
                    {'role': 'support'},
                    {'author_id': 'support'},
                    {'role': 'driver'},
                    {'role': 'driver'},
                ],
                'metadata': {
                    'db': 'ee6aad2097104bde9a5debbf2d814171',
                    'driver_uuid': '9dcc7f3a81c94e528176c4aa4a6d22e0',
                    'user_locale': 'en',
                    'new_messages': 3,
                    'platform': 'taximeter',
                },
            },
        ),
        (
            '5bd8249c779fb33f90e2b45a',
            '5b436ca8779fb3302cc784bf',
            {'message_key': 'user_chat.csat_request'},
            '9dcc7f3a81c94e528176c4aa4a6d22e0',
            'ee6aad2097104bde9a5debbf2d814171',
            False,
            'ru',
            'uber://screen/support/chat',
            {
                'id': '5b436ece779fb3302cc784b0',
                'participants': [
                    {'role': 'support'},
                    {'author_id': 'support'},
                    {'role': 'driver'},
                ],
                'metadata': {
                    'db': 'ee6aad2097104bde9a5debbf2d814171',
                    'driver_uuid': '9dcc7f3a81c94e528176c4aa4a6d22e0',
                    'user_locale': 'ru',
                    'new_messages': 3,
                    'platform': 'uberdriver',
                },
            },
        ),
    ],
)
@pytest.mark.translations(**conftest.TRANSLATIONS)
async def test_driver_push_communications(
        taxi_driver_support_app_stq,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        chat_id,
        task_id,
        task_kwargs,
        driver_uuid,
        db_id,
        driver_offline,
        lang,
        expected_action_link,
        support_chat_response,
):
    @patch_aiohttp_session(discovery.find_service('support_chat').url, 'GET')
    def patch_support_chat_request(method, url, **kwargs):
        assert method == 'get'
        return response_mock(json=support_chat_response)

    def _check_notification_action(**kwargs):
        params = kwargs['params']
        assert params == {
            'action': 'PersonalOffer',
            'code': '1300',
            'dbid': db_id,
            'uuid': driver_uuid,
            'ttl': '30',
        }

        if driver_offline:
            return mockserver.make_response(
                json={'error': {'text': 'Driver is offline'}}, status=400,
            )

        data = kwargs['json']
        message_key = task_kwargs.get('message_key', 'user_chat.new_message')
        message_text = conftest.TRANSLATIONS['notify'][message_key][lang]
        assert data == {
            'data': {
                'id': task_id,
                'text': message_text,
                'action': conftest.TRANSLATIONS['taximeter_messages'][
                    'notification_open_driver_messages'
                ][lang],
                'action_link': expected_action_link,
                'action_link_need_auth': False,
                'need_notification': False,
            },
        }
        return mockserver.make_response(json={})

    def _check_unread_messages_action(**kwargs):
        params = kwargs['params']
        assert params == {
            'action': 'UnreadSupportMessages',
            'code': '1500',
            'dbid': db_id,
            'uuid': driver_uuid,
            'ttl': '30',
        }

        if driver_offline:
            return mockserver.make_response(
                json={'error': {'text': 'Driver is offline'}}, status=400,
            )

        assert kwargs['json'] == {
            'data': {
                'id': task_id,
                'count': 3,
                'version': '2019-11-12T12:00:00Z',
            },
        }
        return mockserver.make_response(json={})

    @mockserver.json_handler('/communications/driver/notification/push')
    def patch_communications_request(request):
        assert request.method == 'POST'
        data = request.query
        if data['action'] == 'PersonalOffer':
            return _check_notification_action(params=data, json=request.json)
        return _check_unread_messages_action(params=data, json=request.json)

    await stq_task.driver_push(
        taxi_driver_support_app_stq, chat_id, task_id, **task_kwargs,
    )


@pytest.mark.now('2019-11-12T12:00:00+00:00')
@pytest.mark.config(DRIVER_SUPPORT_ENABLE_CLIENT_NOTIFY_PUSH=False)
@pytest.mark.parametrize(
    (
        'task_kwargs',
        'push_count',
        'new_messages_count_expected',
        'support_chat_response',
    ),
    [
        (
            {'zero_messages': True},
            1,
            0,
            {
                'id': '5b436ece779fb3302cc784b0',
                'metadata': {
                    'db': 'ee6aad2097104bde9a5debbf2d814171',
                    'driver_uuid': '9dcc7f3a81c94e528176c4aa4a6d22e0',
                    'user_locale': 'ru',
                    'new_messages': 0,
                },
            },
        ),
        (
            {},
            2,
            3,
            {
                'id': '5b436ece779fb3302cc784b0',
                'metadata': {
                    'db': 'ee6aad2097104bde9a5debbf2d814171',
                    'driver_uuid': '9dcc7f3a81c94e528176c4aa4a6d22e0',
                    'user_locale': 'ru',
                    'new_messages': 3,
                },
            },
        ),
        (
            {'message_key': 'user_chat.csat_request'},
            1,
            0,
            {
                'id': '5b436ece779fb3302cc784b0',
                'metadata': {
                    'db': 'ee6aad2097104bde9a5debbf2d814171',
                    'driver_uuid': '9dcc7f3a81c94e528176c4aa4a6d22e0',
                    'user_locale': 'ru',
                    'new_messages': 0,
                },
            },
        ),
        (
            {},
            0,
            0,
            {
                'id': '5b436ece779fb3302cc784b0',
                'metadata': {
                    'db': 'ee6aad2097104bde9a5debbf2d814171',
                    'driver_uuid': '9dcc7f3a81c94e528176c4aa4a6d22e0',
                    'user_locale': 'ru',
                    'new_messages': 0,
                },
            },
        ),
    ],
)
@pytest.mark.translations(**conftest.TRANSLATIONS)
async def test_driver_push_unread_messages_communication(
        taxi_driver_support_app_stq,
        patch_aiohttp_session,
        mockserver,
        response_mock,
        task_kwargs,
        push_count,
        new_messages_count_expected,
        support_chat_response,
):
    @patch_aiohttp_session(discovery.find_service('support_chat').url, 'GET')
    def patch_support_chat_request(method, url, **kwargs):
        assert method == 'get'
        return response_mock(json=support_chat_response)

    @mockserver.json_handler('/communications/driver/notification/push')
    def patch_communications_request(request, **kwargs):
        assert request.method == 'POST'
        data = request.query
        action = data['action']
        if not push_count:
            assert action == 'UnreadSupportMessages'
        else:
            if action == 'UnreadSupportMessages':
                assert (
                    request.json['data']['count']
                    == new_messages_count_expected
                )
        return mockserver.make_response(json={})

    chat_id = '5bd8249c779fb33f90e2b45a'
    task_id = '5b436ca8779fb3302cc784bf'
    await stq_task.driver_push(
        taxi_driver_support_app_stq, chat_id, task_id, **task_kwargs,
    )
    assert patch_communications_request.times_called == push_count
