# pylint: disable=unused-variable,invalid-name,protected-access

import pandas as pd
import pytest


from crm_admin import error_codes
from crm_admin import settings
from crm_admin import storage
from crm_admin.entity import error
from crm_admin.utils.grouping import policy
from crm_admin.utils.grouping import processing
from crm_admin.utils.grouping import statistics

CRM_ADMIN_GROUPS_V2 = {'all_on': True}

CRM_ADMIN_EFFICIENCY_SETTINGS = {'group_size': 1000}

CRM_ADMIN_TEST_SUMMON = {
    'on_error': {
        'message': '{{logins}}. Кампания перешла в статус \'{{state}}\'',
        'users': ['stasnam', 'apkonkova'],
    },
}

CRM_ADMIN_SETTINGS = {
    'PolicySettings': {
        'channels': {'User': ['promo_fs', 'push'], 'Driver': ['sms', 'push']},
        'table_path': '//some/path',
    },
    'SparkSettings': {'discovery_path': 'discovery_path'},
}

POLICY_SETTINGS = {
    'PolicySettings': {
        'channels': {'User': ['promo_fs', 'push']},
        'table_path': '//some/path',
    },
    'SparkSettings': {'discovery_path': 'discovery_path'},
}


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.config(
    CRM_ADMIN_EFFICIENCY_SETTINGS=CRM_ADMIN_EFFICIENCY_SETTINGS,
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.parametrize('campaign_id, operation_id', [(1, 1), (2, 2)])
async def test_start_operation(
        stq3_context, patch, load_json, campaign_id, operation_id,
):
    class TaskInfo:
        id = 'task_id'
        exec_tries = 0

    @patch(
        'crm_admin.utils.grouping.processing.GroupProcessing._submit_pollable_spark_job',  # noqa: E501
    )
    async def submit_pollable_spark_job(*args, **kwargs):
        return 'submission-id'

    g = processing.GroupProcessing(
        stq3_context, campaign_id, operation_id, TaskInfo(),
    )
    await g._on_started()

    expected = load_json('jobs.json')[str(campaign_id)]

    args = submit_pollable_spark_job.call
    assert args['kwargs']['job'] == 'grouping.py'
    assert args['kwargs']['job_config'] == expected


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.config(CRM_ADMIN_SETTINGS=POLICY_SETTINGS)
@pytest.mark.parametrize('retry', [False, True])
@pytest.mark.parametrize(
    'operation_id, campaign_id, policy_on', [(1, 1, True), (4, 4, False)],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_finish_grouping(
        stq3_context, patch, retry, operation_id, campaign_id, policy_on,
):
    class TaskInfo:
        id = 'task_id'
        exec_tries = 0

    processor = processing.GroupProcessing(
        stq3_context, campaign_id, operation_id, TaskInfo(),
    )

    @patch('crm_admin.utils.grouping.policy.start_group_policy')
    async def start_group_policy(*args, **kwargs):
        pass

    @patch('crm_admin.utils.grouping.statistics.start_group_statistics')
    async def start_group_statistics(*args, **kwargs):
        pass

    @patch('crm_admin.utils.grouping.processing.GroupProcessing._exists')
    async def exists(path):
        return not retry

    @patch('crm_admin.utils.grouping.processing.GroupProcessing._rename')
    async def rename(src, dst):
        pass

    await processor._on_finished(True, None)

    args = rename.call
    if retry:
        assert args is None
    else:
        job_config = processor._get_job_config()
        assert args['src'] == job_config['output_table']
        assert args['dst'] == job_config['input_table']

        if policy_on:
            assert start_group_policy.calls
        else:
            assert start_group_statistics.calls


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_start_groups_policy(stq3_context, patch):
    class TaskInfo:
        id = 'task_id'
        exec_tries = 0

    @patch('crm_admin.utils.spark.policy_spark.submit_policy_task')
    async def submit_policy_task(*args, **kwargs):
        return 'submission-id'

    campaign_id = 1
    operation_id = 1

    processor = policy.GroupPolicy(
        stq3_context, campaign_id, operation_id, TaskInfo(),
    )
    await processor._on_started()

    assert submit_policy_task.calls


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_finish_groups_policy(stq3_context, patch):
    class TaskInfo:
        id = 'task_id'
        exec_tries = 0

    @patch('crm_admin.utils.common.rename')
    async def rename(*args):
        pass

    @patch(
        'crm_admin.utils.grouping.statistics.GroupStatistics.start_stq_task',
    )
    async def start_stq_task(*args, **kwargs):
        pass

    campaign_id = 1
    operation_id = 3

    processor = policy.GroupPolicy(
        stq3_context, campaign_id, operation_id, TaskInfo(),
    )
    await processor._on_finished(True, None)

    assert rename.calls
    assert start_stq_task.calls


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_groups_policy_error(stq3_context, patch):
    class TaskInfo:
        id = 'task_id'
        exec_tries = 0

    @patch('crm_admin.utils.startrek.trigger.summon_by_section')
    async def summon_by_section(*args, **kwargs):
        pass

    campaign_id = 1
    operation_id = 3

    processor = policy.GroupPolicy(
        stq3_context, campaign_id, operation_id, TaskInfo(),
    )
    with pytest.raises(error.OperationFailure):
        await processor._on_finished(False, None)

    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)
    assert campaign.state == settings.GROUPS_ERROR
    assert campaign.error_code == error_codes.SUBMISSION_FAILED


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_start_groups_statistics(stq3_context, patch):
    class TaskInfo:
        id = 'task_id'
        exec_tries = 0

    @patch(
        'crm_admin.utils.grouping.statistics.GroupStatistics'
        '._submit_pollable_spark_job',
    )
    async def submit_pollable_spark_job(*args, **kwargs):
        return 'submission-id'

    campaign_id = 1
    operation_id = 1

    processor = statistics.GroupStatistics(
        stq3_context, campaign_id, operation_id, TaskInfo(),
    )
    await processor._on_started()

    assert submit_pollable_spark_job.calls


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_finish_groups_statistics(stq3_context, patch):
    class TaskInfo:
        id = 'task_id'
        exec_tries = 0

    campaign_id = 1
    operation_id = 3
    processor = statistics.GroupStatistics(
        stq3_context, campaign_id, operation_id, TaskInfo(),
    )

    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)

    db_group = storage.DbGroup(stq3_context)
    groups = await db_group.fetch_by_segment(campaign.segment_id)

    groups_stat = pd.DataFrame()
    groups_stat['group_name'] = [groups[0].params.name]
    groups_stat['total'] = 20
    groups_stat['comm_push_blocked'] = 10
    groups_stat['comm_promo_fs_blocked'] = 5
    groups_stat['efficiency'] = 2

    @patch(
        'crm_admin.utils.grouping.statistics.GroupStatistics.'
        '_read_groups_stat',
    )
    async def read_groups_stat(*args, **kwargs):
        return groups_stat

    await processor._process_groups_stat(campaign)

    groups = await db_group.fetch_by_segment(campaign.segment_id)
    assert groups[0].params.computed.extra['total'] == 20
    assert groups[0].params.computed.extra['PUSH'] == 10
    assert groups[0].params.computed.extra['promo.fs'] == 15
    assert groups[0].params.computed.extra['efficiency_subgroup_size'] == 2

    # the second group is missing in the segment,
    # so its statistics are all zeros
    #
    assert groups[1].params.computed.extra['total'] == 0
    assert groups[1].params.computed.extra['PUSH'] == 0
    assert groups[1].params.computed.extra['promo.fs'] == 0
    assert groups[1].params.computed.extra['efficiency_subgroup_size'] == 0


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_groups_statistics_error(stq3_context, patch):
    class TaskInfo:
        id = 'task_id'
        exec_tries = 0

    @patch('crm_admin.utils.startrek.trigger.summon_by_section')
    async def summon_by_section(*args, **kwargs):
        pass

    campaign_id = 1
    operation_id = 3

    processor = statistics.GroupStatistics(
        stq3_context, campaign_id, operation_id, TaskInfo(),
    )
    with pytest.raises(error.OperationFailure):
        await processor._on_finished(False, None)

    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)
    assert campaign.state == settings.GROUPS_ERROR
    assert campaign.error_code == error_codes.SUBMISSION_FAILED


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.config(CRM_ADMIN_SUMMON=CRM_ADMIN_TEST_SUMMON)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_start_error(
        stq3_context,
        patch,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
):
    class TaskInfo:
        id = 'task_id'
        exec_tries = 0

    @patch(
        'crm_admin.utils.grouping.processing.GroupProcessing'
        '._submit_pollable_spark_job',
    )
    async def submit_pollable_spark_job(*args, **kwargs):
        raise error.OperationFailure('error')

    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/ticket/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        assert kwargs['json']['summonees'] == ['stasnam', 'apkonkova']
        assert (
            kwargs['json']['text'] == '@stasnam, @apkonkova. Кампания перешла '
            'в статус \'GROUPS_ERROR\''
        )
        return response_mock(json={})

    campaign_id = 1
    operation_id = 3
    processor = processing.GroupProcessing(
        stq3_context, campaign_id, operation_id, TaskInfo(),
    )
    with pytest.raises(error.OperationFailure):
        await processor._on_started()

    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)
    assert campaign.state == settings.GROUPS_ERROR
    assert campaign.error_code == error_codes.COULD_NOT_SUBMIT


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.config(CRM_ADMIN_SUMMON=CRM_ADMIN_TEST_SUMMON)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_finish_grouping_error(
        stq3_context,
        patch,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
):
    class TaskInfo:
        id = 'task_id'
        exec_tries = 0

    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/ticket/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        assert 'summonees' in kwargs['json']
        assert kwargs['json']['summonees'] == ['stasnam', 'apkonkova']
        assert (
            kwargs['json']['text'] == '@stasnam, @apkonkova. Кампания перешла '
            'в статус \'GROUPS_ERROR\''
        )
        return response_mock(json={})

    campaign_id = 1
    operation_id = 3
    processor = processing.GroupProcessing(
        stq3_context, campaign_id, operation_id, TaskInfo(),
    )

    with pytest.raises(error.OperationFailure):
        await processor._on_finished(False, None)

    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)
    assert campaign.state == settings.GROUPS_ERROR
    assert campaign.error_code == error_codes.SUBMISSION_FAILED


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.parametrize('is_regular', [True, False])
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_regular_campaign(stq3_context, patch, is_regular):
    @patch(
        'crm_admin.utils.grouping.statistics.GroupStatistics'
        '._process_groups_stat',
    )
    async def process_groups_stat(*args, **kwargs):
        pass

    @patch('crm_admin.utils.startrek.startrek.TicketManager.add_comment')
    async def add_comment(*args, **kwargs):
        pass

    class TaskInfo:
        id = 'task_id'
        exec_tries = 0

    campaign_id = 1
    operation_id = 3
    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)
    campaign.is_regular = is_regular
    campaign.is_active = is_regular
    await db_campaign.update(campaign)

    processor = statistics.GroupStatistics(
        stq3_context, campaign_id, operation_id, TaskInfo(),
    )

    await processor._on_finished(True, None)

    db_group = storage.DbGroup(stq3_context)
    groups = await db_group.fetch_by_segment(campaign.segment_id)
    if is_regular:
        assert all(
            g.params.state
            in {settings.GROUP_STATE_NEW, settings.GROUP_STATE_HOLD}
            for g in groups
        )
    else:
        assert not any(
            g.params.state == settings.GROUP_STATE_NEW for g in groups
        )


@pytest.mark.config(CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2)
@pytest.mark.config(CRM_ADMIN_SETTINGS=POLICY_SETTINGS)
@pytest.mark.parametrize(
    'step_cls',
    [
        processing.GroupProcessing,
        policy.GroupPolicy,
        statistics.GroupStatistics,
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_submission_lost(stq3_context, patch, step_cls):
    @patch('crm_admin.utils.startrek.trigger.summon_by_section')
    async def summon_by_section(*args, **kwargs):
        pass

    @patch('crm_admin.utils.stq_tasks.start_groups_processing')
    async def start_groups_processing(*args, **kwargs):
        pass

    campaign_id = 4
    operation_id = 4

    processor = step_cls(stq3_context, campaign_id, operation_id, None)
    processor.info['status'] = 'NOT_FOUND'
    await processor._on_finished(False, None)

    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)
    assert campaign.state != settings.GROUPS_ERROR
