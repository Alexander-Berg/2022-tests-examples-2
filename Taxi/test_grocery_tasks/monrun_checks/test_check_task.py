# pylint: disable=protected-access
from typing import Dict

import pytest

from taxi.util import monrun

from grocery_tasks.crontasks import scheduled_crontasks
from grocery_tasks.generated.web import run_monrun
from grocery_tasks.monrun_checks import check_task


def _make_insert_query(
        *,
        task_id='100',
        start_at,
        end_at='null',
        status='in_progress',
        report_short='null',
):
    if end_at != 'null':
        end_at = f'{end_at!r}'
    if report_short != 'null':
        report_short = f'{report_short!r}'
    return f"""
        INSERT INTO grocery_tasks.history
            (task_id, task_name, start_at, end_at, status, report_short)
        VALUES
            ({task_id}, 'autoorder-run_calc',
             {start_at!r}, {end_at}, {status!r}, {report_short});
    """


def _modulate_report_message(explicit_task_reports: Dict[str, dict]) -> str:
    task_reports = []
    status = monrun.LEVEL_NORMAL
    for task_name in scheduled_crontasks.AUTOORDER_TASKS:
        task_status = monrun.LEVEL_NORMAL
        task_report = check_task.TaskReport(
            name=task_name,
            status=task_status,
            message=f'Task {task_name}: '
            'not found any launches in the last 129600 seconds',
        )
        if task_name in explicit_task_reports.keys():
            task_status = explicit_task_reports[task_name]['status']
            message = explicit_task_reports[task_name]['message'].format(
                task_name=task_name,
            )
            task_report = check_task.TaskReport(
                name=task_name, status=task_status, message=message,
            )

        status = max(status, task_status)
        task_reports.append(task_report)

    expected_message = check_task._create_monrun_message(task_reports)

    return f'{status}; {expected_message}'


@pytest.mark.now('2020-04-14T07:06:00+03:00')
@pytest.mark.parametrize(
    'explicit_task_reports',
    [
        pytest.param({}),
        pytest.param(
            {
                'autoorder-run_calc': {
                    'status': monrun.LEVEL_NORMAL,
                    'message': (
                        'Task {task_name} in progress: '
                        'last start at 2020-04-14 07:04, duration=2 min'
                    ),
                },
            },
            marks=pytest.mark.pgsql(
                'grocery_tasks',
                queries=[
                    _make_insert_query(
                        task_id='99',
                        start_at='2020-04-14T03:02:00+03:00',
                        end_at='2020-04-14T03:10:00+03:00',
                        status='error',
                    ),
                    _make_insert_query(start_at='2020-04-14T07:04:00+03:00'),
                ],
            ),
        ),
        pytest.param(
            {
                'autoorder-run_calc': {
                    'status': monrun.LEVEL_NORMAL,
                    'message': (
                        'Task {task_name} finished: '
                        'last start at 2020-04-14 07:04, end at 2020-04-14 07:20, '  # noqa: E501
                        'duration=16 min'
                    ),
                },
            },
            marks=pytest.mark.pgsql(
                'grocery_tasks',
                queries=[
                    _make_insert_query(
                        start_at='2020-04-14T07:04:00+03:00',
                        end_at='2020-04-14T07:20:00+03:00',
                        status='ok',
                    ),
                ],
            ),
        ),
        pytest.param(
            {
                'autoorder-run_calc': {
                    'status': monrun.LEVEL_CRITICAL,
                    'message': (
                        'Task {task_name} failed: '
                        'last start at 2020-04-14 07:04, end at 2020-04-14 07:20, '  # noqa: E501
                        'duration=16 min, see '
                        'https://tariff-editor.taxi.tst.yandex-team.ru/dev/cron/'  # noqa: E501
                        'grocery_tasks-autoorder-run_calc?logId=100'
                    ),
                },
            },
            marks=pytest.mark.pgsql(
                'grocery_tasks',
                queries=[
                    _make_insert_query(
                        start_at='2020-04-14T07:04:00+03:00',
                        end_at='2020-04-14T07:20:00+03:00',
                        status='error',
                    ),
                ],
            ),
        ),
        pytest.param(
            {
                'autoorder-run_calc': {
                    'status': monrun.LEVEL_NORMAL,
                    'message': (
                        'Task {task_name} failed: '
                        'last start at 2020-04-14 06:04, end at 2020-04-14 06:05, '  # noqa: E501
                        'duration=1 min, status forced into OK after 60 min'
                    ),
                },
            },
            marks=pytest.mark.pgsql(
                'grocery_tasks',
                queries=[
                    _make_insert_query(
                        start_at='2020-04-14T06:04:00+03:00',
                        end_at='2020-04-14T06:05:00+03:00',
                        status='error',
                    ),
                ],
            ),
        ),
        pytest.param(
            {
                'autoorder-run_calc': {
                    'status': monrun.LEVEL_NORMAL,
                    'message': (
                        'Task {task_name} finished: '
                        'last start at 2020-04-14 07:04, end at 2020-04-14 07:20, '  # noqa: E501
                        'duration=16 min, short warning'
                    ),
                },
            },
            marks=pytest.mark.pgsql(
                'grocery_tasks',
                queries=[
                    _make_insert_query(
                        start_at='2020-04-14T07:04:00+03:00',
                        end_at='2020-04-14T07:20:00+03:00',
                        status='warning',
                        report_short='short warning',
                    ),
                ],
            ),
        ),
    ],
)
async def test_check_task(explicit_task_reports):
    msg = await run_monrun.run(
        ['grocery_tasks.monrun_checks.check_task', 'AUTOORDER_TASKS'],
    )

    expected_msg = _modulate_report_message(explicit_task_reports)

    assert msg == expected_msg
