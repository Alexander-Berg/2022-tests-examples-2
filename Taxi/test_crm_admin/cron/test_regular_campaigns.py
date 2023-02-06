# pylint: disable=unused-argument,unused-variable

import contextlib
import datetime

import asynctest
import pytest

from taxi.util import dates

from crm_admin import entity
from crm_admin import settings
from crm_admin import storage
from crm_admin.crontasks import regular_campaigns
from crm_admin.generated.cron import run_cron
from crm_admin.utils import regular
from crm_admin.utils.state import group_state_processing
from crm_admin.utils.state import segment_state_processing


@pytest.mark.now('2021-01-27T11:59:00.0')
@pytest.mark.pgsql('crm_admin', files=['init-manager.sql'])
async def test_manager(cron_context):
    idle_state = regular_campaigns.IDLE_STATE
    await regular.manager.schedule_campaigns(cron_context, idle_state)

    db_schedule = storage.DbSchedule(cron_context)
    pending = await db_schedule.list_pending_campaigns(
        idle_state,
        (dates.utcnow(), dates.utcnow() + datetime.timedelta(hours=1)),
    )

    expected = [
        {
            'campaign_id': 1,
            'scheduled_for': datetime.datetime(2021, 1, 27, 12, 1),
        },
        {
            'campaign_id': 3,
            'scheduled_for': datetime.datetime(2021, 1, 26, 12, 0),
        },
    ]
    actual = sorted(
        [
            {
                'campaign_id': c['campaign_id'],
                'scheduled_for': c['scheduled_for'],
            }
            for c in pending
        ],
        key=lambda item: item['campaign_id'],
    )
    assert actual == expected


@pytest.mark.now('2021-01-27T11:59:00.0')
@pytest.mark.pgsql('crm_admin', files=['init-draft-applying.sql'])
@pytest.mark.config(CRM_ADMIN_GROUPS_V2={'all_on': True})
async def test_draft_applying(cron_context, patch):
    @patch('crm_admin.utils.startrek.trigger.summon_by_section')
    async def summon_by_section(*args, **kwargs):
        pass

    idle_state = regular_campaigns.IDLE_STATE
    await regular.manager.apply_drafts(cron_context)
    await regular.manager.schedule_campaigns(cron_context, idle_state)

    db_schedule = storage.DbSchedule(cron_context)
    pending = await db_schedule.list_pending_campaigns(
        idle_state,
        (dates.utcnow(), dates.utcnow() + datetime.timedelta(hours=1)),
    )

    db_campaign = storage.DbCampaign(cron_context)
    db_group = storage.DbGroup(cron_context)
    db_creative = storage.DbCreative(cron_context)

    expected = [
        {
            'campaign_id': 3,
            'scheduled_for': datetime.datetime(2021, 1, 26, 12, 0),
        },
        {
            'campaign_id': 9,
            'scheduled_for': datetime.datetime(2021, 1, 27, 12, 1),
        },
        {
            'campaign_id': 10,
            'scheduled_for': datetime.datetime(2021, 1, 27, 12, 1),
        },
    ]
    actual = sorted(
        [
            {
                'campaign_id': c['campaign_id'],
                'scheduled_for': c['scheduled_for'],
            }
            for c in pending
        ],
        key=lambda item: item['campaign_id'],
    )
    assert actual == expected

    archived_campaign = await db_campaign.fetch(1)
    new_actual_campaign = await db_campaign.fetch(9)

    assert archived_campaign.version_state == settings.VersionState.ARCHIVE
    assert not archived_campaign.is_active
    assert archived_campaign.state == settings.REGULAR_STOPPED

    assert new_actual_campaign.version_state == settings.VersionState.ACTUAL
    assert new_actual_campaign.is_active
    assert new_actual_campaign.state == idle_state

    archived_group = (await db_group.fetch_by_campaign_id(1))[0]
    new_actual_group = (await db_group.fetch_by_campaign_id(9))[0]

    assert archived_group.params.version_info
    assert (
        archived_group.params.version_info.version_state
        == settings.VersionState.ARCHIVE
    )

    assert new_actual_group.params.version_info
    assert (
        new_actual_group.params.version_info.version_state
        == settings.VersionState.ACTUAL
    )

    archived_creative = (await db_creative.fetch_by_campaign_id(1))[0]
    new_actual_creative = (await db_creative.fetch_by_campaign_id(9))[0]

    assert archived_creative.version_state == settings.VersionState.ARCHIVE

    assert new_actual_creative.version_state == settings.VersionState.ACTUAL


