from dmp_suite import datetime_utils as dtu
from dmp_suite.task import args
from dmp_suite.task import cli
from dmp_suite.lock.typed_lock import entities
from dmp_suite.yt.task import locks
from dmp_suite.yt import table


class NonPartitionedTestTable(table.YTTable):
    __layout__ = table.NotLayeredYtLayout('test', 'test')
    __location_cls__ = table.NotLayeredYtLocation

    a = table.Int()
    b = table.String()
    c = table.Any()


class PartitionedTestTable(table.YTTable):
    __layout__ = table.NotLayeredYtLayout('test', 'test')
    __location_cls__ = table.NotLayeredYtLocation
    __partition_scale__ = table.YearPartitionScale(partition_key='p')

    p = table.Datetime()
    a = table.Int()
    b = table.String()
    c = table.Any()


def test_exclusive_lock_provider():
    provider = locks.YtExclusiveLockProvider(NonPartitionedTestTable)

    task_args = cli.parse_cli_args({}, [])
    requested_locks = provider.locks(task_args)
    assert requested_locks == [entities.LockInfo(key='yt:hahn://dummy/test/test', mode=entities.LockMode.EXCLUSIVE)]


def test_lock_non_partitioned_table_wo_period():
    provider = locks.YtPeriodLockProvider(NonPartitionedTestTable, None)

    task_args = cli.parse_cli_args({}, [])
    requested_locks = provider.locks(task_args)
    assert requested_locks == [entities.LockInfo(key='yt:hahn://dummy/test/test', mode=entities.LockMode.EXCLUSIVE)]


def test_lock_non_partitioned_table_with_period():
    provider = locks.YtPeriodLockProvider(
        NonPartitionedTestTable,
        period=dtu.Period(start='2020-01-01 00:00:00', end='2020-12-31 23:59:59')
    )

    # no period in args
    task_args = cli.parse_cli_args({}, [])
    requested_locks = provider.locks(task_args)
    assert requested_locks == [entities.LockInfo(key='yt:hahn://dummy/test/test', mode=entities.LockMode.EXCLUSIVE)]

    # period in args has no effect
    task_args = cli.parse_cli_args(
        {'period': cli.Period(dtu.Period(start='2020-01-01 00:00:00', end='2020-12-31 23:59:59'))},
       [],
    )
    requested_locks = provider.locks(task_args)
    assert requested_locks == [entities.LockInfo(key='yt:hahn://dummy/test/test', mode=entities.LockMode.EXCLUSIVE)]


def test_lock_partitioned_table_wo_period():
    provider = locks.YtPeriodLockProvider(PartitionedTestTable, None)

    task_args = cli.parse_cli_args({}, [])
    requested_locks = provider.locks(task_args)
    assert requested_locks == [entities.LockInfo(key='yt:hahn://dummy/test/test', mode=entities.LockMode.EXCLUSIVE)]


def test_lock_partitioned_table_with_static_period():
    provider = locks.YtPeriodLockProvider(
        PartitionedTestTable,
        period=dtu.Period(start='2020-01-01 00:00:00', end='2020-12-31 23:59:59')
    )

    # no period in args
    task_args = cli.parse_cli_args({}, [])
    requested_locks = provider.locks(task_args)
    assert requested_locks == [
        entities.LockInfo(key='yt:hahn://dummy/test/test', mode=entities.LockMode.SHARED),
        entities.LockInfo(key='yt:hahn://dummy/test/test/2020-01-01', mode=entities.LockMode.EXCLUSIVE),
    ]

    # period in args has no effect
    task_args = cli.parse_cli_args(
        {'period': cli.Period(dtu.Period(start='2021-01-01 00:00:00', end='2021-12-31 23:59:59'))},
       [],
    )
    requested_locks = provider.locks(task_args)
    assert requested_locks == [
        entities.LockInfo(key='yt:hahn://dummy/test/test', mode=entities.LockMode.SHARED),
        entities.LockInfo(key='yt:hahn://dummy/test/test/2020-01-01', mode=entities.LockMode.EXCLUSIVE),
    ]


def test_lock_partitioned_table_with_period():
    provider = locks.YtPeriodLockProvider(
        PartitionedTestTable,
        period=args.use_arg('period', default=None),
    )

    # no period in args
    task_args = cli.parse_cli_args({}, [])
    requested_locks = provider.locks(task_args)
    assert requested_locks == [
        entities.LockInfo(key='yt:hahn://dummy/test/test', mode=entities.LockMode.EXCLUSIVE),
    ]

    # with period in args
    task_args = cli.parse_cli_args(
        {'period': cli.Period(dtu.Period(start='2020-05-01 00:00:00', end='2020-11-11 23:59:59'))},
       [],
    )
    requested_locks = provider.locks(task_args)
    assert requested_locks == [
        entities.LockInfo(key='yt:hahn://dummy/test/test', mode=entities.LockMode.SHARED),
        entities.LockInfo(key='yt:hahn://dummy/test/test/2020-01-01', mode=entities.LockMode.EXCLUSIVE),
    ]


def test_lock_partitioned_table_on_partition_edges():
    provider = locks.YtPeriodLockProvider(
        PartitionedTestTable,
        period=args.use_arg('period', default=None),
    )

    task_args = cli.parse_cli_args(
        {'period': cli.Period(dtu.Period(start='2020-12-31 23:59:59', end='2021-01-01 00:00:00'))},
        [],
    )
    requested_locks = provider.locks(task_args)
    assert requested_locks == [
        entities.LockInfo(key='yt:hahn://dummy/test/test', mode=entities.LockMode.SHARED),
        entities.LockInfo(key='yt:hahn://dummy/test/test/2020-01-01', mode=entities.LockMode.EXCLUSIVE),
        entities.LockInfo(key='yt:hahn://dummy/test/test/2021-01-01', mode=entities.LockMode.EXCLUSIVE),
    ]


def test_lock_partitioned_table_with_non_period_type_arg():
    provider = locks.YtPeriodLockProvider(
        PartitionedTestTable,
        period=args.use_arg('period', default=None),
    )

    task_args = cli.parse_cli_args(
        {'period': cli.DisjointedPeriods([dtu.Period(start='2020-12-31 23:59:59', end='2021-01-01 00:00:00')])},
        [],
    )
    requested_locks = provider.locks(task_args)
    assert requested_locks == [
        entities.LockInfo(key='yt:hahn://dummy/test/test', mode=entities.LockMode.EXCLUSIVE),
    ]
