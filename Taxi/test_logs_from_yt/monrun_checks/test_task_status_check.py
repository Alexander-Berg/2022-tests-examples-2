import pytest

from logs_from_yt.monrun_checks import task_status_check


@pytest.mark.now('2019-08-07T16:00:00.0')
async def test_warn(cron_context):
    result = await task_status_check.run_check(cron_context)
    assert result == (
        '1; Some problems were detected: '
        'processing of task task_1 spent more than 90.0 minutes; '
        'task task_2 is running more than 90.0 minutes; '
        'task task_3 is failed with message error; '
        'task task_4 is in queued status more than 90.0 minutes'
    )


@pytest.mark.now('2019-08-07T20:00:00.0')
async def test_ok(cron_context):
    result = await task_status_check.run_check(cron_context)
    assert result == '0; Check done'
