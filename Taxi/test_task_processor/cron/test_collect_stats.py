import pytest

from task_processor.generated.cron import run_cron

CRON_RUN_PARAMS = ['task_processor.crontasks.collect_stats', '-t', '0']


def sensor_to_dict(sensor):
    return {'value': sensor.value, 'labels': sensor.labels}


async def test_collect_no_data(mock_stats):
    await run_cron.main(CRON_RUN_PARAMS)
    assert not mock_stats


@pytest.mark.pgsql('task_processor', files=['test_data.sql'])
async def test_collect_with_data(mock_stats):
    await run_cron.main(CRON_RUN_PARAMS)
    assert len(mock_stats) == 11
    assert sum(len(x) for x in mock_stats) == 13
    assert (
        sorted(
            [sensor_to_dict(x) for sensors in mock_stats for x in sensors],
            key=lambda x: (
                x['labels'].get('job', x['labels'].get('task')),
                x['value'],
            ),
        )
        == [
            {
                'value': 1.0,
                'labels': {
                    'sensor': 'TaskProcessorTaskRealTime',
                    'task': 'CubeDeploy2',
                },
            },
            {
                'value': 1.0,
                'labels': {
                    'sensor': 'TaskProcessorTaskRealTime',
                    'task': 'CubeDeploy2',
                },
            },
            {
                'value': 1.0,
                'labels': {
                    'sensor': 'TaskProcessorTaskTotalTime',
                    'task': 'CubeDeploy2',
                },
            },
            {
                'value': 1.0,
                'labels': {
                    'sensor': 'TaskProcessorTaskTotalTime',
                    'task': 'CubeDeploy2',
                },
            },
            {
                'value': 300.0,
                'labels': {
                    'sensor': 'TaskProcessorTaskDuration',
                    'task': 'CubeDeploy2',
                    'status': 'success',
                },
            },
            {
                'value': 360.0,
                'labels': {
                    'sensor': 'TaskProcessorTaskDuration',
                    'task': 'CubeDeploy2',
                    'status': 'failed',
                },
            },
            {
                'value': 1.0,
                'labels': {
                    'job': 'job1',
                    'sensor': 'TaskProcessorJobRealTime',
                },
            },
            {
                'value': 1.0,
                'labels': {
                    'job': 'job1',
                    'sensor': 'TaskProcessorJobTotalTime',
                },
            },
            {
                'value': 60.0,
                'labels': {
                    'sensor': 'TaskProcessorJobDuration',
                    'job': 'job1',
                    'status': 'success',
                },
            },
            {
                'value': 1.0,
                'labels': {
                    'job': 'job2',
                    'sensor': 'TaskProcessorJobRealTime',
                },
            },
            {
                'value': 1.0,
                'labels': {
                    'job': 'job2',
                    'sensor': 'TaskProcessorJobTotalTime',
                },
            },
            {
                'value': 60.0,
                'labels': {
                    'sensor': 'TaskProcessorJobDuration',
                    'job': 'job2',
                    'status': 'failed',
                },
            },
            {
                'value': 1.0,
                'labels': {'sensor': 'TaskProcessorActiveJob', 'job': 'job3'},
            },
        ]
    )
