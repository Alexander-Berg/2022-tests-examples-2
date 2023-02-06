# pylint: disable=unused-variable
import datetime
import http

import bson
import pytest

from taxi import discovery

from chatterbox.api import rights

NOW = datetime.datetime(2018, 6, 15, 12, 34)
SECONDS_IN_DAY = datetime.timedelta(days=1).total_seconds()


@pytest.mark.config(
    CHATTERBOX_TASK_ALLOW_CHANGE_FIELDS={
        'user_phone': {
            'max_tries': 2,
            'permissions': {'add': ['add_phone'], 'update': ['upd_phone']},
            'label': 'fields.user_phone',
            'type': 'input',
            'validator': 'phone',
        },
        'phone_type': {
            'max_tries': 1,
            'permissions': {'add': ['restrict'], 'update': ['upd_phone_type']},
            'label': 'fields.phone_type',
            'type': 'select',
            'default': 'yandex',
            'options': {
                'uber': 'fields.phone_type_uber',
                'yandex': 'fields.phone_type_yandex',
            },
        },
        'order_id': {
            'permissions': {'update': ['upd_order_id']},
            'need_additional_meta': True,
            'label': 'fields.order_id',
            'type': 'input',
        },
    },
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
    'task_id, data, login, groups, additional_meta, expected_data, '
    'expected_request, expected_history, expected_response',
    [
        # superuser can change any field
        (
            '5b2cae5cb2682a976914c2a9',
            {'user_phone': '+79999999999'},
            'superuser',
            [],
            {
                'metadata': {
                    'user_phone': '+79999999999',
                    'user_id': 'user_id',
                    'payment_type': 'corp',
                },
            },
            {
                'user_phone': '+79999999999',
                'driver_license': 'aaabbb',
                'user_phone_pd_id': 'phone_pd_id_1',
            },
            {'user_phone': '+79999999999'},
            [
                {
                    'action': 'manual_update_meta',
                    'created': NOW,
                    'line': 'first',
                    'login': 'superuser',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'user_phone',
                            'value': '+79999999999',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'user_phone_pd_id',
                            'value': 'phone_pd_id_1',
                        },
                    ],
                },
            ],
            {},
        ),
        # user normally add field
        (
            '5b2cae5cb2682a976914c2a0',
            {'user_phone': ' +79999999999\t'},
            'user1',
            ['add_phone'],
            {'metadata': {}},
            {
                'user_phone': '+79999999999',
                'driver_license': 'aaabbb',
                'user_phone_pd_id': 'phone_pd_id_1',
            },
            {'user_phone': '+79999999999'},
            [
                {
                    'action': 'manual_update_meta',
                    'created': NOW,
                    'line': 'first',
                    'login': 'user1',
                    'latency': 3369544,
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'user_phone',
                            'value': '+79999999999',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'user_phone_pd_id',
                            'value': 'phone_pd_id_1',
                        },
                    ],
                },
            ],
            {},
        ),
        # user add restrict by permissions
        (
            '5b2cae5cb2682a976914c2a0',
            {'phone_type': 'yandex'},
            'user1',
            [],
            {'metadata': {}},
            {'driver_license': 'aaabbb'},
            {},
            [],
            {
                'status': 'request_error',
                'message': 'Field phone_type add restrict',
            },
        ),
        # user normally update field
        (
            '5b2cae5cb2682a976914c2a1',
            {'phone_type': 'uber'},
            'user1',
            ['upd_phone_type'],
            {'metadata': {}},
            {'user_phone': '+79999999999', 'phone_type': 'uber'},
            {'user_phone': '+79999999999', 'phone_type': 'uber'},
            [
                {
                    'action': 'manual_update_meta',
                    'created': NOW,
                    'line': 'first',
                    'login': 'user1',
                    'latency': 3369544,
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'phone_type',
                            'value': 'uber',
                        },
                    ],
                },
            ],
            {},
        ),
        # user update restrict by max_tries
        (
            '5b2cae5cb2682a976914c2a2',
            {'phone_type': 'uber'},
            'user1',
            ['upd_phone_type'],
            {'metadata': {}},
            {'user_phone': '+79999999999', 'phone_type': 'yandex'},
            {},
            [
                {
                    'action': 'manual_update_meta',
                    'created': datetime.datetime(2018, 5, 7, 12, 34, 56),
                    'line': 'first',
                    'login': 'user1',
                    'latency': 3369544,
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'phone_type',
                            'value': 'uber',
                        },
                    ],
                },
            ],
            {
                'status': 'request_error',
                'message': 'Field phone_type changed too much',
            },
        ),
        # order_id add with empty permissions + need_additional_meta enabled
        (
            '5b2cae5cb2682a976914c2a0',
            {'order_id': 'new_order_id'},
            'user1',
            [],
            {'metadata': {'user_phone': '+79999999999'}},
            {
                'antifraud_rules': ['taxi_free_trips'],
                'order_id': 'new_order_id',
                'driver_license': 'aaabbb',
                'user_phone': '+79999999999',
                'user_phone_pd_id': 'phone_pd_id_1',
            },
            {'order_id': 'new_order_id'},
            [
                {
                    'action': 'manual_update_meta',
                    'created': datetime.datetime(2018, 6, 15, 12, 34),
                    'latency': 3369544,
                    'line': 'first',
                    'login': 'user1',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'order_id',
                            'value': 'new_order_id',
                        },
                    ],
                },
                {
                    'action': 'update_meta',
                    'created': datetime.datetime(2018, 6, 15, 12, 34),
                    'latency': 3369544.0,
                    'line': 'first',
                    'login': 'user1',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'order_id',
                            'value': 'new_order_id',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'user_phone',
                            'value': '+79999999999',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'antifraud_rules',
                            'value': ['taxi_free_trips'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'user_phone_pd_id',
                            'value': 'phone_pd_id_1',
                        },
                    ],
                },
            ],
            {},
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_add_to_meta(
        cbox,
        task_id,
        data,
        login,
        groups,
        additional_meta,
        expected_data,
        expected_request,
        expected_history,
        expected_response,
        patch_aiohttp_session,
        response_mock,
        patch_auth,
        mock_personal,
        mock_translate,
        patch_support_chat_get_history,
):
    # pylint: disable=R0913
    support_info_service = discovery.find_service('support_info')

    mock_translate('ru')
    patch_support_chat_get_history(
        response={
            'messages': [
                {
                    'id': '0',
                    'sender': {'id': 'login', 'role': 'client'},
                    'text': 'lala',
                    'metadata': {'created': '2021-01-01T20:00:00'},
                },
            ],
        },
    )
    patch_auth(
        login=login,
        groups=groups + [rights.CHATTERBOX_BASIC],
        superuser=(login == 'superuser'),
    )

    @patch_aiohttp_session(support_info_service.url, 'POST')
    def patch_request(method, url, **kwargs):
        assert method == 'post'
        assert url == '%s/v1/get_additional_meta' % support_info_service.url
        assert kwargs['json'] == {'metadata': expected_request}
        return response_mock(json=additional_meta)

    await cbox.post('v1/tasks/{}/add_to_meta'.format(task_id), data=data)
    assert cbox.status == (
        http.HTTPStatus.OK
        if not expected_response
        else http.HTTPStatus.BAD_REQUEST
    )
    assert cbox.body_data == expected_response

    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId(task_id)},
    )
    assert task['meta_info'] == expected_data
    assert task.get('history', []) == expected_history


