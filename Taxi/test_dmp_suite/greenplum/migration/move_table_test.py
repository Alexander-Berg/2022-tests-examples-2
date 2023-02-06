from datetime import datetime

import mock
import pytest
from psycopg2.sql import SQL, Composed, Literal

from connection import greenplum as gp
from dmp_suite.greenplum import (
    Datetime,
    GPTable,
    Int,
    MonthPartitionScale,
    RangePartitionItem,
    resolve_meta,
    ExternalGPLocation,
    ExternalGPLayout,
)
from dmp_suite.greenplum import migration
from dmp_suite.greenplum.connection import EtlConnection
from dmp_suite.greenplum.view import View, ViewMeta
from dmp_suite.migration import migration as migration_task
from dmp_suite.migration.exceptions import MigrationError
from dmp_suite.table import LayeredLayout, LayoutBase, TableMeta
from test_dmp_suite.greenplum import utils
from .utils import (
    create,
    write,
    run_migration_in_same_process,
)


def meta_rename_table():
    # Тест на ренейминг без переноса между схемами
    class TableBefore(GPTable):
        __layout__ = utils.TestLayout(name='name_before')
        a = Int()

    class TableAfter(TableBefore):
        __layout__ = utils.TestLayout(name='name_after')

    return TableBefore, TableAfter


def meta_change_schema():
    # Тест на перенос из одной схемы в другую
    old_layout = LayeredLayout(layer='testing', name='just_name', prefix_key='test')
    new_layout = LayeredLayout(layer='testing_after_migration', name='just_name', prefix_key='test')

    class TableBefore(GPTable):
        __layout__ = old_layout
        a = Int()

    class TableAfter(TableBefore):
        __layout__ = new_layout

    return TableBefore, TableAfter


def meta_change_name_and_schema():
    # Тест на перенос из одной схемы в другую + смена имени
    old_layout = LayeredLayout(layer='testing', name='name_before', prefix_key='test')
    new_layout = LayeredLayout(layer='testing_after_migration', name='name_after', prefix_key='test')

    class TableBefore(GPTable):
        __layout__ = old_layout
        a = Int()

    class TableAfter(TableBefore):
        __layout__ = new_layout

    return TableBefore, TableAfter


def test_create_view():
    class HellMetaTrash(TableMeta):
        pass

    class MyTable(GPTable, metaclass=HellMetaTrash):
        a = Int()
        __layout__ = LayeredLayout(layer='testing', name='table_name')

    with mock.patch('dmp_suite.greenplum.migration.move_table._get_view_layout_from_ctl',
                    return_value=ExternalGPLayout('my_schema', 'my_name')):
        view = migration.move_table.get_view(MyTable)

        assert isinstance(view, ViewMeta)
        assert issubclass(view, View)

        # Проверяем, вызов get_sql работает адекватно
        some_sql = view().get_sql()
        assert isinstance(some_sql, Composed)

        # Проверяем, что вью зависит от нашей таблицы
        assert len(view.__tables__) == 1
        assert list(view.__tables__.values())[0] == MyTable

        assert view.__location_cls__ == ExternalGPLocation
        assert isinstance(view.__layout__, LayoutBase)

        # Имя класса важно для локов, т.к. может быть использовано в имени таска миграции
        assert view.__name__ == 'MoveView_MyTable'

        meta = resolve_meta(view)
        assert meta.table_name.startswith('my_name')  # Not equal, because a test hash in ExternalGPLocation
        assert meta.schema == 'my_schema'


@pytest.mark.slow('gp')
@pytest.mark.parametrize(
    'table_before,table_after', [
        meta_rename_table(),
        meta_change_schema(),
        meta_change_name_and_schema(),
    ]
)
def test_move_just_work(table_before, table_after):
    create(table_before)
    write(table_before, [{'a': 100500}])
    connection = EtlConnection(**gp.get_default_connection_conf(), parent_role='etl')

    gp_meta = resolve_meta(table_before)
    connection.grant(gp_meta, 'SELECT', 'robot-taxi-stat')  # Для теста захардкодить роль

    task = migration_task(
        'TEST-123',
        migration.move_gp_table(table_before, table_after.get_layout(), datetime(9999, 1, 1))
    )

    with mock.patch('dmp_suite.migration.move_table.startrek.create_migration_notice_issue'):
        run_migration_in_same_process(task)

    # TableAfter
    with connection.transaction():
        assert connection.table_exists(table_after)
        assert not connection.table_exists(table_before)
        assert connection.view_exists(table_before)


@pytest.mark.slow('gp')
@pytest.mark.parametrize(
    'table_before,table_after', [
        meta_rename_table(),
        meta_change_schema(),
        meta_change_name_and_schema(),
    ]
)
def test_move_table_idempotent(table_before, table_after):
    # Проверяем, что миграция завершается успешно, если она уже была выполнена ранее
    create(table_before)

    task = migration_task(
        'TEST-123',
        migration.move_gp_table(table_before, table_after.get_layout(), datetime(9999, 1, 1))
    )

    with mock.patch('dmp_suite.migration.move_table.startrek.create_migration_notice_issue'):
        run_migration_in_same_process(task)
        run_migration_in_same_process(task)


