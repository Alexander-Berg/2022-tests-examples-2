import datetime

import pytest
import typing as tp

from dmp_suite.greenplum.connection import EtlConnection
from connection import greenplum as gp
from dmp_suite import datetime_utils as dtu, py_env
from dmp_suite.greenplum.table import Tablespace, ColumnStorageParameters, Level, Orientation
from dmp_suite.postgresql.connection import ConnectionWrapperError
from dmp_suite.table import LayeredLayout
from dmp_suite.greenplum import (
    ExternalGPLayout, Int, String, Datetime, Date, Double,
    BigInt, Json, Array, Boolean, Distribution, MonthPartitionScale,
    resolve_meta, GPMeta, BtreeIndex, GPTable,
    RangePartitionItem, MAX_DATETIME_PARTITION, StorageParameters,
    ListPartitionItem, PartitionList, SmallInt, Numeric, Point, Uuid,
)
from test_dmp_suite.greenplum import utils
from test_dmp_suite.greenplum.meta_test import NoKeyTable, KeyTable, MultiKeyTable, WrongTableName


class SchemaTestTable(GPTable):
    __layout__ = LayeredLayout(layer='schema', name='connection_test', prefix_key='test')
    f1 = Int()


class NoDistributionTable(GPTable):
    __layout__ = LayeredLayout(layer='summary', name='connection_test', prefix_key='test')

    f1 = Int()
    f2 = String()
    f3 = String(length=10)
    f4 = Double()
    f5 = BigInt()
    f6 = Array(String)
    f7 = Json()
    f8 = Date()
    f9 = Datetime()
    f10 = Boolean()


class NoPartitionTable(NoDistributionTable):
    __distributed_by__ = Distribution('f1', 'f2')


class PartitionTable(NoPartitionTable):
    __partition_scale__ = MonthPartitionScale('f9')


class MaxDatetimePartitionTable(NoPartitionTable):
    __partition_scale__ = MonthPartitionScale('f9', extra_partitions=[MAX_DATETIME_PARTITION])


class PartitionListTable(NoPartitionTable):
    __partition_scale__ = PartitionList('f1', [ListPartitionItem("one", 1)])


class IndexTable(NoPartitionTable):
    __indexes__ = [BtreeIndex('f1')]


class ListAndRangePartitionTable(NoPartitionTable):
    __partition_scale__ = PartitionList(
        partition_key='f1',
        partition_list=[ListPartitionItem("one", 1), ListPartitionItem("two", 2)],
        subpartition=MonthPartitionScale('f9', start='2021-01-01', end='2021-04-01', is_subpartition=True)
    )


class RangeAndListPartitionTable(NoPartitionTable):
    __partition_scale__ = MonthPartitionScale(
        'f9',
        start='2021-01-01',
        end='2021-04-01',
        subpartition=PartitionList(
            partition_key='f1',
            partition_list=[ListPartitionItem("one", 1), ListPartitionItem("two", 2)],
            is_subpartition=True)
    )


class RangeAndRangePartitionTable(NoPartitionTable):
    __partition_scale__ = MonthPartitionScale(
        'f8',
        start='2021-01-01',
        end='2021-02-01',
        subpartition=MonthPartitionScale('f9', start='2021-01-01', end='2021-04-01', is_subpartition=True)
    )


@pytest.mark.parametrize('random_table', [
    SchemaTestTable,
], indirect=True)
@pytest.mark.slow('gp')
def test_create_exists_drop_schema(random_table):
    with gp.connection.transaction():
        assert not gp.connection.check_table_schema_exists(random_table)

        gp.connection.create_table(random_table)
        assert gp.connection.check_table_schema_exists(random_table)

        gp.connection.drop_table(random_table)
        assert gp.connection.check_table_schema_exists(random_table)

        gp.connection.create_table(random_table)
        assert gp.connection.check_table_schema_exists(random_table)

    with pytest.raises(Exception):
        with gp.connection.transaction():
            gp.connection.drop_schema(random_table)

    with gp.connection.transaction():
        assert gp.connection.check_table_schema_exists(random_table)

        gp.connection.drop_table(random_table)
        gp.connection.drop_schema(random_table)
        assert not gp.connection.check_table_schema_exists(random_table)

        gp.connection.create_table(random_table)
        gp.connection.drop_table(random_table)


