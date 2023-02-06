import json

import pytest

from taxi_protocol.handlers import support_chat2


@pytest.mark.parametrize(
    'setting_name',
    [
        'simple',
        'add_header_meta',
        'add_user_phone',
        'add_yandex_uid',
        'add_eats_uid',
        'add_message_metadata',
        'exclude_attachments',
        'add_lavka_store_id',
        'add_user_id',
    ],
)
def test_create_metadata(load_json, setting_name):
    setting = load_json('metadata.json')[setting_name]
    # pylint: disable=protected-access
    metadata = support_chat2._create_metadata(**setting['input'])
    assert metadata == setting['expected_metadata']


@pytest.mark.usefixtures(
    'mock_get_users', 'mock_stq_put', 'mock_get_user_phone_from_db',
)
@pytest.mark.config(TVM_RULES=[{'src': 'protocol-py3', 'dst': 'support_chat'}])
@pytest.mark.parametrize(
    'prefix',
    [
        '4.0/lab/support_chat',
        '4.0/support_chat',
        'eats/v1/support_chat',
        'eats/v1/website_support_chat',
        'eats/v1/restapp_support_chat',
    ],
)
@pytest.mark.parametrize(
    ('request_name', 'chat_new_setting', 'expected'),
    [
        ('taxi', 'taxi', 'success_taxi'),
        ('safety_center', 'safety_center', 'success_safety_center'),
        ('eats', 'eats', 'success_eats'),
        ('eats_app', 'eats_app', 'success_eats_app'),
        ('help_yandex_ru', 'help_yandex_ru', 'success_help'),
        ('labs_admin_yandex_ru', 'labs_admin_yandex_ru', 'success_labs'),
        ('drive', 'drive', 'success_drive'),
        ('scouts', 'scouts', 'success_drive'),
        ('no_message_id', 'empty', 'bad_request'),
        ('no_type', 'empty', 'bad_request'),
        ('no_auth_header', 'empty', 'bad_request'),
        ('not_allowed_service', 'empty', 'bad_request'),
    ],
)
async def test_create_multichat(
        protocol_client,
        load_json,
        request_name,
        mock_chat_new,
        chat_new_setting,
        expected,
        prefix,
):
    request = load_json('requests.json')[request_name]
    support_chat_setting = load_json('chat_new_mock.json')[chat_new_setting]
    mock_chat_new(support_chat_setting)

    response = await protocol_client.post(
        f'/{prefix}/v2/create_chat/',
        headers=request['headers'],
        params=request['params'],
        data=json.dumps(request['data']),
    )

    expected_response = load_json('expected_responses.json')[expected]
    assert response.status == expected_response['code']
    if response.status == 201:
        data = await response.json()
        assert data == expected_response['data']


@pytest.mark.usefixtures(
    'mock_get_users',
    'mock_stq_put',
    'mock_get_user_phone_from_db',
    'mock_chat_add_update',
)
@pytest.mark.config(ALLOWED_MULTICHAT_SERVICES=['taxi'])
@pytest.mark.parametrize(
    'prefix',
    [
        '4.0/lab/support_chat',
        '4.0/support_chat',
        'eats/v1/support_chat',
        'eats/v1/website_support_chat',
        'eats/v1/restapp_support_chat',
    ],
)
@pytest.mark.parametrize(
    ('request_name', 'expected'),
    [('taxi', 'success_add_message'), ('scouts', 'success_add_message')],
)
async def test_add_message(
        protocol_client,
        load_json,
        request_name,
        expected,
        mock_chat_create,
        prefix,
):
    mock_chat_create = mock_chat_create(False)

    request = load_json('requests.json')[request_name]

    response = await protocol_client.post(
        f'/{prefix}/v2/chats/5ff4901c583745e089e55be4/message/',
        headers=request['headers'],
        params=request['params'],
        data=json.dumps(request['data']),
    )

    expected_response = load_json('expected_responses.json')[expected]
    assert response.status == expected_response['code']
    if response.status == 201:
        data = await response.json()
        assert data == expected_response['data']


