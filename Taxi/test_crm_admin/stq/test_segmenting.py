# pylint: disable=unused-argument,unused-variable,protected-access,invalid-name

import pandas as pd
import pytest

from crm_admin import audience
from crm_admin import entity
from crm_admin import error_codes
from crm_admin import settings
from crm_admin import storage
from crm_admin.entity import error
from crm_admin.generated.service.swagger import models
from crm_admin.stq import segment_processing
from crm_admin.utils.segment import quicksegment as qs_utils
from crm_admin.utils.segmenting import policy
from crm_admin.utils.segmenting import processing
from crm_admin.utils.segmenting import statistics

CRM_ADMIN_TEST_SUMMON = {
    'on_error': {
        'message': '{{logins}}. Кампания перешла в статус \'{{state}}\'',
        'users': ['stasnam', 'apkonkova'],
    },
}

CRM_ADMIN_TEST_SETTINGS = {
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
    'SparkSettings': {'discovery_path': 'discovery_path'},
}

CRM_ADMIN_TEST_SUMMON_DRIVERS = {
    'by_kind': [
        {
            'country_type': 'common',
            'final_approvers': ['final', 'approvers'],
            'idea_approvers': ['idea', 'approvers'],
            'kind': ['tariff_in_city'],
        },
    ],
    'defaults': {
        'common': {
            'final_approvers': ['simushin'],
            'idea_approvers': ['simushin'],
        },
        'international': {
            'final_approvers': ['esdomracheva'],
            'idea_approvers': ['esdomracheva'],
        },
    },
}


POLICY_SETTINGS = {
    'PolicySettings': {
        'channels': {'User': ['promo_fs', 'push']},
        'table_path': '//some/path',
    },
}


@pytest.mark.parametrize('campaign_id', [1, 4])
@pytest.mark.parametrize(
    'mode, stage',
    [(None, None), (entity.Mode.SEGMENT, entity.Stage.SEGMENT_PROCESSING)],
)
@pytest.mark.pgsql(
    'crm_admin', files=['init_campaigns.sql', 'init_qs_schemas.sql'],
)
async def test_process_segment_by_entity_type(
        stq3_context, patch, campaign_id, mode, stage,
):
    operation_id = 1

    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)
    campaign.settings = []

    @patch(
        'crm_admin.utils.segmenting.processing.SegmentProcessing._submit_pollable_spark_job',  # noqa: E501
    )
    async def submit_pollable_spark_job(*args, **kwargs):
        return 'submission-id'

    processor = processing.SegmentProcessing(
        stq3_context, campaign_id, operation_id, None, mode, stage,
    )
    await processor.process_segment(campaign)

    assert submit_pollable_spark_job.calls


@pytest.mark.pgsql(
    'crm_admin', files=['init_campaigns.sql', 'init_qs_schemas.sql'],
)
@pytest.mark.parametrize(
    'mode, stage',
    [(None, None), (entity.Mode.SEGMENT, entity.Stage.SEGMENT_PROCESSING)],
)
async def test_spark_output_path(stq3_context, patch, mode, stage):
    campaign_id = 4
    operation_id = 1

    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)
    campaign.settings = []

    db_segment = storage.DbSegment(stq3_context)
    segment = await db_segment.fetch(campaign.segment_id)
    assert not segment.yt_table.startswith('//')

    @patch(
        'crm_admin.utils.segmenting.processing.SegmentProcessing._submit_pollable_spark_job',  # noqa: E501
    )
    async def submit_pollable_spark_job(*args, **kwargs):
        return 'submission-id'

    processor = processing.SegmentProcessing(
        stq3_context, campaign_id, operation_id, None, mode, stage,
    )
    await processor.process_segment(campaign)

    job_config = submit_pollable_spark_job.call['kwargs']['job_config']
    assert job_config['output_path'].startswith('//')


