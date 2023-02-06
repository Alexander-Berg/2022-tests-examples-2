import uuid

from datetime import datetime
import pytest

from connection import greenplum as gp
from dmp_suite.greenplum import (
    Date, GPMeta, Int, MonthPartitionScale, String, Datetime, GPTable,
)
from dmp_suite.greenplum.connection import EtlConnection
from dmp_suite.greenplum.task import validators
from dmp_suite.greenplum import transformations
from dmp_suite.greenplum.transformations import sources
from dmp_suite.greenplum.transformations import exceptions
from dmp_suite.datetime_utils import period
from test_dmp_suite.greenplum.utils import TestLayout


class TestTable(GPTable):
    __layout__ = TestLayout(name='partitioned_table')
    id = Int(key=True)
    value = String()
    dt = Date()


class PartitionedTestTable(GPTable):
    __layout__ = TestLayout(name='partitioned_table')
    __partition_scale__ = MonthPartitionScale(partition_key='dt',
                                              start=datetime(2019, 1, 1),
                                              end=datetime(2019, 4, 1))

    id = Int(key=True)
    dt = Date()
    value = String()


class PartitionedDatetimeTestTable(GPTable):
    __layout__ = TestLayout(name='partitioned_dt_table')
    __partition_scale__ = MonthPartitionScale(partition_key='dttm',
                                              start=datetime(2019, 1, 1, 0, 0, 0),
                                              end=datetime(2019, 4, 1, 0, 0, 0))

    id = Int(key=True)
    dttm = Datetime()
    value = String()


class TestSCD2Table(GPTable):
    __layout__ = TestLayout(name='test_scd2_table')
    id = Int(key=True)
    value = String()
    dt = Date()
    valid_from_dttm = Datetime()
    valid_to_dttm = Datetime()


class TestSCD2TableManyId(GPTable):
    __layout__ = TestLayout(name='test_scd2_table_many_id')
    id1 = Int(key=True)
    id2 = Int(key=True)
    value = String()
    dt = Date()
    valid_from_dttm = Datetime()
    valid_to_dttm = Datetime()


class PartitionedDatetimeTestSCD2Table(GPTable):
    __layout__ = TestLayout(name='partitioned_scd2_table')
    __partition_scale__ = MonthPartitionScale(partition_key='dt',
                                              start=datetime(2019, 1, 1),
                                              end=datetime(2019, 4, 1))
    id = Int(key=True)
    value = String()
    dt = Date()
    valid_from_dttm = Datetime()
    valid_to_dttm = Datetime()


@pytest.mark.slow('gp')
@pytest.mark.parametrize('table', [TestTable, PartitionedTestTable])
def test_snapshot(table):
    sql = """create temp table result_table on commit drop as
    (select 1 as id, 'aaa' as value, '2019-01-01'::date as dt)
    """

    transformations.SnapshotTransformation(
        sources.SqlSource.from_string(sql),
        table,
        gp.connection
    ).run()

    expected = [dict(id=1, value='aaa', dt=datetime(2019, 1, 1).date())]
    actual = [dict(row) for row in gp.connection.select_all(table)]

    assert expected == actual


@pytest.mark.slow('gp')
@pytest.mark.parametrize('table', [
    TestTable,
    PartitionedTestTable
])
def test_delete_insert(table):
    old_data = [
        dict(id=1, value='a', dt=datetime(2019, 1, 1).date()),
        dict(id=2, value='b', dt=datetime(2019, 3, 1).date())
    ]

    gp.connection.create_table(table)
    gp.connection.insert(table, old_data)

    increment_data = [
        dict(id=2, value='c', dt=datetime(2019, 3, 1).date()),
        dict(id=3, value='d', dt=datetime(2019, 1, 2).date())
    ]

    stg = gp.connection.create_stg_table(table, add_unique_table_name_suffix=True)

    gp.connection.insert(stg, increment_data)

    transformations.DeleteInsertTransformation(
        sources.TableSource(stg),
        table,
        gp.connection
    ).run()

    expected = [
        dict(id=1, value='a', dt=datetime(2019, 1, 1).date()),
        dict(id=2, value='c', dt=datetime(2019, 3, 1).date()),
        dict(id=3, value='d', dt=datetime(2019, 1, 2).date())
    ]
    expected = sorted(expected, key=lambda d: d['id'])

    actual = [dict(row) for row in gp.connection.select_all(table)]
    actual = sorted(actual, key=lambda d: d['id'])

    assert expected == actual


