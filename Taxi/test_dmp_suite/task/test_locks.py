import uuid

import mock
import pytest

from connection import pgaas
from dmp_suite import datetime_utils as dtu
from dmp_suite.lock.typed_lock import lock as typed_lock

from dmp_suite.task import cli
from dmp_suite.task import execution
from dmp_suite.task import locks as typed_locks
from dmp_suite.task import base as base_task
from dmp_suite.lock.typed_lock import entities
from dmp_suite.lock.typed_lock import errors

from test_dmp_suite.task.utils import SimpleTask


def _get_ctl_connection():
    return pgaas.get_pgaas_connection('ctl', writable=True)


def __default_execution_args():
    return execution.ExecutionArgs(
        accident_used=False,
        lock_used=True,
    )


class SharedLockTask(SimpleTask):
    def get_lock_providers(self):
        return [typed_locks.TaskSharedLockProvider(self.name)]


@pytest.mark.parametrize('key, error_cls', [
    ('a', None),
    ('2', None),
    ('a1', None),
    ('a-a-a-1', None),
    ('a_a_a-9', None),
    ('test-name_1', None),
    ('10-test-name_1', None),
    (1, TypeError),
    (None, TypeError),
    ('', ValueError),
])
def test_lock_key_validation(key, error_cls):
    if error_cls:
        with pytest.raises(error_cls):
            typed_locks.TaskExclusiveLockProvider(key).static_locks()
    else:
        typed_locks.TaskExclusiveLockProvider(key).static_locks()


def test_lock_not_given_implicit():
    task = SimpleTask('task_name')

    assert isinstance(task.get_lock(), tuple)
    assert task.get_lock() == ('task_name',)


def test_custom_lock():
    task = SimpleTask('task_name')
    task.set_lock('custom_lock_name')

    assert isinstance(task.get_lock(), tuple)
    assert task.get_lock() == ('custom_lock_name',)


def test_try_set_lock_none():
    task = SimpleTask('task_name')
    try:
        task.set_lock(None)
    except AssertionError:
        pass
    else:
        assert False, 'set_lock должен падать при попытке поставить None'


def test_with_run_standalone_task():
    """
    Тест проверят, что executor не пытается вызвать lock для запука в ExecutionMode.STANDALONE_TASK
    """
    task = SimpleTask('task_name')

    with mock.patch('dmp_suite.lock.typed_lock.lock.TypedBatchLock') as _mock:
        execution.run_task(
            task,
            execution_mode=execution.ExecutionMode.STANDALONE_TASK,
            execution_args=execution.ExecutionArgs(lock_used=False)
        )

        assert _mock.call_count == 0


def test_with_run_graph():
    """
    Тест проверят, что executor не пытается вызвать lock для запука в ExecutionMode.GRAPH
    """
    sub_task = (
        SimpleTask('sub_task')
    )
    root = (
        SimpleTask('root_task')
        .requires(sub_task)
    )

    with mock.patch('dmp_suite.lock.typed_lock.lock.TypedBatchLock') as _mock:
        execution.run_task(
            root,
            execution_mode=execution.ExecutionMode.GRAPH,
            execution_args=execution.ExecutionArgs(lock_used=False)
        )

        assert _mock.call_count == 0


def test_task_lock_keys_are_additive():
    task = SimpleTask('task_name')
    assert task.get_task_lock_keys() == {'task_name'}

    task.set_lock('custom')
    assert task.get_task_lock_keys() == {'task_name', 'custom'}


def test_task_exclusive_lock_provider():
    provider = typed_locks.TaskExclusiveLockProvider('test')
    assert {l for l in provider.static_locks()} == {
        entities.LockInfo(key='task:dmp_suite:test', mode=entities.LockMode.EXCLUSIVE),
    }


def test_task_shared_lock_provider():
    provider = typed_locks.TaskSharedLockProvider('test')
    assert {l for l in provider.static_locks()} == {
        entities.LockInfo(key='task:dmp_suite:test', mode=entities.LockMode.SHARED),
    }


def test_graph_root_lock_provider():
    provider = typed_locks.RootGraphTaskLockProvider('test')
    assert {l for l in provider.static_locks()} == {
        entities.LockInfo(key='graph:root:dmp_suite:test', mode=entities.LockMode.EXCLUSIVE),
    }


def test_global_exclusive_lock_provider():
    provider = typed_locks.GlobalExclusiveLockProvider('test')
    assert {l for l in provider.static_locks()} == {
        entities.LockInfo(key='global:test', mode=entities.LockMode.EXCLUSIVE),
    }


