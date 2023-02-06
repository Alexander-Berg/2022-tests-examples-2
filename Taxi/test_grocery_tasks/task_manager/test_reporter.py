import json

import pytest

from grocery_tasks.task_manager import reporter


class ExampleError(Exception):
    pass


@pytest.mark.parametrize(
    'status, report_short, report_full, need_raise, expected_status',
    [
        (None, None, None, False, reporter.TaskStatus.ok_status.value),
        (
            reporter.TaskStatus.warning.value,
            'report example',
            {'abc': 123},
            False,
            reporter.TaskStatus.warning.value,
        ),
        (None, None, None, True, reporter.TaskStatus.error.value),
    ],
)
async def test_task_reporter(
        cron_context,
        status,
        report_short,
        report_full,
        need_raise,
        expected_status,
):
    async def _get_task_info():
        return await cron_context.pg.grocery_tasks.fetchrow(
            'SELECT * FROM grocery_tasks.history WHERE task_id=\'id\'',
        )

    async def _assert_in_progress():
        task_info = await _get_task_info()
        assert task_info['start_at'] is not None
        assert task_info['end_at'] is None
        assert task_info['status'] == reporter.TaskStatus.in_progress.value

    assert (await _get_task_info()) is None

    task_reporter = reporter.TaskReporter(
        cron_context.pg.grocery_tasks, cron_context.sqlt, 'id', 'name',
    )
    if need_raise:
        with pytest.raises(ExampleError):
            async with task_reporter:
                await _assert_in_progress()
                raise ExampleError
    else:
        async with task_reporter as report_setter:
            await _assert_in_progress()
            report_setter.set_report(
                short=report_short, full=report_full, status=status,
            )

    task_info = await _get_task_info()
    assert task_info['status'] == expected_status
    assert task_info['report_short'] == report_short
    report_full_json = (
        json.dumps(report_full) if report_full is not None else None
    )
    assert task_info['report_full'] == report_full_json
    assert task_info['end_at']