@pytest.mark.parametrize(
    'prefix',
    [
        '4.0/lab/support_chat',
        '4.0/support_chat',
        'eats/v1/support_chat',
        'eats/v1/website_support_chat',
        'eats/v1/restapp_support_chat',
    ],
)
@pytest.mark.parametrize(
    'use_support_info, request_key, expected_status, expected_create_chat, '
    'expected_stq_calls',
    [
        (
            False,
            'simplechat',
            200,
            {
                'owner_id': '5ff4901c583745e089e55be4',
                'owner_role': 'scouts_client',
                'message_text': 'Привет!',
                'message_sender_id': '5ff4901c583745e089e55be4',
                'message_sender_role': 'scouts_client',
                'metadata': {
                    'user_id': '5ff4901c583745e089e55be4',
                    'user_application': 'scouts_app',
                    'user_locale': 'ru',
                    'user_uid': '5ff4901c583745e089e55be4',
                },
                'message_metadata': None,
                'platform': 'scouts_app',
                'headers': None,
                'include_history': True,
                'scenario_context': None,
            },
            [
                {
                    'args': None,
                    'eta': None,
                    'kwargs': {
                        'chat_id': '5ff4901c583745e089e55be4',
                        'metadata': {
                            'user_application': 'scouts_app',
                            'user_id': '5ff4901c583745e089e55be4',
                            'user_locale': 'ru',
                            'user_uid': '5ff4901c583745e089e55be4',
                        },
                    },
                    'queue': 'support_chat_create_chatterbox_task',
                    'task_id': None,
                },
            ],
        ),
        (
            False,
            'taxi_realtime',
            200,
            {
                'owner_id': '1234567890abcdef7890abcd',
                'owner_role': 'client',
                'message_text': 'Привет!',
                'message_sender_id': '1234567890abcdef7890abcd',
                'message_sender_role': 'client',
                'metadata': {
                    'some_field': 'value',
                    'user_id': '1234567890abcdef7890abcd',
                    'user_application': 'test_app',
                    'user_locale': 'ru',
                    'user_phone': 'test_phone',
                    'phone_type': 'yandex',
                    'user_phone_id': '1234567890abcdef7890abcd',
                    'user_uid': '5ff4901c583745e089e55be4',
                },
                'message_metadata': {
                    'encrypt_key': '123',
                    'some_field': 'value',
                },
                'platform': 'test_app',
                'headers': None,
                'include_history': True,
                'scenario_context': None,
            },
            [
                {
                    'args': None,
                    'eta': None,
                    'kwargs': {
                        'chat_id': '5ff4901c583745e089e55be4',
                        'metadata': {
                            'some_field': 'value',
                            'user_application': 'test_app',
                            'user_id': '1234567890abcdef7890abcd',
                            'user_locale': 'ru',
                            'user_phone': 'test_phone',
                            'phone_type': 'yandex',
                            'user_phone_id': '1234567890abcdef7890abcd',
                            'user_uid': '5ff4901c583745e089e55be4',
                        },
                    },
                    'queue': 'support_chat_create_chatterbox_task',
                    'task_id': None,
                },
            ],
        ),
        (
            True,
            'taxi_realtime',
            200,
            {
                'owner_id': '1234567890abcdef7890abcd',
                'owner_role': 'client',
                'message_text': 'Привет!',
                'message_sender_id': '1234567890abcdef7890abcd',
                'message_sender_role': 'client',
                'metadata': {
                    'some_field': 'value',
                    'user_id': '1234567890abcdef7890abcd',
                    'user_application': 'test_app',
                    'user_locale': 'ru',
                    'user_phone': 'test_phone',
                    'phone_type': 'yandex',
                    'user_phone_id': '1234567890abcdef7890abcd',
                    'user_uid': '5ff4901c583745e089e55be4',
                },
                'message_metadata': {
                    'encrypt_key': '123',
                    'some_field': 'value',
                },
                'platform': 'test_app',
                'headers': None,
                'include_history': True,
                'scenario_context': None,
            },
            [
                {
                    'args': None,
                    'eta': None,
                    'kwargs': {
                        'chat_id': '5ff4901c583745e089e55be4',
                        'metadata': {
                            'some_field': 'value',
                            'user_application': 'test_app',
                            'user_id': '1234567890abcdef7890abcd',
                            'user_locale': 'ru',
                            'user_phone': 'test_phone',
                            'phone_type': 'yandex',
                            'user_phone_id': '1234567890abcdef7890abcd',
                            'user_uid': '5ff4901c583745e089e55be4',
                        },
                    },
                    'queue': 'support_chat_prepare_chatterbox_meta',
                    'task_id': None,
                },
            ],
        ),
        (False, 'taxi', 400, None, None),
        (False, 'taxi_realtime_bad_handler_type', 400, None, None),
        (
            False,
            'eats_order_id',
            200,
            {
                'owner_id': 'eats_id_72343',
                'owner_role': 'eats_app_client',
                'message_text': 'Привет!',
                'message_sender_id': 'eats_id_72343',
                'message_sender_role': 'eats_app_client',
                'metadata': {
                    'user_id': 'eats_id_72343',
                    'user_application': 'eats_app',
                    'user_locale': 'ru',
                    'eats_user_id': 'eats_id_72343',
                    'eats_order_id': 'test_eats_order_id',
                    'order_id': 'test_eats_order_id',
                },
                'message_metadata': {
                    'eats_order_id': 'test_eats_order_id',
                    'order_id': 'test_eats_order_id',
                },
                'platform': 'eats_app',
                'headers': None,
                'include_history': True,
                'scenario_context': None,
            },
            [
                {
                    'args': None,
                    'eta': None,
                    'kwargs': {
                        'chat_id': '5ff4901c583745e089e55be4',
                        'metadata': {
                            'user_application': 'eats_app',
                            'user_id': 'eats_id_72343',
                            'user_locale': 'ru',
                            'eats_user_id': 'eats_id_72343',
                            'eats_order_id': 'test_eats_order_id',
                            'order_id': 'test_eats_order_id',
                        },
                    },
                    'queue': 'support_chat_create_chatterbox_task',
                    'task_id': None,
                },
            ],
        ),
    ],
)
@pytest.mark.usefixtures(
    'mock_get_users', 'mock_chat_add_update', 'mock_get_user_phone_from_db',
)
@pytest.mark.config(ALLOWED_MULTICHAT_SERVICES=[])
async def test_create_simplechat(
        protocol_client,
        protocol_app,
        load_json,
        mock_chat_create,
        mock_stq_put,
        use_support_info,
        request_key,
        expected_status,
        expected_create_chat,
        expected_stq_calls,
        prefix,
):
    protocol_app.config.PROTOCOL_TAKE_META_FROM_SUPPORT_INFO = use_support_info
    request = load_json('requests.json')[request_key]
    mocked_chat_create = mock_chat_create(False)

    response = await protocol_client.post(
        f'/{prefix}/v2/create_chat/',
        headers=request['headers'],
        params=request['params'],
        data=json.dumps(request['data']),
    )

    assert response.status == expected_status
    if expected_status != 200:
        return

    create_chat_call = mocked_chat_create.calls[0]['kwargs']
    create_chat_call.pop('log_extra')
    assert create_chat_call == expected_create_chat

    stq_calls = mock_stq_put.calls
    if expected_stq_calls is None:
        assert not stq_calls
    else:
        for call in stq_calls:
            del call['kwargs']['log_extra']
            del call['loop']
            assert stq_calls == expected_stq_calls