@pytest.mark.now('2021-01-27T11:59:00.0')
@pytest.mark.pgsql('crm_admin', files=['init-segment.sql'])
async def test_start_segmenting(cron_context, patch):
    @patch(
        'crm_admin.utils.regular.segment.stq_tasks.start_segment_processing',
    )
    async def start_segment_processing(context, campaign_id, eta):
        pass

    idle_state = regular_campaigns.IDLE_STATE
    await regular.segment.start_all(cron_context, idle_state)

    expected = [
        {'campaign_id': 1, 'eta': datetime.datetime(2021, 1, 26, 13, 0)},
        {'campaign_id': 2, 'eta': datetime.datetime(2021, 1, 26, 12, 20)},
    ]
    actual = sorted(
        [
            {'campaign_id': c['campaign_id'], 'eta': c['eta']}
            for c in start_segment_processing.calls
        ],
        key=lambda item: item['campaign_id'],
    )
    assert actual == expected

    # check that a campaign will not be started again
    #
    await regular.segment.start_all(cron_context, idle_state)
    assert not start_segment_processing.calls


@pytest.mark.now('2021-01-27T11:59:00.0')
@pytest.mark.pgsql('crm_admin', files=['init-segment.sql'])
@pytest.mark.config(
    CRM_ADMIN_CALCULATIONS_STQ_ENABLED={
        'segment_enabled': True,
        'group_enabled': True,
    },
)
async def test_start_calculations_segmenting(cron_context, patch):
    @patch(
        'crm_admin.utils.regular.segment.'
        'stq_tasks.start_calculations_processing',
    )
    async def start_calculations_processing(
            context, campaign_id, mode, stage, eta,
    ):
        pass

    idle_state = regular_campaigns.IDLE_STATE
    await regular.segment.start_all(cron_context, idle_state)

    expected = [
        {'campaign_id': 1, 'eta': datetime.datetime(2021, 1, 26, 13, 0)},
        {'campaign_id': 2, 'eta': datetime.datetime(2021, 1, 26, 12, 20)},
    ]
    actual = sorted(
        [
            {'campaign_id': c['campaign_id'], 'eta': c['eta']}
            for c in start_calculations_processing.calls
        ],
        key=lambda item: item['campaign_id'],
    )
    assert actual == expected

    # check that a campaign will not be started again
    #
    await regular.segment.start_all(cron_context, idle_state)
    assert not start_calculations_processing.calls


@pytest.mark.now('2021-01-27T11:59:00.0')
@pytest.mark.pgsql('crm_admin', files=['init-groups.sql'])
async def test_start_grouping(cron_context, patch):
    @patch('crm_admin.utils.regular.segment.stq_tasks.start_groups_processing')
    async def start_groups_processing(context, campaign_id):
        pass

    await regular.groups.start_all(cron_context, settings.SEGMENT_RESULT_STATE)

    expected = [{'campaign_id': 1}]
    actual = sorted(
        [
            {'campaign_id': c['campaign_id']}
            for c in start_groups_processing.calls
        ],
        key=lambda item: item['campaign_id'],
    )
    assert actual == expected