@pytest.mark.config(CRM_ADMIN_SUMMON=CRM_ADMIN_TEST_SUMMON)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.parametrize(
    'mode, stage',
    [(None, None), (entity.Mode.SEGMENT, entity.Stage.SEGMENT_STATISTICS)],
)
async def test_empty_segment(
        stq3_context,
        patch,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
        mode,
        stage,
):
    @patch(
        'crm_admin.utils.segmenting.statistics.SegmentStatistics._read_segment_summary',  # noqa E501
    )
    async def read_segment_summary(segment):
        return pd.DataFrame()

    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/ticket/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        assert kwargs['json']['summonees'] == ['stasnam', 'apkonkova']
        assert (
            kwargs['json']['text'] == '@stasnam, @apkonkova. Кампания перешла '
            'в статус \'SEGMENT_EMPTY\''
        )
        return response_mock(json={})

    campaign_id = 3
    operation_id = 1
    processor = statistics.SegmentStatistics(
        stq3_context, campaign_id, operation_id, None, mode, stage,
    )
    await processor._on_finished(ok=True, result=None)

    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)
    assert campaign.state == settings.SEGMENT_EMPTY
    assert campaign.error_code == error_codes.INVALID_RESULT

    db_segment = storage.DbSegment(stq3_context)
    segment = await db_segment.fetch(campaign.segment_id)
    assert segment.aggregate_info.size == 0


@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.parametrize(
    'mode, stage',
    [(None, None), (entity.Mode.SEGMENT, entity.Stage.SEGMENT_PROCESSING)],
)
async def test_detect_duplicate_records(
        stq3_context,
        patch,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
        mode,
        stage,
):
    @patch(
        'crm_admin.utils.segmenting.statistics.SegmentStatistics._read_segment_summary',  # noqa E501
    )
    async def read_segment_summary(segment):
        return pd.DataFrame([{'city': '*', 'total': 100, 'account_cnt': 100}])

    @patch(
        'crm_admin.generated.stq3.yt_wrapper.plugin'
        '.AsyncYTClient.get_attribute',
    )
    async def _yt_client_get_attribute(*args, **kwargs):
        return True

    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/ticket/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        return response_mock(json={})

    campaign_id = 3
    operation_id = 1
    processor = statistics.SegmentStatistics(
        context=stq3_context,
        campaign_id=campaign_id,
        operation_id=operation_id,
        task_info=None,
        mode=mode,
        stage=stage,
    )

    with pytest.raises(error.OperationFailure):
        await processor._on_finished(ok=True, result=None)

    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)
    assert campaign.state == settings.SEGMENT_ERROR
    assert campaign.error_code == error_codes.DUPLICATE_KEYS


@pytest.mark.config(CRM_ADMIN_SUMMON=CRM_ADMIN_TEST_SUMMON)
@pytest.mark.pgsql(
    'crm_admin', files=['init_campaigns.sql', 'init_qs_schemas.sql'],
)
@pytest.mark.parametrize(
    'mode, stage',
    [(None, None), (entity.Mode.SEGMENT, entity.Stage.SEGMENT_PROCESSING)],
)
async def test_submission_error(
        stq3_context,
        patch,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
        mode,
        stage,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/ticket/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        assert kwargs['json']['summonees'] == ['stasnam', 'apkonkova']
        assert (
            kwargs['json']['text'] == '@stasnam, @apkonkova. Кампания перешла'
            ' в статус \'SEGMENT_ERROR\''
        )
        return response_mock(json={})

    @patch(
        'crm_admin.utils.segmenting.processing.SegmentProcessing._submit_pollable_spark_job',  # noqa: E501
    )
    async def submit_pollable_spark_job(*args, **kwargs):
        raise error.OperationFailure('error')

    campaign_id = 4
    operation_id = 1
    processor = processing.SegmentProcessing(
        stq3_context, campaign_id, operation_id, None, mode, stage,
    )
    with pytest.raises(error.OperationFailure):
        await processor._on_started()

    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)
    assert campaign.state == settings.SEGMENT_ERROR
    assert campaign.error_code == error_codes.COULD_NOT_SUBMIT


