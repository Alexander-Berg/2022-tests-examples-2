# pylint: disable=redefined-outer-name
import pytest

from support_info import stq_task


@pytest.mark.translations(
    support_info={
        'doctor_callback.body': {
            'en': 'Please call doctor to {phone!s}',
            'ru': 'Надо позвонить доктору на {phone!s}',
        },
    },
)
@pytest.mark.parametrize(
    'user_uid, phone, locale, urgent, expected_create_chat, expected_tasks',
    [
        (
            '123',
            '+79000000000',
            'ru',
            False,
            {
                'data': None,
                'params': None,
                'headers': {'Content-Type': 'application/json'},
                'json': {
                    'request_id': '2104653b-dac3-43e3-9ac5-7869d0bd738d',
                    'owner': {
                        'id': '+79000000000_doctor_callback',
                        'role': 'sms_client',
                        'platform': 'help_yandex',
                    },
                    'message': {
                        'text': 'Надо позвонить доктору на +79000000000',
                        'sender': {
                            'id': '+79000000000_doctor_callback',
                            'role': 'sms_client',
                            'platform': 'help_yandex',
                        },
                    },
                    'metadata': {
                        'user_application': 'help_yandex',
                        'owner_phone': '+79000000000',
                    },
                },
            },
            {
                'params': None,
                'headers': {'Content-Type': 'application/json'},
                'json': {
                    'type': 'chat',
                    'external_id': '5cf82c4f629526419ea4486d',
                    'metadata': {
                        'update_meta': [
                            {
                                'change_type': 'set',
                                'field_name': 'user_phone',
                                'value': '+79000000000',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'user_uid',
                                'value': '123',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'user_platform',
                                'value': 'help_yandex',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'newest_message_id',
                                'value': 'some_message_id',
                            },
                        ],
                        'update_tags': [
                            {
                                'change_type': 'add',
                                'tag': 'perseus_doctor_callback_tag',
                            },
                            {'change_type': 'add', 'tag': 'sms_task'},
                        ],
                    },
                },
            },
        ),
        (
            '1234',
            '+79000000001',
            'en',
            True,
            {
                'data': None,
                'params': None,
                'headers': {'Content-Type': 'application/json'},
                'json': {
                    'request_id': '2104653b-dac3-43e3-9ac5-7869d0bd738d',
                    'owner': {
                        'id': '+79000000001_doctor_callback',
                        'role': 'sms_client',
                        'platform': 'help_yandex',
                    },
                    'message': {
                        'text': 'Please call doctor to +79000000001',
                        'sender': {
                            'id': '+79000000001_doctor_callback',
                            'role': 'sms_client',
                            'platform': 'help_yandex',
                        },
                    },
                    'metadata': {
                        'user_application': 'help_yandex',
                        'owner_phone': '+79000000001',
                    },
                },
            },
            {
                'params': None,
                'headers': {'Content-Type': 'application/json'},
                'json': {
                    'type': 'chat',
                    'external_id': '5cf82c4f629526419ea4486d',
                    'metadata': {
                        'update_meta': [
                            {
                                'change_type': 'set',
                                'field_name': 'user_phone',
                                'value': '+79000000001',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'user_uid',
                                'value': '1234',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'user_platform',
                                'value': 'help_yandex',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'newest_message_id',
                                'value': 'some_message_id',
                            },
                        ],
                        'update_tags': [
                            {
                                'change_type': 'add',
                                'tag': 'perseus_doctor_callback_tag',
                            },
                            {'change_type': 'add', 'tag': 'sms_task'},
                            {
                                'change_type': 'add',
                                'tag': 'perseus_doctor_urgent_callback',
                            },
                        ],
                    },
                },
            },
        ),
        (
            '1234',
            '+79000000001',
            'fr',
            False,
            {
                'data': None,
                'params': None,
                'headers': {'Content-Type': 'application/json'},
                'json': {
                    'request_id': '2104653b-dac3-43e3-9ac5-7869d0bd738d',
                    'owner': {
                        'id': '+79000000001_doctor_callback',
                        'role': 'sms_client',
                        'platform': 'help_yandex',
                    },
                    'message': {
                        'text': (
                            'Перезвонить пользователю по '
                            'номеру +79000000001'
                        ),
                        'sender': {
                            'id': '+79000000001_doctor_callback',
                            'role': 'sms_client',
                            'platform': 'help_yandex',
                        },
                    },
                    'metadata': {
                        'user_application': 'help_yandex',
                        'owner_phone': '+79000000001',
                    },
                },
            },
            {
                'params': None,
                'headers': {'Content-Type': 'application/json'},
                'json': {
                    'type': 'chat',
                    'external_id': '5cf82c4f629526419ea4486d',
                    'metadata': {
                        'update_meta': [
                            {
                                'change_type': 'set',
                                'field_name': 'user_phone',
                                'value': '+79000000001',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'user_uid',
                                'value': '1234',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'user_platform',
                                'value': 'help_yandex',
                            },
                            {
                                'change_type': 'set',
                                'field_name': 'newest_message_id',
                                'value': 'some_message_id',
                            },
                        ],
                        'update_tags': [
                            {
                                'change_type': 'add',
                                'tag': 'perseus_doctor_callback_tag',
                            },
                            {'change_type': 'add', 'tag': 'sms_task'},
                        ],
                    },
                },
            },
        ),
    ],
)
async def test_create_urgenthelp_ticket(
        support_info_app_stq,
        patch_support_chat_create_chat,
        patch_chatterbox_tasks,
        mock_uuid_fixture,
        user_uid,
        phone,
        locale,
        urgent,
        expected_create_chat,
        expected_tasks,
):

    mock_chat_create = patch_support_chat_create_chat(
        {
            'id': '5cf82c4f629526419ea4486d',
            'newest_message_id': 'some_message_id',
        },
    )
    mock_chatterbox_tasks = patch_chatterbox_tasks({'id': 'some_id'})
    await stq_task.create_doctor_callback_ticket(
        support_info_app_stq, user_uid, phone, locale, urgent,
    )
    create_chat_calls = mock_chat_create.calls
    assert create_chat_calls[0]['kwargs'] == expected_create_chat

    tasks_calls = mock_chatterbox_tasks.calls
    assert tasks_calls[0]['kwargs'] == expected_tasks
