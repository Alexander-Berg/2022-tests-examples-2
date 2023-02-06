import pytest


@pytest.mark.parametrize(
    'request_params',
    (
        {},
        {'callcenter_phone': '+79999999999'},
        {'user_phone': '+79999999999'},
        {'is_missed_call': False},
        {'request_id': 'request_id'},
        {
            'callcenter_phone': '+79999999999',
            'user_phone': '+79999999999',
            'is_missed_call': 'invalid',
            'request_id': 'request_id',
        },
    ),
)
async def test_incoming_call_validation(
        support_info_client, request_params: dict,
):
    response = await support_info_client.post(
        '/v1/webhooks/incoming_call', json=request_params,
    )
    assert response.status == 400


@pytest.mark.parametrize(
    ('headers', 'expected_status'),
    (
        ({}, 403),
        ({'YaTaxi-Api-Key': ''}, 403),
        ({'YaTaxi-Api-Key': 'test_telphin_api_key'}, 200),
    ),
)
async def test_incoming_call_auth(
        support_info_client,
        patch_support_chat_create_chat,
        patch_chatterbox_tasks,
        headers: dict,
        expected_status: int,
):
    patch_support_chat_create_chat(response={'id': 'chat_id'})
    patch_chatterbox_tasks(response={'id': 'task_id'})

    response = await support_info_client.post(
        '/v1/webhooks/incoming_call',
        json={
            'user_phone': '+79999999999',
            'callcenter_phone': '+79999999999',
            'is_missed_call': False,
            'request_id': 'request_id',
        },
        headers=headers,
    )
    assert response.status == expected_status
    if response.status == 403:
        assert await response.json() == {
            'error': 'Invalid token YaTaxi-Api-Key or X-YaTaxi-Api-Key: None',
            'status': 'error',
        }


@pytest.mark.parametrize('is_missed_call', (True, False))
async def test_incoming_call(
        support_info_client,
        patch_support_chat_create_chat,
        patch_chatterbox_tasks,
        is_missed_call: bool,
):
    patched_create_chat = patch_support_chat_create_chat(
        response={'id': 'chat_id', 'newest_message_id': 'newest_message_id'},
    )
    patched_tasks = patch_chatterbox_tasks(response={'id': 'task_id'})

    request_id = 'request_id'
    if is_missed_call:
        expected_request_id = 'request_id_missed_incoming_call'
    else:
        expected_request_id = 'request_id_new_incoming_call'

    response = await support_info_client.post(
        '/v1/webhooks/incoming_call',
        json={
            'user_phone': '+79999999999',
            'callcenter_phone': '+79999999999',
            'is_missed_call': is_missed_call,
            'request_id': request_id,
        },
        headers={'YaTaxi-Api-Key': 'test_telphin_api_key'},
    )
    if is_missed_call:
        message_text = (
            'Пропущеный звонок с номера +79999999999 на номер +79999999999'
        )
    else:
        message_text = (
            'Входящий звонок с номера +79999999999 на номер +79999999999'
        )
    assert patched_create_chat.calls[0]['kwargs']['json'] == {
        'message': {
            'sender': {
                'id': 'incoming_call_+79999999999',
                'role': 'sms_client',
                'platform': 'yandex',
            },
            'text': message_text,
        },
        'metadata': {
            'owner_phone': '+79999999999',
            'user_application': 'yandex',
        },
        'owner': {
            'id': 'incoming_call_+79999999999',
            'role': 'sms_client',
            'platform': 'yandex',
        },
        'request_id': expected_request_id,
    }
    expected_tags = [
        {'change_type': 'add', 'tag': 'sms_task'},
        {'change_type': 'add', 'tag': 'incoming_call_task'},
    ]
    if is_missed_call:
        expected_tags.append(
            {'change_type': 'add', 'tag': 'missed_incoming_call_task'},
        )
    assert patched_tasks.calls[0]['kwargs']['json'] == {
        'external_id': 'chat_id',
        'metadata': {
            'update_meta': [
                {
                    'change_type': 'set',
                    'field_name': 'callcenter_phone',
                    'value': '+79999999999',
                },
                {
                    'change_type': 'set',
                    'field_name': 'user_phone',
                    'value': '+79999999999',
                },
                {
                    'change_type': 'set',
                    'field_name': 'newest_message_id',
                    'value': 'newest_message_id',
                },
            ],
            'update_tags': expected_tags,
        },
        'type': 'chat',
    }

    assert response.status == 200


@pytest.mark.config(
    INCOMING_CALLS_CALLCENTER_PHONES_ALLOWED=['+79999999999', '+79999999789'],
)
@pytest.mark.parametrize(
    ('request_params', 'status'),
    (
        (
            {
                'user_phone': '+79999999333',
                'callcenter_phone': '+79999999999',
                'is_missed_call': False,
                'request_id': 'request_id',
            },
            200,
        ),
        (
            {
                'user_phone': '+79999999333',
                'callcenter_phone': '+79999999789',
                'is_missed_call': False,
                'request_id': 'request_id',
            },
            200,
        ),
        (
            {
                'user_phone': '+79999999789',
                'callcenter_phone': '+79999999333',
                'is_missed_call': False,
                'request_id': 'request_id',
            },
            406,
        ),
    ),
)
async def test_incoming_call_allowed(
        support_info_client,
        request_params: dict,
        status: int,
        patch_support_chat_create_chat,
        patch_chatterbox_tasks,
):
    patch_support_chat_create_chat(response={'id': 'chat_id'})
    patch_chatterbox_tasks(response={'id': 'task_id'})

    response = await support_info_client.post(
        '/v1/webhooks/incoming_call',
        json=request_params,
        headers={'YaTaxi-Api-Key': 'test_telphin_api_key'},
    )
    assert response.status == status
