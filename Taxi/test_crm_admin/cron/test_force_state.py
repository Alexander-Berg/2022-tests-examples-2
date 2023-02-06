import datetime

import pytest

from taxi.util import dates

from crm_admin import settings
from crm_admin.generated.cron import run_cron


QUERY_CAMPAIG_WITH_STATE = (
    'SELECT DISTINCT ON'
    '  (c.id) c.id as campaign_id, '
    '  l.state_to, '
    '  l.updated_at, '
    '  l.state_from, '
    '  c.state, '
    '  c.is_regular, '
    '  c.created_at '
    'FROM crm_admin.campaign AS c '
    'LEFT JOIN crm_admin.campaign_state_log AS l ON c.id = l.campaign_id '
    'ORDER BY c.id, l.id DESC '
    ';'
)


@pytest.mark.now('2020-04-15 18:30:00')
@pytest.mark.config(
    CRM_ADMIN_FORCE_STATE=[
        {
            'src_state': 'NEW',
            'dst_state': 'EXPIRED',
            'campaign_type': 'oneshot',
            'days_limit': 30,
        },
        {
            'src_state': 'READY',
            'dst_state': 'EXPIRED',
            'campaign_type': 'oneshot',
            'days_limit': 30,
        },
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_force_state_oneshot(cron_context):
    states = ['NEW', 'READY']

    async with cron_context.pg.master_pool.acquire() as conn:
        campaigns_before = list(await conn.fetch(QUERY_CAMPAIG_WITH_STATE))
        await run_cron.main(
            ['crm_admin.crontasks.force_campaign_state', '-t', '0'],
        )
        campaigns_after = list(await conn.fetch(QUERY_CAMPAIG_WITH_STATE))
        campaigns_after = {
            campaign['campaign_id']: campaign for campaign in campaigns_after
        }

        assert len(campaigns_before) == 12 and len(campaigns_after) == 12

        forced_counter = 0
        for before in campaigns_before:
            after = campaigns_after[before['campaign_id']]
            now = dates.utcnow()

            if after['state_to']:
                assert after['state_to'] == after['state']

            updated_at = (
                dates.naive_tz_to_naive_utc(
                    before['updated_at'], 'Europe/Moscow',
                )
                if before['updated_at']
                else None
            )
            before_updated_at = updated_at or before['created_at']
            before_state = before['state_to'] or before['state']

            if (
                    now - before_updated_at > datetime.timedelta(days=30)
                    and not before['is_regular']
                    and before['state'] in states
            ):
                forced_counter += 1
                assert after['state'] == settings.EXPIRED
                assert before_state == after['state_from']
            else:
                assert after['state'] == before['state']

        assert forced_counter == 5


@pytest.mark.now('2020-04-15 18:30:00')
@pytest.mark.config(
    CRM_ADMIN_FORCE_STATE=[
        {
            'src_state': 'NEW',
            'dst_state': 'EXPIRED',
            'campaign_type': 'regular',
            'days_limit': 30,
        },
        {
            'src_state': 'READY',
            'dst_state': 'EXPIRED',
            'campaign_type': 'regular',
            'days_limit': 30,
        },
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_force_state_regular(cron_context):
    states = ['NEW', 'READY']

    async with cron_context.pg.master_pool.acquire() as conn:
        campaigns_before = list(await conn.fetch(QUERY_CAMPAIG_WITH_STATE))
        await run_cron.main(
            ['crm_admin.crontasks.force_campaign_state', '-t', '0'],
        )
        campaigns_after = list(await conn.fetch(QUERY_CAMPAIG_WITH_STATE))
        campaigns_after = {
            campaign['campaign_id']: campaign for campaign in campaigns_after
        }

        assert len(campaigns_before) == 12 and len(campaigns_after) == 12

        forced_counter = 0
        for before in campaigns_before:
            after = campaigns_after[before['campaign_id']]
            now = dates.utcnow()

            if after['state_to']:
                assert after['state_to'] == after['state']

            updated_at = (
                dates.naive_tz_to_naive_utc(
                    before['updated_at'], 'Europe/Moscow',
                )
                if before['updated_at']
                else None
            )
            before_updated_at = updated_at or before['created_at']
            before_state = before['state_to'] or before['state']

            if (
                    now - before_updated_at > datetime.timedelta(days=30)
                    and before['is_regular']
                    and before['state'] in states
            ):
                forced_counter += 1
                assert after['state'] == settings.EXPIRED
                assert before_state == after['state_from']
            else:
                assert after['state'] == before['state']

        assert forced_counter == 2


@pytest.mark.now('2020-04-15 18:30:00')
@pytest.mark.config(CRM_ADMIN_FORCE_STATE=[])
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_force_state_empty(cron_context):
    campaigns_query = 'SELECT * FROM crm_admin.campaign'

    async with cron_context.pg.master_pool.acquire() as conn:
        before = list(await conn.fetch(campaigns_query))
        await run_cron.main(
            ['crm_admin.crontasks.force_campaign_state', '-t', '0'],
        )
        after = list(await conn.fetch(campaigns_query))
        assert before == after


@pytest.mark.now('2019-01-24 01:00:00')
@pytest.mark.config(
    CRM_ADMIN_FORCE_STATE=[
        {
            'src_state': 'NEW',
            'dst_state': 'EXPIRED',
            'campaign_type': 'regular',
            'days_limit': 0,
        },
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_force_state_timezone_1(cron_context):
    async with cron_context.pg.master_pool.acquire() as conn:
        campaigns_before = list(await conn.fetch(QUERY_CAMPAIG_WITH_STATE))
        await run_cron.main(
            ['crm_admin.crontasks.force_campaign_state', '-t', '0'],
        )
        campaigns_after = list(await conn.fetch(QUERY_CAMPAIG_WITH_STATE))
        assert len(set(campaigns_after) - set(campaigns_before)) == 1


@pytest.mark.now('2019-01-24 00:50:00')
@pytest.mark.config(
    CRM_ADMIN_FORCE_STATE=[
        {
            'src_state': 'NEW',
            'dst_state': 'EXPIRED',
            'campaign_type': 'regular',
            'days_limit': 0,
        },
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_force_state_timezone_2(cron_context):
    async with cron_context.pg.master_pool.acquire() as conn:
        campaigns_before = list(await conn.fetch(QUERY_CAMPAIG_WITH_STATE))
        await run_cron.main(
            ['crm_admin.crontasks.force_campaign_state', '-t', '0'],
        )
        campaigns_after = list(await conn.fetch(QUERY_CAMPAIG_WITH_STATE))
        assert campaigns_after == campaigns_before


@pytest.mark.now('2019-03-21 01:00:00')
@pytest.mark.config(
    CRM_ADMIN_FORCE_STATE=[
        {
            'src_state': 'NEW',
            'dst_state': 'EXPIRED',
            'campaign_type': 'oneshot',
            'days_limit': 0,
        },
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_force_state_timezone_3(cron_context):
    async with cron_context.pg.master_pool.acquire() as conn:
        campaigns_before = list(await conn.fetch(QUERY_CAMPAIG_WITH_STATE))
        await run_cron.main(
            ['crm_admin.crontasks.force_campaign_state', '-t', '0'],
        )
        campaigns_after = list(await conn.fetch(QUERY_CAMPAIG_WITH_STATE))
        assert len(set(campaigns_after) - set(campaigns_before)) == 1


@pytest.mark.now('2019-03-21 00:50:00')
@pytest.mark.config(
    CRM_ADMIN_FORCE_STATE=[
        {
            'src_state': 'NEW',
            'dst_state': 'EXPIRED',
            'campaign_type': 'oneshot',
            'days_limit': 0,
        },
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_force_state_timezone_4(cron_context):
    async with cron_context.pg.master_pool.acquire() as conn:
        campaigns_before = list(await conn.fetch(QUERY_CAMPAIG_WITH_STATE))
        await run_cron.main(
            ['crm_admin.crontasks.force_campaign_state', '-t', '0'],
        )
        campaigns_after = list(await conn.fetch(QUERY_CAMPAIG_WITH_STATE))
        assert not set(campaigns_after) - set(campaigns_before)