@pytest.mark.config(CRM_ADMIN_SUMMON=CRM_ADMIN_TEST_SUMMON)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.parametrize(
    'mode, stage, operation_id, status',
    [
        (None, None, 1, None),
        (entity.Mode.SEGMENT, entity.Stage.SEGMENT_PROCESSING, 1, None),
        (None, None, 4, 'OP_FAILURE'),
    ],
)
async def test_segment_error(
        stq3_context,
        patch,
        simple_secdist,
        patch_aiohttp_session,
        response_mock,
        mode,
        stage,
        operation_id,
        status,
):
    campaign_id = 3
    db_campaign = storage.DbCampaign(stq3_context)

    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + f'issues/ticket/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        assert kwargs['json']['summonees'] == ['stasnam', 'apkonkova']
        assert (
            kwargs['json']['text'] == '@stasnam, @apkonkova. Кампания перешла '
            'в статус \'SEGMENT_ERROR\''
        )
        return response_mock(json={})

    processor = processing.SegmentProcessing(
        stq3_context, campaign_id, operation_id, None, mode, stage,
    )

    processor.info['status'] = status

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.get')
    async def _get(*args, **kwargs):
        return []

    with pytest.raises(error.OperationFailure):
        await processor._on_finished(False, None)

    campaign = await db_campaign.fetch(campaign_id)
    assert campaign.state == settings.SEGMENT_ERROR
    assert campaign.error_code == error_codes.POLLING_SPARK_LOG


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
@pytest.mark.config(CRM_ADMIN_SUMMON=CRM_ADMIN_TEST_SUMMON)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.parametrize(
    'mode, stage',
    [(None, None), (entity.Mode.SEGMENT, entity.Stage.SEGMENT_PROCESSING)],
)
async def test_segment_error_retry(stq3_context, patch, mode, stage):
    campaign_id = 6
    operation_id = 5
    new_operation_id = 6
    db_campaign = storage.DbCampaign(stq3_context)

    @patch(
        'crm_admin.generated.service.stq_client.plugin.QueueClient.call_later',
    )
    async def call(*args, **kwargs):
        pass

    @patch('crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.get')
    async def _get(*args, **kwargs):
        return []

    processor = processing.SegmentProcessing(
        stq3_context, campaign_id, operation_id, None, mode, stage,
    )
    processor.info['status'] = 'OP_FAILURE'

    await processor._on_finished(False, None)

    campaign = await db_campaign.fetch(campaign_id)
    assert campaign.state == settings.SEGMENT_PREPROCESSING_STATE
    assert call.calls

    db_operations = storage.DbOperations(stq3_context)
    operation = await db_operations.fetch(new_operation_id)

    assert operation.retry_count == 2


@pytest.mark.config(CRM_ADMIN_SUMMON=CRM_ADMIN_TEST_SUMMON)
@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
@pytest.mark.parametrize('global_control', [0, 1])
@pytest.mark.parametrize('campaign_type', ['User', 'Driver'])
async def test_segment_stat(
        stq3_context, patch, global_control, load_json, campaign_type,
):
    class BatchCampaign:
        def __init__(self):
            self.campaign_id = 123
            self.global_control = global_control
            self.entity_type = campaign_type

    campaign = BatchCampaign()

    summary = pd.DataFrame(
        load_json(f'{campaign_type.lower()}-segment-stat.json'),
    )

    audience_cmp = audience.get_audience(campaign)

    info = await audience_cmp.processing.segment_stat(
        context=stq3_context, campaign=campaign, segment_summary=summary,
    )

    assert len(info.distribution) == 1
    assert len(info.distribution[0].locales) == 2

    expected_total = summary.loc[summary.city == '*'].total.sum()
    total = sum(item.value for item in info.distribution[0].locales)
    assert total == expected_total

    if global_control:
        expected_global_control = summary.loc[
            (summary.city == '*') & (summary.global_control_flg == '1')
        ].total.sum()
    else:
        expected_global_control = 0
    assert info.global_control == expected_global_control


@pytest.mark.parametrize('campaign_id', [1, 3])
@pytest.mark.parametrize(
    'mode, stage',
    [(None, None), (entity.Mode.SEGMENT, entity.Stage.SEGMENT_PROCESSING)],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.config(CRM_ADMIN_SUMMON=CRM_ADMIN_TEST_SUMMON)
@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DRIVERS=CRM_ADMIN_TEST_SUMMON_DRIVERS)
async def test_segment_statistics(
        stq3_context,
        patch,
        campaign_id,
        patch_aiohttp_session,
        simple_secdist,
        response_mock,
        mode,
        stage,
):
    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + 'issues/Тикет1/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        return response_mock(json={})

    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)

    @patch(
        'crm_admin.utils.segmenting.statistics.SegmentStatistics._process_aggregates',  # noqa E501
    )
    async def process_aggregates(campaign):
        pass

    operation_id = 1
    processor = statistics.SegmentStatistics(
        stq3_context, campaign.campaign_id, operation_id, None, mode, stage,
    )
    await processor._on_finished(True, None)

    assert process_aggregates.calls


@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.parametrize(
    'mode, stage',
    [(None, None), (entity.Mode.SEGMENT, entity.Stage.SEGMENT_STATISTICS)],
)
async def test_segment_statistics_error(stq3_context, patch, mode, stage):
    @patch('crm_admin.utils.startrek.trigger.summon_by_section')
    async def summon_by_section(*args, **kwargs):
        pass

    operation_id = 1
    campaign_id = 1

    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)

    processor = statistics.SegmentStatistics(
        stq3_context, campaign.campaign_id, operation_id, None, mode, stage,
    )
    with pytest.raises(error.OperationFailure):
        await processor._on_finished(False, None)


