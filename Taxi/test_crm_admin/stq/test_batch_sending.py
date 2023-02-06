# pylint: disable=unused-variable,unused-argument,invalid-name
import datetime

from aiohttp import web
import asynctest
import pytest

from taxi.util import dates

from crm_admin import settings
from crm_admin import storage
from crm_admin.storage import campaign_adapters
from crm_admin.storage import group_adapters
from crm_admin.storage import sending_adapters
from crm_admin.stq import batch_sending


CRM_ADMIN_SETTINGS = {
    'StartrekSettings': {
        'campaign_queue': 'CRMTEST',
        'creative_queue': 'CRMTEST',
        'idea_approved_statuses': ['В работе', 'Одобрено'],
        'target_statuses': ['Одобрено', 'Closed'],
        'unapproved_statuses': ['В работе', 'Открыт'],
    },
}


class TaskInfo:
    id = 'task_id'
    exec_tries = 0


async def check_sending_state(sending_storage, sending_id, expected_value):
    sending_info = await sending_storage.fetch(sending_id)

    assert sending_info.state == expected_value


async def check_group_state(context, group_id, expected_value):
    db_group = group_adapters.DbGroup(context)
    group = await db_group.fetch(group_id=group_id)
    assert group.params.state == expected_value


@pytest.mark.parametrize(
    'sending_id, sending_info_type, sending_type, expected_group_state',
    [
        (
            1,
            storage.SendingType.PRODUCTION,
            'EFFICIENCY',
            settings.GROUP_STATE_PLANNED,
        ),
        (
            2,
            storage.SendingType.VERIFY,
            'DIRECTLY',
            settings.GROUP_STATE_TESTING,
        ),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_start_sending_oneshot(
        stq3_context,
        mock_crm_hub,
        sending_id,
        sending_info_type,
        sending_type,
        expected_group_state,
):
    @mock_crm_hub('/v1/communication/bulk/new')
    async def bulk_new(request):
        return web.json_response({}, status=200)

    @mock_crm_hub('/v1/communication/bulk/verify')
    async def bulk_verify(request):
        return web.json_response({}, status=200)

    reschedule = asynctest.CoroutineMock()
    stq3_context.stq.crm_admin_batch_sending.reschedule = reschedule

    task_info = TaskInfo()

    await batch_sending.task(stq3_context, task_info, sending_id, sending_type)
    await check_group_state(stq3_context, sending_id, expected_group_state)

    if sending_info_type == storage.SendingType.PRODUCTION:
        assert bulk_new.has_calls
        assert not bulk_verify.has_calls
    else:
        assert not bulk_new.has_calls
        assert bulk_verify.has_calls

    assert reschedule.calls

    sending_storage = sending_adapters.SendingStorage(stq3_context)

    await check_sending_state(
        sending_storage, sending_id, storage.SendingState.PROCESSING,
    )


@pytest.mark.parametrize('sending_id, is_active', [(4, True), (5, False)])
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_start_sending_regular(
        stq3_context, mock_crm_hub, sending_id, is_active,
):
    @mock_crm_hub('/v1/communication/bulk/new')
    async def bulk_new(request):
        return web.json_response({}, status=200)

    reschedule = asynctest.CoroutineMock()
    stq3_context.stq.crm_admin_batch_sending.reschedule = reschedule

    task_info = TaskInfo()

    await batch_sending.task(stq3_context, task_info, sending_id, 'MAIN')

    if is_active:
        assert bulk_new.has_calls
        assert reschedule.called
    else:
        assert not bulk_new.has_calls
        assert not reschedule.called

    sending_storage = sending_adapters.SendingStorage(stq3_context)

    if is_active:
        await check_sending_state(
            sending_storage, sending_id, storage.SendingState.PROCESSING,
        )


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_cancel_inactive_campaign(stq3_context, mock_crm_hub, patch):
    sending_id = campaign_id = group_id = 6
    task_info = TaskInfo()

    @patch('crm_admin.stq.batch_sending.send_utils.cancel')
    async def cancel(context, campaign_id):
        pass

    @patch('crm_admin.utils.startrek.trigger.on_regular')
    async def on_regular(*args, **kwargs):
        pass

    @mock_crm_hub('/v1/communication/bulk/status')
    async def bulk_status(request):
        return web.json_response(
            {'data': storage.SendingState.CANCELED}, status=200,
        )

    await batch_sending.task(stq3_context, task_info, sending_id, 'DIRECTLY')

    assert cancel.calls

    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)

    assert campaign.state == settings.REGULAR_STOPPED

    db_group = storage.DbGroup(stq3_context)
    group = await db_group.fetch(group_id)

    assert group.params.state == settings.GROUP_STATE_SENT


@pytest.mark.parametrize(
    'sending_id, bulk_status_data, expected_group_state',
    [
        (7, 'PROCESSING', settings.GROUP_STATE_SENDING),
        (7, 'FINISHED', settings.GROUP_STATE_SENT),
        (16, 'PROCESSING', settings.GROUP_STATE_TESTING),
        (16, 'FINISHED', settings.GROUP_STATE_NEW),
    ],
)
@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_start_sending_in_process(
        stq3_context,
        mock_crm_hub,
        sending_id,
        bulk_status_data,
        expected_group_state,
):
    @mock_crm_hub('/v1/communication/bulk/status')
    async def bulk_status(request):
        return web.json_response({'data': bulk_status_data}, status=200)

    reschedule = asynctest.CoroutineMock()
    stq3_context.stq.crm_admin_batch_sending.reschedule = reschedule

    task_info = TaskInfo()

    await batch_sending.task(stq3_context, task_info, sending_id, 'MAIN')

    assert bulk_status.has_calls
    await check_group_state(stq3_context, sending_id, expected_group_state)

    if bulk_status_data == 'PROCESSING':
        assert reschedule.called
    if bulk_status_data == 'FINISHED':
        sending_storage = sending_adapters.SendingStorage(stq3_context)
        await check_sending_state(
            sending_storage, sending_id, storage.SendingState.FINISHED,
        )


@pytest.mark.parametrize(
    'sending_id, sending_status',
    [(8, 'FINISHED'), (9, 'FINISHED'), (8, 'ERROR'), (9, 'ERROR')],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_processing_efficiency_analysis(
        stq3_context, mock_crm_hub, sending_id, sending_status,
):
    sending_stats = {'planned': 100, 'sent': 30, 'failed': 20, 'skipped': 40}

    @mock_crm_hub('/v1/communication/bulk/results')
    async def bulk_results(request):
        return web.json_response(sending_stats, status=200)

    @mock_crm_hub('/v1/communication/bulk/status')
    async def _bulk_status(request):
        return web.json_response({'data': sending_status}, status=200)

    reschedule = asynctest.CoroutineMock()
    stq3_context.stq.crm_admin_batch_sending.reschedule = reschedule

    task_info = TaskInfo()

    await batch_sending.task(stq3_context, task_info, sending_id, 'MAIN')

    assert bulk_results.has_calls
    assert reschedule.called

    db_group = group_adapters.DbGroup(stq3_context)
    group = await db_group.fetch(group_id=sending_id)

    assert group.sending_stats.serialize() == sending_stats

    if sending_id == 8:
        assert group.params.state == settings.GROUP_STATE_SENT


@pytest.mark.now('2021-01-27 00:00:00')
@pytest.mark.parametrize('sending_id', [13])
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_start_efficiency_analysis_with_reschedule(
        stq3_context, mock_crm_hub, sending_id,
):
    reschedule = asynctest.CoroutineMock()
    stq3_context.stq.crm_admin_batch_sending.reschedule = reschedule

    task_info = TaskInfo()
    await batch_sending.task(stq3_context, task_info, sending_id, 'MAIN')

    async with stq3_context.pg.master_pool.acquire() as conn:
        db_group = group_adapters.DbGroup(stq3_context, conn)
        group = await db_group.fetch(group_id=sending_id)

        sending_storage = sending_adapters.SendingStorage(stq3_context, conn)
        sending = await sending_storage.fetch(sending_id)

        db_campaign = campaign_adapters.DbCampaign(stq3_context, conn)
        campaign = await db_campaign.fetch(sending.campaign_id)

    reschedule.assert_awaited_once_with(
        eta=sending.send_at + datetime.timedelta(seconds=1),
        task_id=task_info.id,
    )
    assert group.params.state == settings.GROUP_STATE_EFFICIENCY_PLANNED
    assert sending.state == sending_adapters.SendingState.NEW
    assert campaign.state == settings.SENDING_PLANNED


@pytest.mark.now('2021-01-28 00:10:00')
@pytest.mark.parametrize('sending_id', [14])
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_start_efficiency_analysis_without_reschedule(
        stq3_context, mock_crm_hub, sending_id,
):
    """
    Function tests that we do not reschedule on send_at in
    try_start_efficiency_analysis function
    """

    reschedule = asynctest.CoroutineMock()
    stq3_context.stq.crm_admin_batch_sending.reschedule = reschedule

    task_info = TaskInfo()
    await batch_sending.task(stq3_context, task_info, sending_id, 'MAIN')

    async with stq3_context.pg.master_pool.acquire() as conn:
        db_group = group_adapters.DbGroup(stq3_context, conn)
        group = await db_group.fetch(group_id=sending_id)

        sending_storage = sending_adapters.SendingStorage(stq3_context, conn)
        sending = await sending_storage.fetch(sending_id)

        db_campaign = campaign_adapters.DbCampaign(stq3_context, conn)
        campaign = await db_campaign.fetch(sending.campaign_id)

    reschedule.assert_awaited_once_with(
        eta=dates.utcnow() + datetime.timedelta(seconds=10),
        task_id=task_info.id,
    )
    assert group.params.state == settings.GROUP_STATE_EFFICIENCY
    assert sending.state == sending_adapters.SendingState.PROCESSING
    assert campaign.state == settings.EFFICIENCY


@pytest.mark.now('2021-01-01')
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_start_same_sending_stats(stq3_context, mock_crm_hub):
    sending_stats = {}
    sending_id = 10

    @mock_crm_hub('/v1/communication/bulk/results')
    async def bulk_results(request):
        return web.json_response(sending_stats, status=200)

    reschedule = asynctest.CoroutineMock()
    stq3_context.stq.crm_admin_batch_sending.reschedule = reschedule

    task_info = TaskInfo()

    await batch_sending.task(stq3_context, task_info, sending_id, 'MAIN')

    assert bulk_results.has_calls
    assert reschedule.called
    db_group = group_adapters.DbGroup(stq3_context)
    group = await db_group.fetch(group_id=sending_id)

    assert group.sending_stats.serialize() == sending_stats
    assert group.updated_at == datetime.datetime(2021, 3, 27, 2, 0, 0)


@pytest.mark.now('2021-01-01')
@pytest.mark.parametrize(
    'sending_id, sending_stats',
    [
        (11, {'planned': 100, 'sent': 30, 'failed': 20, 'skipped': 40}),
        (12, {}),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_start_sending_finished(
        stq3_context, mock_crm_hub, sending_id, sending_stats,
):
    @mock_crm_hub('/v1/communication/bulk/results')
    async def bulk_results(request):
        return web.json_response(sending_stats, status=200)

    reschedule = asynctest.CoroutineMock()
    stq3_context.stq.crm_admin_batch_sending.reschedule = reschedule

    task_info = TaskInfo()

    await batch_sending.task(stq3_context, task_info, sending_id, 'MAIN')

    assert bulk_results.has_calls
    assert not reschedule.called

    db_group = group_adapters.DbGroup(stq3_context)
    group = await db_group.fetch(group_id=sending_id)

    assert group.sending_stats.serialize() == sending_stats

    if sending_id == 12:
        assert group.updated_at == datetime.datetime(2021, 3, 27, 2, 0, 0)
