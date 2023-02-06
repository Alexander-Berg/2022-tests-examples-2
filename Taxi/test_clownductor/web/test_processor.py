import pytest

from clownductor.internal.tasks import processor


@pytest.mark.config(
    CLOWNDUCTOR_TASK_PROCESSOR_JOBS_QOS={
        'enabled': False,
        'default_job': {'priority': 1000, 'at_most_amount': 3},
        'jobs': [
            {
                'priority': 10000,
                'at_most_amount': 2,
                'names': ['LowJob1', 'LowJob2', 'LowJob3'],
            },
            {'priority': 10, 'names': ['HighJob1', 'HighJob2']},
        ],
    },
)
@pytest.mark.pgsql('clownductor', files=['test_task_data.sql'])
# pylint: disable=protected-access
async def test_old_processor_tasks(web_context):
    qos_config = processor._qos_from_raw_config(
        web_context.config.CLOWNDUCTOR_TASK_PROCESSOR_JOBS_QOS,
    )
    tasks = await processor._get_ready_tasks_ids(web_context, qos_config)
    assert set(tasks) == set(range(3, 18))


@pytest.mark.config(
    CLOWNDUCTOR_TASK_PROCESSOR_JOBS_QOS={
        'enabled': True,
        'default_job': {'priority': 1000, 'at_most_amount': 3},
        'jobs': [
            {
                'priority': 10000,
                'at_most_amount': 2,
                'names': ['LowJob1', 'LowJob2', 'LowJob3'],
            },
            {'priority': 10, 'names': ['HighJob1', 'HighJob2']},
        ],
    },
)
@pytest.mark.pgsql('clownductor', files=['test_task_data.sql'])
# pylint: disable=protected-access
async def test_processor_tasks(web_context):
    qos_config = processor._qos_from_raw_config(
        web_context.config.CLOWNDUCTOR_TASK_PROCESSOR_JOBS_QOS,
    )
    tasks = await processor._get_ready_tasks_ids(web_context, qos_config)
    high_tasks = 5
    low_tasks = 2
    default_tasks = 3
    assert len(tasks) == low_tasks + default_tasks + high_tasks
    high_group = set(tasks[:high_tasks])
    default_group = set(tasks[high_tasks : high_tasks + default_tasks])
    low_group = set(tasks[high_tasks + default_tasks :])
    expected_high_group = set(range(3, 8))
    expected_default_group = set(range(8, 13))
    expected_low_group = set(range(13, 18))

    assert high_group == expected_high_group
    assert len(expected_default_group - default_group) == 2
    assert len(expected_low_group - low_group) == 3
