# pylint: disable=unused-argument,unused-variable

import asynctest
import pytest

from crm_admin import settings
from crm_admin import storage
from crm_admin.utils import regular

CRM_ADMIN_GROUPS_V2 = {'all_on': True}


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.now('2021-01-27T11:59:00.0')
@pytest.mark.pgsql('crm_admin', files=['init-sending.sql'])
async def test_send_all(cron_context, patch):
    batch_sending_call = asynctest.CoroutineMock()
    cron_context.stq.crm_admin_batch_sending.call = batch_sending_call

    await regular.send.send_all(cron_context, settings.GROUPS_RESULT_STATE)

    sending_ids = [
        kwargs['kwargs']['sending_id']
        for _, kwargs in batch_sending_call.call_args_list
    ]

    db_sending = storage.SendingStorage(cron_context)
    campaign_ids = set()
    for sending_id in sending_ids:
        info = await db_sending.fetch(sending_id)
        campaign_ids.add(info.campaign_id)

    assert len(sending_ids) == 2
    assert campaign_ids == {1, 2}