@pytest.mark.parametrize('throwaway_table', [
    NoDistributionTable,
    NoPartitionTable,
    PartitionTable,
    IndexTable
], indirect=True)
@pytest.mark.slow('gp')
def test_create_exists_drop(throwaway_table):
    with gp.connection.transaction():
        gp.connection.drop_table(throwaway_table)
        assert not gp.connection.table_exists(throwaway_table)
        assert gp.connection.create_table(throwaway_table).table_class is throwaway_table
        assert gp.connection.table_exists(throwaway_table)
        assert gp.connection.create_table(throwaway_table).table_class is throwaway_table
        gp.connection.drop_table(throwaway_table)
        assert not gp.connection.table_exists(throwaway_table)


@pytest.mark.parametrize('random_table', [
    NoKeyTable,
    KeyTable,
    MultiKeyTable
], indirect=True)
@pytest.mark.slow('gp')
def test_stg_table(random_table):
    with gp.connection.transaction():

        meta = GPMeta(random_table)

        stg_meta = gp.connection.create_stg_table(random_table)
        try:
            assert gp.connection.table_exists(stg_meta)

            assert stg_meta.schema.endswith('stg')
            assert stg_meta.table_name == meta.schema + '_' + meta.table_name
            assert stg_meta.partition_scale is None
            assert stg_meta.storage_parameters == meta.storage_parameters

            if meta.unique_key:
                assert list(sorted(stg_meta.distribution.keys)) == list(sorted(meta.unique_key))
                assert not stg_meta.distribution.is_randomly_distributed
            else:
                assert stg_meta.distribution.is_randomly_distributed
        finally:
            gp.connection.drop_stg_table(stg_meta)
            assert not gp.connection.table_exists(stg_meta)


@pytest.mark.parametrize('random_table', [
    NoKeyTable
], indirect=True)
@pytest.mark.slow('gp')
def test_stg_table_with_suffix(random_table):
    with gp.connection.transaction():
        meta = GPMeta(random_table)

        stg_meta = gp.connection.create_stg_table(meta, add_unique_table_name_suffix=True)
        try:
            assert gp.connection.table_exists(stg_meta)

            assert stg_meta.schema.endswith('stg')
            assert stg_meta.table_name.startswith(meta.schema + '_' + meta.table_name)
            assert len(stg_meta.table_name) > len(meta.schema + '_' + meta.table_name)
        finally:
            gp.connection.drop_stg_table(stg_meta)
            assert not gp.connection.table_exists(stg_meta)


@pytest.mark.parametrize('random_table', [
    WrongTableName
], indirect=True)
@pytest.mark.slow('gp')
def test_raise_stg_table_without_suffix(random_table):
    with gp.connection.transaction():
        meta = GPMeta(random_table)

        with pytest.raises(ValueError) as err:
            gp.connection.create_stg_table(meta, add_unique_table_name_suffix=False)
        assert 'Length of table name' in str(err)


@pytest.mark.parametrize('random_table', [
    NoKeyTable,
    KeyTable,
    MultiKeyTable
], indirect=True)
@pytest.mark.slow('gp')
def test_external_table(random_table):
    with gp.connection.transaction():
        meta = GPMeta(random_table)

        ext_meta = gp.connection.create_external_table(
            random_table, '', '', host='', port=8090)
        assert gp.connection.table_exists(ext_meta)

        assert ext_meta.schema.endswith('ext')
        assert ext_meta.table_name == meta.schema + '_' + meta.table_name
        assert ext_meta.partition_scale is None
        assert ext_meta.distribution is None
        assert ext_meta.storage_parameters is None

        gp.connection.drop_external_table(random_table)
        assert not gp.connection.table_exists(ext_meta)

        ext_meta = gp.connection.create_external_table(
            table=random_table,
            file_path='',
            transform='',
            host='',
            port=8090,
            segment_reject_limit=10
        )
        assert gp.connection.table_exists(ext_meta)
        gp.connection.drop_external_table(random_table)
        assert not gp.connection.table_exists(ext_meta)


