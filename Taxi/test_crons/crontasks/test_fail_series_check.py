import datetime

import pytest

from crons.generated.cron import run_cron


@pytest.mark.config(
    CRON_FAIL_SERIES_SETTINGS=[
        {
            'task_name': 'taxi_strongbox-crontasks-refresh_secrets',
            'startrek_queue': 'TAXIPLATFORM',
            'startrek_component': 'test',
            'fail_series_length': 3,
            'fail_series_duration': 3600,
        },
        {
            'task_name': 'update_parks_balances',
            'startrek_queue': 'TAXIPLATFORM',
            'startrek_component': 'test',
            'fail_series_duration': 3600 * 2,
        },
        {
            'task_name': 'logs_from_yt-crontasks-loader',
            'startrek_queue': 'TAXIPLATFORM',
            'startrek_component': 'test',
            'fail_series_length': 1,
            'fail_series_duration': 3600,
        },
        {
            'task_name': 'logs_from_yt-crontasks-cleaner',
            'startrek_queue': 'TAXIPLATFORM',
            'startrek_component': 'test',
            'fail_series_length': 1,
            'fail_series_duration': 3600,
        },
    ],
)
@pytest.mark.now('2019-08-21T03:00:00')
async def test_fail_series_check(patch, cron_context):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_ticket')
    async def create_ticket(*args, **kwargs):
        return {'key': 'TAXIPLATFORM-1'}

    await run_cron.main(['crons.crontasks.fail_series_check', '-t', '0'])
    kwargs_list = [call['kwargs'] for call in create_ticket.calls]
    assert len(kwargs_list) == 2
    assert {
        'summary': (
            '[cron-fail-series-check] fail series duration of task '
            'taxi_maintenance.stuff.update_parks_balances is more '
            'than threshold'
        ),
        'queue': 'TAXIPLATFORM',
        'description': (
            'List of fail runs:\n'
            '((/dev/cron/taxi_maintenance.stuff.update_parks_balances?logId=12'
            ' 12)) 2019-08-21T05:00:00+0300\n'
            '((/dev/cron/taxi_maintenance.stuff.update_parks_balances?logId=11'
            ' 11)) 2019-08-21T00:00:00+0300'
        ),
        'custom_fields': {'components': ['test']},
    } in kwargs_list
    assert {
        'summary': (
            '[cron-fail-series-check] fail series length of task '
            'taxi_strongbox-crontasks-refresh_secrets is more '
            'than threshold'
        ),
        'queue': 'TAXIPLATFORM',
        'description': (
            'List of fail runs:\n'
            '((/dev/cron/taxi_strongbox-crontasks-refresh_secrets?logId=4 4)) '
            '2019-08-20T07:00:00+0300\n'
            '((/dev/cron/taxi_strongbox-crontasks-refresh_secrets?logId=3 3)) '
            '2019-08-20T06:00:00+0300\n'
            '((/dev/cron/taxi_strongbox-crontasks-refresh_secrets?logId=2 2)) '
            '2019-08-20T05:00:00+0300'
        ),
        'custom_fields': {'components': ['test']},
    } in kwargs_list
    monitor_docs = (
        await cron_context.mongo_wrapper.primary.cron_monitor.find().to_list(
            None,
        )
    )
    monitor_docs_by_id = {
        monitor_doc['_id']: monitor_doc for monitor_doc in monitor_docs
    }
    assert (
        monitor_docs_by_id['taxi_maintenance.stuff.update_parks_balances'][
            'fail_series_check'
        ]['first_fail_series_task_id']
        == '11'
    )
    assert monitor_docs_by_id['taxi_maintenance.stuff.update_parks_balances'][
        'fail_series_check'
    ]['last_finished_task_time'] == datetime.datetime(2019, 8, 20, 20, 0)
    assert (
        monitor_docs_by_id['taxi_strongbox-crontasks-refresh_secrets'][
            'fail_series_check'
        ]['first_fail_series_task_id']
        == '2'
    )
    assert monitor_docs_by_id['taxi_strongbox-crontasks-refresh_secrets'][
        'fail_series_check'
    ]['last_finished_task_time'] == datetime.datetime(2019, 8, 20, 7, 0)
    assert (
        monitor_docs_by_id['logs_from_yt-crontasks-loader'][
            'fail_series_check'
        ]['first_fail_series_task_id']
        == '13'
    )
    assert monitor_docs_by_id['logs_from_yt-crontasks-loader'][
        'fail_series_check'
    ]['last_finished_task_time'] == datetime.datetime(2019, 8, 21, 3, 0)
