import datetime

import bson
import pytest


NOW = datetime.datetime(2018, 6, 15, 12, 34)


@pytest.mark.config(
    CHATTERBOX_LINES={
        'test_line': {
            'name': 'Тест',
            'types': ['client'],
            'priority': 4,
            'sort_order': 1,
        },
    },
    CHATTERBOX_IVR_OUTGOING_CALLS_PHONE={
        'default_phone': '+7123',
        'default_dialup_timeout': 30,
        'sources': [{'conditions': {'line': {'#in': ['test_line']}}}],
    },
)
@pytest.mark.parametrize(
    (
        'task_id',
        'data',
        'expected_status',
        'expected_response',
        'expected_message',
        'expected_call',
        'check_meta_info_fields',
    ),
    [
        ('5b2cae5cb2682a976914c2a1', {}, 400, None, None, None, None),
        (
            '5b2cae5cb2682a976914c2a2',
            {'phone': '+7987654321'},
            404,
            None,
            None,
            None,
            None,
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {'phone': '+7987654321'},
            200,
            {
                'call_id': (
                    'outgoing_5b2cae5cb2682a976914c2a1_'
                    '00000000000040008000000000000000'
                ),
            },
            {
                'contactPoint': {'channel': 'TELEPHONY', 'id': '+7123'},
                'service': {
                    'callId': (
                        'outgoing_5b2cae5cb2682a976914c2a1_'
                        '00000000000040008000000000000000'
                    ),
                    'timeout': 30,
                    'type': 'OUTGOING',
                    'yuid': '1120000000410312',
                },
                'timestamp': '2018-06-15T12:34:00+0000',
                'to': {'id': '+7987654321'},
            },
            {
                'created_at': '2018-06-15T12:34:00+0000',
                'direction': 'outgoing',
                'id': (
                    'outgoing_5b2cae5cb2682a976914c2a1_'
                    '00000000000040008000000000000000'
                ),
                'line': 'first',
                'login': 'support',
                'num_from': '+7123',
                'num_to': '+7987654321',
                'source': 'ivr',
            },
            {
                'call_id': (
                    'outgoing_5b2cae5cb2682a976914c2a1_'
                    '00000000000040008000000000000000'
                ),
                'contact_point_id': '+7123',
                'ivr_call_status': 'active',
            },
        ),
        (
            '5b2cae5cb2682a976914c2a4',
            {'phone': '+7987654321'},
            409,
            None,
            None,
            None,
            None,
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_post_ivr_outgoing_call(
        cbox,
        patch_auth,
        task_id,
        data,
        expected_status,
        expected_response,
        expected_message,
        expected_call,
        check_meta_info_fields,
        mock_passport_for_lb,
        mock_logbroker_producer,
        mock_uuid_uuid4,
        mock_chat_get_history,
):
    patch_auth(login='support', superuser=True)
    mock_chat_get_history({'messages': []})
    mock_passport_for_lb(
        users={
            'users': [
                {'uid': {'value': '1120000000410312'}, 'login': 'user_17'},
            ],
        },
    )
    mock_logbroker_producer(expected_message)
    await cbox.post(
        '/v1/tasks/{}/ivr/outgoing_call'.format(task_id), data=data,
    )
    assert cbox.status == expected_status

    if expected_status == 200:
        assert cbox.body_data == expected_response
        task = await cbox.db.support_chatterbox.find_one(
            {'_id': bson.ObjectId(task_id)},
        )
        assert task['meta_info']['calls'][0] == expected_call
        for field, value in check_meta_info_fields.items():
            assert task['meta_info'][field] == value


@pytest.mark.config(
    CHATTERBOX_LINES={
        'test_line': {
            'name': 'Тест',
            'types': ['client'],
            'priority': 4,
            'sort_order': 1,
        },
    },
    CHATTERBOX_IVR_OUTGOING_CALLS_PHONE={
        'default_phone': '+7123',
        'default_dialup_timeout': 30,
        'sources': [{'conditions': {'line': {'#in': ['test_line']}}}],
    },
)
@pytest.mark.parametrize(
    ('task_id', 'params', 'expected_status', 'expected_response'),
    [
        ('5b2cae5cb2682a976914c2a3', {}, 400, None),
        ('5b2cae5cb2682a976914c2a3', {'call_id': 'wrong'}, 404, None),
        (
            '5b2cae5cb2682a976914c2a3',
            {
                'call_id': (
                    'outgoing_5b2cae5cb2682a976914c2a1_'
                    '00000000000040008000000000000000'
                ),
            },
            200,
            {'status': 'failed'},
        ),
        (
            '5b2cae5cb2682a976914c2a3',
            {
                'call_id': (
                    'outgoing_5b2cae5cb2682a976914c2a1_'
                    '00000000000040008000000000000001'
                ),
            },
            200,
            {'status': 'initialization'},
        ),
        (
            '5b2cae5cb2682a976914c2a3',
            {
                'call_id': (
                    'outgoing_5b2cae5cb2682a976914c2a1_'
                    '00000000000040008000000000000002'
                ),
            },
            200,
            {'status': 'error'},
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_get_ivr_outgoing_call(
        cbox,
        patch_auth,
        task_id,
        params,
        expected_status,
        expected_response,
        mock_uuid_uuid4,
):
    patch_auth(login='support', superuser=True)
    await cbox.query(
        '/v1/tasks/{}/ivr/outgoing_call'.format(task_id), params=params,
    )
    assert cbox.status == expected_status

    if expected_status == 200:
        assert cbox.body_data == expected_response