@pytest.mark.now('2021-01-27T11:59:00.0')
@pytest.mark.pgsql('crm_admin', files=['init-groups.sql'])
@pytest.mark.config(
    CRM_ADMIN_CALCULATIONS_STQ_ENABLED={
        'segment_enabled': True,
        'group_enabled': True,
    },
)
async def test_start_calculations_grouping(cron_context, patch):
    @patch(
        'crm_admin.utils.regular.segment.'
        'stq_tasks.start_calculations_processing',
    )
    async def start_calculations_processing(context, campaign_id, mode, stage):
        pass

    await regular.groups.start_all(cron_context, settings.SEGMENT_RESULT_STATE)

    expected = [{'campaign_id': 1}]
    actual = sorted(
        [
            {'campaign_id': c['campaign_id']}
            for c in start_calculations_processing.calls
        ],
        key=lambda item: item['campaign_id'],
    )
    assert actual == expected


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


@pytest.mark.now('2021-02-01T12:00:00.0')
@pytest.mark.pgsql('crm_admin', files=['init-failed-campaigns.sql'])
async def test_restore_from_fail_states(cron_context):
    idle_state = regular_campaigns.IDLE_STATE
    await regular.manager.restore_from_fail_states(cron_context, idle_state)

    db_schedule = storage.DbSchedule(cron_context)
    now = dates.utcnow()
    campaigns = await db_schedule.list_idle_campaigns(
        idle_state, (now, now + regular.manager.WINDOW_SIZE),
    )

    expected = [1, 2, 6]
    actual = sorted(c['campaign_id'] for c in campaigns)

    assert actual == expected


@pytest.mark.now('2021-03-26T12:00:00.0')
@pytest.mark.pgsql('crm_admin', files=['init-expired-campaigns.sql'])
async def test_finish_expired_campaigns(cron_context, patch):
    @patch('crm_admin.utils.startrek.trigger.on_regular')
    async def summon_on_regular(*args, **kwargs):
        pass

    await regular.manager.finish_expired_campaigns(cron_context)

    db_schedule = storage.DbSchedule(cron_context)
    expired_campaigns = await db_schedule.list_expired_campaigns(
        final_state=settings.REGULAR_COMPLETED, skipped_states=[],
    )

    # this should not be completed since it is in SENDING_PROCESSING state
    assert expired_campaigns == [
        {'campaign_id': 4, 'state': 'SENDING_PROCESSING'},
    ]

    db_campaign = storage.DbCampaign(cron_context)
    assert (await db_campaign.fetch(1)).state == 'SCHEDULED'
    assert (await db_campaign.fetch(2)).state == 'COMPLETED'
    assert (await db_campaign.fetch(3)).state == 'COMPLETED'


@pytest.mark.now('2021-01-27T11:59:00.0')
@pytest.mark.pgsql('crm_admin', files=['init-workflow.sql'])
async def test_workflow(cron_context, patch):
    async def update_campaign_state(context, campaign_id, campaign_state):
        db_campaign = storage.DbCampaign(context)
        campaign = await db_campaign.fetch(campaign_id)
        campaign.state = campaign_state
        await db_campaign.update_state(campaign)

    @patch('crm_admin.storage.db_storage.DbStorage._conn')
    @contextlib.asynccontextmanager
    async def _conn():
        async with cron_context.pg.master_pool.acquire() as connection:
            yield connection

    @patch(
        'crm_admin.utils.regular.segment.stq_tasks.start_segment_processing',
    )
    async def start_segment_processing(context, campaign_id, eta):
        campaign = await storage.DbCampaign(context).fetch(campaign_id)
        await segment_state_processing.start_segment_processing(
            context, campaign,
        )
        await update_campaign_state(
            context, campaign_id, settings.SEGMENT_RESULT_STATE,
        )

    @patch('crm_admin.utils.regular.segment.stq_tasks.start_groups_processing')
    async def start_groups_processing(context, campaign_id):
        campaign = await storage.DbCampaign(context).fetch(campaign_id)
        await group_state_processing.start_groups_processing(context, campaign)
        await update_campaign_state(
            context, campaign_id, settings.GROUPS_RESULT_STATE,
        )

    @patch('crm_admin.utils.regular.send._send_campaign')
    async def send_campaign(context, campaign_id, start_id):
        await update_campaign_state(
            context, campaign_id, settings.SENDING_PROCESSING_STATE,
        )

    @patch('crm_admin.utils.startrek.trigger.on_regular')
    async def summon_on_regular(*args, **kwargs):
        pass

    await run_cron.main(['crm_admin.crontasks.regular_campaigns', '-t', '0'])

    assert [c['campaign_id'] for c in start_segment_processing.calls] == [1]
    assert [c['campaign_id'] for c in start_groups_processing.calls] == [1]
    assert [c['campaign_id'] for c in send_campaign.calls] == [1]

    # this campaign should have been restored from SEGMENT_ERROR state
    #
    now = dates.utcnow()

    idle_state = regular_campaigns.IDLE_STATE
    db_schedule = storage.DbSchedule(cron_context)
    idle_campaigns = await db_schedule.list_idle_campaigns(
        idle_state, (now, now + regular.manager.WINDOW_SIZE),
    )
    assert [c['campaign_id'] for c in idle_campaigns] == [2]

    db_campaign = storage.DbCampaign(cron_context)
    campaign = await db_campaign.fetch(campaign_id=3)
    assert campaign.state == settings.REGULAR_COMPLETED
    assert not campaign.is_active