@pytest.mark.slow('gp')
@pytest.mark.parametrize('table', [
    TestTable,
    PartitionedTestTable
])
def test_replace_by_key(table):
    old_data = [
        dict(id=1, value='a', dt=datetime(2019, 1, 1).date()),
        dict(id=2, value='b', dt=datetime(2019, 3, 1).date())
    ]

    gp.connection.create_table(table)
    gp.connection.insert(table, old_data)

    sql = """
    create temp table result_table on commit drop as
    select 2 as id, 'c' as value, '2019-01-01'::date as dt
    union all
    select 3 as id, 'd' as value, '2019-01-02'::date as dt
    """

    source = sources.SqlSource.from_string(sql)
    trns = transformations.replace_by_key_transformation(source, table, gp.connection)

    if GPMeta(table).partition_scale is None:
        trns = trns.with_partition_key('dt')

    trns.run()

    expected = [
        dict(id=2, value='b', dt=datetime(2019, 3, 1).date()),
        dict(id=2, value='c', dt=datetime(2019, 1, 1).date()),
        dict(id=3, value='d', dt=datetime(2019, 1, 2).date())
    ]
    expected = sorted(expected, key=lambda d: str(d['id']) + str(d['dt']))

    actual = [dict(row) for row in gp.connection.select_all(table)]
    actual = sorted(actual, key=lambda d: str(d['id']) + str(d['dt']))

    assert expected == actual


@pytest.mark.slow('gp')
@pytest.mark.parametrize('table', [
    TestTable,
    PartitionedTestTable
])
def test_period_snapshot_date(table):
    old_data = [
        dict(id=1, value='a', dt=datetime(2019, 1, 1).date()),
        dict(id=2, value='b', dt=datetime(2019, 3, 1).date())
    ]

    gp.connection.create_table(table)
    gp.connection.insert(table, old_data)

    sql = '''create temp table result_table on commit drop as
    select 2 as id, 'c' as value, '2019-03-01'::date as dt
    union all
    select 3 as id, 'd' as value, '2019-03-02'::date as dt
    '''

    source = sources.SqlSource.from_string(sql)
    trns = transformations.PeriodSnapshotTransformation(
        source,
        table,
        gp.connection
    ).set_period(
        period('2019-03-01', '2019-03-15')
    )

    if GPMeta(table).partition_scale is None:
        trns = trns.with_column_name('dt')

    trns.run()

    expected = [
        dict(id=1, value='a', dt=datetime(2019, 1, 1).date()),
        dict(id=2, value='c', dt=datetime(2019, 3, 1).date()),
        dict(id=3, value='d', dt=datetime(2019, 3, 2).date())
    ]
    expected = sorted(expected, key=lambda d: str(d['id']) + str(d['dt']))

    actual = [dict(row) for row in gp.connection.select_all(table)]
    actual = sorted(actual, key=lambda d: str(d['id']) + str(d['dt']))

    assert expected == actual


@pytest.mark.slow('gp')
@pytest.mark.parametrize('table', [
    PartitionedDatetimeTestTable
])
def test_period_snapshot_datetime(table):
    old_data = [
        dict(id=1, value='a', dttm=datetime(2019, 1, 1, 12, 00, 00)),
        dict(id=2, value='b', dttm=datetime(2019, 3, 1, 15, 24, 11)),
        dict(id=3, value='c', dttm=datetime(2019, 3, 1, 15, 00, 54))
    ]

    gp.connection.create_table(table)
    gp.connection.insert(table, old_data)

    sql = """
    create temp table result_table on commit drop as
    select 2 as id, 'c' as value, '2019-03-01 19:11:11'::TIMESTAMP WITHOUT TIME ZONE as dttm
    union all
    select 3 as id, 'd' as value, '2019-03-02 16:25:35'::TIMESTAMP WITHOUT TIME ZONE as dttm
    """

    source = sources.SqlSource.from_string(sql)
    trns = transformations.PeriodSnapshotTransformation(
        source,
        table,
        gp.connection
    ).set_period(
        period('2019-03-01 15:10:00', '2019-03-15 00:00:00')
    )

    if GPMeta(table).partition_scale is None:
        trns = trns.with_column_name('dttm')

    trns.run()

    expected = [
        dict(id=1, value='a', dttm=datetime(2019, 1, 1, 12, 00, 00)),
        dict(id=2, value='c', dttm=datetime(2019, 3, 1, 19, 11, 11)),
        dict(id=3, value='c', dttm=datetime(2019, 3, 1, 15, 00, 54)),
        dict(id=3, value='d', dttm=datetime(2019, 3, 2, 16, 25, 35))
    ]
    expected = sorted(expected, key=lambda d: str(d['id']) + str(d['dttm']))

    actual = [dict(row) for row in gp.connection.select_all(table)]
    actual = sorted(actual, key=lambda d: str(d['id']) + str(d['dttm']))

    assert expected == actual



