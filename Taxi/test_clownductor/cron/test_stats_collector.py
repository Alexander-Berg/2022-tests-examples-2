# pylint: disable=protected-access, redefined-outer-name

import pytest

from clownductor.generated.cron import run_cron


def sensor_to_dict(sensor):
    return {'value': sensor.value, 'labels': sensor.labels}


async def test_collect_no_data(mock_stats):
    await run_cron.main(['clownductor.crontasks.stats_collector', '-t', '0'])
    assert not mock_stats


@pytest.mark.pgsql('clownductor', files=['test_data.sql'])
async def test_collect_with_data(mock_stats):
    await run_cron.main(['clownductor.crontasks.stats_collector', '-t', '0'])
    assert len(mock_stats) == 9
    assert sum(len(x) for x in mock_stats) == 9
    assert [sensor_to_dict(x) for senors in mock_stats for x in senors] == [
        {
            'value': 60.0,
            'labels': {
                'sensor': 'jobs.run_timings',
                'job': 'job1',
                'status': 'success',
            },
        },
        {
            'labels': {'job': 'job1', 'sensor': 'ClownductorJobRealTime'},
            'value': 1.0,
        },
        {
            'labels': {'job': 'job1', 'sensor': 'ClownductorJobTotalTime'},
            'value': 1.0,
        },
        {
            'value': 40.0,
            'labels': {
                'sensor': 'tasks.run_timings',
                'task': 'task2',
                'status': 'success',
            },
        },
        {
            'value': 1.0,
            'labels': {'sensor': 'ClownductorTaskRealTime', 'task': 'task2'},
        },
        {
            'value': 1.0,
            'labels': {'sensor': 'ClownductorTaskTotalTime', 'task': 'task2'},
        },
        {
            'value': 60.0,
            'labels': {
                'sensor': 'tasks.run_timings',
                'task': 'task1',
                'status': 'success',
            },
        },
        {
            'value': 1.0,
            'labels': {'sensor': 'ClownductorTaskRealTime', 'task': 'task1'},
        },
        {
            'value': 1.0,
            'labels': {'sensor': 'ClownductorTaskTotalTime', 'task': 'task1'},
        },
    ]