@pytest.mark.parametrize('throwaway_table', [
    NoDistributionTable,
    NoPartitionTable,
    PartitionTable,
    MaxDatetimePartitionTable,
], indirect=True)
@pytest.mark.slow('gp')
def test_query_execute(throwaway_table):
    with gp.connection.transaction():
        now = datetime.datetime.utcnow()
        table_name = resolve_meta(throwaway_table).table_full_name
        sql = '''insert into {} (f1, f2, f9)
        values(1, 'aaa', %(f9)s)'''
        gp.connection.execute(sql.format(table_name), f9=now)
        sql = 'select * from {} where f1 = %(f1)s'.format(table_name)
        actual = dict(next(gp.connection.query(sql, f1=1)))
        expected = dict(f1=1, f2='aaa', f3=None, f4=None, f5=None, f6=None, f7=None,
                        f8=None, f9=now, f10=None)
        assert actual == expected


@pytest.mark.parametrize('throwaway_table', [
    NoDistributionTable,
    NoPartitionTable,
    PartitionTable,
    MaxDatetimePartitionTable,
], indirect=True)
@pytest.mark.slow('gp')
def test_query_insert(throwaway_table):
    with gp.connection.transaction():
        now = datetime.datetime.utcnow()
        table_name = resolve_meta(throwaway_table).table_full_name

        data = dict(f1=1, f2='aaa', f3=None, f4=None, f5=None, f6=None, f7=None,
                    f8=None, f9=now, f10=None)
        gp.connection.insert(throwaway_table, [data])
        sql = 'select * from {} where f1 = %(f1)s'.format(table_name)
        actual = dict(next(gp.connection.query(sql, f1=1)))
        assert actual == data


@pytest.mark.parametrize("throwaway_table", [MaxDatetimePartitionTable], indirect=True)
@pytest.mark.slow('gp')
def test_insert_max_datetime(throwaway_table):
    with gp.connection.transaction():
        table_name = resolve_meta(throwaway_table).table_full_name

        data = dict(f1=1, f2='aaa', f3=None, f4=None, f5=None, f6=None, f7=None,
                    f8=None, f9=dtu.parse_datetime(dtu.MAX_DATETIME_STRING), f10=None)
        gp.connection.insert(throwaway_table, [data])
        sql = 'select * from {} where f1 = %(f1)s'.format(table_name)
        actual = dict(next(gp.connection.query(sql, f1=1)))
        assert actual == data


@pytest.mark.parametrize(
    "throwaway_table, partition",
    [
        [PartitionTable, RangePartitionItem("9999-12-31 23:59:59", "10000-01-01 00:00:00", name="max")],
        [
            PartitionTable,
            RangePartitionItem(
                "9999-12-31 23:59:59",
                "10000-01-01 00:00:00",
                name="max",
                storage_parameters=StorageParameters(),
            ),
        ],
        [PartitionListTable, ListPartitionItem("two", 2)],
        [
            PartitionListTable,
            ListPartitionItem("two", 2, storage_parameters=StorageParameters()),
        ],
    ],
    indirect=["throwaway_table"]
)
@pytest.mark.slow('gp')
def test_add_partition(throwaway_table, partition):
    with gp.connection.transaction():
        gp.connection.add_partition(throwaway_table, partition)


@pytest.mark.parametrize(
    "throwaway_table, partitions",
    [
        (
            PartitionTable,
            [RangePartitionItem("2021-02-01", "2021-03-01", name="202102"),
             RangePartitionItem("2021-03-01", "2021-04-01", name="202103")]
        ),
        (
            PartitionListTable,
            [ListPartitionItem("two", 2), ListPartitionItem("three", 3)]
        ),
    ],
    indirect=["throwaway_table"]
)
@pytest.mark.slow("gp")
def test_add_partitions(throwaway_table, partitions):
    with gp.connection.transaction():
        expected_count = _get_partition_count(throwaway_table) + len(partitions)
        gp.connection.add_partitions(throwaway_table, partitions)
        assert _get_partition_count(throwaway_table) == expected_count