@pytest.mark.slow('gp')
@pytest.mark.parametrize('table', [
    TestTable,
    PartitionedTestTable])
def test_append_transformation(table):
    random_tmp_table = 'result_table_' + str(uuid.uuid4())[:8]
    sql = f'''create temp table {random_tmp_table} on commit drop as
    select 1 as id, 'aaa' as value, '2019-01-01'::date as dt'''

    source = sources.SqlSource.from_string(sql, result_table=random_tmp_table)
    transformations.AppendTransformation(source, table).run()

    expected = [dict(id=1, value='aaa', dt=datetime(2019, 1, 1).date())]
    actual = [dict(row) for row in gp.connection.select_all(table)]

    assert actual == expected

    # Запуск трансформации по второму разу должен привести к увеличению вдвое
    # числа строк к результирующей табличке.
    transformations.AppendTransformation(source, table).run()

    expected = [
        dict(id=1, value='aaa', dt=datetime(2019, 1, 1).date()),
        dict(id=1, value='aaa', dt=datetime(2019, 1, 1).date()),
    ]
    actual = [dict(row) for row in gp.connection.select_all(table)]

    assert actual == expected


@pytest.mark.slow('gp')
@pytest.mark.parametrize('cls, source_is_empty, raise_on_empty_source', [
    (transformations.SnapshotTransformation, False, False),
    (transformations.SnapshotTransformation, False, True),
    (transformations.SnapshotTransformation, True, False),
    (transformations.SnapshotTransformation, True, True),
    (transformations.DeleteInsertTransformation, False, False),
    (transformations.DeleteInsertTransformation, False, True),
    (transformations.DeleteInsertTransformation, True, False),
    (transformations.DeleteInsertTransformation, True, True),
    (transformations.replace_by_key_transformation, False, False),
    (transformations.replace_by_key_transformation, False, True),
    (transformations.replace_by_key_transformation, True, False),
    (transformations.replace_by_key_transformation, True, True),
])
def test_raise_on_empty_source_parameter(cls, source_is_empty, raise_on_empty_source):
    table = PartitionedTestTable
    data = [
        dict(id=1, value='a', dt=datetime(2019, 1, 1).date()),
        dict(id=2, value='b', dt=datetime(2019, 3, 1).date()),
    ]

    stg = gp.connection.create_stg_table(table)
    if not source_is_empty:
        gp.connection.insert(stg, data)
    trns = cls(sources.TableSource(stg), table, gp.connection, raise_on_empty_source=raise_on_empty_source)

    if source_is_empty and raise_on_empty_source:
        with pytest.raises(exceptions.EmptySource):
            trns.run()
    else:
        trns.run()


source_validation_duplicate = validators.validate_empty(
    query="""
            select id, count(*)
            from {result_table}
            group by 1
            having count(*) > 1
            limit 1
        """,
    message_pattern='Duplicate 1',
)


class DummyValidator(validators.Validator):
    def validate(self, connection: EtlConnection, result_table: str):
        pass


source_validation_dummy = DummyValidator()


@pytest.mark.slow('gp')
@pytest.mark.parametrize('cls, source_validation, is_error', [
    (transformations.SnapshotTransformation, None, False),
    (transformations.SnapshotTransformation, source_validation_duplicate, True),
    (transformations.SnapshotTransformation, source_validation_dummy, False),
    (transformations.DeleteInsertTransformation, None, False),
    (transformations.DeleteInsertTransformation, source_validation_duplicate, True),
    (transformations.DeleteInsertTransformation, source_validation_dummy, False),
    (transformations.replace_by_key_transformation, None, False),
    (transformations.replace_by_key_transformation, source_validation_duplicate, True),
    (transformations.replace_by_key_transformation, source_validation_dummy, False),
    (transformations.PeriodSnapshotTransformation, None, False),
    (transformations.PeriodSnapshotTransformation, source_validation_duplicate, True),
    (transformations.PeriodSnapshotTransformation, source_validation_dummy, False),
])
def test_source_validation_parameter(cls, source_validation, is_error):
    table = PartitionedTestTable

    random_tmp_table = 'result_table_' + str(uuid.uuid4())[:8]
    sql = f'''
        create temp table {random_tmp_table} on commit drop as
        (
            select 1::int as id, 'aaa'::varchar as value, '2019-01-01'::date as dt
            union all
            select 1::int as id, 'aaa'::varchar as value, '2019-01-01'::date as dt
        )
    '''

    gp.connection.create_table(table)

    trns = cls(
        sources.SqlSource.from_string(sql, result_table=random_tmp_table),
        table, gp.connection,
        source_validation=source_validation
    )

    if cls == transformations.PeriodSnapshotTransformation:
        trns.set_period(period('2019-01-01 00:00:00', '2019-01-01 23:59:59'))

    if is_error:
        with pytest.raises(ValueError):
            trns.run()
    else:
        trns.run()


