import re

import pytest

import crm_hub.logic.communication as comm
import crm_hub.logic.communication.base as comm_base
from test_crm_hub.web.utils import db

DB_ID, UUID = (
    '7ad36bc7560449998acbe2c57a75c293',
    '870fbf758122ac002c302cff682d3488',
)
ENTITY_TYPE = 'driver'
AUDIENCE_TYPE = 'Driver'
CHANNEL = 'PUSH'
CHANNEL_NAME = 'driver_push'
SENDING_TABLE_NAME = 'test_table'


@pytest.mark.config(
    CRM_HUB_BATCH_SENDING_SETTINGS={
        'channel_settings': {
            'driver_push': {
                'max_connections': 4,
                'cooling_off_limit': 100,
                'cooling_off_time_ms': 500,
                'chunk_size': 2,
                'channel_policy_allowed': False,
            },
        },
    },
)
@pytest.mark.parametrize(
    'code, action', [(100, 'MessageNew'), (1300, 'PersonalOffer')],
)
@pytest.mark.pgsql('crm_hub', files=['batch_sending.sql'])
async def test_driver_push_bulk_communicate(
        code, stq3_context, mockserver, action,
):
    @mockserver.json_handler('crm-admin/v1/batch-sending/item')
    async def _batch_sending(*_a, **_kw):
        return {
            'name': 'my_name',
            'entity_type': AUDIENCE_TYPE,
            'channel': CHANNEL,
            'yt_table': 'my_yt_table',
            'yt_test_table': 'yt_test_table',
            'global_control': False,
            'local_control': False,
            'channel_info': {
                'action': 'MessageNew',
                'channel_name': CHANNEL_NAME,
                'content': 'my_content',
                'deeplink': 'my_deeplink',
                'code': code,
                'ttl': 30,
                'collapse_key': 'MessageNew:test',
            },
        }

    @mockserver.json_handler('/client-notify/v2/bulk-push')
    async def _bulk_push(request):
        assert 'data' in request.json

        id_field = request.json['data'].pop('id')
        assert re.fullmatch(r'([0-9a-f]{32})', id_field)

        if code == 1300:
            assert request.json['data'].pop('text') == 'my_content'
        else:
            assert code == 100
            assert request.json['data'].pop('message') == 'my_content'

        assert request.json == {
            'intent': action,
            'service': 'taximeter',
            'recipients': [
                {
                    'client_id': '{}-{}'.format(DB_ID, UUID),
                    'data': {'id': 1, 'covid': 19, 'message': {'yes': 'no'}},
                },
                {'client_id': '{}-{}'.format(DB_ID, UUID), 'data': {'id': 2}},
            ],
            'collapse_key': 'MessageNew:test',
            'ttl': 30,
            'data': {'campaign_id': 2, 'cm_group_id': 99, 'cm_wave_id': 0},
        }

        return {
            'notifications': [
                {'notification_id': 'notification_1'},
                {'notification_id': 'notification_2'},
            ],
        }

    entities = [
        {
            'id': 1,
            'db_id': DB_ID,
            'driver_uuid': UUID,
            'covid': 19,
            'message': {'yes': 'no'},
        },
        {'id': 2, 'db_id': DB_ID, 'driver_uuid': UUID},
    ]

    await db.create_table_for_sending(
        context=stq3_context, entities=entities, table_name=SENDING_TABLE_NAME,
    )

    communication_data = comm_base.StqBulkCommunicationData(
        campaign_id=2,
        group_id=99,
        batch_info={'start_id': 0},
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
            'start_id': 0,
        },
    )

    assert _batch_sending.times_called == 1
    assert _bulk_push.times_called == 1
