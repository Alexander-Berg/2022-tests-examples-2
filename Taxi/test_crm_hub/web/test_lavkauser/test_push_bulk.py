import pytest

import crm_hub.logic.communication as comm
import crm_hub.logic.communication.base as comm_base
from test_crm_hub.web.utils import db

USER_ID = 'd668480cf6799d9532f43e326f0ecfd8'
ENTITY_TYPE = 'lavkauser'
AUDIENCE_TYPE = 'LavkaUser'
CHANNEL = 'PUSH'
CHANNEL_NAME = 'lavkauser_push'
SENDING_TABLE_NAME = 'test_table'


@pytest.mark.config(
    CRM_HUB_BATCH_SENDING_SETTINGS={
        'channel_settings': {
            'lavkauser_push': {
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
async def test_lavkauser_push_bulk_communicate(
        stq3_context, mockserver, patch,
):
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
        },
        {
            'id': 2,
            'user_id': USER_ID,
            'city': 'Кот д\'Вуар',
            'country': 'France',
            'application': 'android',
            'locale': 'fr_FR',
        },
    ]

    await db.create_table_for_sending(
        context=stq3_context, entities=entities, table_name=SENDING_TABLE_NAME,
    )

    communication_data = comm_base.StqBulkCommunicationData(
        campaign_id=2,
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
    assert _bulk_push.times_called == 1
    bulk_push_call = _bulk_push.next_call()['_a'][0].json
    assert bulk_push_call['intent'] == 'some_intent'
    assert bulk_push_call['ttl'] == 30
    recipients = bulk_push_call['recipients']
    assert recipients[0]['user_id'] == USER_ID
    assert recipients[0]['locale'] == 'ru_RU'
