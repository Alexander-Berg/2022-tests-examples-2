# pylint: disable=unused-variable,invalid-name,protected-access

import pytest

from crm_admin import entity
from crm_admin import error_codes
from crm_admin import settings
from crm_admin import storage
from crm_admin.entity import error
from crm_admin.utils.segment import segment_splitting

CRM_ADMIN_EFFICIENCY_SETTINGS = {'group_size': 1000}

CRM_ADMIN_TEST_SUMMON = {
    'on_error': {
        'message': '{{logins}}. Кампания перешла в статус \'{{state}}\'',
        'users': ['stasnam', 'apkonkova'],
    },
}

CRM_ADMIN_SETTINGS = {
    'StartrekSettings': {
        'campaign_queue': 'CRMTEST',
        'creative_queue': 'CRMTEST',
        'idea_approved_statuses': ['В работе'],
        'target_statuses': ['target_status'],
        'unapproved_statuses': ['В работе'],
    },
    'PolicySettings': {
        'channels': {'User': ['promo_fs', 'push'], 'Driver': ['sms', 'push']},
        'table_path': '//some/path',
    },
}

POLICY_SETTINGS = {
    'PolicySettings': {
        'channels': {'User': ['promo_fs', 'push']},
        'table_path': '//some/path',
    },
}


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.parametrize(
    'mode, stage',
    [(None, None), (entity.Mode.GROUP, entity.Stage.GROUP_SEGMENT_SPLITTING)],
)
async def test_start_segment_splitting(stq3_context, patch, mode, stage):
    class TaskInfo:
        id = 'task_id'

    @patch(
        'crm_admin.utils.segment.segment_splitting.SegmentSplitting'
        '._submit_pollable_splitter_job',
    )
    async def _submit_pollable_splitter_job(*args, **kwargs):
        return

    campaign_id = 1
    operation_id = 1

    processor = segment_splitting.SegmentSplitting(
        stq3_context, campaign_id, operation_id, TaskInfo(), mode, stage,
    )
    await processor._on_started()

    assert _submit_pollable_splitter_job.calls


@pytest.mark.config(CRM_ADMIN_SETTINGS=POLICY_SETTINGS)
@pytest.mark.parametrize(
    'mode, stage',
    [(None, None), (entity.Mode.GROUP, entity.Stage.GROUP_SEGMENT_SPLITTING)],
)
@pytest.mark.parametrize(
    'operation_id, campaign_id, policy_on', [(1, 1, True), (3, 4, False)],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_finish_segment_splitting(
        stq3_context, patch, operation_id, campaign_id, policy_on, mode, stage,
):
    class TaskInfo:
        id = 'task_id'

    processor = segment_splitting.SegmentSplitting(
        stq3_context, campaign_id, operation_id, TaskInfo(), mode, stage,
    )

    @patch('crm_admin.utils.grouping.policy.start_group_policy')
    async def start_group_policy(*args, **kwargs):
        pass

    @patch('crm_admin.utils.grouping.statistics.start_group_statistics')
    async def start_group_statistics(*args, **kwargs):
        pass

    @patch(
        'crm_admin.utils.segment.segment_splitting.SegmentSplitting._exists',
    )
    async def exists(path):
        return True

    @patch(
        'crm_admin.utils.segment.segment_splitting.SegmentSplitting._rename',
    )
    async def rename(src, dst):
        pass

    @patch('crm_admin.utils.stq_tasks.start_calculations_processing')
    async def start_calculations_processing(*args, **kwargs):
        pass

    await processor._on_finished(True, None)

    args = rename.call
    job_config = processor._get_job_config()
    assert args['src'] == job_config['output_table']
    assert args['dst'] == job_config['input_table']

    if mode:
        assert start_calculations_processing.calls
    else:
        if policy_on:
            assert start_group_policy.calls
        else:
            assert start_group_statistics.calls


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.parametrize(
    'mode, stage',
    [(None, None), (entity.Mode.GROUP, entity.Stage.GROUP_SEGMENT_SPLITTING)],
)
async def test_segmet_splitting_error(stq3_context, patch, mode, stage):
    class TaskInfo:
        id = 'task_id'

    @patch('crm_admin.utils.startrek.trigger.summon_by_section')
    async def summon_by_section(*args, **kwargs):
        pass

    campaign_id = 1
    operation_id = 2

    processor = segment_splitting.SegmentSplitting(
        stq3_context, campaign_id, operation_id, TaskInfo(), mode, stage,
    )
    with pytest.raises(error.OperationFailure):
        await processor._on_finished(False, None)

    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)
    assert campaign.state == settings.GROUPS_ERROR
    assert campaign.error_code == error_codes.SUBMISSION_FAILED