@pytest.mark.config(CRM_ADMIN_SUMMON=CRM_ADMIN_TEST_SUMMON)
@pytest.mark.parametrize(
    'mode, stage',
    [(None, None), (entity.Mode.SEGMENT, entity.Stage.SEGMENT_PROCESSING)],
)
async def test_convert_countries(stq3_context, patch, mode, stage):
    @patch('taxi.clients.territories.TerritoriesApiClient.get_all_countries')
    async def get_all_countries():
        return [
            {'_id': 'blr', 'name': 'Беларусь'},
            {'_id': 'rus', 'name': 'Россия'},
        ]

    campaign_id = 1
    operation_id = 1
    processor = processing.SegmentProcessing(
        stq3_context, campaign_id, operation_id, None, mode, stage,
    )

    countries = ['blr', 'rus']
    names = await processor.convert_countries(countries)
    assert set(names) == {'Белоруссия', 'Беларусь', 'Россия'}


async def test_variables():
    input_vars = [
        models.api.FilterFieldInfo('var1', 'value'),
        models.api.FilterFieldInfo(
            'g1',
            [
                [
                    models.api.FilterFieldInfo('var2', 'value'),
                    models.api.FilterFieldInfo('var3', 'value'),
                ],
            ],
        ),
        models.api.FilterFieldInfo('var4', []),
        models.api.FilterFieldInfo(
            'var5', models.api.FilterValue(label='label', value='val5'),
        ),
    ]
    variables = qs_utils.make_variables(input_vars)

    expected = {
        'var1': 'value',
        'g1': [{'var2': 'value', 'var3': 'value'}],
        'var5': 'val5',
    }
    assert variables.asdict() == expected


@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_qs_context(stq3_context):
    campaign_id = 1
    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)

    variables = qs_utils.make_variables([])
    processing.SegmentProcessing.init_context_variables(campaign, variables)

    assert variables.get('campaign.id') == campaign.campaign_id
    assert variables.get('campaign.issue_cd') == campaign.ticket
    assert variables.get('campaign.trend') == campaign.trend
    assert variables.get('campaign.type') == campaign.entity_type


@pytest.mark.parametrize('is_regular', [True, False])
@pytest.mark.pgsql(
    'crm_admin', files=['init_campaigns.sql', 'init_qs_schemas.sql'],
)
@pytest.mark.parametrize(
    'mode, stage',
    [(None, None), (entity.Mode.SEGMENT, entity.Stage.SEGMENT_PROCESSING)],
)
async def test_recompute_regular(stq3_context, patch, is_regular, mode, stage):
    @patch(
        'crm_admin.utils.segmenting.processing.SegmentProcessing._submit_pollable_spark_job',  # noqa: E501
    )
    async def submit_pollable_spark_job(*args, **kwargs):
        return 'submission-id'

    campaign_id = 3
    operation_id = 1

    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)
    campaign.is_regular = is_regular
    campaign.is_active = is_regular
    await db_campaign.update(campaign)

    processor = processing.SegmentProcessing(
        stq3_context, campaign_id, operation_id, None, mode, stage,
    )
    await processor.process_segment(campaign)

    db_group = storage.DbGroup(stq3_context)
    groups = await db_group.fetch_by_segment(campaign.segment_id)
    assert groups


@pytest.mark.pgsql(
    'crm_admin', files=['init_campaigns.sql', 'init_qs_schemas.sql'],
)
@pytest.mark.parametrize(
    'mode, stage',
    [(None, None), (entity.Mode.SEGMENT, entity.Stage.SEGMENT_PROCESSING)],
)
async def test_reset_group_counters(stq3_context, patch, mode, stage):
    @patch(
        'crm_admin.utils.segmenting.processing.SegmentProcessing._submit_pollable_spark_job',  # noqa: E501
    )
    async def submit_pollable_spark_job(*args, **kwargs):
        return 'submission-id'

    campaign_id = 1
    operation_id = 1

    processor = processing.SegmentProcessing(
        stq3_context, campaign_id, operation_id, None, mode, stage,
    )

    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)
    await processor.process_segment(campaign)

    db_group = storage.DbGroup(stq3_context)
    groups = await db_group.fetch_by_segment(campaign.segment_id)
    assert all(g.params.computed is None for g in groups)


