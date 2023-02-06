import pytest

from connection import greenplum as gp
from dmp_suite.greenplum import (
    GPTable,
    Int,
)
from dmp_suite.greenplum import migration
from dmp_suite.greenplum.query import GreenplumQuery
from test_dmp_suite.greenplum import utils
from .utils import (
    create,
    read,
    write,
    run_migration_in_same_process,
)


def test_lock_names():
    class TestTable(GPTable):
        a = Int()

    task = migration.add_columns(TestTable)
    assert task.get_lock() == ('add_columns_to_test_dmp_suite_greenplum_migration_migration_test_TestTable',)

    task = migration.drop_columns(TestTable)
    assert task.get_lock() == ('drop_columns_from_test_dmp_suite_greenplum_migration_migration_test_TestTable',)

    task = migration.rename_column(TestTable, 'a', 'b')
    assert task.get_lock() == ('rename_column_a_to_b_in_test_dmp_suite_greenplum_migration_migration_test_TestTable',)

    task = migration.sync_view(TestTable)
    assert task.get_lock() == ('sync_view_test_dmp_suite_greenplum_migration_migration_test_TestTable',)


@pytest.mark.slow('gp')
def test_run_sql_migration():
    class ExampleTable(GPTable):
        __layout__ = utils.TestLayout(name='example')

        a = Int()

    query = GreenplumQuery.from_string("""
        DELETE FROM {example_table} tbl
        WHERE tbl.a >= 10;
    """).add_tables(
        example_table=ExampleTable,
    )

    with gp.connection.transaction():
        create(ExampleTable)
        write(ExampleTable, [{'a': a} for a in range(100)])
        task = migration.sql('delete_all_items_above_threshold', query, ExampleTable, idempotent=True)
        run_migration_in_same_process(task)

        actual = sorted(read(ExampleTable), key=lambda x: x['a'])
        expected = sorted([{'a': a} for a in range(10)], key=lambda x: x['a'])
        assert actual == expected
