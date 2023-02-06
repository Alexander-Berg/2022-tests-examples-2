from dmp_suite.migration.flow import _table_to_creator_tasks
from callcenter_etl.layer.yt.summary.callcenter.call_statistic.table import CallStatistic
from callcenter_etl.layer.yt.summary.callcenter.call_statistic.loader import task as call_statistic_task


def test_task_to_target_tables_function():
    # Проверим, функцию на каком-нибудь реальном классе
    assert list(_table_to_creator_tasks(CallStatistic)) == [call_statistic_task]
