# pylint: disable=too-many-lines, too-many-arguments, redefined-outer-name
# pylint: disable=unused-variable, too-many-locals, no-member
import datetime
import http

import pytest


NOW = datetime.datetime(2018, 5, 7, 12, 34, 56)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {
            'user_phone': 'phones',
            'user_email': 'emails',
            'driver_license': 'driver_licenses',
            'driver_phone': 'phones',
            'park_phone': 'phones',
            'park_email': 'emails',
        },
    },
)
@pytest.mark.parametrize(
    ('data', 'expected_response'),
    [
        (
            {'login': 'support_login', 'only_active': True},
            [
                {
                    'metadata': {
                        'driver_id': ['id_uuid_1', 'id_uuid_4'],
                        'driver_uuid': ['uuid_1'],
                        'order_alias_id': [
                            'order_alias_1',
                            'order_alias_2',
                            'order_alias_4',
                            'order_alias_5',
                        ],
                        'order_id': ['some_order_id_1', 'some_order_id_4'],
                        'park_db_id': ['db_id_1', 'db_id_4'],
                        'user_email': ['user1@yandex.ru', 'user4@yandex.ru'],
                        'user_phone': [
                            '+79999999999',
                            'user_phone_task_broken',
                        ],
                        'user_phone_pd_id': ['phone_pd_id_1', 'phone_pd_id_4'],
                    },
                    'task_id': '5b2cae5cb2682a976914c2a1',
                },
            ],
        ),
        (
            {'login': 'support_login'},
            [
                {
                    'metadata': {
                        'driver_id': ['id_uuid_3'],
                        'driver_uuid': ['uuid_3'],
                        'order_alias_id': ['order_alias_3'],
                        'order_id': ['some_order_id_3'],
                        'park_db_id': ['db_id_3'],
                        'user_email': ['user3@yandex.ru'],
                        'user_phone': ['missing_user_phone'],
                        'user_phone_pd_id': ['phone_pd_id_3'],
                    },
                    'task_id': '5b2cae5cb2682a976914c2a3',
                },
                {'metadata': {}, 'task_id': '5b2cae5cb2682a976914c2a4'},
                {
                    'metadata': {
                        'driver_id': ['id_uuid_1', 'id_uuid_4'],
                        'driver_uuid': ['uuid_1'],
                        'order_alias_id': [
                            'order_alias_1',
                            'order_alias_2',
                            'order_alias_4',
                            'order_alias_5',
                        ],
                        'order_id': ['some_order_id_1', 'some_order_id_4'],
                        'park_db_id': ['db_id_1', 'db_id_4'],
                        'user_email': ['user1@yandex.ru', 'user4@yandex.ru'],
                        'user_phone': [
                            '+79999999999',
                            'user_phone_task_broken',
                        ],
                        'user_phone_pd_id': ['phone_pd_id_1', 'phone_pd_id_4'],
                    },
                    'task_id': '5b2cae5cb2682a976914c2a1',
                },
            ],
        ),
        (
            {'login': 'support_login', 'only_active': False},
            [
                {
                    'metadata': {
                        'driver_id': ['id_uuid_3'],
                        'driver_uuid': ['uuid_3'],
                        'order_alias_id': ['order_alias_3'],
                        'order_id': ['some_order_id_3'],
                        'park_db_id': ['db_id_3'],
                        'user_email': ['user3@yandex.ru'],
                        'user_phone': ['missing_user_phone'],
                        'user_phone_pd_id': ['phone_pd_id_3'],
                    },
                    'task_id': '5b2cae5cb2682a976914c2a3',
                },
                {'metadata': {}, 'task_id': '5b2cae5cb2682a976914c2a4'},
                {
                    'metadata': {
                        'driver_id': ['id_uuid_1', 'id_uuid_4'],
                        'driver_uuid': ['uuid_1'],
                        'order_alias_id': [
                            'order_alias_1',
                            'order_alias_2',
                            'order_alias_4',
                            'order_alias_5',
                        ],
                        'order_id': ['some_order_id_1', 'some_order_id_4'],
                        'park_db_id': ['db_id_1', 'db_id_4'],
                        'user_email': ['user1@yandex.ru', 'user4@yandex.ru'],
                        'user_phone': [
                            '+79999999999',
                            'user_phone_task_broken',
                        ],
                        'user_phone_pd_id': ['phone_pd_id_1', 'phone_pd_id_4'],
                    },
                    'task_id': '5b2cae5cb2682a976914c2a1',
                },
            ],
        ),
        ({'login': 'no_such_support', 'only_active': False}, []),
    ],
)
async def test_get_support_tasks_data(
        cbox,
        patch_aiohttp_session,
        mock_personal,
        response_mock,
        data,
        expected_response,
):
    def _prepare(data):
        return sorted(data, key=lambda x: x['task_id'])

    await cbox.post('/v1/user/get_support_tasks_data', data=data)
    assert cbox.status == http.HTTPStatus.OK
    assert _prepare(cbox.body_data['data']) == _prepare(expected_response)
