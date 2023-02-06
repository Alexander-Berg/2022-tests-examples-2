import mock
import pytest

from dmp_suite import greenplum as gp
from dmp_suite import datetime_utils as dtu
from dmp_suite.task import args
from dmp_suite.task import cli
from dmp_suite.lock.typed_lock import entities
from dmp_suite.greenplum.task import locks
from test_dmp_suite.greenplum import utils as test_utils



class NonPartitionedTestTable(gp.GPTable):
    __layout__ = test_utils.TestLayout('dummy')

    id = gp.Int()
    value = gp.String()
    value_2 = gp.String()


class PartitionedTestTable(gp.GPTable):
    __layout__ = test_utils.TestLayout('dummy')
    __partition_scale__ = gp.YearPartitionScale('col_dttm', start='2020-01-01')

    id = gp.Int()
    col_dttm = gp.Datetime()
    value = gp.String()
    value_2 = gp.String()


class ListPartitionedTestTable(gp.GPTable):
    __layout__ = test_utils.TestLayout('dummy')
    __partition_scale__ = gp.PartitionList(
        partition_key='value',
        partition_list=[
            gp.ListPartitionItem('one', 1),
            gp.ListPartitionItem('two', 2),
        ],
    )
    id = gp.Int()
    col_dttm = gp.Datetime()
    value = gp.String()
    value_2 = gp.String()


class PartitionedTestTableWithSubpartitions(gp.GPTable):
    __layout__ = test_utils.TestLayout('dummy')
    __partition_scale__ = gp.YearPartitionScale(
        'col_dttm',
        start='2020-01-01',
        end='2022-01-01',
        subpartition=gp.PartitionList(
            partition_key='value',
            partition_list=[
                gp.ListPartitionItem('one', 1),
                gp.ListPartitionItem('two', 2),
            ],
            is_subpartition=True,
        )
    )

    id = gp.Int()
    col_dttm = gp.Datetime()
    value = gp.String()
    value_2 = gp.String()


def test_exclusive_lock_provider():
    provider = locks.GpExclusiveLockProvider(NonPartitionedTestTable)

    task_args = cli.parse_cli_args({}, [])
    requested_locks = provider.locks(task_args)
    assert requested_locks == [
        entities.LockInfo(key='greenplum:dummy_pfxvalue_testing.dummy', mode=entities.LockMode.EXCLUSIVE),
    ]

def test_period_lock_provider_for_non_partitioned_table():
    provider = locks.GpPeriodLockProvider(
        NonPartitionedTestTable,
        period=args.use_arg('period', default=None),
    )

    task_args = cli.parse_cli_args(
        {'period': cli.Period(dtu.Period(start='2020-12-31 23:59:59', end='2021-01-01 00:00:00'))},
        [],
    )
    requested_locks = provider.locks(task_args)
    assert requested_locks == [
        entities.LockInfo(key='greenplum:dummy_pfxvalue_testing.dummy', mode=entities.LockMode.EXCLUSIVE),
    ]


@pytest.mark.parametrize('table, period, expected_locks', [
    (
            PartitionedTestTable,
            None,
            [
                entities.LockInfo(key='greenplum:dummy_pfxvalue_testing.dummy', mode=entities.LockMode.EXCLUSIVE),
            ],
    ),
    (
            PartitionedTestTable,
            dtu.Period(start='2020-12-31 23:59:59.999999', end='2021-01-01 00:00:00'),
            [
                entities.LockInfo(key='greenplum:dummy_pfxvalue_testing.dummy', mode=entities.LockMode.SHARED),
                entities.LockInfo(key='greenplum:dummy_pfxvalue_testing.dummy#2020', mode=entities.LockMode.EXCLUSIVE),
                entities.LockInfo(key='greenplum:dummy_pfxvalue_testing.dummy#2021', mode=entities.LockMode.EXCLUSIVE),
            ],
    ),
    (
            PartitionedTestTable,
            dtu.Period(start='2222-12-31 23:59:59.999999', end='2222-12-31 23:59:59.999999'),
            [
                entities.LockInfo(key='greenplum:dummy_pfxvalue_testing.dummy', mode=entities.LockMode.SHARED),
                entities.LockInfo(key='greenplum:dummy_pfxvalue_testing.dummy#2222', mode=entities.LockMode.EXCLUSIVE),
            ],
    ),
    (
            PartitionedTestTableWithSubpartitions,
            None,
            [
                entities.LockInfo(key='greenplum:dummy_pfxvalue_testing.dummy', mode=entities.LockMode.EXCLUSIVE),
            ],
    ),
    (
            PartitionedTestTableWithSubpartitions,
            dtu.Period(start='2020-12-31 23:59:59.999999', end='2021-01-01 00:00:00'),
            [
                entities.LockInfo(key='greenplum:dummy_pfxvalue_testing.dummy', mode=entities.LockMode.SHARED),
                entities.LockInfo(key='greenplum:dummy_pfxvalue_testing.dummy#2020', mode=entities.LockMode.EXCLUSIVE),
                entities.LockInfo(key='greenplum:dummy_pfxvalue_testing.dummy#2021', mode=entities.LockMode.EXCLUSIVE),
            ],
    ),
    (
            PartitionedTestTableWithSubpartitions,
            dtu.Period(start='2222-12-31 23:59:59.999999', end='2222-12-31 23:59:59.999999'),
            [
                entities.LockInfo(key='greenplum:dummy_pfxvalue_testing.dummy', mode=entities.LockMode.SHARED),
                entities.LockInfo(key='greenplum:dummy_pfxvalue_testing.dummy#2222', mode=entities.LockMode.EXCLUSIVE),
            ],
    ),
    (
            ListPartitionedTestTable,
            None,
            [
                entities.LockInfo(key='greenplum:dummy_pfxvalue_testing.dummy', mode=entities.LockMode.EXCLUSIVE),
            ],
    ),
    (
            ListPartitionedTestTable,
            dtu.Period(start='2020-12-31 23:59:59.999999', end='2021-01-01 00:00:00'),
            [
                entities.LockInfo(key='greenplum:dummy_pfxvalue_testing.dummy', mode=entities.LockMode.EXCLUSIVE),
            ],
    ),
])
def test_period_lock_provider_partitioned_table(table, period, expected_locks):
    provider = locks.GpPeriodLockProvider(
        table,
        period=args.use_arg('period', default=None),
    )

    task_args = cli.parse_cli_args(
        {'period': cli.Period(period)},
        [],
    )
    requested_locks = provider.locks(task_args)
    assert requested_locks == expected_locks