@pytest.mark.usefixtures('mock_get_users')
@pytest.mark.parametrize(
    'prefix',
    [
        '4.0/lab/support_chat',
        '4.0/support_chat',
        'eats/v1/support_chat',
        'eats/v1/website_support_chat',
        'eats/v1/restapp_support_chat',
    ],
)
@pytest.mark.parametrize(
    ('request_name', 'expected'),
    [
        ('config_one', 'config_one_success'),
        ('config_custom', 'config_custom_success'),
        ('config_one_no_auth_header', 'bad_request'),
        ('config_multi', 'config_multi_success'),
        ('config_multi_double_auth', 'config_multi_success_double'),
        ('config_multi_not_compatible', 'error_config_multi_not_compatible'),
    ],
)
@pytest.mark.config(
    ALLOWED_MULTICHAT_SERVICES=['taxi'],
    PROTOCOL_ALLOW_UPLOAD_FILES={'regular': True, '__default__': False},
    SUPPORT_CHAT_COMPATIBLE_SERVICES=[['taxi', 'scouts', 'drive']],
    PROTOCOL_DEFAULT_HANDLER_TYPES={
        'taxi': 'realtime',
        'drive': 'regular',
        'scouts': 'realtime',
    },
    CHAT_ATTACHMENT_ALLOWED_MIMETYPES={
        '__default__': ['image/png', 'image/jpeg'],
        'drive': ['text/plain'],
    },
)
async def test_chat_configs(
        protocol_client, load_json, request_name, expected, prefix,
):
    request = load_json('requests.json')[request_name]

    response = await protocol_client.get(
        f'/{prefix}/v2/configs/',
        headers=request['headers'],
        params=request['params'],
        data=json.dumps(request['data']),
    )

    expected_response = load_json('expected_responses.json')[expected]
    assert response.status == expected_response['code']
    if response.status == 200:
        data = await response.json()
        assert data == expected_response['data']
    else:
        assert response.reason == expected_response['reason']