@pytest.mark.slow('gp')
@pytest.mark.parametrize('table', [
    TestSCD2Table
])
def test_scd2(table):
    old_data = [
        dict(id=1, value='a', dt=datetime(2018, 10, 10).date(), valid_from_dttm=datetime(2019, 1, 1, 11, 24, 30),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
        dict(id=2, value='b', dt=datetime(2019, 3, 1).date(), valid_from_dttm=datetime(2019, 3, 2, 18, 51, 29),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
    ]

    gp.connection.create_table(table)
    gp.connection.insert(table, old_data)

    sql = """
    CREATE TEMPORARY TABLE result_table ON COMMIT DROP AS
    SELECT 1 AS id, 'b'::VARCHAR AS value, '2018-10-10'::DATE AS dt,
           '2019-01-01 14:22:31'::TIMESTAMP WITHOUT TIME ZONE AS valid_from_dttm
    UNION ALL
    SELECT 1 AS id, 'b'::VARCHAR AS value, '2019-01-21'::DATE AS dt,
           '2019-01-22 11:01:54'::TIMESTAMP WITHOUT TIME ZONE AS valid_from_dttm
    UNION ALL
    SELECT 2 AS id, 'a'::VARCHAR AS value, '2019-03-01'::DATE AS dt,
           '2019-03-02 18:51:29'::TIMESTAMP WITHOUT TIME ZONE AS valid_from_dttm
    UNION ALL
    SELECT 2 AS id, 'b'::VARCHAR AS value, '2019-03-05'::DATE AS dt,
           '2019-04-01 08:32:22'::TIMESTAMP WITHOUT TIME ZONE AS valid_from_dttm
    UNION ALL
    SELECT 2 AS id, 'c'::VARCHAR AS value, '2019-03-05'::DATE AS dt,
           '2019-04-04 15:22:51'::TIMESTAMP WITHOUT TIME ZONE AS valid_from_dttm
    UNION ALL
    SELECT 2 AS id, 'c'::VARCHAR AS value, '2019-03-05'::DATE AS dt,
           '2019-04-09 11:11:31'::TIMESTAMP WITHOUT TIME ZONE AS valid_from_dttm
    """

    source = sources.SqlSource.from_string(sql)
    trns = transformations.SCD2Transformation(
        source,
        table,
        valid_from_column='valid_from_dttm',
        valid_to_column='valid_to_dttm',
        connection=gp.connection,
        append_only=False
    )
    trns.run()

    expected = [
        dict(id=1, value='a', dt=datetime(2018, 10, 10).date(), valid_from_dttm=datetime(2019, 1, 1, 11, 24, 30),
             valid_to_dttm=datetime(2019, 1, 1, 14, 22, 30)),
        dict(id=1, value='b', dt=datetime(2018, 10, 10).date(), valid_from_dttm=datetime(2019, 1, 1, 14, 22, 31),
             valid_to_dttm=datetime(2019, 1, 22, 11, 1, 53)),
        dict(id=1, value='b', dt=datetime(2019, 1, 21).date(), valid_from_dttm=datetime(2019, 1, 22, 11, 1, 54),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
        dict(id=2, value='a', dt=datetime(2019, 3, 1).date(), valid_from_dttm=datetime(2019, 3, 2, 18, 51, 29),
             valid_to_dttm=datetime(2019, 4, 1, 8, 32, 21)),
        dict(id=2, value='b', dt=datetime(2019, 3, 5).date(), valid_from_dttm=datetime(2019, 4, 1, 8, 32, 22),
             valid_to_dttm=datetime(2019, 4, 4, 15, 22, 50)),
        dict(id=2, value='c', dt=datetime(2019, 3, 5).date(), valid_from_dttm=datetime(2019, 4, 4, 15, 22, 51),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
    ]
    expected = sorted(expected, key=lambda d: str(d['id']) + str(d['valid_from_dttm']))

    actual = [dict(row) for row in gp.connection.select_all(table)]
    actual = sorted(actual, key=lambda d: str(d['id']) + str(d['valid_from_dttm']))

    assert expected == actual


@pytest.mark.slow('gp')
@pytest.mark.parametrize('table', [
    PartitionedDatetimeTestSCD2Table
])
def test_scd2_partitioned(table):
    old_data = [
        dict(id=1, value='a', dt=datetime(2019, 2, 10).date(), valid_from_dttm=datetime(2019, 1, 1, 11, 24, 30),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
        dict(id=2, value='b', dt=datetime(2019, 3, 15).date(), valid_from_dttm=datetime(2019, 3, 2, 18, 51, 29),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
        dict(id=3, value='a', dt=datetime(2019, 1, 2).date(), valid_from_dttm=datetime(2019, 3, 2, 18, 51, 29),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
    ]

    gp.connection.create_table(table)
    gp.connection.insert(table, old_data)

    sql = """
    CREATE TEMPORARY TABLE result_table ON COMMIT DROP AS
    SELECT 1 AS id, 'b'::VARCHAR AS value, '2019-02-10'::DATE AS dt,
           '2019-01-01 14:22:31'::TIMESTAMP WITHOUT TIME ZONE AS valid_from_dttm
    UNION ALL
    SELECT 2 AS id, 'a'::VARCHAR AS value, '2019-02-10'::DATE AS dt,
           '2019-03-02 18:51:29'::TIMESTAMP WITHOUT TIME ZONE AS valid_from_dttm
    UNION ALL
    SELECT 2 AS id, 'b'::VARCHAR AS value, '2019-02-10'::DATE AS dt,
           '2019-04-01 08:32:22'::TIMESTAMP WITHOUT TIME ZONE AS valid_from_dttm
    UNION ALL
    SELECT 2 AS id, 'c'::VARCHAR AS value, '2019-02-10'::DATE AS dt,
           '2019-04-04 15:22:51'::TIMESTAMP WITHOUT TIME ZONE AS valid_from_dttm
    UNION ALL
    SELECT 2 AS id, 'c'::VARCHAR AS value, '2019-02-10'::DATE AS dt,
           '2019-04-09 11:11:31'::TIMESTAMP WITHOUT TIME ZONE AS valid_from_dttm
    UNION ALL
    SELECT 3 AS id, 'b'::VARCHAR AS value, '2019-02-10'::DATE AS dt,
           '2019-03-20 14:18:21'::TIMESTAMP WITHOUT TIME ZONE AS valid_from_dttm
    """

    source = sources.SqlSource.from_string(sql)
    trns = transformations.SCD2Transformation(
        source,
        table,
        valid_from_column='valid_from_dttm',
        valid_to_column='valid_to_dttm',
        connection=gp.connection,
        append_only=False
    ).with_partition_key('dt')
    trns.run()

    expected = [
        dict(id=1, value='a', dt=datetime(2019, 2, 10).date(), valid_from_dttm=datetime(2019, 1, 1, 11, 24, 30),
             valid_to_dttm=datetime(2019, 1, 1, 14, 22, 30)),
        dict(id=1, value='b', dt=datetime(2019, 2, 10).date(), valid_from_dttm=datetime(2019, 1, 1, 14, 22, 31),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
        dict(id=2, value='b', dt=datetime(2019, 3, 15).date(), valid_from_dttm=datetime(2019, 3, 2, 18, 51, 29),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
        dict(id=2, value='a', dt=datetime(2019, 2, 10).date(), valid_from_dttm=datetime(2019, 3, 2, 18, 51, 29),
             valid_to_dttm=datetime(2019, 4, 1, 8, 32, 21)),
        dict(id=2, value='b', dt=datetime(2019, 2, 10).date(), valid_from_dttm=datetime(2019, 4, 1, 8, 32, 22),
             valid_to_dttm=datetime(2019, 4, 4, 15, 22, 50)),
        dict(id=2, value='c', dt=datetime(2019, 2, 10).date(), valid_from_dttm=datetime(2019, 4, 4, 15, 22, 51),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
        # Ошибки с id=3 нет. Так работает, когда backfill=False. Все из-за фильтра по партициям - см. описание лоадера
        dict(id=3, value='a', dt=datetime(2019, 1, 2).date(), valid_from_dttm=datetime(2019, 3, 2, 18, 51, 29),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
        dict(id=3, value='b', dt=datetime(2019, 2, 10).date(), valid_from_dttm=datetime(2019, 3, 20, 14, 18, 21),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
    ]
    expected = sorted(expected, key=lambda d: str(d['id']) + str(d['dt']) + str(d['valid_from_dttm']))

    actual = [dict(row) for row in gp.connection.select_all(table)]
    actual = sorted(actual, key=lambda d: str(d['id']) + str(d['dt']) + str(d['valid_from_dttm']))

    assert expected == actual


@pytest.mark.slow('gp')
@pytest.mark.parametrize('table', [
    PartitionedDatetimeTestSCD2Table
])
def test_scd2_partitioned_with_backfill(table):
    old_data = [
        dict(id=1, value='a', dt=datetime(2019, 2, 10).date(), valid_from_dttm=datetime(2019, 1, 1, 11, 24, 30),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
        dict(id=3, value='a', dt=datetime(2019, 1, 2).date(), valid_from_dttm=datetime(2019, 3, 2, 18, 51, 29),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
    ]

    gp.connection.create_table(table)
    gp.connection.insert(table, old_data)

    sql = """
    CREATE TEMPORARY TABLE result_table ON COMMIT DROP AS
    SELECT 1 AS id, 'b'::VARCHAR AS value, '2019-02-10'::DATE AS dt,
           '2019-01-01 14:22:31'::TIMESTAMP WITHOUT TIME ZONE AS valid_from_dttm
    UNION ALL
    SELECT 3 AS id, 'b'::VARCHAR AS value, '2019-02-10'::DATE AS dt,
           '2019-03-20 14:18:21'::TIMESTAMP WITHOUT TIME ZONE AS valid_from_dttm
    """

    source = sources.SqlSource.from_string(sql)
    trns = transformations.SCD2Transformation(
        source,
        table,
        valid_from_column='valid_from_dttm',
        valid_to_column='valid_to_dttm',
        connection=gp.connection,
        append_only=False,
        backfill=True
    ).with_partition_key('dt')
    trns.run()

    expected = [
        dict(id=1, value='a', dt=datetime(2019, 2, 10).date(), valid_from_dttm=datetime(2019, 1, 1, 11, 24, 30),
             valid_to_dttm=datetime(2019, 1, 1, 14, 22, 30)),
        dict(id=1, value='b', dt=datetime(2019, 2, 10).date(), valid_from_dttm=datetime(2019, 1, 1, 14, 22, 31),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
        dict(id=3, value='a', dt=datetime(2019, 1, 2).date(), valid_from_dttm=datetime(2019, 3, 2, 18, 51, 29),
             valid_to_dttm=datetime(2019, 3, 20, 14, 18, 20)),
        dict(id=3, value='b', dt=datetime(2019, 2, 10).date(), valid_from_dttm=datetime(2019, 3, 20, 14, 18, 21),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
    ]
    expected = sorted(expected, key=lambda d: str(d['id']) + str(d['dt']) + str(d['valid_from_dttm']))

    actual = [dict(row) for row in gp.connection.select_all(table)]
    actual = sorted(actual, key=lambda d: str(d['id']) + str(d['dt']) + str(d['valid_from_dttm']))

    assert expected == actual


@pytest.mark.slow('gp')
@pytest.mark.parametrize('table', [
    TestSCD2Table
])
def test_scd2_append_only(table):
    old_data = [
        dict(id=1, value='a', dt=datetime(2018, 10, 10).date(), valid_from_dttm=datetime(2019, 1, 1, 11, 24, 30),
             valid_to_dttm=datetime(2019, 2, 2, 22, 44, 10)),
        dict(id=1, value='b', dt=datetime(2018, 10, 10).date(), valid_from_dttm=datetime(2019, 2, 2, 22, 44, 11),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
        dict(id=2, value='a', dt=datetime(2019, 3, 1).date(), valid_from_dttm=datetime(2019, 3, 2, 18, 51, 29),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
    ]

    gp.connection.create_table(table)
    gp.connection.insert(table, old_data)

    sql = """
        CREATE TEMPORARY TABLE result_table ON COMMIT DROP AS
        SELECT 1 AS id, 'c'::VARCHAR AS value, '2018-10-10'::DATE AS dt,
               '2019-03-01 14:22:31'::TIMESTAMP WITHOUT TIME ZONE AS valid_from_dttm
        UNION ALL
        SELECT 2 AS id, 'b'::VARCHAR AS value, '2019-03-01'::DATE AS dt,
               '2019-04-09 11:11:31'::TIMESTAMP WITHOUT TIME ZONE AS valid_from_dttm
        """

    source = sources.SqlSource.from_string(sql)
    trns = transformations.SCD2Transformation(
        source,
        table,
        valid_from_column='valid_from_dttm',
        valid_to_column='valid_to_dttm',
        connection=gp.connection,
        append_only=True
    )
    trns.run()

    expected = [
        dict(id=1, value='a', dt=datetime(2018, 10, 10).date(), valid_from_dttm=datetime(2019, 1, 1, 11, 24, 30),
             valid_to_dttm=datetime(2019, 2, 2, 22, 44, 10)),
        dict(id=1, value='b', dt=datetime(2018, 10, 10).date(), valid_from_dttm=datetime(2019, 2, 2, 22, 44, 11),
             valid_to_dttm=datetime(2019, 3, 1, 14, 22, 30)),
        dict(id=1, value='c', dt=datetime(2018, 10, 10).date(), valid_from_dttm=datetime(2019, 3, 1, 14, 22, 31),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
        dict(id=2, value='a', dt=datetime(2019, 3, 1).date(), valid_from_dttm=datetime(2019, 3, 2, 18, 51, 29),
             valid_to_dttm=datetime(2019, 4, 9, 11, 11, 30)),
        dict(id=2, value='b', dt=datetime(2019, 3, 1).date(), valid_from_dttm=datetime(2019, 4, 9, 11, 11, 31),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
    ]

    expected = sorted(expected, key=lambda d: str(d['id']) + str(d['valid_from_dttm']))

    actual = [dict(row) for row in gp.connection.select_all(table)]
    actual = sorted(actual, key=lambda d: str(d['id']) + str(d['valid_from_dttm']))

    assert expected == actual


@pytest.mark.slow('gp')
@pytest.mark.parametrize('table', [
    TestSCD2TableManyId
])
def test_scd2_close_window(table):
    old_data = [
        dict(id1=1, id2=11, value='a', dt=datetime(2018, 10, 10).date(), valid_from_dttm=datetime(2019, 1, 1, 11, 24, 30),
             valid_to_dttm=datetime(2019, 2, 2, 22, 44, 10)),
        dict(id1=1, id2=11, value='b', dt=datetime(2018, 10, 10).date(), valid_from_dttm=datetime(2019, 2, 2, 22, 44, 11),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
        dict(id1=2, id2=12, value='a', dt=datetime(2019, 3, 1).date(), valid_from_dttm=datetime(2019, 3, 2, 18, 51, 29),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
        dict(id1=3, id2=13, value='x', dt=datetime(2019, 3, 2).date(), valid_from_dttm=datetime(2019, 3, 3, 11, 54, 19),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
        dict(id1=4, id2=14, value='y', dt=datetime(2019, 3, 3).date(), valid_from_dttm=datetime(2019, 3, 4, 9, 22, 45),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
    ]

    gp.connection.create_table(table)
    gp.connection.insert(table, old_data)

    sql = """
        CREATE TEMPORARY TABLE result_table ON COMMIT DROP AS
        SELECT 1 AS id1, 11 AS id2, 'c'::VARCHAR AS value, '2018-10-10'::DATE AS dt,
               '2019-03-01 14:22:31'::TIMESTAMP WITHOUT TIME ZONE AS valid_from_dttm
        UNION ALL
        SELECT 2 AS id1, 12 AS id2, 'b'::VARCHAR AS value, '2019-03-01'::DATE AS dt,
               '2019-04-09 11:11:31'::TIMESTAMP WITHOUT TIME ZONE AS valid_from_dttm
        """

    source = sources.SqlSource.from_string(sql)
    with gp.connection.transaction():
        trns = transformations.SCD2Transformation(
            source,
            table,
            valid_from_column='valid_from_dttm',
            valid_to_column='valid_to_dttm',
            connection=gp.connection,
            append_only=True,
            close_window=True
        )
        trns.run()
        with gp.connection.cursor() as cur:
            cur.execute('SELECT now()::TIMESTAMP WITHOUT TIME ZONE;')
            res = cur.fetchone()

    expected = [
        dict(id1=1, id2=11, value='a', dt=datetime(2018, 10, 10).date(), valid_from_dttm=datetime(2019, 1, 1, 11, 24, 30),
             valid_to_dttm=datetime(2019, 2, 2, 22, 44, 10)),
        dict(id1=1, id2=11, value='b', dt=datetime(2018, 10, 10).date(), valid_from_dttm=datetime(2019, 2, 2, 22, 44, 11),
             valid_to_dttm=datetime(2019, 3, 1, 14, 22, 30)),
        dict(id1=1, id2=11, value='c', dt=datetime(2018, 10, 10).date(), valid_from_dttm=datetime(2019, 3, 1, 14, 22, 31),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
        dict(id1=2, id2=12, value='a', dt=datetime(2019, 3, 1).date(), valid_from_dttm=datetime(2019, 3, 2, 18, 51, 29),
             valid_to_dttm=datetime(2019, 4, 9, 11, 11, 30)),
        dict(id1=2, id2=12, value='b', dt=datetime(2019, 3, 1).date(), valid_from_dttm=datetime(2019, 4, 9, 11, 11, 31),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
        dict(id1=3, id2=13, value='x', dt=datetime(2019, 3, 2).date(), valid_from_dttm=datetime(2019, 3, 3, 11, 54, 19),
             valid_to_dttm=res[0]),
        dict(id1=4, id2=14, value='y', dt=datetime(2019, 3, 3).date(), valid_from_dttm=datetime(2019, 3, 4, 9, 22, 45),
             valid_to_dttm=res[0])
    ]

    expected = sorted(expected, key=lambda d: str(d['id1']) + str(d['id2']) + str(d['valid_from_dttm']))

    actual = [dict(row) for row in gp.connection.select_all(table)]
    actual = sorted(actual, key=lambda d: str(d['id1']) + str(d['id2']) + str(d['valid_from_dttm']))

    assert expected == actual


@pytest.mark.slow('gp')
@pytest.mark.parametrize('table', [
    PartitionedDatetimeTestSCD2Table
])
def test_scd2_append_only_partitioned(table):
    old_data = [
        dict(id=1, value='a', dt=datetime(2019, 2, 10).date(), valid_from_dttm=datetime(2019, 1, 1, 11, 24, 30),
             valid_to_dttm=datetime(2019, 2, 2, 22, 44, 10)),
        dict(id=1, value='b', dt=datetime(2019, 2, 10).date(), valid_from_dttm=datetime(2019, 2, 2, 22, 44, 11),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
        dict(id=2, value='a', dt=datetime(2019, 3, 1).date(), valid_from_dttm=datetime(2019, 3, 2, 18, 51, 29),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
    ]

    gp.connection.create_table(table)
    gp.connection.insert(table, old_data)

    sql = """
        CREATE TEMPORARY TABLE result_table ON COMMIT DROP AS
        SELECT 1 AS id, 'c'::VARCHAR AS value, '2019-03-01'::DATE AS dt,
               '2019-03-01 14:22:31'::TIMESTAMP WITHOUT TIME ZONE AS valid_from_dttm
        UNION ALL
        SELECT 2 AS id, 'b'::VARCHAR AS value, '2019-03-01'::DATE AS dt,
               '2019-04-09 11:11:31'::TIMESTAMP WITHOUT TIME ZONE AS valid_from_dttm
        """

    source = sources.SqlSource.from_string(sql)
    trns = transformations.SCD2Transformation(
        source,
        table,
        valid_from_column='valid_from_dttm',
        valid_to_column='valid_to_dttm',
        connection=gp.connection,
        append_only=True
    ).with_partition_key('dt')
    trns.run()

    expected = [
        dict(id=1, value='a', dt=datetime(2019, 2, 10).date(), valid_from_dttm=datetime(2019, 1, 1, 11, 24, 30),
             valid_to_dttm=datetime(2019, 2, 2, 22, 44, 10)),
        dict(id=1, value='b', dt=datetime(2019, 2, 10).date(), valid_from_dttm=datetime(2019, 2, 2, 22, 44, 11),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
        dict(id=1, value='c', dt=datetime(2019, 3, 1).date(), valid_from_dttm=datetime(2019, 3, 1, 14, 22, 31),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59)),
        dict(id=2, value='a', dt=datetime(2019, 3, 1).date(), valid_from_dttm=datetime(2019, 3, 2, 18, 51, 29),
             valid_to_dttm=datetime(2019, 4, 9, 11, 11, 30)),
        dict(id=2, value='b', dt=datetime(2019, 3, 1).date(), valid_from_dttm=datetime(2019, 4, 9, 11, 11, 31),
             valid_to_dttm=datetime(9999, 12, 31, 23, 59, 59))
    ]

    expected = sorted(expected, key=lambda d: str(d['id']) + str(d['valid_from_dttm']))

    actual = [dict(row) for row in gp.connection.select_all(table)]
    actual = sorted(actual, key=lambda d: str(d['id']) + str(d['valid_from_dttm']))

    assert expected == actual
