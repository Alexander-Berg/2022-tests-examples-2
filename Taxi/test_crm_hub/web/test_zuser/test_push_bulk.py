import pytest

import crm_hub.logic.communication as comm
import crm_hub.logic.communication.base as comm_base
from test_crm_hub.web.utils import db

USER_ID = 'asd12x123d213C21312223'
ENTITY_TYPE = 'zuser'
AUDIENCE_TYPE = 'Zuser'
CHANNEL = 'PUSH'
CHANNEL_NAME = 'zuser_push'
SENDING_TABLE_NAME = 'test_table'

PUSH_TOKENS = {
    'apns_token': 'apns_token',
    'gcm_token': 'gcm_token',
    'hms_token': 'hms_token',
}


@pytest.mark.config(
    CRM_HUB_BATCH_SENDING_SETTINGS={
        'channel_settings': {
            'zuser_push': {
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
async def test_zuser_push_bulk_communicate(stq3_context, mockserver, patch):
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

    @mockserver.json_handler(
        'ucommunications/user/unauthorized/notification/push',
    )
    async def _zuser_push(*args, **kwargs):
        return {}

    entities = [
        {
            'id': 1,
            'zuser_id': USER_ID,
            'city': 'Кот д’Вуар',
            'country': 'Russia',
            'application': 'android',
            'locale': 'ru_RU',
            'yes': 'no',
            'text': 'hello1',
            'deeplink': 'yandextaxi://banner?id=5f7488db',
            **PUSH_TOKENS,
        },
        {
            'id': 2,
            'zuser_id': USER_ID,
            'city': 'Кот д\'Вуар',
            'country': 'France',
            'application': 'android',
            'locale': 'fr_FR',
            'text': 'hello2',
            'deeplink': 'yandextaxi://banner?id=5f7488db',
            **PUSH_TOKENS,
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

    assert _batch_sending.times_called == 1
    assert _zuser_push.times_called == 2

    for entity in entities:
        zuser_push_call = _zuser_push.next_call()['args'][0].json
        assert zuser_push_call['intent'] == 'some_intent'
        assert zuser_push_call['ttl'] == 30
        assert zuser_push_call['application'] == entity['application']

        assert zuser_push_call['push_tokens'] == PUSH_TOKENS

        actual_payload = zuser_push_call['data']['payload']
        assert actual_payload['category'] == 'QR'
        assert actual_payload['deeplink'] == entity['deeplink']
        assert actual_payload['msg'] == entity['text']
        assert actual_payload['show_in_foreground']

        actual_repack = zuser_push_call['data']['repack']

        # fcm
        assert len(actual_repack['fcm']) == 2
        assert 'repack_payload' in actual_repack['fcm']

        # hms
        assert len(actual_repack['hms']) == 2
        assert 'repack_payload' in actual_repack['hms']

        # apns
        assert len(actual_repack['apns']) == 2
        assert len(actual_repack['apns']['aps']) == 3
        assert 'repack_payload' in actual_repack['apns']


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
async def test_silent_bulk_push(stq3_context, mockserver, patch):
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

    @mockserver.json_handler(
        'ucommunications/user/unauthorized/notification/push',
    )
    async def _zuser_push(*args, **kwargs):
        return {}

    entities = [
        {
            'id': 1,
            'zuser_id': USER_ID,
            'city': 'Кот д’Вуар',
            'country': 'Russia',
            'application': 'android',
            'locale': 'ru_RU',
            'yes': 'no',
            'text': 'hello1',
            'deeplink': 'yandextaxi://banner?id=5f7488db',
            **PUSH_TOKENS,
        },
        {
            'id': 2,
            'zuser_id': USER_ID,
            'city': 'Кот д\'Вуар',
            'country': 'France',
            'application': 'android',
            'locale': 'fr_FR',
            'text': 'hello2',
            'deeplink': 'yandextaxi://banner?id=5f7488db',
            **PUSH_TOKENS,
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
    assert _zuser_push.times_called == 2

    for entity in entities:
        zuser_push_call = _zuser_push.next_call()['args'][0].json
        assert zuser_push_call['intent'] == 'some_intent'
        assert zuser_push_call['ttl'] == 30
        assert zuser_push_call['application'] == entity['application']

        assert zuser_push_call['push_tokens'] == PUSH_TOKENS
        assert zuser_push_call['data']['payload'] == expected_payload

        actual_repack = zuser_push_call['data']['repack']

        # fcm
        assert len(actual_repack['fcm']) == 1
        assert 'repack_payload' in actual_repack['fcm']

        # hms
        assert len(actual_repack['hms']) == 1
        assert 'repack_payload' in actual_repack['hms']

        # apns
        assert len(actual_repack['apns']) == 2
        assert len(actual_repack['apns']['aps']) == 2
        assert 'repack_payload' in actual_repack['apns']
