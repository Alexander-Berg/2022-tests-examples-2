import datetime
import json

import pytest

from taxi.util import dates

from crm_admin import settings
from crm_admin.storage import schedule


async def get_schedule_state(context, _id):
    query = f'SELECT sending_stats FROM crm_admin.schedule WHERE id = {_id}'
    async with context.pg.master_pool.acquire() as conn:
        retrieved = await conn.fetchrow(query)

    sending_stats = json.loads(retrieved[0])
    return sending_stats


@pytest.mark.parametrize('campaign_id, start_id', [(1, 5), (2, 10)])
@pytest.mark.pgsql('crm_admin', files=['init_schedule.sql'])
async def test_get_last_start(web_context, campaign_id, start_id):
    schedule_storage = schedule.DbSchedule(web_context)
    start = await schedule_storage.get_last_start(campaign_id)
    assert start['id'] == start_id


@pytest.mark.parametrize(
    'campaign_id, stats',
    [
        (1, {}),
        (1, {'planned': 1000, 'sent': 700, 'failed': 100, 'skipped': 200}),
        (2, {'planned': 2000, 'sent': 1400, 'failed': 200, 'skipped': 300}),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_schedule.sql'])
async def test_update_stats(web_context, campaign_id, stats):
    schedule_storage = schedule.DbSchedule(web_context)
    await schedule_storage.update_stats(campaign_id, stats)
    retrieved = await get_schedule_state(web_context, campaign_id)
    assert retrieved == stats


@pytest.mark.now('2021-03-26T12:00:00.0')
@pytest.mark.pgsql('crm_admin', files=['init_schedule.sql'])
async def test_list_expired_campaigns(web_context):
    schedule_storage = schedule.DbSchedule(web_context)
    expired_campaigns = await schedule_storage.list_expired_campaigns(
        final_state=settings.REGULAR_COMPLETED,
        skipped_states=[settings.SENDING_PROCESSING_STATE],
    )

    assert [c['campaign_id'] for c in expired_campaigns] == [3]


@pytest.mark.parametrize(
    'campaign_id, is_idle', [(2, True), (6, False), (7, False), (8, True)],
)
@pytest.mark.now('2021-02-01T00:00:00.0')
@pytest.mark.pgsql('crm_admin', files=['init_schedule.sql'])
async def test_list_idle_campaigns(web_context, campaign_id, is_idle):
    schedule_storage = schedule.DbSchedule(web_context)
    campaigns = await schedule_storage.list_idle_campaigns(
        settings.REGULAR_SCHEDULED,
        (dates.utcnow(), dates.utcnow() + datetime.timedelta(hours=1)),
    )

    assert (campaign_id in [c['campaign_id'] for c in campaigns]) == is_idle


@pytest.mark.now('2021-02-01T00:00:00.0')
@pytest.mark.pgsql('crm_admin', files=['init_schedule.sql'])
async def test_list_pending_campaigns(web_context):
    schedule_storage = schedule.DbSchedule(web_context)
    campaigns = await schedule_storage.list_pending_campaigns(
        settings.REGULAR_SCHEDULED,
        (dates.utcnow(), dates.utcnow() + datetime.timedelta(hours=1)),
    )
    expected = [
        {'campaign_id': 6, 'start_id': 11},
        {'campaign_id': 7, 'start_id': 12},
        {'campaign_id': 9, 'start_id': 14},
        {'campaign_id': 10, 'start_id': 16},
    ]
    actual = [
        {'campaign_id': c['campaign_id'], 'start_id': c['start_id']}
        for c in campaigns
    ]
    assert actual == expected