@pytest.mark.config(CRM_ADMIN_SETTINGS=POLICY_SETTINGS)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.parametrize(
    'operation_id, campaign_id, policy_on', [(1, 1, True), (2, 4, False)],
)
@pytest.mark.parametrize(
    'mode, stage',
    [(None, None), (entity.Mode.SEGMENT, entity.Stage.SEGMENT_PROCESSING)],
)
async def test_segmenting_next_step(
        stq3_context, patch, operation_id, campaign_id, policy_on, mode, stage,
):
    @patch('crm_admin.utils.segmenting.policy.start_segment_policy')
    async def start_segment_policy(*args, **kwargs):
        pass

    @patch('crm_admin.utils.segmenting.statistics.start_segment_statistics')
    async def start_segment_statistics(*args, **kwargs):
        pass

    @patch('crm_admin.utils.stq_tasks.start_calculations_processing')
    async def start_calculations_processing(*args, **kwargs):
        pass

    operation_id = 1

    processor = processing.SegmentProcessing(
        stq3_context, campaign_id, operation_id, None, mode, stage,
    )
    await processor._on_finished(True, None)

    if mode:
        assert start_calculations_processing.calls
    else:
        if policy_on:
            assert start_segment_policy.calls
        else:
            assert start_segment_statistics.calls


@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.parametrize(
    'mode, stage',
    [(None, None), (entity.Mode.SEGMENT, entity.Stage.SEGMENT_POLICY)],
)
async def test_start_policy(stq3_context, patch, mode, stage):
    @patch('crm_admin.utils.spark.policy_spark.submit_policy_task')
    async def submit_policy_task(*args, **kwargs):
        return 'submission-id'

    campaign_id = 1
    operation_id = 1

    processor = policy.SegmentPolicy(
        stq3_context, campaign_id, operation_id, None, mode, stage,
    )
    await processor._on_started()

    assert submit_policy_task.calls


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.parametrize(
    'mode, stage',
    [(None, None), (entity.Mode.SEGMENT, entity.Stage.SEGMENT_POLICY)],
)
async def test_start_policy_failure(stq3_context, patch, mode, stage):
    @patch('crm_admin.utils.startrek.trigger.summon_by_section')
    async def summon_by_section(*args, **kwargs):
        pass

    @patch(
        'crm_admin.utils.segmenting.policy.SegmentPolicy._submit_pollable_spark_job',  # noqa E501
    )
    async def submit_pollable_spark_job(*args, **kwargs):
        raise error.OperationFailure('error')

    campaign_id = 1
    operation_id = 1

    processor = policy.SegmentPolicy(
        stq3_context, campaign_id, operation_id, None, mode, stage,
    )
    with pytest.raises(error.OperationFailure):
        await processor._on_started()

    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)
    assert campaign.state == settings.SEGMENT_ERROR
    assert campaign.error_code == error_codes.COULD_NOT_SUBMIT


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.parametrize(
    'mode, stage',
    [(None, None), (entity.Mode.SEGMENT, entity.Stage.SEGMENT_POLICY)],
)
async def test_policy_finished(stq3_context, patch, mode, stage):
    @patch('crm_admin.utils.common.rename')
    async def rename(*args):
        pass

    @patch(
        'crm_admin.utils.segmenting.statistics.SegmentStatistics.start_stq_task',  # noqa E501
    )
    async def start_stq_task(*args, **kwargs):
        pass

    @patch('crm_admin.utils.stq_tasks.start_calculations_processing')
    async def start_calculations_processing(*args, **kwargs):
        pass

    campaign_id = 1
    operation_id = 1

    processor = policy.SegmentPolicy(
        stq3_context, campaign_id, operation_id, None, mode, stage,
    )
    await processor._on_finished(True, None)

    assert rename.calls
    if mode:
        assert start_calculations_processing.calls
    else:
        assert start_stq_task.calls


@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.parametrize(
    'mode, stage',
    [(None, None), (entity.Mode.SEGMENT, entity.Stage.SEGMENT_POLICY)],
)
async def test_policy_error(stq3_context, patch, mode, stage):
    @patch('crm_admin.utils.startrek.trigger.summon_by_section')
    async def summon_by_section(*args, **kwargs):
        pass

    campaign_id = 1
    operation_id = 1

    processor = policy.SegmentPolicy(
        stq3_context, campaign_id, operation_id, None, mode, stage,
    )
    with pytest.raises(error.OperationFailure):
        await processor._on_finished(False, None)

    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)
    assert campaign.state == settings.SEGMENT_ERROR
    assert campaign.error_code == error_codes.POLLING_SPARK_LOG


