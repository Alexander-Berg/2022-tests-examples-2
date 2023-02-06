from dmp_suite.greenplum import GPTable
from dmp_suite.greenplum.task.transformations import GPTableTaskTarget
from dmp_suite.table import LayeredLayout


def test_abstract_table_task_target_wrapper():
    # Все наследники AbstractTableTaskTarget
    # должны быть эквивалентны той таблице,
    # которая в них обёрнута.
    # Иначе поиск тасков-источников в dmp_suite.migration.flow
    # будет работать неправильно.
    class TestTable(GPTable):
        __layout__ = LayeredLayout(name='test', layer='test')

    wrapper = GPTableTaskTarget.wrap(TestTable)
    assert wrapper == TestTable
    assert TestTable == wrapper