def test_merge_exclusive_with_shared_locks():
    task_args = cli.parse_cli_args({}, [])

    task = SimpleTask('task_name')

    # check initial state
    requested_locks = task.get_execution_locks(task_args)
    assert len(requested_locks) == 1
    assert set(requested_locks) == {
        entities.LockInfo(key='task:dmp_suite:task_name', mode=entities.LockMode.EXCLUSIVE),
    }

    task.set_extra_lock_providers(
        typed_locks.TaskSharedLockProvider('task_name'),
        typed_locks.TaskSharedLockProvider('other_name'),
    )

    # check locks have not changed
    requested_locks = task.get_execution_locks(task_args)
    assert len(requested_locks) == 2
    assert set(requested_locks) == {
        entities.LockInfo(key='task:dmp_suite:task_name', mode=entities.LockMode.EXCLUSIVE),
        entities.LockInfo(key='task:dmp_suite:other_name', mode=entities.LockMode.SHARED),
    }


def test_merge_shared_with_exclusive_locks():
    task_args = cli.parse_cli_args({}, [])

    task = SharedLockTask('task_name')

    # check initial state
    requested_locks = task.get_execution_locks(task_args)
    assert len(requested_locks) == 1
    assert set(requested_locks) == {
        entities.LockInfo(key='task:dmp_suite:task_name', mode=entities.LockMode.SHARED),
    }

    task.set_extra_lock_providers(
        typed_locks.TaskExclusiveLockProvider('task_name'),
        typed_locks.TaskSharedLockProvider('other_name'),
    )

    # check locks have changed from shared to exclusive
    requested_locks = task.get_execution_locks(task_args)
    assert len(requested_locks) == 2
    assert set(requested_locks) == {
        entities.LockInfo(key='task:dmp_suite:task_name', mode=entities.LockMode.EXCLUSIVE),
        entities.LockInfo(key='task:dmp_suite:other_name', mode=entities.LockMode.SHARED),
    }


def test_root_graph_locks():
    # test default
    task = SimpleTask('task_name')
    graph_locks = task.get_graph_execution_locks()
    assert set(graph_locks) == {
        entities.LockInfo(key='graph:root:dmp_suite:task_name', mode=entities.LockMode.EXCLUSIVE),
    }

    # test locks were merged
    task.set_extra_graph_lock_providers(typed_locks.RootGraphTaskLockProvider('task_name'))
    graph_locks = task.get_graph_execution_locks()
    assert set(graph_locks) == {
        entities.LockInfo(key='graph:root:dmp_suite:task_name', mode=entities.LockMode.EXCLUSIVE),
    }

    # test locks were added
    task.set_extra_graph_lock_providers(
        typed_locks.RootGraphTaskLockProvider('other'),
        typed_locks.RootGraphTaskLockProvider('one_more'),
    )
    graph_locks = task.get_graph_execution_locks()
    assert set(graph_locks) == {
        entities.LockInfo(key='graph:root:dmp_suite:task_name', mode=entities.LockMode.EXCLUSIVE),
        entities.LockInfo(key='graph:root:dmp_suite:other', mode=entities.LockMode.EXCLUSIVE),
        entities.LockInfo(key='graph:root:dmp_suite:one_more', mode=entities.LockMode.EXCLUSIVE),
    }


def test_set_lock_adds_root_graph_locks():
    task = SimpleTask('task_name')
    graph_locks = task.get_graph_execution_locks()
    assert set(graph_locks) == {
        entities.LockInfo(key='graph:root:dmp_suite:task_name', mode=entities.LockMode.EXCLUSIVE),
    }

    task.set_lock(('other', 'one_more'))
    graph_locks = task.get_graph_execution_locks()
    assert set(graph_locks) == {
        entities.LockInfo(key='graph:root:dmp_suite:task_name', mode=entities.LockMode.EXCLUSIVE),
        entities.LockInfo(key='graph:root:dmp_suite:other', mode=entities.LockMode.EXCLUSIVE),
        entities.LockInfo(key='graph:root:dmp_suite:one_more', mode=entities.LockMode.EXCLUSIVE),
    }

    task.set_extra_graph_lock_providers(typed_locks.RootGraphTaskLockProvider('and_more'))
    graph_locks = task.get_graph_execution_locks()
    assert set(graph_locks) == {
        entities.LockInfo(key='graph:root:dmp_suite:task_name', mode=entities.LockMode.EXCLUSIVE),
        entities.LockInfo(key='graph:root:dmp_suite:other', mode=entities.LockMode.EXCLUSIVE),
        entities.LockInfo(key='graph:root:dmp_suite:one_more', mode=entities.LockMode.EXCLUSIVE),
        entities.LockInfo(key='graph:root:dmp_suite:and_more', mode=entities.LockMode.EXCLUSIVE),
    }

    task.set_extra_graph_lock_providers(typed_locks.RootGraphTaskLockProvider('other'))
    graph_locks = task.get_graph_execution_locks()
    assert set(graph_locks) == {
        entities.LockInfo(key='graph:root:dmp_suite:task_name', mode=entities.LockMode.EXCLUSIVE),
        entities.LockInfo(key='graph:root:dmp_suite:other', mode=entities.LockMode.EXCLUSIVE),
        entities.LockInfo(key='graph:root:dmp_suite:one_more', mode=entities.LockMode.EXCLUSIVE),
    }


