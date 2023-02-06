import pytest

import crm_hub.logic.communication as comm
import crm_hub.logic.communication.base as comm_base
from crm_hub.logic.communication.user import push_utils
from test_crm_hub.web.utils import db

USER_ID = 'd668480cf6799d9532f43e326f0ecfd8'
ENTITY_TYPE = 'user'
AUDIENCE_TYPE = 'User'
CHANNEL = 'PUSH'
CHANNEL_NAME = 'user_push'
SENDING_TABLE_NAME = 'test_table'


@pytest.mark.config(
    CRM_HUB_BATCH_SENDING_SETTINGS={
        'channel_settings': {
            'user_push': {
                'max_connections': 4,
                'cooling_off_limit': 100,
                'cooling_off_time_ms': 500,
                'chunk_size': 2,
                'channel_policy_allowed': False,
            },
        },
    },
    CRM_HUB_RETRIES_SETTINGS={},
)
@pytest.mark.pgsql('crm_hub', files=['batch_sending.sql'])
async def test_user_push_bulk_communicate(stq3_context, mockserver, patch):
    @mockserver.json_handler('crm-admin/v1/batch-sending/item')
    async def _batch_sending(*_a, **_kw):
        return {
            'name': 'my_name',
            'entity_type': AUDIENCE_TYPE,
            'channel': CHANNEL,
            'content': 'my_content',
            'deeplink': 'my_deeplink',
            'global_control': False,
            'local_control': False,
            'yt_table': 'my_yt_table',
            'yt_test_table': 'yt_test_table',
            'channel_info': {
                'channel_name': CHANNEL_NAME,
                'intent': 'some_intent',
                'content': 'sample text',
                'ttl': 30,
                'deeplink': 't1.ru/a/',
            },
            'report_group_id': '1_test',
            'group_name': 'Group 1',
        }

    @mockserver.json_handler('ucommunications/user/notification/bulk-push')
    async def _bulk_push(*_a, **_kw):
        return {}

    entities = [
        {
            'id': 1,
            'user_id': USER_ID,
            'city': 'Кот д’Вуар',
            'country': 'Russia',
            'application': 'android',
            'locale': 'ru_RU',
            'yes': 'no',
            'text': 'hello1',
            'deeplink': 'yandextaxi://banner?id=5f7488db',
        },
        {
            'id': 2,
            'user_id': USER_ID,
            'city': 'Кот д\'Вуар',
            'country': 'France',
            'application': 'android',
            'locale': 'fr_FR',
            'text': 'hello2',
            'deeplink': 'yandextaxi://banner?id=5f7488db',
        },
    ]

    await db.create_table_for_sending(
        context=stq3_context, entities=entities, table_name=SENDING_TABLE_NAME,
    )

    communication_data = comm_base.StqBulkCommunicationData(
        campaign_id=1,
        group_id=99,
        batch_info={},
        verify=False,
        control=False,
        denied=False,
    )
    communication = await comm.create_communication_from_task(
        stq3_context, communication_data,
    )
    await communication.process(
        entities=entities,
        filtered=[],
        batch_info={
            'id': '00000000000000000000000000000001',
            'pg_table': SENDING_TABLE_NAME,
            'entity_type': ENTITY_TYPE,
        },
    )

    get_payload = push_utils.UserPushCommunicationMixin.get_default_payload
    expected_payload = get_payload('sample text')
    expected_payload['deeplink'] = 't1.ru/a/'
    payload_keys = list(expected_payload.keys())

    assert _batch_sending.times_called == 1
    assert _bulk_push.times_called == 1

    bulk_push_call = _bulk_push.next_call()['_a'][0].json
    assert bulk_push_call['intent'] == 'some_intent'
    assert bulk_push_call['ttl'] == 30
    assert bulk_push_call['data']['payload'] == expected_payload

    assert len(bulk_push_call['data']['repack']['fcm']) == 2
    assert 'repack_payload' in bulk_push_call['data']['repack']['fcm']

    assert len(bulk_push_call['data']['repack']['hms']) == 2
    assert 'repack_payload' in bulk_push_call['data']['repack']['hms']

    assert len(bulk_push_call['data']['repack']['apns']) == 2
    assert len(bulk_push_call['data']['repack']['apns']['aps']) == 3

    recipients = bulk_push_call['recipients']
    for recipient in recipients:
        assert recipient['user_id'] == USER_ID
        assert recipient['locale'] in ('ru_RU', 'fr_FR')

        expected_payload['msg'] = recipient['data']['payload']['msg']
        expected_payload['deeplink'] = 'yandextaxi://banner?id=5f7488db'
        assert recipient['data']['payload'] == expected_payload

        repack = recipient['data']['repack']
        assert repack['apns']['repack_payload'] == payload_keys
        assert repack['fcm']['repack_payload'] == payload_keys
        assert repack['hms']['repack_payload'] == payload_keys


