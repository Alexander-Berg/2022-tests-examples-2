import pytest

from connection import greenplum as gp
from dmp_suite.greenplum import (
    GPTable,
    Int,
)
from dmp_suite.greenplum import migration
from test_dmp_suite.greenplum import utils
from .utils import (
    run_migration_in_same_process,
)


@pytest.mark.slow('gp')
def test_run_recreate_table_migration():
    class ExampleTable(GPTable):
        __layout__ = utils.TestLayout(name='example')
        a = Int()

    with gp.connection.transaction():
        assert not gp.connection.table_exists(ExampleTable)
        task = migration.recreate_table(ExampleTable)
        run_migration_in_same_process(task)
        assert gp.connection.table_exists(ExampleTable)
        task = migration.recreate_table(ExampleTable)
        run_migration_in_same_process(task)
        assert gp.connection.table_exists(ExampleTable)
