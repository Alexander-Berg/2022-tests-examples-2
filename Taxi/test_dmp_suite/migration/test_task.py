from dmp_suite.migration.task import build_task_name
from dmp_suite.yt import YTTable


def test_build_task_name():
    class TestTable(YTTable):
        pass

    task_name = build_task_name('foo', TestTable)
    assert task_name == 'foo_test_dmp_suite_migration_test_task_TestTable'
