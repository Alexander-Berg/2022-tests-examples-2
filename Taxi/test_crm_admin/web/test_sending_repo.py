import datetime

import pytest

from crm_admin import storage
from crm_admin.generated.service.swagger import models


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_repo(web_context):
    send_at = datetime.datetime(2020, 10, 10, 10, 10, 10)

    sending_info = models.api.Sending(
        campaign_id=1,
        group_id=2,
        type=storage.SendingType.VERIFY,
        state=storage.SendingState.NEW,
        send_at=send_at,
        start_id=0,
    )

    sending_storage = storage.SendingStorage(web_context)
    sending_full = await sending_storage.create(sending_info)

    fetched_sending = await sending_storage.fetch(sending_full.id)
    assert fetched_sending.type == storage.SendingType.VERIFY
    assert fetched_sending.state == storage.SendingState.NEW
    assert fetched_sending.send_at == send_at
    assert fetched_sending.start_id == 0

    sending_full.type = storage.SendingType.PRODUCTION
    sending_full.state = storage.SendingState.PROCESSING
    sending_full.start_id = 3

    await sending_storage.update(sending_full)

    fetched_sending = await sending_storage.fetch(sending_full.id)
    assert fetched_sending.type == storage.SendingType.PRODUCTION
    assert fetched_sending.state == storage.SendingState.PROCESSING
    assert fetched_sending.send_at == send_at
    assert fetched_sending.start_id == 3