@pytest.mark.now('2021-01-27T11:59:00.0')
@pytest.mark.pgsql('crm_admin', files=['init-workflow.sql'])
@pytest.mark.config(
    CRM_ADMIN_CALCULATIONS_STQ_ENABLED={
        'segment_enabled': True,
        'group_enabled': True,
    },
)
async def test_calculations_workflow(cron_context, patch):
    async def update_campaign_state(context, campaign_id, campaign_state):
        db_campaign = storage.DbCampaign(context)
        campaign = await db_campaign.fetch(campaign_id)
        campaign.state = campaign_state
        await db_campaign.update_state(campaign)

    @patch('crm_admin.storage.db_storage.DbStorage._conn')
    @contextlib.asynccontextmanager
    async def _conn():
        async with cron_context.pg.master_pool.acquire() as connection:
            yield connection

    @patch(
        'crm_admin.utils.regular.segment.'
        'stq_tasks.start_calculations_processing',
    )
    async def start_calculations_processing(
            context, campaign_id, mode, stage, eta=None,
    ):
        if mode is entity.Mode.SEGMENT:
            await update_campaign_state(
                context, campaign_id, settings.SEGMENT_RESULT_STATE,
            )
        if mode is entity.Mode.GROUP:
            await update_campaign_state(
                context, campaign_id, settings.GROUPS_RESULT_STATE,
            )

    @patch('crm_admin.utils.regular.send._send_campaign')
    async def send_campaign(context, campaign_id, start_id):
        await update_campaign_state(
            context, campaign_id, settings.SENDING_PROCESSING_STATE,
        )

    @patch('crm_admin.utils.startrek.trigger.on_regular')
    async def summon_on_regular(*args, **kwargs):
        pass

    await run_cron.main(['crm_admin.crontasks.regular_campaigns', '-t', '0'])

    assert [
        (c['campaign_id'], c['mode'])
        for c in start_calculations_processing.calls
    ] == [(1, entity.Mode.SEGMENT), (1, entity.Mode.GROUP)]
    assert [c['campaign_id'] for c in send_campaign.calls] == [1]

    # this campaign should have been restored from SEGMENT_ERROR state
    #
    now = dates.utcnow()

    idle_state = regular_campaigns.IDLE_STATE
    db_schedule = storage.DbSchedule(cron_context)
    idle_campaigns = await db_schedule.list_idle_campaigns(
        idle_state, (now, now + regular.manager.WINDOW_SIZE),
    )
    assert [c['campaign_id'] for c in idle_campaigns] == [2]

    db_campaign = storage.DbCampaign(cron_context)
    campaign = await db_campaign.fetch(campaign_id=3)
    assert campaign.state == settings.REGULAR_COMPLETED
    assert not campaign.is_active
