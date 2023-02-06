import datetime

import pytest

from crm_admin import settings
from crm_admin.api import get_trigger_campaign_list
from crm_admin.entity import error
from crm_admin.generated.service.swagger import requests
from crm_admin.storage import campaign_adapters


def test_schedule_interval():
    assert campaign_adapters.schedule_interval(
        '*/30 * * * *',
    ) == datetime.timedelta(minutes=30)

    assert campaign_adapters.schedule_interval(
        '0 1 * * *',
    ) == datetime.timedelta(days=1)


@pytest.mark.parametrize(
    'name, cooldown',
    [
        ('oneshot campaign', campaign_adapters.COOLDOWN),
        ('regular campaign', 86400 - 60),
    ],
)
@pytest.mark.now('2021-02-01T12:00:00.0')
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_group_cooldown(web_context, name, cooldown):
    params = requests.GetTriggerCampaignList(
        log_extra=None,
        middlewares=None,
        limit=10,
        offset=0,
        update_timestamp=None,
        projections=[settings.EXPERIMENT_PROJECTION],
        name=name,
        owner=None,
        status=None,
        entity_type=None,
        created_at=None,
        updated_at=None,
        order_by=None,
        order=None,
    )

    campaigns = await get_trigger_campaign_list.fetch_campaign_projections(
        context=web_context, request=params,
    )

    assert campaigns[0].experiment.groups[0].cooldown == cooldown


@pytest.mark.now('2021-02-01T12:00:00.0')
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_update_state(web_context):
    db_campaign = campaign_adapters.DbCampaign(web_context)
    target_state = 'NEW'

    campaign = await db_campaign.fetch(campaign_id=1)
    assert campaign.state != target_state

    # `update()` does not change a campaign state
    campaign.state = target_state
    await db_campaign.update(campaign)
    campaign = await db_campaign.fetch(campaign_id=1)
    assert campaign.state != target_state

    # while `update_sate()` does
    campaign.state = target_state
    await db_campaign.update_state(campaign)
    campaign = await db_campaign.fetch(campaign_id=1)
    assert campaign.state == target_state

    # unknown campaign id causes EntityNotFound error
    campaign.campaign_id = 100
    with pytest.raises(error.EntityNotFound):
        await db_campaign.update_state(campaign)


@pytest.mark.now('2021-02-01T12:00:00.0')
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_update_kind(web_context):
    db_campaign = campaign_adapters.DbCampaign(web_context)
    target_kind = 'tariff_in_city'
    target_subkind = 'comfortplus'

    campaign = await db_campaign.fetch(campaign_id=1)
    assert campaign.kind != target_kind
    assert campaign.subkind != target_subkind

    campaign.kind = target_kind
    campaign.subkind = target_subkind
    await db_campaign.update(campaign)

    campaign = await db_campaign.fetch(campaign_id=1)
    assert campaign.kind == target_kind
    assert campaign.subkind == target_subkind
