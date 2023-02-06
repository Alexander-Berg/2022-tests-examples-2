import logging
import uuid

import dateutil

from crm_hub.generated.service.swagger import models
from crm_hub.logic import utils


async def test_register_sending_in_scheduler(web_context, mockserver):
    @mockserver.json_handler('/crm-scheduler/v1/register_communiction_to_send')
    def _register_communication(request):
        return mockserver.make_response(status=200, json={})

    sending = models.api.BatchSendingFull(
        id=uuid.UUID('0' * 32),
        campaign_id=11,
        group_id=22,
        timezone_name='Europe/Moscow',
        entity_type='user',
        group_type='control',
        channel='push',
        channel_info=models.api.UserPushInfo.deserialize(
            {'channel_name': 'user_push'},
        ),
        start_id=33,
        state='NEW',
        use_policy=True,
        filter='filter',
        subfilters=[
            models.api.FilterObject.deserialize(
                {'column': 'efficiency', 'value': '0'},
            ),
        ],
        yt_table='yt_table',
        yt_test_table='yt_test_table',
        pg_table='pg_table',
        processing_chunk_size=10,
        created_at=dateutil.parser.parse('2021-07-08 12:05:00'),
        updated_at=None,
    )
    logger = logging.getLogger(__name__)
    crm_scheduler = web_context.clients.crm_scheduler
    await utils.register_sending_in_scheduler(
        context=web_context,
        is_admin_sending=True,
        sending=sending,
        crm_scheduler=crm_scheduler,
        sending_size=None,
        policy_enabled=None,
        send_enabled=None,
        dependency_id=None,
        logger=logger,
    )
    assert _register_communication.times_called == 1