@pytest.mark.parametrize("throwaway_table", [PartitionTable], indirect=["throwaway_table"])
@pytest.mark.slow("gp")
def test_add_range_partitions_by_period(throwaway_table):
    with gp.connection.transaction():
        real_partition_count = _get_partition_count(throwaway_table)
        gp.connection.add_range_partitions_by_period(throwaway_table, dtu.Period("2021-02-01", "2021-03-01"))
        assert _get_partition_count(throwaway_table) == real_partition_count + 2
        gp.connection.add_range_partitions_by_period(throwaway_table, dtu.Period("2021-01-01", "2021-02-20"))
        assert _get_partition_count(throwaway_table) == real_partition_count + 3


# будут созданы базовые партиции + у каждой базовой партиции будут еще подпартиции, итого
# expected_count = partitions + partitions * subpartitions
@pytest.mark.parametrize(
    "throwaway_table, expected_count",
    [
        (ListAndRangePartitionTable, 2 + 2 * 4),
        (RangeAndListPartitionTable, 4 + 4 * 2),
        (RangeAndRangePartitionTable, 2 + 2 * 4),
    ],
    indirect=["throwaway_table"])
@pytest.mark.slow("gp")
def test_add_range_partitions_by_period(throwaway_table, expected_count):
    assert _get_partition_count(throwaway_table) == expected_count


def _get_partition_count(table):
    meta = resolve_meta(table)
    # Партиции создаваемые через dmp_suite (create table/alter table) должны иметь название
    sql = """
    SELECT COUNT(1) as cnt
      FROM pg_partitions
     WHERE schemaname = %(schema_name)s
       AND tablename = %(table_name)s
       AND partitionname is not null
    """
    response = gp.connection.query(
        sql,
        schema_name=meta.schema,
        table_name=meta.table_name
    )
    return next(response)['cnt']


@pytest.mark.slow("gp")
def test_get_ext_table_class():

    def get_fields(table: tp.Type[GPTable]):
        return {
            name: table.get_field(name).data_type
            for name in table.field_names()
        }

    class GpAllDmpTypesTable(GPTable):

        __layout__ = utils.TestLayout(name="test_get_ext_table_class")

        col_int = Int()
        col_bigint = BigInt()
        col_smallint = SmallInt()
        col_boolean = Boolean()
        col_numeric = Numeric()
        col_double = Double()
        col_varchar = String()
        col_text = String()
        col_dt = Date()
        col_dttm = Datetime()
        col_json = Json()
        col_point = Point()
        col_uuid = Uuid()
        col_array_int = Array(Int)
        col_array_str = Array(String)
        col_array_dt = Array(Date)
        col_array_dttm = Array(Datetime)
        col_array_bool = Array(Boolean)

    with gp.connection.transaction():

        gp.connection.create_table(GpAllDmpTypesTable)
        expected = get_fields(GpAllDmpTypesTable)

        meta = GPMeta(GpAllDmpTypesTable)
        ext_table = gp.connection.get_ext_table_class(
            table_name=meta.table_name,
            schema_name=meta.schema,
        )
        actual = get_fields(ext_table)

        assert actual == expected
        assert isinstance(ext_table.__layout__, ExternalGPLayout)
        assert ext_table.__layout__.name == meta.table_name
        assert ext_table.__layout__.schema == meta.schema


@pytest.mark.parametrize('role', [None, 'etl'])
@pytest.mark.slow('gp')
def test_with_role(role):
    # роль работает на подключение, создаем отдельное подключение тут
    connection = EtlConnection(
        **gp.get_default_connection_conf(),
        parent_role=role,
    )
    etl_role = role if role else 'none'

    assert connection.current_role == 'none'

    with connection.with_parent_role():
        assert connection.current_role == etl_role
    assert connection.current_role == 'none'

    assert connection.current_role == 'none'
    with connection.with_parent_role():
        assert connection.current_role == etl_role
        with connection.with_parent_role():
            assert connection.current_role == etl_role
        assert connection.current_role == etl_role
    assert connection.current_role == 'none'

    try:
        assert connection.current_role == 'none'
        with connection.with_parent_role():
            assert connection.current_role == etl_role
            raise RuntimeError()
    except RuntimeError:
        assert connection.current_role == 'none'

    try:
        assert connection.current_role == 'none'
        with connection.with_parent_role():
            assert connection.current_role == etl_role
            with connection.with_parent_role():
                assert connection.current_role == etl_role
                raise RuntimeError()
    except RuntimeError:
        assert connection.current_role == 'none'