PAYLOAD_SAMPLE = [
    {
        'campaign_id': 1,
        'group_id': 99,
        'payload': {'hello': 'hi', 'smth': 'one', 'two': 2, '3': 3},
    },
]


@pytest.mark.config(
    CRM_HUB_BATCH_SENDING_SETTINGS={
        'channel_settings': {
            'user_push': {
                'max_connections': 4,
                'cooling_off_limit': 100,
                'cooling_off_time_ms': 500,
                'chunk_size': 2,
                'channel_policy_allowed': False,
            },
        },
    },
    CRM_HUB_SILENT_PUSH=PAYLOAD_SAMPLE,
    CRM_HUB_RETRIES_SETTINGS={},
)
@pytest.mark.pgsql('crm_hub', files=['batch_sending.sql'])
async def test_silent_push(stq3_context, mockserver, patch):
    @mockserver.json_handler('crm-admin/v1/batch-sending/item')
    async def _batch_sending(*_a, **_kw):
        return {
            'name': 'my_name',
            'entity_type': AUDIENCE_TYPE,
            'channel': CHANNEL,
            'content': 'my_content',
            'deeplink': 'my_deeplink',
            'global_control': False,
            'local_control': False,
            'yt_table': 'my_yt_table',
            'yt_test_table': 'yt_test_table',
            'channel_info': {
                'channel_name': CHANNEL_NAME,
                'intent': 'some_intent',
                'content': 'sample text',
                'ttl': 30,
                'deeplink': 't1.ru/a/',
            },
            'report_group_id': '1_test',
            'group_name': 'Group 1',
        }

    @mockserver.json_handler('ucommunications/user/notification/bulk-push')
    async def _bulk_push(*_a, **_kw):
        return {}

    entities = [
        {
            'id': 1,
            'user_id': USER_ID,
            'city': 'Кот д’Вуар',
            'country': 'Russia',
            'application': 'android',
            'locale': 'ru_RU',
            'yes': 'no',
            'text': 'hello1',
            'deeplink': 'yandextaxi://banner?id=5f7488db',
        },
        {
            'id': 2,
            'user_id': USER_ID,
            'city': 'Кот д\'Вуар',
            'country': 'France',
            'application': 'android',
            'locale': 'fr_FR',
            'text': 'hello2',
            'deeplink': 'yandextaxi://banner?id=5f7488db',
        },
    ]

    await db.create_table_for_sending(
        context=stq3_context, entities=entities, table_name=SENDING_TABLE_NAME,
    )

    communication_data = comm_base.StqBulkCommunicationData(
        campaign_id=1,
        group_id=99,
        batch_info={},
        verify=False,
        control=False,
        denied=False,
    )
    communication = await comm.create_communication_from_task(
        stq3_context, communication_data,
    )
    await communication.process(
        entities=entities,
        filtered=[],
        batch_info={
            'id': '00000000000000000000000000000001',
            'pg_table': SENDING_TABLE_NAME,
            'entity_type': ENTITY_TYPE,
        },
    )

    expected_payload = PAYLOAD_SAMPLE[0]['payload']

    assert _batch_sending.times_called == 1
    assert _bulk_push.times_called == 1

    bulk_push_call = _bulk_push.next_call()['_a'][0].json
    assert bulk_push_call['intent'] == 'some_intent'
    assert bulk_push_call['ttl'] == 30
    assert bulk_push_call['data']['payload'] == expected_payload

    assert len(bulk_push_call['data']['repack']['fcm']) == 1
    assert 'repack_payload' in bulk_push_call['data']['repack']['fcm']

    assert len(bulk_push_call['data']['repack']['hms']) == 1
    assert 'repack_payload' in bulk_push_call['data']['repack']['hms']

    assert len(bulk_push_call['data']['repack']['apns']) == 2
    assert len(bulk_push_call['data']['repack']['apns']['aps']) == 2

    recipients = bulk_push_call['recipients']
    for recipient in recipients:
        assert recipient['user_id'] == USER_ID
        assert recipient['locale'] in ('ru_RU', 'fr_FR')
        assert 'data' not in recipient