@pytest.mark.slow('gp')
@pytest.mark.parametrize(
    'table_before,table_after', [
        meta_rename_table(),
        meta_change_schema(),
        meta_change_name_and_schema(),
    ]
)
def test_move_raise_exception(table_before, table_after):
    # Проверяем, что миграция падает, если table_after уже существует
    create(table_before)
    create(table_after)

    task = migration_task(
        'TEST-123',
        migration.move_gp_table(table_before, table_after.get_layout(), datetime(9999, 1, 1))
    )

    with pytest.raises(MigrationError):
        with mock.patch('dmp_suite.migration.move_table.startrek.create_migration_notice_issue'):
            run_migration_in_same_process(task)


@pytest.mark.slow('gp')
def test_move_with_partitions():
    # Тест на перенос из одной схемы в другую + смена имени
    old_layout = LayeredLayout(layer='testing', name='name_before', prefix_key='test')
    new_layout = LayeredLayout(layer='testing_after_migration', name='name_after', prefix_key='test')

    class TableBefore(GPTable):
        __layout__ = old_layout
        __partition_scale__ = MonthPartitionScale(partition_key='dttm')
        dttm = Datetime()
        a = Int()

    class TableAfter(TableBefore):
        __layout__ = new_layout

    create(TableBefore)
    partitions = [
        RangePartitionItem('2021-02-01', '2021-03-01', name='202102'),
        RangePartitionItem('2021-03-01', '2021-04-01', name='202103')
    ]

    meta_before = resolve_meta(TableBefore)
    meta_after = resolve_meta(TableAfter)

    # В транзакции работает
    with gp.connection.transaction() as tx:
        gp.connection.add_partitions(TableBefore, partitions)
        gp.connection.grant(meta_before, 'SELECT', 'robot-taxi-stat')  # Для теста захардкодить роль

        task = migration_task(
            'TEST-123',
            migration.move_gp_table(TableBefore, TableAfter.get_layout(), datetime(9999, 1, 1)),
        )

        with mock.patch('dmp_suite.migration.move_table.startrek.create_migration_notice_issue'):
            run_migration_in_same_process(task)

    # Базовые проверки:
    with gp.connection.transaction():
        assert gp.connection.table_exists(TableAfter)
        assert not gp.connection.table_exists(TableBefore)
        assert gp.connection.view_exists(TableBefore)

        # Проверяем, что партиции лежат в той же схеме, где таблица
        sql = """
            SELECT
                nmsp_parent.nspname AS parent_schema,
                parent.relname      AS parent,
                nmsp_child.nspname  AS child_schema,
                child.relname       AS child
            FROM pg_inherits
                JOIN pg_class parent            ON pg_inherits.inhparent = parent.oid
                JOIN pg_class child             ON pg_inherits.inhrelid   = child.oid
                JOIN pg_namespace nmsp_parent   ON nmsp_parent.oid  = parent.relnamespace
                JOIN pg_namespace nmsp_child    ON nmsp_child.oid   = child.relnamespace
            WHERE nmsp_parent.nspname = {schema_name}
            AND parent.relname = {table_name}
            -- nmsp_parent.nspname - схема с таблицей
            -- nmsp_child.nspname - схема с партицией
            AND nmsp_parent.nspname = nmsp_child.nspname;
        """
        sql_table_before = SQL(sql).format(
            schema_name=Literal(meta_before.schema),
            table_name=Literal(meta_before.table_name),
        )
        sql_table_after = SQL(sql).format(
            schema_name=Literal(meta_after.schema),
            table_name=Literal(meta_after.table_name),
        )

        with gp.connection.cursor() as cur:
            cur.execute(sql_table_before)
            partitions = cur.fetchall()
            assert not partitions

            cur.execute(sql_table_after)
            partitions = cur.fetchall()
            assert len(partitions) > 0


@pytest.mark.slow('gp')
def test_table_does_not_exists():
    # Проверить, что миграция падает, если таблицы не существует
    old_layout = LayeredLayout(layer='testing', name='name_before', prefix_key='test')
    new_layout = LayeredLayout(layer='testing_after_migration', name='name_after', prefix_key='test')

    class TableBefore(GPTable):
        __partition_scale__ = MonthPartitionScale(partition_key='dttm')
        __layout__ = old_layout
        a = Int()

    with pytest.raises(MigrationError):
        task = migration_task(
            'TEST-123',
            migration.move_gp_table(TableBefore, new_layout, datetime(9999, 1, 1)),
        )
        with mock.patch('dmp_suite.migration.move_table.startrek.create_migration_notice_issue'):
            run_migration_in_same_process(task)


@pytest.mark.slow('gp')
def test_user_try_revert_migtation():
    table_right, table_wrong = meta_rename_table()
    create(table_right)

    task = migration_task(
        'TEST-123',
        migration.move_gp_table(table_right, table_wrong.get_layout(), datetime(9999, 1, 1))
    )
    with mock.patch('dmp_suite.migration.move_table.startrek.create_migration_notice_issue'):
        run_migration_in_same_process(task)

    task_revert = migration_task(
        'TEST-321',
        migration.move_gp_table(table_wrong, table_right.get_layout(), datetime(9999, 1, 1))
    )
    with pytest.raises(MigrationError):
        run_migration_in_same_process(task_revert)
