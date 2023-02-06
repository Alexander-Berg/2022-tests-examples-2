import pytest
from sandbox.projects.yabs.AnomalyAuditReport.lib.config_reader import Database, Cluster
from sandbox.projects.yabs.AnomalyAuditReport.lib.query_executor import QueryExecutorFactory


def test_get_query_executor_error():
    with pytest.raises(ValueError):
        QueryExecutorFactory.get_query_executor('Dummy', 'yql_tmp_folder', 'token')


def test_get_query_executor():
    QueryExecutorFactory.get_query_executor(Database.YT, 'yql_tmp_folder', 'token')


def test_get_query_executor_by_config_error():
    report_config = {'database': 'Dummy', 'cluster': Cluster.Hahn}
    with pytest.raises(ValueError):
        QueryExecutorFactory.get_query_executor_by_config(report_config, 'token')


def test_get_query_executor_by_config():
    report_config = {'database': Database.ClickHouse, 'cluster': Cluster.Hahn}
    QueryExecutorFactory.get_query_executor_by_config(report_config, 'token')


def test_get_query_executor_retry():
    with pytest.raises(Exception):
        queryExecutor = QueryExecutorFactory.get_query_executor(Database.YT, 'yql_tmp_folder', 'token')
        queryExecutor.execute_query('query')
