import collections

import pytest

from stq import config
from stq.server.dbhandlers import handler


def test_setup_dbhandler_methods_ok(monkeypatch):
    DummyExchange = collections.namedtuple('DummyExchange', ['identifier'])
    dbh_config = config.DBHandlerConfig(
        max_tasks=10, max_execution_time=10, min_poll_interval=0.5)
    dbh = handler.DBHandler(
        DummyExchange('id'), 'node_id', 'fake_path', None, None, dbh_config,
    )

    calls = collections.defaultdict(list)

    class DummyModule(object):
        @staticmethod
        def init(common_params, local_params):
            return 'connection'

        @staticmethod
        def mark_done(connection, node_id, task_id, exec_time):
            calls['mark_done'].append(
                (connection, node_id, task_id, exec_time),
            )

        @staticmethod
        def mark_failed(connection, node_id, task_id, exec_time, exec_tries):
            calls['mark_failed'].append(
                (connection, node_id, task_id, exec_time, exec_tries),
            )

        @staticmethod
        def free(connection, node_id, task_id):
            calls['free'].append((connection, node_id, task_id))

        @staticmethod
        def prolong(connection, node_id, task_ids):
            calls['prolong'].append((connection, node_id, task_ids))

        @staticmethod
        def take_ready(connection, node_id, max_tasks):
            calls['take_ready'].append((connection, node_id, max_tasks))

    dbh._database_module = DummyModule()
    dbh._setup_dbhandler_methods()
    dbh._mark_done_method(task_id='task_id', exec_time=123)
    dbh._mark_failed_method(
        task_id='task_id', exec_time=123, repeat_time=0.3, exec_tries=2,
    )
    dbh._free_method(task_id='task_id')
    dbh._prolong_method(task_ids=['task_1', 'task_2'])
    dbh._take_ready_method(max_tasks=5)
    assert dbh._max_tasks == 10
    assert dbh._max_execution_time == 10
    assert dbh._min_poll_interval == 0.5

    assert calls['free'] == [('connection', 'node_id', 'task_id')]
    assert calls['mark_done'] == [
        ('connection', 'node_id', 'task_id', 123)]
    assert calls['mark_failed'] == [
        ('connection', 'node_id', 'task_id', 123, 2)]
    assert calls['free'] == [('connection', 'node_id', 'task_id')]
    assert calls['prolong'] == [
        ('connection', 'node_id', ['task_1', 'task_2'])]
    assert calls['take_ready'] == [('connection', 'node_id', 5)]


def test_setup_dbhandler_methods_error(monkeypatch):
    DummyExchange = collections.namedtuple('DummyExchange', ['identifier'])

    dbh_config = config.DBHandlerConfig(
        max_tasks=10, max_execution_time=10, min_poll_interval=0.5)
    dbh = handler.DBHandler(
        DummyExchange('id'), 'node_id', 'fake_path', None, None, dbh_config,
    )

    class DummyModule(object):
        @staticmethod
        def init(common_params, local_params):
            return 'connection'

        @staticmethod
        def mark_done(connection, node_id, task_id, extra_arg):
            pass

        @staticmethod
        def mark_failed(connection, node_id, task_id, exec_tries):
            pass

        @staticmethod
        def free(connection, node_id, task_id):
            pass

        @staticmethod
        def prolong(connection, node_id, task_ids):
            pass

        @staticmethod
        def take_ready(connection, node_id, max_tasks):
            pass

    dbh._database_module = DummyModule()
    with pytest.raises(RuntimeError):
        dbh._setup_dbhandler_methods()
