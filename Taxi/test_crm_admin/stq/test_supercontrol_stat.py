# pylint: disable=unused-variable,invalid-name,protected-access
import datetime

import pytest

from crm_admin import entity
from crm_admin import storage
from crm_admin.stq import supercontrol_stat


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.now('2021-05-05 05:05:05')
async def test_supercontrol_stat(stq3_context, patch, load_json):
    campaign_id = 1
    file = 'result.json'

    params = load_json(file)

    class TaskInfo:
        id = 'task_id'
        exec_tries = 0

    params = load_json(file)

    @patch('crm_admin.generated.stq3.yt_wrapper.plugin.AsyncYTClient.get')
    async def get(*args, **kwargs):
        return [{'name': 'comm_push_blocked'}, {'name': 'comm_sms_blocked'}]

    @patch('client_chyt.components.AsyncChytClient.execute')
    async def execute(query):
        return params['query_result']

    @patch('crm_admin.stq.supercontrol_stat.remove_yt_table')
    async def remove_yt_table(*args, **kwargs):
        pass

    @patch('crm_admin.stq.supercontrol_stat.is_exist_yt')
    async def is_exist_yt(*args, **kwargs):
        return True

    await supercontrol_stat.task(stq3_context, TaskInfo(), campaign_id)

    db_campaign = storage.DbCampaign(stq3_context)
    campaign = await db_campaign.fetch(campaign_id)

    assert campaign.segment_id
    assert campaign.segment_stats_status
    assert (
        campaign.segment_stats_status.state
        == entity.AggregateInfoState.COMPUTED
    )
    assert (
        campaign.segment_stats_status.updated_at
        == datetime.datetime.strptime(
            '2021-05-05 05:05:05', '%Y-%m-%d %H:%M:%S',
        )
    )

    db_segment = storage.DbSegment(stq3_context)
    segment = await db_segment.fetch(campaign.segment_id)

    assert segment.aggregate_info
    assert (
        segment.aggregate_info.filtered
        == params['query_result'][0]['filtered']
    )
    assert [
        target_stat.serialize()
        for target_stat in segment.aggregate_info.targets_stat
    ] == params['query_result'][0]['targets_stat']

    assert segment.applied_targets

    applied_targets = [
        applied_target.serialize()
        for applied_target in segment.applied_targets
    ]

    assert applied_targets == params['applied_targets']
