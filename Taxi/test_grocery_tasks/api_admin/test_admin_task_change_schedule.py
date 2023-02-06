import datetime

from dateutil import parser as dateparser
import pytest

from grocery_tasks.task_manager import scheduler

_TASK_NAME = 'autoorder-run_data_copy'
_NOW = datetime.datetime(2020, 4, 13, 12, 40)


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.pgsql('grocery_tasks', files=['pg_schedule.sql'])
@pytest.mark.parametrize(
    'json_request, expected_response',
    [
        (
            {
                'task_name': _TASK_NAME,
                'change_type': 'set_cron_schedule',
                'options': {'cron_schedule': '* * * * *'},
            },
            {
                'task_name': _TASK_NAME,
                'schedule': {
                    'cron_schedule': '* * * * *',
                    'next_scheduled_run': '2020-04-13T15:40:00+03:00',
                },
            },
        ),
        (
            {'task_name': _TASK_NAME, 'change_type': 'unset_cron_schedule'},
            {'task_name': _TASK_NAME, 'schedule': {}},
        ),
        (
            {
                'task_name': _TASK_NAME,
                'change_type': 'set_next_manual_run',
                'options': {'next_manual_run': '2020-04-13T17:43+03:00'},
            },
            {
                'task_name': _TASK_NAME,
                'schedule': {
                    'cron_schedule': '3 4 * * *',
                    'next_scheduled_run': '2020-04-14T04:03:00+03:00',
                    'next_manual_run': '2020-04-13T17:43:00+03:00',
                },
            },
        ),
        (
            {'task_name': _TASK_NAME, 'change_type': 'unset_next_manual_run'},
            {
                'task_name': _TASK_NAME,
                'schedule': {
                    'cron_schedule': '3 4 * * *',
                    'next_scheduled_run': '2020-04-14T04:03:00+03:00',
                },
            },
        ),
        (
            {'task_name': _TASK_NAME, 'change_type': 'run_now'},
            {
                'task_name': _TASK_NAME,
                'schedule': {
                    'cron_schedule': '3 4 * * *',
                    'next_scheduled_run': '2020-04-14T04:03:00+03:00',
                    'next_manual_run': '2020-04-13T15:41:00+03:00',
                },
            },
        ),
    ],
)
async def test_change_schedule(
        web_app_client, cron_context, json_request, expected_response,
):
    response = await web_app_client.post(
        '/admin/v1/task/change_schedule', json=json_request,
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected_response

    schedules = await scheduler.TaskScheduler(
        cron_context.pg.grocery_tasks, cron_context.sqlt,
    ).load((_TASK_NAME,))
    schedule = schedules[_TASK_NAME]

    expected_schedule = expected_response.get('schedule', {})
    assert schedule.cron_schedule == expected_schedule.get('cron_schedule')

    expected_next_manual_run = expected_schedule.get('next_manual_run')
    if expected_next_manual_run is not None:
        assert schedule.next_run == dateparser.parse(expected_next_manual_run)
    else:
        assert schedule.next_run is None
