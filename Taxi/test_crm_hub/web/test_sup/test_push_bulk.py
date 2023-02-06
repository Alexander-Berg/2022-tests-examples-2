from aiohttp import web
import pytest

import crm_hub.logic.communication as comm
import crm_hub.logic.communication.base as comm_base
from test_crm_hub.web.utils import db

DEVICE_ID = '000b7e9672807dbc8c85996794e1173a'
ENTITY_TYPE = 'geo'
AUDIENCE_TYPE = 'Geo'
CHANNEL = 'PUSH'
CHANNEL_NAME = 'geo_push'
SENDING_TABLE_NAME = 'test_table'


@pytest.mark.config(
    CRM_HUB_BATCH_SENDING_SETTINGS={
        'channel_settings': {
            CHANNEL_NAME: {
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
async def test_sup_push_bulk_communicate(stq3_context, mockserver, mock_sup):
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
                'push_id': 'something_interesting',
            },
            'report_group_id': '1_test',
            'group_name': 'Group 1',
        }

    communication_data = comm_base.StqBulkCommunicationData(
        campaign_id=1,
        group_id=1,
        batch_info={'start_id': 0},
        verify=False,
        control=False,
        denied=False,
    )

    # Need mock crm-admin
    communication = await comm.create_communication_from_task(
        stq3_context, communication_data,
    )

    exp_entities = [
        {
            'id': 1,
            'device_id': DEVICE_ID,
            'city': 'Saint Petersburg',
            'country': 'Russia',
            'locale': 'ru_RU',
            'title': 'Hello1',
            'text': 'hello1',
            'deeplink': 'yandextaxi://banner?id=5f7488db',
        },
        {
            'id': 2,
            'device_id': DEVICE_ID,
            'city': 'Moscow',
            'country': 'Russian',
            'locale': 'fr_FR',
            'title': 'Hello2',
            'text': 'hello2',
            'deeplink': 'yandextaxi://banner?id=5f7488db',
        },
    ]

    await db.create_table_for_sending(
        context=stq3_context,
        entities=exp_entities,
        table_name=SENDING_TABLE_NAME,
    )

    @mock_sup('/pushes')
    async def _send_push(request):
        return web.json_response(request.json, status=200)

    await communication.process(
        entities=exp_entities,
        filtered=[],
        batch_info={
            'id': '00000000000000000000000000000001',
            'pg_table': SENDING_TABLE_NAME,
            'entity_type': ENTITY_TYPE,
        },
    )

    assert _batch_sending.times_called == 1
    assert _send_push.times_called == 2

    for exp_entity in exp_entities:
        request_json = _send_push.next_call()['request'].json

        assert request_json['receiver'][0].split('==')[1] == DEVICE_ID
        assert request_json['notification']['title'] == exp_entity['title']
        assert request_json['notification']['body'] == exp_entity['text']
        assert request_json['notification']['link'] == exp_entity['deeplink']

        assert request_json['data']['transit_id'] == f'1_1_0_{DEVICE_ID}'
        assert request_json['data']['push_id'] == 'something_interesting'
