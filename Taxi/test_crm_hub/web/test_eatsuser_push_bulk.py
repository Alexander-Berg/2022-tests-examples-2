import pytest

import crm_hub.logic.communication as comm
import crm_hub.logic.communication.base as comm_base
from test_crm_hub.web.utils import db


EDA_CLIENT_ID = 'd668480cf6799d9532f43e326f0ecfd8'
ENTITY_TYPE = 'eatsuser'
AUDIENCE_TYPE = 'EatsUser'
CHANNEL_NAME = 'eatsuser_push'
SENDING_TABLE_NAME = 'test_table'


@pytest.mark.config(
    CRM_HUB_BATCH_SENDING_SETTINGS={
        'channel_settings': {
            'eatsuser_push': {
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
            'channel': 'PUSH',
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

    @mockserver.json_handler('client-notify/v2/push')
    async def _patch_send(request):
        assert request.json['meta'] == {'campaign_id': 3, 'group_id': 99}
        return {'notification_id': 'notification_1'}

    entities = [
        {
            'id': 1,
            'eda_client_id': EDA_CLIENT_ID,
            'text': 'Тут был дед',
            'title': 'Заголовок деда',
            'link': 'some',
        },
        {
            'id': 2,
            'eda_client_id': EDA_CLIENT_ID,
            'text': 'Со сменой президента, друзья!',
            'title': 'Победа в выборах',
            'link': 'some',
        },
    ]

    await db.create_table_for_sending(
        context=stq3_context, entities=entities, table_name=SENDING_TABLE_NAME,
    )

    communication_data = comm_base.StqBulkCommunicationData(
        campaign_id=3,
        group_id=99,
        batch_info={'start_id': 1010},
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
            'id': '00000000000000000000000000000003',
            'pg_table': SENDING_TABLE_NAME,
            'entity_type': ENTITY_TYPE,
            'start_id': 1010,
        },
    )

    assert _batch_sending.times_called == 1
    assert _patch_send.times_called == 2

    bulk_push_call = _patch_send.next_call()['request'].json
    assert bulk_push_call['client_id'] == EDA_CLIENT_ID
    assert bulk_push_call['service'] == 'eda-client'
    assert bulk_push_call['intent'] == 'some_intent'
    assert bulk_push_call['ttl'] == 30
