# pylint: disable=protected-access
import datetime

import pytest

from taxi.stq import async_worker_ng

from crm_admin.storage import campaign_adapters
from crm_admin.utils.spark import spark_error_poller


@pytest.mark.parametrize(
    'error_log, expected_result',
    [
        (
            '2021-09-17 17:21:18,116 - ERROR - spyt.client -'
            ' Shutdown SparkSession after exception: cannot resolve '
            '\'`yt_db_id`\' given input columns: '
            '[yt_external_segment.yt_user_phone_id]; line 64 pos 15;',
            {
                'error': 'MISSING_KEY_COLUMN',
                'description': {'error_msg': 'yt_db_id'},
            },
        ),
        (
            '2021-09-20 19:02:16,910 - ERROR - spyt.client - '
            'Shutdown SparkSession after exception: An error '
            'occurred while calling o353.save.',
            {
                'error': 'SEGMENT_RESTART_NEEDED',
                'description': {
                    'error_msg': 'An error occurred while calling o353.save.',
                },
            },
        ),
        (
            '2021-09-30 12:26:15,883 - ERROR - spyt.client - '
            'Shutdown SparkSession after exception: float division by zero',
            {
                'error': 'UNEXPECTED_SPARK_ERROR',
                'description': {
                    'error_msg': (
                        'spyt.client - Shutdown SparkSession '
                        'after exception: float division by zero'
                    ),
                },
            },
        ),
        (
            '2021-09-30 12:26:15,883 - INVALID - some log',
            {
                'error': 'UNEXPECTED_SPARK_ERROR',
                'description': {
                    'error_msg': (
                        '2021-09-30 12:26:15,883 - INVALID - some log'
                    ),
                },
            },
        ),
    ],
)
async def test_match_error_log(error_log, expected_result):
    result = await spark_error_poller._match_error_log(error_log)
    result = {
        'error': result.get_error_code(),
        'description': result.get_error_description(),
    }

    assert expected_result == result


@pytest.mark.parametrize(
    'app_driver_id, op_failure_time, error_log_responses,'
    ' expected_fetch_error_call_args, expected_result',
    [
        (
            'id123',
            datetime.datetime(year=2020, month=1, day=1, hour=10, minute=20),
            ['some_log'],
            [
                [
                    'id123',
                    '//home/taxi-crm/production/'
                    'spark/logs/worker_log/2020-01-01',
                ],
            ],
            'some_log',
        ),
        (
            'id123',
            datetime.datetime(year=2020, month=1, day=2, hour=0, minute=20),
            [None, 'some_log'],
            [
                [
                    'id123',
                    '//home/taxi-crm/production/'
                    'spark/logs/worker_log/2020-01-02',
                ],
                [
                    'id123',
                    '//home/taxi-crm/production/'
                    'spark/logs/worker_log/2020-01-01',
                ],
            ],
            'some_log',
        ),
        (
            'id123',
            datetime.datetime(year=2020, month=1, day=2, hour=23, minute=40),
            [None, 'some_log'],
            [
                [
                    'id123',
                    '//home/taxi-crm/production/'
                    'spark/logs/worker_log/2020-01-02',
                ],
                [
                    'id123',
                    '//home/taxi-crm/production/'
                    'spark/logs/worker_log/2020-01-03',
                ],
            ],
            'some_log',
        ),
        (
            'id123',
            datetime.datetime(year=2020, month=1, day=2, hour=23, minute=40),
            [None, None],
            [
                [
                    'id123',
                    '//home/taxi-crm/production/'
                    'spark/logs/worker_log/2020-01-02',
                ],
                [
                    'id123',
                    '//home/taxi-crm/production/'
                    'spark/logs/worker_log/2020-01-03',
                ],
            ],
            None,
        ),
    ],
)
async def test_poll_operation_error_log(
        stq3_context,
        patch,
        app_driver_id,
        op_failure_time,
        error_log_responses,
        expected_fetch_error_call_args,
        expected_result,
):
    iter_responses = iter(error_log_responses)
    fetch_error_call_args = []

    @patch('crm_admin.utils.spark.spark_error_poller._fetch_error')
    async def _fetch_error(context, app_driver_id, yt_table_path):
        fetch_error_call_args.append([app_driver_id, yt_table_path])
        return next(iter_responses)

    result = await spark_error_poller._poll_operation_error_log(
        context=stq3_context,
        app_driver_id=app_driver_id,
        operation_failure_time_utc=op_failure_time,
    )

    assert expected_fetch_error_call_args == fetch_error_call_args
    assert expected_result == result


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_collect_operation_fail_details(stq3_context, patch):

    db_campaign = campaign_adapters.DbCampaign(stq3_context)

    some_error_log = 'some_error'

    @patch('crm_admin.utils.spark.spark_error_poller._fetch_error')
    async def _fetch_error(context, app_driver_id, yt_table_path):
        return some_error_log

    campaign = await db_campaign.fetch(campaign_id=1)
    assert campaign.error_code == 'POLLING_SPARK_LOG'
    assert not campaign.error_description

    # normal case, should update
    task_info = async_worker_ng.TaskInfo(
        id='whatever', exec_tries=0, reschedule_counter=0, queue='whatever',
    )
    await spark_error_poller.collect_operation_fail_details(
        context=stq3_context,
        task_info=task_info,
        campaign_id=1,
        operation_id=1,
    )

    campaign = await db_campaign.fetch(campaign_id=1)
    assert campaign.error_code == 'UNEXPECTED_SPARK_ERROR'
    assert campaign.error_description == {'error_msg': some_error_log}

    # campaign state changed/unexpected, should do nothing
    task_info = async_worker_ng.TaskInfo(
        id='whatever', exec_tries=0, reschedule_counter=0, queue='whatever',
    )
    await spark_error_poller.collect_operation_fail_details(
        context=stq3_context,
        task_info=task_info,
        campaign_id=2,
        operation_id=2,
    )

    campaign = await db_campaign.fetch(campaign_id=2)
    assert campaign.error_code == 'POLLING_SPARK_LOG'
    assert not campaign.error_description
