import pytest

from stq_agent_py3.generated.cron import run_cron


@pytest.mark.fillstqdb(collections=[('stq', 'dbstq', 'example_queue')])
@pytest.mark.parametrize(
    'queue_name,dead_letter',
    [
        ('remove_fails_num', False),
        ('dead_letter_fails_num', True),
        ('remove_fails_duration', False),
        ('dead_letter_fails_duration', True),
    ],
)
@pytest.mark.now('2022-02-22 19:00:00')
async def test_dead_tasks_remove_failed_num(
        mockserver, stq_db, cron_context, queue_name, dead_letter,
):
    await cron_context.mongo.stq_config.delete_many(
        {'_id': {'$ne': f'{queue_name}_queue'}},
    )

    await cron_context.mongo.stq_dead_tasks.insert(
        {
            '_id': f'{queue_name}_queue/task_to_remove_2',
            'task': {
                '_id': 'task_to_remove_2',
                'e': 16725225600,
                'f': 6,
                'ff': 1645545540,
                'x': None,
            },
            'queue': f'{queue_name}_queue',
            'reported_at': 2022,
            'cleaned_at': 0,
        },
    )

    await run_cron.main(['stq_agent_py3.crontasks.cleanup_dead_tasks'])

    for shard in stq_db.iter_shards():
        tasks_not_to_remove = await shard.find().to_list(None)
        assert len(tasks_not_to_remove) == 2
        for task_not_to_remove in tasks_not_to_remove:
            assert task_not_to_remove['_id'].startswith('task_not_to_remove')

    tasks_to_remove = await cron_context.mongo.stq_dead_tasks.find().to_list(
        None,
    )

    if dead_letter:
        assert len(tasks_to_remove) == 2
        for task_to_remove in tasks_to_remove:
            assert task_to_remove['_id'].startswith(
                f'{queue_name}_queue/task_to_remove',
            )
            assert 'reported_at' not in task_to_remove
            assert task_to_remove['cleaned_at'] != 0
    else:
        assert len(tasks_to_remove) == 1
        assert tasks_to_remove[0]['cleaned_at'] == 0
        assert 'reported_at' in tasks_to_remove[0]