@pytest.mark.config(
    CHATTERBOX_TASK_ALLOW_CHANGE_FIELDS={
        'user_phone': {
            'label': 'fields.user_phone',
            'type': 'input',
            'validator': 'phone',
        },
        'phone_type': {
            'label': 'fields.phone_type',
            'type': 'select',
            'default': 'yandex',
            'options': {
                'uber': 'fields.phone_type_uber',
                'yandex': 'fields.phone_type_yandex',
            },
        },
        'order_id': {
            'label': 'fields.order_id',
            'type': 'input',
            'validator': 'order',
        },
    },
)
@pytest.mark.parametrize(
    'data, expected_response',
    [
        (
            {'phone_type': 'invalid_type'},
            {
                'message': (
                    'For field phone_type value should be in uber, yandex'
                ),
                'status': 'request_error',
            },
        ),
        (
            {'user_phone': '89999999999'},
            {
                'message': 'Field user_phone invalid format',
                'status': 'request_error',
            },
        ),
        (
            {'user_phone': '1'},
            {
                'message': 'Field user_phone invalid format',
                'status': 'request_error',
            },
        ),
        (
            {'user_phone': 'a'},
            {
                'message': 'Field user_phone invalid format',
                'status': 'request_error',
            },
        ),
        ({}, {'message': 'Empty request body', 'status': 'request_error'}),
        (
            {'order_id': 'order_Id'},
            {
                'message': 'Field order_id invalid format',
                'status': 'request_error',
            },
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_add_to_meta_validation(cbox, data, expected_response):
    await cbox.post('v1/tasks/5b2cae5cb2682a976914c2a9/add_to_meta', data=data)
    assert cbox.status == http.HTTPStatus.BAD_REQUEST
    assert cbox.body_data == expected_response