@pytest.mark.usefixtures('mock_get_users', 'mock_chat_search_json')
@pytest.mark.translations(
    client_messages={
        'support_chat.header': {
            'ru': 'Обращение от %(date)s',
            'en': 'Appeal from %(date)s',
        },
    },
)
@pytest.mark.parametrize(
    'prefix',
    [
        '4.0/lab/support_chat',
        '4.0/support_chat',
        'eats/v1/support_chat',
        'eats/v1/website_support_chat',
        'eats/v1/restapp_support_chat',
    ],
)
@pytest.mark.parametrize(
    ('request_name', 'expected'),
    [
        ('chat_list', 'chat_list'),
        ('chat_list_with_limit', 'chat_list_with_limit'),
        ('chat_list_next_page', 'chat_list_next_page'),
        ('chat_list_opened', 'chat_list_opened'),
        ('chat_list_closed', 'chat_list_closed'),
    ],
)
@pytest.mark.config(
    PROTOCOL_DEFAULT_HANDLER_TYPES={
        'eats': 'realtime',
        'eats_app': 'realtime',
        'taxi': 'realtime',
        'drive': 'regular',
        'scouts': 'realtime',
    },
)
async def test_chat_list(
        protocol_client, load_json, request_name, expected, prefix,
):
    request = load_json('requests.json')[request_name]

    response = await protocol_client.get(
        f'/{prefix}/v2/chats/',
        headers=request['headers'],
        params=request['params'],
        data=json.dumps(request['data']),
    )

    expected_response = load_json('expected_responses.json')[expected]
    assert response.status == expected_response['code']
    if response.status == 200:
        data = await response.json()
        assert data == expected_response['data']
    else:
        assert response.reason == expected_response['reason']


@pytest.mark.parametrize(
    'prefix',
    [
        '4.0/lab/support_chat',
        '4.0/support_chat',
        'eats/v1/support_chat',
        'eats/v1/website_support_chat',
        'eats/v1/restapp_support_chat',
    ],
)
@pytest.mark.parametrize(
    ('key', 'call_headers'),
    [
        ('get_chat', None),
        ('get_chat_with_actions', None),
        ('get_unowned_chat_fail', None),
        ('get_unowned_chat_success', None),
        ('get_chat_with_csat', None),
        ('get_chat_accept_language', {'Accept-Language': 'fr'}),
    ],
)
@pytest.mark.usefixtures(
    'mock_get_users',
    'mock_chat_search',
    'mock_read_chat',
    'mock_chat_history',
)
async def test_get_chat(
        protocol_client, load_json, mock_get_chat, key, call_headers, prefix,
):
    request = load_json('requests.json')[key]

    response = await protocol_client.get(
        f'/{prefix}/v2/chats/{request["chat_id"]}',
        headers=request['headers'],
        params=request['params'],
        data=json.dumps(request['data']),
    )

    expected_response = load_json('expected_responses.json')[key]
    assert response.status == expected_response['code']

    if response.status != 200:
        assert response.reason == expected_response['reason']
        return

    data = await response.json()
    assert data == expected_response['data']

    get_chat_call = mock_get_chat.calls[0]
    get_chat_call['kwargs'].pop('log_extra', None)
    assert get_chat_call == {
        'chat_id': request['chat_id'],
        'args': (),
        'kwargs': {
            'headers': call_headers,
            'include_history': True,
            'include_actions': True,
        },
    }
