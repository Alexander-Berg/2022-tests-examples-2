import pytest

from taxi.stq import async_worker_ng

from workforce_management.common import constants
from workforce_management.stq import periodic_jobs


@pytest.mark.pgsql(
    'workforce_management',
    files=[
        'simple_operators.sql',
        'simple_shifts.sql',
        'simple_actual_states.sql',
    ],
)
async def test_base(stq_runner, stq, stq3_context, get_stats_by_label_values):
    await stq_runner.workforce_management_periodic_jobs.call(
        task_id='shift_violations_stats', args=(), kwargs={},
    )
    assert stq.workforce_management_periodic_jobs.times_called

    task_id = constants.PeriodicJobTypes.shift_violations_stats.value
    task_info = async_worker_ng.TaskInfo(
        task_id, 0, 0, queue=constants.StqQueueNames.periodic_jobs.value,
    )
    await periodic_jobs.task(stq3_context, task_info)
    stats = get_stats_by_label_values(
        stq3_context,
        {'sensor': 'violations.current', 'violation_type': 'total'},
    )
    assert stats[0]['value'] == 1
