import datetime

import pytest

from logs_from_yt.generated.cron import run_cron


@pytest.mark.now('2019-08-07T11:00:00')
async def test_do_stuff(patch):
    @patch('logs_from_yt.crontasks.stat_collector._send_to_graphite')
    async def _send_to_graphite(*args, **kwargs):
        pass

    await run_cron.main(['logs_from_yt.crontasks.stat_collector', '-t', '0'])

    args = {call['args'] for call in _send_to_graphite.calls}
    assert ('cancelled_count', 1, datetime.datetime(2019, 8, 5)) in args
    assert ('count', 4, datetime.datetime(2019, 8, 7)) in args
    assert (
        'current_queued_count',
        2,
        datetime.datetime(2019, 8, 7, 11),
    ) in args
    assert (
        'current_started_count',
        1,
        datetime.datetime(2019, 8, 7, 11),
    ) in args
    assert ('day_count', 2, datetime.datetime(2019, 8, 7, 8)) in args
    assert ('failed_count', 1, datetime.datetime(2019, 8, 7)) in args
    assert ('finished_count', 1, datetime.datetime(2019, 8, 6)) in args
    assert ('logs_age', 4969860.0, datetime.datetime(2019, 8, 5, 8, 1)) in args
    assert ('failed_count', 1, datetime.datetime(2019, 8, 7)) in args
    assert ('request_range', 3600, datetime.datetime(2019, 8, 5, 8, 1)) in args
    assert ('service_count', 2, datetime.datetime(2019, 8, 7, 8)) in args
    assert ('table_count', 4, datetime.datetime(2019, 8, 7, 8)) in args
    assert ('task_duration', 4800, datetime.datetime(2019, 8, 6, 8)) in args
    assert ('yql_op_duration', 3600, datetime.datetime(2019, 8, 6, 8)) in args
