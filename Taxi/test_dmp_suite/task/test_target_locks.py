from dmp_suite.lock.typed_lock import entities
from dmp_suite.task import cli
from dmp_suite.task import base as base_task
from dmp_suite.yt import table
from dmp_suite.yt.task import target as yt_task_target


class DummyTestTable(table.YTTable):
    __layout__ = table.NotLayeredYtLayout('test', 'test')
    __location_cls__ = table.NotLayeredYtLocation


class DummyTaskTarget(base_task.AbstractTaskTarget):
    @property
    def ctl_entity(self):
        return None


def test_task_gets_exclusive_lock_for_empty_targets():
    task = base_task.PyTask(
        'dummy',
        func=lambda *args, **kwargs: None,
        targets=[],
    )

    task_args = cli.parse_cli_args({}, [])
    assert {l for l in task.get_execution_locks(task_args)} == {
        entities.LockInfo(key='task:dmp_suite:dummy', mode=entities.LockMode.EXCLUSIVE),
    }


def test_task_locks_for_targets():
    task = base_task.PyTask(
        'dummy',
        func=lambda *args, **kwargs: None,
        targets=[
            yt_task_target.YtTaskTarget(DummyTestTable),
        ],
    ).set_lock('test')

    task_args = cli.parse_cli_args({}, [])
    requested_locks = task.get_execution_locks(task_args)

    assert len(requested_locks) == 3

    assert set(requested_locks) == {
        entities.LockInfo(key='task:dmp_suite:dummy', mode=entities.LockMode.EXCLUSIVE),
        entities.LockInfo(key='task:dmp_suite:test', mode=entities.LockMode.EXCLUSIVE),
        entities.LockInfo(key='yt:hahn://dummy/test/test', mode=entities.LockMode.EXCLUSIVE),
    }
