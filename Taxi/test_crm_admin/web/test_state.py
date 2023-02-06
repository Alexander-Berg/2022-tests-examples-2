import copy
import datetime

from aiohttp import web
import pytest

from taxi.util import dates

from crm_admin import entity
from crm_admin import settings
from crm_admin import storage
from crm_admin.generated.service.swagger import models
from crm_admin.utils.state import group_state_processing
from crm_admin.utils.state import segment_state_processing
from crm_admin.utils.state import state
from crm_admin.utils.state import state_processing


@pytest.mark.parametrize(
    'campaign_id, group_id, sending_state, group_state',
    [
        (1, 1, storage.SendingState.NEW, 'NEW'),
        (1, 1, storage.SendingState.PROCESSING, 'NEW'),
        (1, 1, storage.SendingState.FINISHED, 'NEW'),
        (1, 2, storage.SendingState.NEW, 'EFFICIENCY_SCHEDULED'),
        (1, 2, storage.SendingState.PROCESSING, 'EFFICIENCY_SENDING'),
        (1, 3, storage.SendingState.NEW, 'EFFICIENCY_SENDING'),
        (1, 3, storage.SendingState.PROCESSING, 'EFFICIENCY_SENDING'),
        (1, 4, storage.SendingState.NEW, 'EFFICIENCY_SKIPPED_SENDING'),
        (1, 4, storage.SendingState.PROCESSING, 'SENDING'),
        (1, 4, storage.SendingState.FINISHED, 'SENT'),
        (1, 5, storage.SendingState.NEW, 'EFFICIENCY_DENIED'),
        (1, 5, storage.SendingState.PROCESSING, 'EFFICIENCY_DENIED'),
        (1, 5, storage.SendingState.FINISHED, 'EFFICIENCY_DENIED'),
        (1, 6, storage.SendingState.NEW, 'EFFICIENCY_ANALYSIS'),
        (1, 6, storage.SendingState.PROCESSING, 'EFFICIENCY_ANALYSIS'),
        (1, 6, storage.SendingState.FINISHED, 'EFFICIENCY_ANALYSIS'),
        (1, 7, storage.SendingState.NEW, 'SCHEDULED'),
        (1, 7, storage.SendingState.PROCESSING, 'SENDING'),
        (1, 7, storage.SendingState.FINISHED, 'SENT'),
        (1, 8, storage.SendingState.NEW, 'SENDING'),
        (1, 8, storage.SendingState.PROCESSING, 'SENDING'),
        (1, 8, storage.SendingState.FINISHED, 'SENT'),
        (1, 9, storage.SendingState.NEW, 'SENT'),
        (1, 9, storage.SendingState.PROCESSING, 'SENT'),
        (1, 9, storage.SendingState.FINISHED, 'SENT'),
        (1, 10, storage.SendingState.NEW, 'HOLD'),
        (1, 10, storage.SendingState.PROCESSING, 'HOLD'),
        (1, 10, storage.SendingState.FINISHED, 'HOLD'),
        (1, 11, storage.SendingState.NEW, 'ERROR'),
        (1, 11, storage.SendingState.PROCESSING, 'ERROR'),
        (1, 11, storage.SendingState.FINISHED, 'ERROR'),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_group_state_changing(
        web_context,
        mock_crm_hub,
        campaign_id,
        group_id,
        sending_state,
        group_state,
):
    @mock_crm_hub('/v1/communication/bulk/results')
    async def _(request):
        return web.json_response({}, status=200)

    group_storage = storage.DbGroup(web_context)

    state_processing_ = state_processing.SendingGroupStateProcessing(
        context=web_context,
        campaign_id=campaign_id,
        group_id=group_id,
        sending_state=sending_state,
        start_id=0,
    )

    await state_processing_.change_group_state()

    group = await group_storage.fetch(group_id)
    assert group.params.state == group_state


@pytest.mark.parametrize(
    'campaign_id, group_id, sending_state, campaign_state',
    [
        (2, 20, storage.SendingState.NEW, 'SCHEDULED'),
        (2, 21, storage.SendingState.PROCESSING, 'SENDING_PROCESSING'),
        (3, 30, storage.SendingState.ERROR, 'SENDING_ERROR'),
        (3, 30, storage.SendingState.PROCESSING, 'SENDING_PROCESSING'),
        (3, 30, storage.SendingState.FINISHED, 'SENDING_FINISHED'),
        (4, 41, storage.SendingState.FINISHED, 'CAMPAIGN_APPROVED'),
        (5, 50, storage.SendingState.FINISHED, 'SENDING_FINISHED'),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_campaign_state_changing(
        web_context,
        mock_crm_hub,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
        campaign_id,
        group_id,
        sending_state,
        campaign_state,
):
    @mock_crm_hub('/v1/communication/bulk/results')
    async def _(request):
        return web.json_response({}, status=200)

    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/ticket/comments',
        'POST',
    )
    def _patch_issue(*args, **kwargs):
        text = kwargs['json']['text']
        assert text == 'Кампания перешла в статус \'SENDING_ERROR\''
        return response_mock(json={})

    sending_info = models.api.SendingFull(
        id=1,
        campaign_id=campaign_id,
        group_id=group_id,
        type=storage.SendingType.PRODUCTION,
        state=sending_state,
        created_at=dates.utcnow(),
    )
    state_processing_ = state_processing.StateProcessingViaHub(
        web_context, sending_info,
    )
    await state_processing_.try_to_finish_sending()

    campaign_storage = storage.DbCampaign(web_context)

    campaign = await campaign_storage.fetch(campaign_id)
    assert campaign.state == campaign_state


# =============================================================================


@pytest.mark.parametrize(
    'in_state, out_state, is_regular, mode',
    [
        (
            settings.SEGMENT_EXPECTED_STATE,
            settings.SEGMENT_PREPROCESSING_STATE,
            False,
            None,
        ),
        (
            settings.SEGMENT_ERROR,
            settings.SEGMENT_PREPROCESSING_STATE,
            False,
            None,
        ),
        (
            settings.REGULAR_SCHEDULED,
            settings.SEGMENT_PREPROCESSING_STATE,
            True,
            None,
        ),
        (
            settings.SEGMENT_PROCESSING_STATE,
            settings.SEGMENT_PREPROCESSING_STATE,
            False,
            None,
        ),
        (
            settings.SEGMENT_PROCESSING_STATE,
            settings.SEGMENT_PREPROCESSING_STATE,
            True,
            None,
        ),
        (settings.SEGMENT_PREPROCESSING_STATE, None, True, None),
        (settings.SEGMENT_PREPROCESSING_STATE, None, False, None),
        (settings.REGULAR_STOPPED, None, False, None),
        (settings.REGULAR_STOPPED, settings.REGULAR_STOPPED, True, None),
        (
            settings.RECALCULATION_SEGMENT_PROCESSING_STATE,
            settings.RECALCULATION_SEGMENT_PREPROCESSING_STATE,
            False,
            entity.Mode.JOINT,
        ),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_start_segment_preprocessing(
        web_context, in_state, out_state, is_regular, mode,
):
    campaign_id = 1
    db_campaign = storage.DbCampaign(web_context)
    campaign = await db_campaign.fetch(campaign_id)
    campaign.state = in_state
    campaign.is_regular = is_regular
    campaign.is_active = is_regular
    await db_campaign.update(campaign)
    await db_campaign.update_state(campaign)

    try:
        await segment_state_processing.segment_preprocessing(
            context=web_context, campaign=campaign, mode=mode,
        )
        campaign = await db_campaign.fetch(campaign_id)
        assert campaign.state == out_state
    except entity.InvalidCampaign:
        assert out_state is None


# =============================================================================


@pytest.mark.parametrize(
    'in_state, out_state, is_regular, mode',
    [
        (settings.SEGMENT_EXPECTED_STATE, None, False, None),
        (settings.SEGMENT_ERROR, None, False, None),
        (settings.REGULAR_SCHEDULED, None, True, None),
        (settings.SEGMENT_PROCESSING_STATE, None, False, None),
        (settings.SEGMENT_PROCESSING_STATE, None, True, None),
        (
            settings.SEGMENT_PREPROCESSING_STATE,
            settings.SEGMENT_PROCESSING_STATE,
            True,
            None,
        ),
        (
            settings.SEGMENT_PREPROCESSING_STATE,
            settings.SEGMENT_PROCESSING_STATE,
            False,
            None,
        ),
        (settings.REGULAR_STOPPED, None, False, None),
        (settings.REGULAR_STOPPED, settings.REGULAR_STOPPED, True, None),
        (
            settings.RECALCULATION_SEGMENT_PREPROCESSING_STATE,
            settings.RECALCULATION_SEGMENT_PROCESSING_STATE,
            False,
            entity.Mode.JOINT,
        ),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_start_segment_processing(
        web_context, in_state, out_state, is_regular, mode,
):
    campaign_id = 1
    db_campaign = storage.DbCampaign(web_context)
    campaign = await db_campaign.fetch(campaign_id)
    campaign.state = in_state
    campaign.is_regular = is_regular
    campaign.is_active = is_regular
    await db_campaign.update(campaign)
    await db_campaign.update_state(campaign)

    try:
        await segment_state_processing.start_segment_processing(
            context=web_context, campaign=campaign, mode=mode, dry_run=True,
        )

        campaign = await db_campaign.fetch(campaign_id)
        assert campaign.state == in_state
    except entity.InvalidCampaign:
        assert out_state is None

    try:
        await segment_state_processing.start_segment_processing(
            context=web_context, campaign=campaign, mode=mode,
        )
        campaign = await db_campaign.fetch(campaign_id)
        assert campaign.state == out_state
    except entity.InvalidCampaign:
        assert out_state is None


# =============================================================================


@pytest.mark.parametrize(
    'in_state, out_state, is_regular, mode',
    [
        (
            settings.SEGMENT_PROCESSING_STATE,
            settings.SEGMENT_RESULT_STATE,
            False,
            None,
        ),
        (
            settings.SEGMENT_PROCESSING_STATE,
            settings.SEGMENT_RESULT_STATE,
            True,
            None,
        ),
        (
            settings.RECALCULATION_SEGMENT_PROCESSING_STATE,
            settings.RECALCULATION_SEGMENT_RESULT_STATE,
            False,
            entity.Mode.JOINT,
        ),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_finish_segment_processing(
        web_context, in_state, out_state, is_regular, mode,
):
    campaign_id = 1
    db_campaign = storage.DbCampaign(web_context)

    campaign = await db_campaign.fetch(campaign_id)
    campaign.state = in_state
    campaign.is_regular = is_regular
    campaign.is_active = is_regular
    await db_campaign.update(campaign)
    await db_campaign.update_state(campaign)

    await segment_state_processing.finish_segment_processing(
        context=web_context, campaign=campaign, mode=mode,
    )

    campaign = await db_campaign.fetch(campaign_id)
    assert campaign.state == out_state


# =============================================================================


@pytest.mark.parametrize(
    'in_state, out_state, is_regular, mode',
    [
        (
            settings.SEGMENT_RESULT_STATE,
            settings.GROUPS_PRECALCULATING_STATE,
            True,
            None,
        ),
        (
            settings.GROUPS_EXPECTED_STATE,
            settings.GROUPS_PRECALCULATING_STATE,
            False,
            None,
        ),
        (
            settings.GROUPS_ERROR,
            settings.GROUPS_PRECALCULATING_STATE,
            False,
            None,
        ),
        (settings.SEGMENT_RESULT_STATE, None, False, None),
        (settings.GROUPS_EXPECTED_STATE, None, True, None),
        (settings.GROUPS_ERROR, None, True, None),
        (
            settings.GROUPS_CALCULATING_STATE,
            settings.GROUPS_PRECALCULATING_STATE,
            False,
            None,
        ),
        (
            settings.GROUPS_CALCULATING_STATE,
            settings.GROUPS_PRECALCULATING_STATE,
            True,
            None,
        ),
        (
            settings.RECALCULATION_GROUPS_CALCULATING_STATE,
            settings.RECALCULATION_GROUPS_PRECALCULATING_STATE,
            False,
            entity.Mode.JOINT,
        ),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_start_groups_preprocessing(
        web_context, in_state, out_state, is_regular, mode,
):
    campaign_id = 1
    db_campaign = storage.DbCampaign(web_context)
    campaign = await db_campaign.fetch(campaign_id)
    campaign.state = in_state
    campaign.is_regular = is_regular
    campaign.is_active = is_regular
    await db_campaign.update(campaign)
    await db_campaign.update_state(campaign)

    try:
        await group_state_processing.groups_preprocessing(
            context=web_context, campaign=campaign, mode=mode,
        )

        campaign = await db_campaign.fetch(campaign_id)
        assert campaign.state == out_state
    except entity.InvalidCampaign:
        assert out_state is None


# =============================================================================


@pytest.mark.parametrize(
    'in_state, out_state, is_regular, mode',
    [
        (settings.SEGMENT_RESULT_STATE, None, True, None),
        (settings.GROUPS_EXPECTED_STATE, None, False, None),
        (settings.GROUPS_ERROR, None, False, None),
        (settings.SEGMENT_RESULT_STATE, None, False, None),
        (settings.GROUPS_EXPECTED_STATE, None, True, None),
        (settings.GROUPS_ERROR, None, True, None),
        (settings.GROUPS_CALCULATING_STATE, None, False, None),
        (settings.GROUPS_CALCULATING_STATE, None, True, None),
        (
            settings.GROUPS_PRECALCULATING_STATE,
            settings.GROUPS_CALCULATING_STATE,
            False,
            None,
        ),
        (
            settings.GROUPS_PRECALCULATING_STATE,
            settings.GROUPS_CALCULATING_STATE,
            True,
            None,
        ),
        (
            settings.RECALCULATION_SEGMENT_RESULT_STATE,
            settings.RECALCULATION_GROUPS_CALCULATING_STATE,
            False,
            entity.Mode.JOINT,
        ),
        (
            settings.RECALCULATION_GROUPS_PRECALCULATING_STATE,
            settings.RECALCULATION_GROUPS_CALCULATING_STATE,
            False,
            entity.Mode.JOINT,
        ),
        (
            settings.RECALCULATION_GROUPS_CALCULATING_STATE,
            settings.RECALCULATION_GROUPS_CALCULATING_STATE,
            False,
            entity.Mode.JOINT,
        ),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_start_groups_processing(
        web_context, in_state, out_state, is_regular, mode,
):
    campaign_id = 1
    db_campaign = storage.DbCampaign(web_context)
    campaign = await db_campaign.fetch(campaign_id)
    campaign.state = in_state
    campaign.is_regular = is_regular
    campaign.is_active = is_regular
    await db_campaign.update(campaign)
    await db_campaign.update_state(campaign)

    try:
        await group_state_processing.start_groups_processing(
            context=web_context, campaign=campaign, mode=mode, dry_run=True,
        )

        campaign = await db_campaign.fetch(campaign_id)
        assert campaign.state == in_state
    except entity.InvalidCampaign:
        assert out_state is None

    try:
        await group_state_processing.start_groups_processing(
            context=web_context, campaign=campaign, mode=mode,
        )
        campaign = await db_campaign.fetch(campaign_id)
        assert campaign.state == out_state
    except entity.InvalidCampaign:
        assert out_state is None


# =============================================================================


@pytest.mark.parametrize(
    'in_state, out_state, is_regular, mode',
    [
        (
            settings.GROUPS_CALCULATING_STATE,
            settings.GROUPS_RESULT_STATE,
            False,
            None,
        ),
        (
            settings.GROUPS_CALCULATING_STATE,
            settings.GROUPS_RESULT_STATE,
            True,
            None,
        ),
        (
            settings.RECALCULATION_GROUPS_CALCULATING_STATE,
            settings.RECALCULATION_GROUPS_RESULT_STATE,
            False,
            entity.Mode.JOINT,
        ),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_finish_groups_processing(
        web_context, in_state, out_state, is_regular, mode,
):
    campaign_id = 1
    db_campaign = storage.DbCampaign(web_context)

    campaign = await db_campaign.fetch(campaign_id)
    campaign.state = in_state
    campaign.is_regular = is_regular
    campaign.is_active = is_regular
    await db_campaign.update(campaign)
    await db_campaign.update_state(campaign)

    await group_state_processing.finish_groups_processing(
        context=web_context, campaign=campaign, mode=mode,
    )

    campaign = await db_campaign.fetch(campaign_id)
    assert campaign.state == out_state


@pytest.mark.parametrize(
    'campaign_id, target_state',
    [
        (5, settings.SEGMENT_EXPECTED_STATE),
        (6, settings.SEGMENT_EXPECTED_STATE),
        (7, settings.SEGMENT_EXPECTED_STATE),
        (8, settings.REGULAR_STOPPED),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_canceled_regular_campaign(
        web_context,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
        campaign_id,
        target_state,
):
    db_campaign = storage.DbCampaign(web_context)
    campaign = await db_campaign.fetch(campaign_id)

    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/ticket/comments',
        'POST',
    )
    def _patch_issue(*args, **kwargs):
        assert (
            kwargs['json']['text'] == 'Кампания перешла в статус \'STOPPED\''
        )
        return response_mock(json={})

    await state.transit(web_context, campaign, [], target_state)

    campaign = await db_campaign.fetch(campaign_id)
    assert campaign.state == target_state


@pytest.mark.now('2021-01-27T10:59:00.0')
@pytest.mark.parametrize('campaign_id', [5, 6, 7])
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_transit_to_error_state(
        web_context,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
        campaign_id,
):
    db_campaign = storage.DbCampaign(web_context)
    campaign = await db_campaign.fetch(campaign_id)

    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/ticket/comments',
        'POST',
    )
    def _patch_issue(*args, **kwargs):
        assert (
            kwargs['json']['text']
            == 'Кампания перешла в статус \'SEGMENT_ERROR\''
        )
        return response_mock(json={})

    if campaign.is_regular and campaign.is_active:
        db_schedule = storage.DbSchedule(web_context)
        await db_schedule.schedule(campaign_id, dates.utcnow())

    target_state = settings.SEGMENT_ERROR
    await state.transit_to_error_state(web_context, campaign, target_state)

    campaign = await db_campaign.fetch(campaign_id)
    assert campaign.state == target_state

    if campaign.is_regular and campaign.is_active:
        db_schedule = storage.DbSchedule(web_context)
        pending_campaigs = await db_schedule.list_pending_campaigns(
            target_state,
            (dates.utcnow(), dates.utcnow() + datetime.timedelta(hours=1)),
        )
        assert campaign_id not in [c['campaign_id'] for c in pending_campaigs]


@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_cant_transit_campaign_from_unexpected_state(web_context):
    db_campaign = storage.DbCampaign(web_context)
    campaign = await db_campaign.fetch(campaign_id=1)

    campaign_copy = copy.deepcopy(campaign)
    campaign_copy.state = settings.SEGMENT_PROCESSING_STATE
    await db_campaign.update_state(campaign_copy)

    with pytest.raises(entity.EntityNotFound):
        await state.transit(
            context=web_context,
            campaign=campaign,
            expected_states=settings.CAMPAIGN_EDITABLE_STATES,
            target_state=settings.SEGMENT_EXPECTED_STATE,
        )