@pytest.mark.slow('gp')
def test_create_table_with_role():
    class TestTable(GPTable):
        __layout__ = utils.TestLayout(name="test_get_ext_table_class")

        id = Int()

    connection = EtlConnection(**gp.get_default_connection_conf(), parent_role='etl')
    with connection.transaction():
        connection.create_table(TestTable)

        meta = GPMeta(TestTable)
        sql = '''
        SELECT r.rolname as role
        FROM pg_class cl
            INNER JOIN pg_namespace pn ON cl.relnamespace = pn.oid
            INNER JOIN pg_roles r ON cl.relowner = r.oid
        WHERE cl.relname = %(table)s
            AND pn.nspname = %(schema)s
        '''
        result = next(
            connection.query(sql, table=meta.table_name, schema=meta.schema)
        )
        assert result['role'] == 'etl'


@pytest.mark.slow('gp')
def test_table_with_tablespace():
    # Проверяем:
    # - tablespace заданный на уровне GPTable наследуется всеми сабпартициями
    # - tablespace переопределенный на уровне партиции наследуется всеми ее сабпартициями
    # - совместимость storage_parameters, tablespace, column_compression
    class ListAndRangePartitionTable(GPTable):
        __layout__ = utils.TestLayout(name="test_list_range_tablespace")
        __storage_parameters__ = StorageParameters(tablespace=Tablespace.SSD)
        __partition_scale__ = PartitionList(
            partition_key='f1',
            partition_list=[
                ListPartitionItem(
                    "one", 1,
                    storage_parameters=StorageParameters(
                        tablespace=Tablespace.NVME,
                        orientation=Orientation.COLUMN,
                        column_compression={
                            'f2': ColumnStorageParameters(compress_level=3)
                        },
                        level=Level.PARTITION)
                ),
                ListPartitionItem("two", 2),
                ListPartitionItem("three", 3),
            ],
            subpartition=MonthPartitionScale(
                'f9',
                start='2021-01-01',
                end='2021-02-01',
                is_subpartition=True
            )
        )

        f1 = Int()
        f2 = String()
        f9 = Datetime()

    with gp.connection.transaction():
        gp.connection.create_table(ListAndRangePartitionTable)

        meta = GPMeta(ListAndRangePartitionTable)
        sql = '''
select partitiontablespace, count(*)
 from pg_partitions
where schemaname = %(schema)s
  and tablename = %(table)s
  and parentpartitionname is not null
group by partitiontablespace
        '''
        result = list(
            gp.connection.query(sql, table=meta.table_name, schema=meta.schema)
        )
        expected = [
            [Tablespace.NVME.value,  2],
            [Tablespace.SSD.value,  4],
        ]
        assert expected == result


@pytest.mark.slow('gp')
def test_closed_connection():
    connection = EtlConnection(**gp.get_default_connection_conf(), parent_role='etl')
    connection.execute('SELECT 1')
    connection.close()
    connection.execute('SELECT 1')


@pytest.mark.slow('gp')
def test_closed_connection_before_transaction():
    connection = EtlConnection(**gp.get_default_connection_conf(), parent_role='etl')
    connection.execute('SELECT 1')
    connection.close()
    with connection.transaction():
        connection.execute('SELECT 1')


@pytest.mark.slow('gp')
def test_closed_connection_inside_transaction():
    connection = EtlConnection(**gp.get_default_connection_conf(), parent_role='etl')
    with pytest.raises(ConnectionWrapperError):
        with connection.transaction():
            connection.execute('SELECT 1')
            connection.close()
            connection.execute('SELECT 1')


@pytest.mark.slow('gp')
def test_application_name():
    connection = EtlConnection(**gp.get_default_connection_conf())
    with connection:
        response = connection.query("SELECT setting FROM pg_settings WHERE name = 'application_name'")
        response = connection.query(
            "SELECT run_id FROM ctl.dmp_application_names WHERE app_name = %(app_name)s",
            app_name=next(response)[0]
        )
        assert py_env.get_taxidwh_run_id() == next(response)[0]