def test_set_extra_graph_lock_providers_raises_error_on_unexpected_type():
    task = SimpleTask('test')

    with pytest.raises(TypeError):
        task.set_extra_graph_lock_providers(typed_locks.TaskSharedLockProvider('other_name'))


@pytest.mark.slow
def test_task_run_skip_on_conflict():
    _unique_name = uuid.uuid4().hex

    class DummyError(Exception):
        pass

    def dummy_work(*args, **kwargs):
        raise DummyError()

    task = base_task.PyTask(
        _unique_name,
        func=dummy_work,
    )

    provider = typed_locks.TaskExclusiveLockProvider(_unique_name)

    conflicted_lock = typed_lock.TypedBatchLock(
        *provider.static_locks(),
        connection_factory=_get_ctl_connection,
    )

    with pytest.raises(execution.TaskProcessExecutionError):
        # check task executed
        execution.run_task(task, execution_args=__default_execution_args())

    with conflicted_lock:
        # check task was not executed
        execution.run_task(task, execution_args=__default_execution_args())


@pytest.mark.slow
def test_graph_task_run_error_on_conflic_with_task_lock():
    _unique_name = uuid.uuid4().hex

    task = base_task.PyTask(
        _unique_name,
        func=lambda *args, **kwargs: None,
    )

    provider = typed_locks.TaskExclusiveLockProvider(_unique_name)

    conflicted_lock = typed_lock.TypedBatchLock(
        *provider.static_locks(),
        connection_factory=_get_ctl_connection,
    )

    with conflicted_lock:
        with pytest.raises(errors.LockConflictError):
            execution.run_task(
                task,
                execution_args=__default_execution_args(),
                execution_mode=execution.ExecutionMode.GRAPH_TASK,
            )


@pytest.mark.slow
def test_graph_run_error_on_conflict_with_graph_lock():
    _unique_name = uuid.uuid4().hex

    child_task = base_task.PyTask(
        _unique_name + '_child',
        func=lambda *args, **kwargs: None,
    )

    task = base_task.PyTask(
        _unique_name,
        func=lambda *args, **kwargs: None,
    ).requires(
        child_task,
    )

    provider = typed_locks.RootGraphTaskLockProvider(_unique_name)

    conflicted_lock = typed_lock.TypedBatchLock(
        *provider.static_locks(),
        connection_factory=_get_ctl_connection,
    )

    execution_args = __default_execution_args()

    # this is required for raising error instead of silent skip (see: _handle_lock_error)
    execution_args.lock_wait_limit = 1
    execution_args.lock_wait_sleep = 0.5

    with conflicted_lock:
        with pytest.raises(errors.LockAcquireTimeoutError):
            execution.run_task(
                task,
                execution_args=execution_args,
                execution_mode=execution.ExecutionMode.GRAPH,
            )


@pytest.mark.slow
def test_task_run_error_on_conflict_with_wait_limit_set():
    _unique_name = uuid.uuid4().hex

    task = base_task.PyTask(
        _unique_name,
        func=lambda *args, **kwargs: None,
    )

    provider = typed_locks.TaskExclusiveLockProvider(_unique_name)

    conflicted_lock = typed_lock.TypedBatchLock(
        *provider.static_locks(),
        connection_factory=_get_ctl_connection,
    )

    with conflicted_lock:
        with pytest.raises(errors.LockAcquireTimeoutError):
            execution.run_task(
                task,
                execution_args=execution.ExecutionArgs(
                    accident_used=False,
                    lock_used=True,
                    lock_wait_limit=2,
                    lock_wait_sleep=1,
                ),
            )


@pytest.mark.slow
def test_task_run_passes_args_to_lock_providers():
    lock_provider_mock = mock.MagicMock()

    class DummyLockProvider(typed_locks.BaseLockProvider):
        locks = lock_provider_mock

    task = base_task.PyTask(
        uuid.uuid4().hex,
        func=lambda *args, **kwargs: None,
    ).set_extra_lock_providers(
        DummyLockProvider(),
    ).arguments(
        period=cli.StartEndDate(dtu.Period(start='2020-01-01', end='2021-01-01')),
    )

    execution.run_task(task, execution_args=__default_execution_args())

    lock_provider_mock.assert_called_once()
    call_period = lock_provider_mock.call_args[0][0].period
    assert call_period == dtu.Period(start='2020-01-01 00:00:00', end='2021-01-01 23:59:59.999999')
