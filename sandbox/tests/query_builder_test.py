import pytest
import base64
import yaml
import logging
from library.python import resource
from sandbox.projects.yabs.AnomalyAuditReport.lib.query_builder import QueryBuilderFactory, ColumnType
from sandbox.projects.yabs.AnomalyAuditReport.lib.config_reader import Database, SelectLevel, Threshold, Totals


def test_get_query_builder_error():
    report_config = {'reportId': 'reportId',
                     'reportName': 'reportName',
                     'database': 'Dummy'
                     }

    with pytest.raises(ValueError):
        QueryBuilderFactory.get_query_builder(report_config, '2021-12-12', '2021-12-11')


def test_query_builder():
    resource_content = resource.find(
        'sandbox/projects/yabs/AnomalyAuditReport/lib/tests/query_builder_test_results.yaml')
    if resource_content is None:
        raise ValueError('Resource query_builder_test_results.yaml is not found')

    test_reports = yaml.load(resource_content, Loader=yaml.FullLoader)

    thresholds = {'default': Threshold(1000, 10, 0.003), 'bmcategoryid': Threshold(10000, 100, 0.3)}

    for report in test_reports:
        report_config = {'reportId': report['reportId'],
                         'reportName': 'Dummy',
                         'database': Database(report['database']),
                         'selectLevel': SelectLevel(report['selectLevel']),
                         'tableName': report['tableName'],
                         'whereClause': report['whereClause'],
                         'whereClauseGoodEvents': report['whereClauseGoodEvents'],
                         'selectGoodEvents': report['selectGoodEvents'],
                         'thresholds': thresholds,
                         'dictionaryColumns': []
                         }

        query_builder = QueryBuilderFactory.get_query_builder(
            report_config, report['currentDate'], report['previousDate'])

        totals = Totals()
        totals.current = report['currentTotalCount']
        totals.previous = report['previousTotalCount']

        for column in report['tests']:
            query = query_builder.get_query(column['columnName'], ColumnType(column['columnType']), totals, column['dbColumnName'])
            base64_query = base64.b64encode(query.encode())

            base64_query_compare = column['queryBase64'].encode()

            if base64_query != base64_query_compare:
                logging.warning(f"Error in Report: {report['reportId']}: {column['columnName']} {column['columnType']}")
                logging.warning(f"- columnName: {column['columnName']}")
                logging.warning(f"  columnType: {column['columnType']}")
                logging.warning(f"  dbColumnName: {column['dbColumnName']}")
                logging.warning(f"  queryBase64: {base64_query}")
                logging.warning(f"  query: {query}")

            assert base64_query == base64_query_compare
