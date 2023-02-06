# pylint: disable=unused-variable,invalid-name,protected-access

import pytest

from crm_admin import entity
from crm_admin import settings
from crm_admin import storage
from crm_admin.stq import draft_processing


CAMPAIGN_COPIED_FIELDS = [
    'name',
    'specification',
    'entity_type',
    'trend',
    'kind',
    'subkind',
    'discount',
    'ticket',
    'ticket_status',
    'settings',
    'extra_data',
    'extra_data_path',
    'creative',
    'test_users',
    'global_control',
    'com_politic',
    'efficiency',
    'tasks',
    'planned_start_date',
    'extra_data_key',
    'is_regular',
    'schedule',
    'regular_start_time',
    'regular_stop_time',
    'efficiency_start_time',
    'efficiency_stop_time',
    'motivation_methods',
]

GROUP_COPIED_FIELDS = [
    *entity.SplittingSettingsFields.SHARE_FIELDS,
    *entity.SplittingSettingsFields.FILTER_FIELDS,
    *entity.SplittingSettingsFields.VALUE_FIELDS,
    'name',
    'send_at',
    'sent',
    'sent_time',
    'efficiency_date',
    'efficiency_time',
]

CRM_ADMIN_GROUPS_V2 = {'all_on': True}


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.parametrize('root_id', [2])
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_draft_processing(stq3_context, patch, load_json, root_id):
    class TaskInfo:
        id = 'task_id'
        exec_tries = 0

    @patch('crm_admin.generated.stq3.yt_wrapper.plugin.AsyncYTClient.copy')
    async def yt_copy(*args, **kwargs):
        pass

    @patch('crm_admin.generated.stq3.yt_wrapper.plugin.AsyncYTClient.exists')
    async def yt_exists(*args, **kwargs):
        return False

    await draft_processing.task(stq3_context, TaskInfo(), 2, 3)

    db_campaign = storage.DbCampaign(stq3_context)

    draft_campaign = await db_campaign.fetch_by_version_state(
        root_id, settings.VersionState.DRAFT,
    )
    actual_campaign = await db_campaign.fetch_by_version_state(
        root_id, settings.VersionState.ACTUAL,
    )

    assert draft_campaign
    assert actual_campaign

    assert draft_campaign.owner_name == 'trusienkodv'
    assert draft_campaign.state == settings.GROUPS_RESULT_STATE
    assert draft_campaign.parent_id == actual_campaign.campaign_id
    assert draft_campaign.root_id == root_id
    assert actual_campaign.child_id == draft_campaign.campaign_id
    assert not draft_campaign.is_active

    for field in CAMPAIGN_COPIED_FIELDS:
        actual_field = getattr(actual_campaign, field, None)
        draft_field = getattr(draft_campaign, field, None)
        assert actual_field == draft_field

    assert actual_campaign.segment_id
    assert draft_campaign.segment_id

    db_segment = storage.DbSegment(stq3_context)

    actual_segment = await db_segment.fetch(actual_campaign.segment_id)
    draft_segment = await db_segment.fetch(draft_campaign.segment_id)

    assert actual_segment != draft_segment
    assert actual_segment.aggregate_info == draft_segment.aggregate_info
    assert actual_segment.mode == draft_segment.mode
    assert actual_segment.control == draft_segment.control
    assert actual_segment.extra_columns == draft_segment.extra_columns
    assert (
        draft_segment.yt_table == f'home/taxi-crm/robot-crm-admin/'
        f'cmp_{draft_campaign.campaign_id}_seg'
    )

    db_creative = storage.DbCreative(stq3_context)

    actual_creatives = await db_creative.fetch_by_campaign_id(
        actual_campaign.campaign_id, None, None,
    )

    draft_creatives = await db_creative.fetch_by_campaign_id(
        draft_campaign.campaign_id, None, None,
    )

    creatives_mapper = {None: None}

    for actual_creative, draft_creative in zip(
            actual_creatives, draft_creatives,
    ):
        assert (
            actual_creative.params.serialize()
            == draft_creative.params.serialize()
        )
        assert actual_creative.name == draft_creative.name
        assert actual_creative.extra_data == draft_creative.extra_data
        assert actual_creative.root_id == draft_creative.root_id
        assert actual_creative.child_id == draft_creative.creative_id
        assert draft_creative.parent_id == actual_creative.creative_id
        creatives_mapper[
            actual_creative.creative_id
        ] = draft_creative.creative_id

    db_group = storage.DbGroup(stq3_context)

    actual_groups = await db_group.fetch_by_campaign_id(
        actual_campaign.campaign_id,
    )
    draft_groups = await db_group.fetch_by_campaign_id(
        draft_campaign.campaign_id,
    )

    for actual_group, draft_group in zip(actual_groups, draft_groups):
        assert (
            draft_group.params.creative_id
            == creatives_mapper[actual_group.params.creative_id]
        )
        assert draft_group.segment_id == draft_segment.segment_id
        assert draft_group.params.state == settings.GROUP_STATE_NEW
        assert (
            actual_group.params.version_info.root_id
            == draft_group.params.version_info.root_id
        )
        assert (
            actual_group.params.version_info.child_id == draft_group.group_id
        )
        assert (
            draft_group.params.version_info.parent_id == actual_group.group_id
        )
        if actual_group.params.computed:
            assert (
                actual_group.params.computed.serialize()
                == draft_group.params.computed.serialize()
            )
        for field in GROUP_COPIED_FIELDS:
            actual_field = getattr(actual_group.params, field, None)
            draft_field = getattr(draft_group.params, field, None)
            assert actual_field == draft_field
