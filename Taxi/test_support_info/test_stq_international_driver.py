import pytest

from support_info import stq_task


@pytest.mark.parametrize(
    'data, expected_create_chat, expected_chatterbox_tasks',
    [
        (
            {
                'subject': 'subject',
                'description': 'description',
                'driver_license': 'driver_license',
                'order_id': 'order_id',
                'requester': 'requester',
                'brand': 'yandex',
                'status': 'new',
            },
            {
                'request_id': 'driver_license_order_id_international_driver',
                'owner': {
                    'id': '+7987_international_driver',
                    'role': 'sms_client',
                    'platform': 'yandex',
                },
                'message': {
                    'text': 'description',
                    'sender': {
                        'id': '+7987_international_driver',
                        'role': 'sms_client',
                        'platform': 'yandex',
                    },
                    'metadata': {
                        'order_id': 'order_id',
                        'order_alias_id': 'alias_id',
                        'driver_uuid': 'uuid',
                        'park_db_id': 'db_id',
                    },
                },
                'metadata': {
                    'user_application': 'taximeter',
                    'owner_phone': '+7987',
                },
            },
            {
                'external_id': '5cf82c4f629526419ea4486d',
                'type': 'chat',
                'metadata': {
                    'update_meta': [
                        {
                            'change_type': 'set',
                            'field_name': 'brand',
                            'value': 'yandex',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'requester',
                            'value': 'requester',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'order_id',
                            'value': 'order_id',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'order_alias_id',
                            'value': 'alias_id',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'clid',
                            'value': 'clid',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'park_db_id',
                            'value': 'db_id',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'driver_license',
                            'value': 'DRIVER_LICENSE',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'driver_uuid',
                            'value': 'uuid',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'user_phone',
                            'value': '+7987',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'city',
                            'value': 'city',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'country',
                            'value': 'rus',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'ticket_subject',
                            'value': 'subject',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'park_phone',
                            'value': '+79123',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'park_name',
                            'value': 'park_name',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'park_city',
                            'value': 'moscow',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'park_country',
                            'value': 'rus',
                        },
                    ],
                    'update_tags': [
                        {'change_type': 'add', 'tag': 'sms_task'},
                        {
                            'change_type': 'add',
                            'tag': 'driver_international_import_tag',
                        },
                    ],
                },
            },
        ),
        (
            {
                'subject': 'subject',
                'description': 'description',
                'driver_license': 'DRIVER_LICENSE',
                'requester': 'requester',
                'city': 'Москва',
                'brand': 'yango',
                'status': 'new',
            },
            {
                'request_id': 'DRIVER_LICENSE_None_international_driver',
                'owner': {
                    'id': '+7987_international_driver',
                    'role': 'sms_client',
                    'platform': 'yango',
                },
                'message': {
                    'text': 'description',
                    'sender': {
                        'id': '+7987_international_driver',
                        'role': 'sms_client',
                        'platform': 'yango',
                    },
                    'metadata': {'driver_uuid': 'uuid', 'park_db_id': 'db_id'},
                },
                'metadata': {
                    'user_application': 'taximeter',
                    'owner_phone': '+7987',
                },
            },
            {
                'external_id': '5cf82c4f629526419ea4486d',
                'type': 'chat',
                'metadata': {
                    'update_meta': [
                        {
                            'change_type': 'set',
                            'field_name': 'brand',
                            'value': 'yango',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'requester',
                            'value': 'requester',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'clid',
                            'value': 'clid',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'park_db_id',
                            'value': 'db_id',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'driver_license',
                            'value': 'DRIVER_LICENSE',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'driver_uuid',
                            'value': 'uuid',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'user_phone',
                            'value': '+7987',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'city',
                            'value': 'Москва',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'country',
                            'value': 'rus',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'ticket_subject',
                            'value': 'subject',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'integration_event',
                            'value': False,
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'yandex_provider',
                            'value': True,
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'park_phone',
                            'value': '+79123',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'park_name',
                            'value': 'park_name',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'park_city',
                            'value': 'moscow',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'park_country',
                            'value': 'rus',
                        },
                    ],
                    'update_tags': [
                        {'change_type': 'add', 'tag': 'sms_task'},
                        {
                            'change_type': 'add',
                            'tag': 'driver_international_import_tag',
                        },
                    ],
                },
            },
        ),
        (
            {
                'subject': 'subject',
                'description': 'description',
                'driver_license': 'DRIVER_LICENSE',
                'order_id': 'alias_id',
                'requester': 'requester',
                'brand': 'yango',
                'status': 'closed',
            },
            {
                'request_id': 'DRIVER_LICENSE_order_id_international_driver',
                'owner': {
                    'id': '+7987_international_driver_solved',
                    'role': 'sms_client',
                    'platform': 'yango',
                },
                'message': {
                    'text': 'description',
                    'sender': {
                        'id': '+7987_international_driver_solved',
                        'role': 'sms_client',
                        'platform': 'yango',
                    },
                    'metadata': {
                        'order_id': 'order_id',
                        'order_alias_id': 'alias_id',
                        'driver_uuid': 'uuid',
                        'park_db_id': 'db_id',
                    },
                },
                'metadata': {
                    'user_application': 'taximeter',
                    'owner_phone': '+7987',
                },
            },
            {
                'external_id': '5cf82c4f629526419ea4486d',
                'type': 'chat',
                'metadata': {
                    'update_meta': [
                        {
                            'change_type': 'set',
                            'field_name': 'brand',
                            'value': 'yango',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'requester',
                            'value': 'requester',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'order_id',
                            'value': 'order_id',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'order_alias_id',
                            'value': 'alias_id',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'clid',
                            'value': 'clid',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'park_db_id',
                            'value': 'db_id',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'driver_license',
                            'value': 'DRIVER_LICENSE',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'driver_uuid',
                            'value': 'uuid',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'user_phone',
                            'value': '+7987',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'city',
                            'value': 'city',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'country',
                            'value': 'rus',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'ticket_subject',
                            'value': 'subject',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'park_phone',
                            'value': '+79123',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'park_name',
                            'value': 'park_name',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'park_city',
                            'value': 'moscow',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'park_country',
                            'value': 'rus',
                        },
                    ],
                    'update_tags': [
                        {'change_type': 'add', 'tag': 'sms_task'},
                        {
                            'change_type': 'add',
                            'tag': 'driver_international_import_tag',
                        },
                        {'change_type': 'add', 'tag': 'закрыть_немедленно'},
                    ],
                },
            },
        ),
        (
            {
                'subject': 'subject',
                'description': 'description',
                'driver_license': 'MISSING_LICENSE',
                'order_id': 'alias_id',
                'requester': 'requester',
                'brand': 'yango',
                'status': 'closed',
            },
            None,
            None,
        ),
    ],
)
async def test_chatterbox_task(
        support_info_client,
        support_info_app_stq,
        mock_get_user_phones,
        mock_personal,
        patch,
        patch_support_chat_create_chat,
        patch_chatterbox_tasks,
        data,
        expected_create_chat,
        expected_chatterbox_tasks,
):
    mock_chat_create = patch_support_chat_create_chat(
        {
            'id': '5cf82c4f629526419ea4486d',
            'newest_message_id': 'some_message_id',
        },
    )
    mock_chatterbox_tasks = patch_chatterbox_tasks({'id': 'some_id'})

    @patch('taxi.clients.archive_api.ArchiveApiClient.get_order_by_id')
    async def _get_order_by_id(order_id, *args, **kwargs):
        return {
            '_id': 'order_id',
            'nz': 'nz',
            'city': 'city',
            'user_phone_id': '539eb65be7e5b1f53980dfa8',
            'performer': {'clid': 'clid', 'taxi_alias': {'id': 'alias_id'}},
            'user_locale': 'ru',
        }

    @patch(
        'taxi.clients.archive_api._NoCodegenOrderArchive.order_proc_retrieve',
    )
    async def _order_proc_retrieve(order_id, *args, **kwargs):
        return {
            'order': {
                '_id': 'order_id',
                'nz': 'nz',
                'city': 'city',
                'user_phone_id': '539eb65be7e5b1f53980dfa8',
                'performer': {
                    'clid': 'clid',
                    'taxi_alias': {'id': 'alias_id'},
                },
                'user_locale': 'ru',
            },
        }

    @patch('taxi.util.country_manager.get_doc_by_zone_name')
    async def _get_doc_by_zone_name(*args, **kwargs):
        return {'_id': 'rus', 'name': 'Россия'}

    await stq_task.international_driver_ticket(support_info_app_stq, data)
    create_chat_calls = mock_chat_create.calls
    if expected_create_chat is None:
        assert not create_chat_calls
    else:
        assert create_chat_calls[0]['kwargs']['json'] == expected_create_chat

    chatterbox_tasks_calls = mock_chatterbox_tasks.calls
    if expected_chatterbox_tasks is None:
        assert not chatterbox_tasks_calls
    else:
        assert (
            chatterbox_tasks_calls[0]['kwargs']['json']
            == expected_chatterbox_tasks
        )
