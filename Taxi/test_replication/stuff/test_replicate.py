# pylint: disable=protected-access
import datetime

from replication import replication_tasks


async def test_replicate(replication_ctx, yt_clients_storage, monkeypatch):
    tasks = []

    class StoringRawReplicationTask(replication_tasks.CronReplicationTask):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            tasks.append(self)

    monkeypatch.setattr(
        replication_tasks, 'CronReplicationTask', StoringRawReplicationTask,
    )

    tasks_to_do = replication_tasks.collect_cron_tasks(
        replication_ctx.rule_keeper,
    )

    class DummyStuffContext:
        data = replication_ctx

    with yt_clients_storage() as all_clients:
        for task_to_do in tasks_to_do:
            for unit in task_to_do.raw_replication_units:
                await unit.state.target.ensure_exists()
            await task_to_do.do_stuff(DummyStuffContext, None)

    expected_replicate_from = {
        'yt-test_rule_bson-hahn': datetime.datetime(2018, 5, 5, 12, 34, 56),
        'yt-test_rule_bson-arni': None,
        'yt-test_rule_struct-arni': datetime.datetime(2018, 1, 1, 0),
    }
    for task in tasks:
        assert len(task.raw_replication_units) == 1
        target_id = task.raw_replication_units[0].target_id
        replicate_from = task._raw_tasks[0].replicate_from
        assert replicate_from == expected_replicate_from[target_id]

    assert all_clients['hahn'].rows_by_ids['test/test_bson'].keys() == {
        b'1',
        b'2',
    }
    assert all_clients['arni'].rows_by_ids['test/test_bson'].keys() == {
        b'to_old',
        b'0',
        b'1',
        b'2',
    }
    assert all_clients['arni'].rows_by_ids['test/test_struct'].keys() == {
        '0',
        '1',
        '2',
    }