@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.parametrize(
    'mode, stage',
    [(None, None), (entity.Mode.SEGMENT, entity.Stage.SEGMENT_POLICY)],
)
async def test_canceled(stq3_context, patch, mode, stage):
    campaign_id = 1
    operation_id = 1

    processor = policy.SegmentPolicy(
        stq3_context, campaign_id, operation_id, None, mode, stage,
    )
    await processor._on_canceled()

    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)
    assert campaign.state == settings.SEGMENT_EXPECTED_STATE


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
@pytest.mark.parametrize(
    'step_cls,mode,stage',
    [
        (processing.SegmentProcessing, None, None),
        (policy.SegmentPolicy, None, None),
        (statistics.SegmentStatistics, None, None),
        (
            processing.SegmentProcessing,
            entity.Mode.SEGMENT,
            entity.Stage.SEGMENT_PROCESSING,
        ),
        (
            policy.SegmentPolicy,
            entity.Mode.SEGMENT,
            entity.Stage.SEGMENT_POLICY,
        ),
        (
            statistics.SegmentStatistics,
            entity.Mode.SEGMENT,
            entity.Stage.SEGMENT_STATISTICS,
        ),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_submission_lost(stq3_context, patch, step_cls, mode, stage):
    @patch('crm_admin.utils.startrek.trigger.summon_by_section')
    async def summon_by_section(*args, **kwargs):
        pass

    @patch('crm_admin.utils.stq_tasks.start_segment_processing')
    async def start_segment_processing(*args, **kwargs):
        pass

    @patch('crm_admin.utils.stq_tasks.start_calculations_processing')
    async def start_calculations_processing(*args, **kwargs):
        pass

    campaign_id = 6
    operation_id = 5

    processor = step_cls(
        stq3_context, campaign_id, operation_id, None, mode, stage,
    )

    processor.info['status'] = 'NOT_FOUND'
    await processor._on_finished(False, None)

    if mode and stage:
        assert not start_segment_processing.calls
        assert start_calculations_processing.calls
    else:
        assert start_segment_processing.calls
        assert not start_calculations_processing.calls

    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)
    assert campaign.state != settings.SEGMENT_ERROR


@pytest.mark.parametrize('campaign_id', [1, 3])
@pytest.mark.parametrize('mode', [entity.Mode.JOINT, entity.Mode.SEGMENT])
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
@pytest.mark.config(CRM_ADMIN_SUMMON=CRM_ADMIN_TEST_SUMMON)
@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_TEST_SETTINGS)
@pytest.mark.config(CRM_ADMIN_SUMMON_DRIVERS=CRM_ADMIN_TEST_SUMMON_DRIVERS)
async def test_segment_statistics_with_group_processing_start(
        stq3_context,
        patch,
        campaign_id,
        patch_aiohttp_session,
        simple_secdist,
        response_mock,
        mode,
):
    @patch('crm_admin.utils.stq_tasks.start_calculations_processing')
    async def start_calculations_processing(*args, **kwargs):
        pass

    st_settings = simple_secdist['settings_override']['STARTRACK_API_PROFILES']

    @patch_aiohttp_session(
        st_settings['robot-crm-admin']['url'] + 'issues/Тикет1/comments',
        'POST',
    )
    def patch_issue(*args, **kwargs):
        return response_mock(json={})

    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)

    @patch(
        'crm_admin.utils.segmenting.statistics.'
        'SegmentStatistics.'
        '_process_aggregates',
    )
    async def process_aggregates(campaign):
        pass

    operation_id = 1
    processor = statistics.SegmentStatistics(
        stq3_context,
        campaign.campaign_id,
        operation_id,
        None,
        mode,
        entity.Stage.SEGMENT_STATISTICS,
    )
    await processor._on_finished(True, None)
    assert process_aggregates.calls

    if mode is entity.Mode.JOINT:
        assert start_calculations_processing.calls
    else:
        assert not start_calculations_processing.calls


@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_stq_was_not_started(stq3_context, patch):
    class TaskInfo:
        id = 'task_id'
        exec_tries = 0

    @patch('crm_admin.utils.segmenting.processing.SegmentProcessing.execute')
    async def execute(*args, **kwargs):
        pass

    campaign_id = 5
    operation_id = 1

    await segment_processing.task(
        stq3_context, TaskInfo(), campaign_id, operation_id,
    )

    assert not execute.calls
