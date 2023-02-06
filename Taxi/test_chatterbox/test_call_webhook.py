# pylint: disable=protected-access,too-many-locals,too-many-arguments
# pylint: disable=no-member,too-many-lines
import datetime

import bson
import pytest


@pytest.mark.now('2019-11-11T12:00:00+0')
@pytest.mark.config(
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {'num_from': 'phones', 'num_to': 'phones'},
    },
)
@pytest.mark.parametrize(
    'task_id, data, expected_code, expected_call_info, first_answer, messages',
    [
        ('5b2cae5cb2682a976914c2a1', {}, 400, [], None, []),
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'id': 'id',
                'user_id': 'user_id',
                'created_at': '2019-01-01T11:22:33Z',
                'ringing_at': '2019-01-01T11:22:33Z',
                'answered_at': '2019-01-01T11:22:33Z',
                'completed_at': None,
                'num_from': '+7900',
                'num_to': '+7901',
                'direction': 'outgoing',
                'record_urls': ['url_1', 'url_2'],
                'status_completed': 'answered',
                'hangup_disposition': None,
                'is_synced': True,
            },
            400,
            [],
            None,
            [],
        ),
        (
            'test_id',
            {
                'id': 'id',
                'user_id': 'user_id',
                'created_at': '2019-01-01T11:22:33Z',
                'ringing_at': '2019-01-01T11:22:33Z',
                'answered_at': '2019-01-01T11:22:33Z',
                'completed_at': None,
                'num_from': '+7900',
                'num_to': '+7901',
                'num_from_pd_id': 'phone_pd_id_9',
                'num_to_pd_id': 'phone_pd_id_10',
                'direction': 'outgoing',
                'record_urls': ['url_1', 'url_2'],
                'status_completed': 'answered',
                'hangup_disposition': None,
                'is_synced': True,
                'provider_id': 'provider_id',
            },
            400,
            [],
            None,
            [],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'id': 'id',
                'user_id': 'user_id',
                'created_at': '2019-01-01T11:22:33Z',
                'ringing_at': '2019-01-01T11:22:33Z',
                'answered_at': '2019-01-01T11:22:33Z',
                'completed_at': None,
                'num_from': '+7900',
                'num_to': '+7901',
                'direction': 'outgoing',
                'record_urls': ['url_1', 'url_2'],
                'status_completed': 'answered',
                'hangup_disposition': None,
                'is_synced': True,
                'error': None,
                'provider_id': 'provider_id',
            },
            200,
            [
                {
                    'id': 'id',
                    'user_id': 'user_id',
                    'created_at': '2019-01-01T11:22:33Z',
                    'ringing_at': '2019-01-01T11:22:33Z',
                    'answered_at': '2019-01-01T11:22:33Z',
                    'completed_at': None,
                    'num_from': '+7900',
                    'num_to': '+7901',
                    'num_from_pd_id': 'phone_pd_id_9',
                    'num_to_pd_id': 'phone_pd_id_10',
                    'direction': 'outgoing',
                    'record_urls': ['url_1', 'url_2'],
                    'status_completed': 'answered',
                    'hangup_disposition': None,
                    'is_synced': True,
                    'error': None,
                    'provider_id': 'provider_id',
                    'stat_created': datetime.datetime(2019, 11, 11, 12, 0),
                    'line': 'first',
                },
            ],
            10,
            [
                {
                    'sender': {'role': 'client'},
                    'metadata': {'created': '2019-01-01T11:22:23Z'},
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'id': 'id',
                'user_id': 'user_id',
                'created_at': '2019-01-01T11:22:33.1Z',
                'ringing_at': '2019-01-01T11:22:33Z',
                'answered_at': '2019-01-01T11:22:33Z',
                'completed_at': None,
                'num_from': '+7900',
                'num_to': '+7901',
                'direction': 'outgoing',
                'record_urls': None,
                'status_completed': 'answered',
                'hangup_disposition': None,
                'is_synced': True,
                'error': None,
                'provider_id': 'provider_id',
            },
            200,
            [
                {
                    'id': 'id',
                    'user_id': 'user_id',
                    'created_at': '2019-01-01T11:22:33.1Z',
                    'ringing_at': '2019-01-01T11:22:33Z',
                    'answered_at': '2019-01-01T11:22:33Z',
                    'completed_at': None,
                    'num_from': '+7900',
                    'num_to': '+7901',
                    'num_from_pd_id': 'phone_pd_id_9',
                    'num_to_pd_id': 'phone_pd_id_10',
                    'direction': 'outgoing',
                    'record_urls': [],
                    'status_completed': 'answered',
                    'hangup_disposition': None,
                    'is_synced': True,
                    'error': None,
                    'provider_id': 'provider_id',
                    'stat_created': datetime.datetime(2019, 11, 11, 12, 0),
                    'line': 'first',
                },
            ],
            20,
            [
                {'sender': {'role': 'support'}},
                {
                    'sender': {'role': 'client'},
                    'metadata': {'created': '2019-01-01T11:22:13Z'},
                },
                {
                    'sender': {'role': 'client'},
                    'metadata': {'created': '2019-01-01T11:22:08Z'},
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'id': 'id',
                'user_id': 'user_id',
                'created_at': '2019-01-01T11:22:33Z',
                'ringing_at': '2019-01-01T11:22:33Z',
                'answered_at': '2019-01-01T11:22:33Z',
                'completed_at': None,
                'num_from': '+7900',
                'num_to': '+7901',
                'direction': 'incoming',
                'record_urls': None,
                'status_completed': 'answered',
                'hangup_disposition': None,
                'is_synced': True,
                'error': None,
                'provider_id': 'provider_id',
            },
            200,
            [
                {
                    'id': 'id',
                    'user_id': 'user_id',
                    'created_at': '2019-01-01T11:22:33Z',
                    'ringing_at': '2019-01-01T11:22:33Z',
                    'answered_at': '2019-01-01T11:22:33Z',
                    'completed_at': None,
                    'num_from': '+7900',
                    'num_to': '+7901',
                    'num_from_pd_id': 'phone_pd_id_9',
                    'num_to_pd_id': 'phone_pd_id_10',
                    'direction': 'incoming',
                    'record_urls': [],
                    'status_completed': 'answered',
                    'hangup_disposition': None,
                    'is_synced': True,
                    'error': None,
                    'provider_id': 'provider_id',
                    'stat_created': datetime.datetime(2019, 11, 11, 12, 0),
                    'line': 'first',
                },
            ],
            None,
            [
                {'sender': {'role': 'support'}},
                {
                    'sender': {'role': 'client'},
                    'metadata': {'created': '2019-01-01T11:22:13Z'},
                },
                {
                    'sender': {'role': 'client'},
                    'metadata': {'created': '2019-01-01T11:22:08Z'},
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'id': 'id',
                'user_id': 'user_id',
                'created_at': '2019-01-01T11:22:33Z',
                'ringing_at': '2019-01-01T11:22:33Z',
                'answered_at': '2019-01-01T11:22:33Z',
                'completed_at': None,
                'num_from': '+7900',
                'num_to': '+7901',
                'direction': 'outgoing',
                'record_urls': None,
                'status_completed': 'answered',
                'hangup_disposition': None,
                'is_synced': True,
                'error': None,
                'provider_id': 'provider_id',
            },
            200,
            [
                {
                    'id': 'id',
                    'user_id': 'user_id',
                    'created_at': '2019-01-01T11:22:33Z',
                    'ringing_at': '2019-01-01T11:22:33Z',
                    'answered_at': '2019-01-01T11:22:33Z',
                    'completed_at': None,
                    'num_from': '+7900',
                    'num_to': '+7901',
                    'num_from_pd_id': 'phone_pd_id_9',
                    'num_to_pd_id': 'phone_pd_id_10',
                    'direction': 'outgoing',
                    'record_urls': [],
                    'status_completed': 'answered',
                    'hangup_disposition': None,
                    'is_synced': True,
                    'error': None,
                    'provider_id': 'provider_id',
                    'stat_created': datetime.datetime(2019, 11, 11, 12, 0),
                    'line': 'first',
                },
            ],
            0,
            [
                {'sender': {'role': 'support'}},
                {
                    'sender': {'role': 'client'},
                    'metadata': {'created': '2019-01-01T11:22:50Z'},
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a2',
            {
                'id': 'id',
                'user_id': 'user_id',
                'created_at': '2019-01-01T11:22:33Z',
                'ringing_at': '2019-01-01T11:22:33Z',
                'answered_at': '2019-01-01T11:22:33Z',
                'completed_at': None,
                'num_from': '+7900',
                'num_to': '+7901',
                'direction': 'outgoing',
                'record_urls': ['url_1', 'url_2'],
                'status_completed': 'answered',
                'hangup_disposition': None,
                'error': None,
                'is_synced': True,
                'provider_id': 'provider_id',
                'csat_value': 5,
            },
            200,
            [
                {'id': 'test_call'},
                {
                    'id': 'id',
                    'user_id': 'user_id',
                    'created_at': '2019-01-01T11:22:33Z',
                    'ringing_at': '2019-01-01T11:22:33Z',
                    'answered_at': '2019-01-01T11:22:33Z',
                    'completed_at': None,
                    'num_from': '+7900',
                    'num_to': '+7901',
                    'num_from_pd_id': 'phone_pd_id_9',
                    'num_to_pd_id': 'phone_pd_id_10',
                    'direction': 'outgoing',
                    'record_urls': ['url_1', 'url_2'],
                    'status_completed': 'answered',
                    'hangup_disposition': None,
                    'error': None,
                    'is_synced': True,
                    'provider_id': 'provider_id',
                    'stat_created': datetime.datetime(2019, 11, 11, 12, 0),
                    'line': 'first',
                    'csat_value': 5,
                },
            ],
            35,
            [
                {'sender': {'role': 'support'}},
                {
                    'sender': {'role': 'driver'},
                    'metadata': {'created': '2019-01-01T11:22:58Z'},
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a2',
            {
                'id': 'id',
                'user_id': 'user_id',
                'created_at': '2019-01-01T11:22:30Z',
                'ringing_at': '2019-01-01T11:22:33Z',
                'answered_at': '2019-01-01T11:22:33Z',
                'completed_at': None,
                'num_from': '+7900',
                'num_to': '+7901',
                'direction': 'outgoing',
                'record_urls': ['url_1', 'url_2'],
                'status_completed': 'answered',
                'hangup_disposition': None,
                'error': None,
                'is_synced': True,
                'provider_id': 'provider_id',
                'csat_value': 5,
            },
            200,
            [
                {'id': 'test_call'},
                {
                    'id': 'id',
                    'user_id': 'user_id',
                    'created_at': '2019-01-01T11:22:30Z',
                    'ringing_at': '2019-01-01T11:22:33Z',
                    'answered_at': '2019-01-01T11:22:33Z',
                    'completed_at': None,
                    'num_from': '+7900',
                    'num_to': '+7901',
                    'num_from_pd_id': 'phone_pd_id_9',
                    'num_to_pd_id': 'phone_pd_id_10',
                    'direction': 'outgoing',
                    'record_urls': ['url_1', 'url_2'],
                    'status_completed': 'answered',
                    'hangup_disposition': None,
                    'error': None,
                    'is_synced': True,
                    'provider_id': 'provider_id',
                    'stat_created': datetime.datetime(2019, 11, 11, 12, 0),
                    'line': 'first',
                    'csat_value': 5,
                },
            ],
            35,
            [
                {'sender': {'role': 'support'}},
                {
                    'sender': {'role': 'driver'},
                    'metadata': {'created': '2019-01-01T11:22:58Z'},
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a2',
            {
                'id': 'id',
                'user_id': 'user_id',
                'created_at': '2019-01-01T11:22:35Z',
                'ringing_at': '2019-01-01T11:22:35Z',
                'answered_at': '2019-01-01T11:22:35Z',
                'completed_at': None,
                'num_from': '+7900',
                'num_to': '+7901',
                'direction': 'outgoing',
                'record_urls': ['url_1', 'url_2'],
                'status_completed': 'answered',
                'hangup_disposition': None,
                'error': None,
                'is_synced': True,
                'provider_id': 'provider_id',
                'csat_value': 5,
            },
            200,
            [
                {'id': 'test_call'},
                {
                    'id': 'id',
                    'user_id': 'user_id',
                    'created_at': '2019-01-01T11:22:35Z',
                    'ringing_at': '2019-01-01T11:22:35Z',
                    'answered_at': '2019-01-01T11:22:35Z',
                    'completed_at': None,
                    'num_from': '+7900',
                    'num_to': '+7901',
                    'num_from_pd_id': 'phone_pd_id_9',
                    'num_to_pd_id': 'phone_pd_id_10',
                    'direction': 'outgoing',
                    'record_urls': ['url_1', 'url_2'],
                    'status_completed': 'answered',
                    'hangup_disposition': None,
                    'error': None,
                    'is_synced': True,
                    'provider_id': 'provider_id',
                    'stat_created': datetime.datetime(2019, 11, 11, 12, 0),
                    'line': 'urgent',
                    'csat_value': 5,
                },
            ],
            35,
            [
                {'sender': {'role': 'support'}},
                {
                    'sender': {'role': 'driver'},
                    'metadata': {'created': '2019-01-01T11:22:58Z'},
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a2',
            {
                'id': 'id',
                'user_id': 'user_id',
                'created_at': 'qweaqwe',
                'ringing_at': '2019-01-01T11:22:35Z',
                'answered_at': '2019-01-01T11:22:35Z',
                'completed_at': None,
                'num_from': '+7900',
                'num_to': '+7901',
                'direction': 'outgoing',
                'record_urls': ['url_1', 'url_2'],
                'status_completed': 'answered',
                'hangup_disposition': None,
                'error': None,
                'is_synced': True,
                'provider_id': 'provider_id',
                'csat_value': 5,
            },
            200,
            [
                {'id': 'test_call'},
                {
                    'id': 'id',
                    'user_id': 'user_id',
                    'created_at': 'qweaqwe',
                    'ringing_at': '2019-01-01T11:22:35Z',
                    'answered_at': '2019-01-01T11:22:35Z',
                    'completed_at': None,
                    'num_from': '+7900',
                    'num_to': '+7901',
                    'num_from_pd_id': 'phone_pd_id_9',
                    'num_to_pd_id': 'phone_pd_id_10',
                    'direction': 'outgoing',
                    'record_urls': ['url_1', 'url_2'],
                    'status_completed': 'answered',
                    'hangup_disposition': None,
                    'error': None,
                    'is_synced': True,
                    'provider_id': 'provider_id',
                    'stat_created': datetime.datetime(2019, 11, 11, 12, 0),
                    'line': 'urgent',
                    'csat_value': 5,
                },
            ],
            35,
            [
                {'sender': {'role': 'support'}},
                {
                    'sender': {'role': 'driver'},
                    'metadata': {'created': '2019-01-01T11:22:58Z'},
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a2',
            {
                'source': 'telphin',
                'id': 'id',
                'user_id': 'user_id',
                'created_at': '2019-01-01T11:22:33Z',
                'ringing_at': '2019-01-01T11:22:33Z',
                'answered_at': '2019-01-01T11:22:33Z',
                'completed_at': None,
                'num_from': '+7900',
                'num_to': '+7901',
                'direction': 'outgoing',
                'record_urls': ['url_1', 'url_2'],
                'status_completed': 'answered',
                'hangup_disposition': None,
                'error': None,
                'is_synced': True,
                'provider_id': 'provider_id',
                'csat_value': 5,
                'tenant': 'ats1',
            },
            200,
            [
                {'id': 'test_call'},
                {
                    'source': 'telphin',
                    'id': 'id',
                    'user_id': 'user_id',
                    'created_at': '2019-01-01T11:22:33Z',
                    'ringing_at': '2019-01-01T11:22:33Z',
                    'answered_at': '2019-01-01T11:22:33Z',
                    'completed_at': None,
                    'num_from': '+7900',
                    'num_to': '+7901',
                    'num_from_pd_id': 'phone_pd_id_9',
                    'num_to_pd_id': 'phone_pd_id_10',
                    'direction': 'outgoing',
                    'record_urls': ['url_1', 'url_2'],
                    'status_completed': 'answered',
                    'hangup_disposition': None,
                    'error': None,
                    'is_synced': True,
                    'provider_id': 'provider_id',
                    'stat_created': datetime.datetime(2019, 11, 11, 12, 0),
                    'line': 'first',
                    'csat_value': 5,
                    'tenant': 'ats1',
                },
            ],
            35,
            [
                {'sender': {'role': 'support'}},
                {
                    'sender': {'role': 'driver'},
                    'metadata': {'created': '2019-01-01T11:22:58Z'},
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a2',
            {
                'source': 'oktell',
                'id': 'id',
                'user_id': 'user_id',
                'created_at': '2019-01-01T11:22:33Z',
                'ringing_at': '2019-01-01T11:22:33Z',
                'answered_at': '2019-01-01T11:22:33Z',
                'completed_at': None,
                'num_to': '+7901',
                'direction': 'outgoing',
                'status_completed': 'answered',
                'hangup_disposition': None,
                'error': None,
                'is_synced': True,
                'csat_value': 5,
            },
            200,
            [
                {'id': 'test_call'},
                {
                    'source': 'oktell',
                    'id': 'id',
                    'user_id': 'user_id',
                    'created_at': '2019-01-01T11:22:33Z',
                    'ringing_at': '2019-01-01T11:22:33Z',
                    'answered_at': '2019-01-01T11:22:33Z',
                    'completed_at': None,
                    'num_to': '+7901',
                    'num_to_pd_id': 'phone_pd_id_10',
                    'direction': 'outgoing',
                    'status_completed': 'answered',
                    'hangup_disposition': None,
                    'record_urls': [],
                    'error': None,
                    'is_synced': True,
                    'stat_created': datetime.datetime(2019, 11, 11, 12, 0),
                    'line': 'first',
                    'csat_value': 5,
                },
            ],
            35,
            [
                {'sender': {'role': 'support'}},
                {
                    'sender': {'role': 'driver'},
                    'metadata': {'created': '2019-01-01T11:22:58Z'},
                },
            ],
        ),
    ],
)
async def test_call_webhook(
        task_id,
        data,
        expected_code,
        expected_call_info,
        first_answer,
        messages,
        cbox,
        mock_chat_get_history,
        mock_personal,
):
    mock_chat_get_history({'messages': messages})
    await cbox.post(
        '/v1/webhooks/%s/call' % task_id,
        data=data,
        headers={'YaTaxi-Api-Key': 'some_telphin_token'},
    )
    assert cbox.status == expected_code
    if cbox.status == 200:
        task = await cbox.db.support_chatterbox.find_one(
            {'_id': bson.ObjectId(task_id)},
        )
        assert task['meta_info']['calls'] == expected_call_info

    await cbox.post(
        '/v1/webhooks/%s/call' % task_id,
        data=data,
        headers={'YaTaxi-Api-Key': 'some_telphin_token'},
    )
    assert cbox.status == expected_code
    if cbox.status == 200:
        task = await cbox.db.support_chatterbox.find_one(
            {'_id': bson.ObjectId(task_id)},
        )
        assert task['meta_info']['calls'] == expected_call_info
        if first_answer is not None:
            assert task['first_answer'] == first_answer
        else:
            assert 'first_answer' not in task


@pytest.mark.now('2019-11-11T12:00:00+0')
@pytest.mark.parametrize(
    'task_id, first_data, second_data, expected_code, expected_call_info,'
    'first_answer',
    [
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'id': 'id',
                'user_id': '',
                'created_at': '2019-01-01T11:22:33Z',
                'ringing_at': '',
                'answered_at': '',
                'completed_at': None,
                'num_from': '',
                'num_to': '',
                'direction': 'outgoing',
                'record_urls': [],
                'status_completed': 'answered',
                'hangup_disposition': None,
                'error': None,
                'is_synced': True,
                'provider_id': '',
            },
            {
                'id': 'id',
                'user_id': 'user_id',
                'created_at': '',
                'ringing_at': '2019-01-01T11:22:33Z',
                'answered_at': '2019-01-01T11:22:33Z',
                'completed_at': None,
                'num_from': '+7900',
                'num_to': '+7901',
                'direction': '',
                'record_urls': ['url_1', 'url_2'],
                'status_completed': '',
                'hangup_disposition': None,
                'error': None,
                'is_synced': True,
                'provider_id': 'provider_id',
            },
            200,
            [
                {
                    'id': 'id',
                    'user_id': 'user_id',
                    'created_at': '2019-01-01T11:22:33Z',
                    'ringing_at': '2019-01-01T11:22:33Z',
                    'answered_at': '2019-01-01T11:22:33Z',
                    'completed_at': None,
                    'num_from': '+7900',
                    'num_to': '+7901',
                    'direction': 'outgoing',
                    'record_urls': ['url_1', 'url_2'],
                    'status_completed': 'answered',
                    'hangup_disposition': None,
                    'error': None,
                    'is_synced': True,
                    'provider_id': 'provider_id',
                    'stat_created': datetime.datetime(2019, 11, 11, 12, 0),
                    'line': 'first',
                },
            ],
            20645257,
        ),
    ],
)
async def test_call_webhook_double_update(
        task_id,
        first_data,
        second_data,
        expected_code,
        expected_call_info,
        first_answer,
        mock_chat_get_history,
        cbox,
):
    mock_chat_get_history({'messages': []})
    await cbox.post(
        '/v1/webhooks/%s/call' % task_id,
        data=first_data,
        headers={'YaTaxi-Api-Key': 'some_telphin_token'},
    )
    assert cbox.status == expected_code
    await cbox.app.db.support_chatterbox.update(
        {'_id': bson.ObjectId(task_id)}, {'$set': {'line': 'second'}},
    )

    await cbox.post(
        '/v1/webhooks/%s/call' % task_id,
        data=second_data,
        headers={'YaTaxi-Api-Key': 'some_telphin_token'},
    )
    assert cbox.status == expected_code
    if cbox.status == 200:
        task = await cbox.db.support_chatterbox.find_one(
            {'_id': bson.ObjectId(task_id)},
        )
        assert task['meta_info']['calls'] == expected_call_info
        if first_answer:
            assert task['first_answer'] == first_answer
        else:
            assert 'first_answer' not in task


@pytest.mark.config(
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {'num_from': 'phones', 'num_to': 'phones'},
    },
)
@pytest.mark.parametrize(
    'ticket, data, expected_code, expected_comment_kwargs',
    [
        ('TESTBACKEND-1', {}, 400, None),
        (
            'TESTBACKEND-1',
            {
                'id': 'id',
                'user_id': 'user_id',
                'created_at': '2019-01-01T11:22:33Z',
                'ringing_at': '2019-01-01T11:22:33Z',
                'answered_at': '2019-01-01T11:22:33Z',
                'completed_at': None,
                'num_from': '+7900',
                'num_to': '+7901',
                'direction': 'outgoing',
                'record_urls': ['host/path/record_1', 'host/path/record_2'],
                'status_completed': 'answered',
                'hangup_disposition': None,
                'is_synced': True,
                'csat_value': 5,
            },
            400,
            None,
        ),
        (
            'TESTBACKEND-1',
            {
                'id': 'call_id',
                'user_id': 'user_id',
                'created_at': '2019-01-01T11:22:33Z',
                'ringing_at': '2019-01-01T11:22:33Z',
                'answered_at': '2019-01-01T11:22:33Z',
                'completed_at': None,
                'num_from': '+7900',
                'num_to': '+7901',
                'direction': 'outgoing',
                'record_urls': ['host/path/record_1', 'host/path/record_2'],
                'status_completed': 'answered',
                'hangup_disposition': None,
                'is_synced': True,
                'error': None,
                'provider_id': 'provider_id',
                'csat_value': 5,
                'tenant': 'default',
            },
            200,
            {
                'text': (
                    'Оператор user_id совершил звонок '
                    'с номера +7900 на номер +7901\n'
                    'Время создания звонка: 01.01.2019 14:22:33\n'
                    'Время установления соединения: 01.01.2019 14:22:33\n'
                    'Время ответа на вызов: 01.01.2019 14:22:33\n'
                    'Время окончания вызова: -\n'
                    'Направление вызова: исходящий\n'
                    'Статус звонка: отвечен\n'
                    'Инициатор разрыва звонка: -\n'
                    'Идентификатор вызова: provider_id\n'
                    'Список записей звонка: '
                    'https://supchat.taxi.dev.yandex-team.ru/chatterbox-api/'
                    'v1/startrek/sip_record/call_id/0, '
                    'https://supchat.taxi.dev.yandex-team.ru/chatterbox-api/'
                    'v1/startrek/sip_record/call_id/1\n'
                    'Ошибка: -\n'
                    'АТС: default\n'
                ),
            },
        ),
        (
            'TESTBACKEND-1',
            {
                'id': 'call_id',
                'user_id': 'user_id',
                'created_at': '2019-01-01T11:22:33Z',
                'ringing_at': '2019-01-01T11:22:33Z',
                'answered_at': '2019-01-01T11:22:33Z',
                'completed_at': None,
                'num_from': '+7900',
                'num_to': '+7901',
                'direction': 'outgoing',
                'record_urls': None,
                'status_completed': 'answered',
                'hangup_disposition': None,
                'is_synced': True,
                'error': None,
                'provider_id': 'provider_id',
                'csat_value': 5,
            },
            200,
            {
                'text': (
                    'Оператор user_id совершил звонок '
                    'с номера +7900 на номер +7901\n'
                    'Время создания звонка: 01.01.2019 14:22:33\n'
                    'Время установления соединения: 01.01.2019 14:22:33\n'
                    'Время ответа на вызов: 01.01.2019 14:22:33\n'
                    'Время окончания вызова: -\n'
                    'Направление вызова: исходящий\n'
                    'Статус звонка: отвечен\n'
                    'Инициатор разрыва звонка: -\n'
                    'Идентификатор вызова: provider_id\n'
                    'Список записей звонка: -\n'
                    'Ошибка: -\n'
                    'АТС: \n'
                ),
            },
        ),
        (
            'TESTBACKEND-1',
            {
                'id': 'call_id',
                'user_id': 'user_id',
                'created_at': '2019-01-01T11:22:33Z',
                'ringing_at': '2019-01-01T11:22:33Z',
                'answered_at': '2019-01-01T11:22:33Z',
                'completed_at': None,
                'num_from': '+7900',
                'num_to': '+7901',
                'direction': 'incoming',
                'record_urls': ['host/path/record_1', 'host/path/record_2'],
                'status_completed': 'rejected',
                'hangup_disposition': 'internal_cancel',
                'error': None,
                'is_synced': True,
                'provider_id': 'provider_id',
                'csat_value': 5,
                'tenant': 'ats1',
            },
            200,
            {
                'text': (
                    'Оператор user_id совершил звонок '
                    'с номера +7900 на номер +7901\n'
                    'Время создания звонка: 01.01.2019 14:22:33\n'
                    'Время установления соединения: 01.01.2019 14:22:33\n'
                    'Время ответа на вызов: 01.01.2019 14:22:33\n'
                    'Время окончания вызова: -\n'
                    'Направление вызова: входящий\n'
                    'Статус звонка: отклонён\n'
                    'Инициатор разрыва звонка: вызов завершен сервером\n'
                    'Идентификатор вызова: provider_id\n'
                    'Список записей звонка: '
                    'https://supchat.taxi.dev.yandex-team.ru/chatterbox-api/'
                    'v1/startrek/sip_record/call_id/0, '
                    'https://supchat.taxi.dev.yandex-team.ru/chatterbox-api/'
                    'v1/startrek/sip_record/call_id/1\n'
                    'Ошибка: -\n'
                    'АТС: ats1\n'
                ),
            },
        ),
    ],
)
async def test_tracker_call_webhook(
        cbox,
        mock_st_get_ticket,
        mock_st_create_comment,
        ticket,
        data,
        expected_code,
        expected_comment_kwargs,
        mock_personal,
):
    await cbox.post(
        '/v1/webhooks/{}/tracker_call'.format(ticket),
        data=data,
        headers={'YaTaxi-Api-Key': 'some_telphin_token'},
    )
    assert cbox.status == expected_code

    if expected_comment_kwargs is not None:
        comment_call = mock_st_create_comment.calls[0]
        assert comment_call['args'] == (ticket,)
        comment_call['kwargs'].pop('log_extra')
        assert comment_call['kwargs'] == expected_comment_kwargs
    else:
        assert not mock_st_create_comment.calls

    if expected_code != 200:
        return
    (get_ticket_call,) = mock_st_get_ticket.calls
    assert get_ticket_call['ticket'] == ticket


@pytest.mark.now('2019-11-11T12:00:00+0')
@pytest.mark.config(
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {'num_from': 'phones', 'num_to': 'phones'},
    },
)
@pytest.mark.parametrize(
    'ticket, data, expected_code, expected_comment_kwargs, expected_pg_recs',
    [
        (
            'TESTBACKEND-1',
            {
                'id': 'call_id',
                'user_id': 'user_id',
                'created_at': '2019-01-01T11:22:33Z',
                'ringing_at': '2019-01-01T11:22:33Z',
                'answered_at': '2019-01-01T11:22:33Z',
                'completed_at': None,
                'num_from': '+7900',
                'num_to': '+7901',
                'direction': 'outgoing',
                'record_urls': ['host/path/record_1', 'host/path/record_2'],
                'status_completed': 'answered',
                'hangup_disposition': None,
                'is_synced': True,
                'error': None,
                'provider_id': 'provider_id',
                'csat_value': 5,
                'tenant': 'test_ats',
            },
            200,
            {
                'text': (
                    'Оператор user_id совершил звонок '
                    'с номера +7900 на номер +7901\n'
                    'Время создания звонка: 01.01.2019 14:22:33\n'
                    'Время установления соединения: 01.01.2019 14:22:33\n'
                    'Время ответа на вызов: 01.01.2019 14:22:33\n'
                    'Время окончания вызова: -\n'
                    'Направление вызова: исходящий\n'
                    'Статус звонка: отвечен\n'
                    'Инициатор разрыва звонка: -\n'
                    'Идентификатор вызова: provider_id\n'
                    'Список записей звонка: '
                    'https://chatterbox.taxi.dev.yandex-team.ru/'
                    'v1/startrek/sip_record/call_id/1, '
                    'https://chatterbox.taxi.dev.yandex-team.ru/'
                    'v1/startrek/sip_record/call_id/2\n'
                    'Ошибка: -\n'
                    'АТС: test_ats\n'
                ),
            },
            [
                (
                    'call_id',
                    'user_id',
                    datetime.datetime(2019, 1, 1, 11, 22, 33),
                    datetime.datetime(2019, 1, 1, 11, 22, 33),
                    datetime.datetime(2019, 1, 1, 11, 22, 33),
                    None,
                    '+7900',
                    '+7901',
                    'outgoing',
                    ['host/path/record_1', 'host/path/record_2'],
                    'answered',
                    None,
                    None,
                    True,
                    'provider_id',
                    5,
                    'phone_pd_id_9',
                    'phone_pd_id_10',
                    'kaluga',
                    'test_ats',
                ),
            ],
        ),
    ],
)
async def test_tracker_save_call_info(
        cbox,
        pgsql,
        mock_st_get_ticket_with_status,
        mock_st_create_comment,
        ticket,
        data,
        expected_code,
        expected_comment_kwargs,
        expected_pg_recs,
        mock_personal,
):
    mocked_get_ticket = mock_st_get_ticket_with_status(
        'open', custom_fields={'ticket_type': 'kaluga'},
    )
    await cbox.post(
        '/v1/webhooks/{}/tracker_call'.format(ticket),
        data=data,
        headers={'YaTaxi-Api-Key': 'some_telphin_token'},
    )
    assert cbox.status == expected_code

    if expected_code != 200:
        return
    (get_ticket_call,) = mocked_get_ticket.calls
    assert get_ticket_call['ticket'] == ticket

    cursor = pgsql['chatterbox'].cursor()
    cursor.execute(
        'SELECT record_urls FROM chatterbox.startrack_sip_calls '
        'WHERE call_id = %s',
        ('my_call',),
    )
    (record_urls,) = cursor.fetchone()
    assert record_urls == [
        'https://chatterbox.orivet.ru/telphin/storage/record-id_1',
        'https://chatterbox.orivet.ru/telphin/storage/record-id_2',
    ]
    cursor.execute(
        'SELECT '
        'call_id, '
        'user_id, '
        'created_at, '
        'ringing_at, '
        'answered_at, '
        'completed_at, '
        'num_from, '
        'num_to, '
        'direction, '
        'record_urls, '
        'status_completed, '
        'hangup_disposition, '
        'error, '
        'is_synced, '
        'provider_id, '
        'csat_value, '
        'num_from_pd_id, '
        'num_to_pd_id, '
        'ticket_type, '
        'tenant '
        'FROM chatterbox.startrack_sip_calls '
        'WHERE call_id = %s',
        ('call_id',),
    )
    recs = cursor.fetchall()
    assert recs == expected_pg_recs
