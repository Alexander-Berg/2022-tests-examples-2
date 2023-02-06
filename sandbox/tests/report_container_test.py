import logging
from sandbox.projects.yabs.AnomalyAuditReport.lib.report_container import AnomalyAuditReportFactory
from sandbox.projects.yabs.AnomalyAuditReport.lib.query_result import YQLQueryResult
from sandbox.projects.yabs.AnomalyAuditReport.lib.config_reader import Database, OutputFormat, Threshold, Totals


def test_get_report_result_txt():
    report_config = {'reportId': 'EventShows',
                     'reportName': 'Dummy',
                     'database': Database.ClickHouse,
                     'thresholds': {'default': Threshold(1000, 10, 0.003), 'bmcategoryid': Threshold(10000, 100, 0.3)},
                     'outputFormat': OutputFormat.TXT,
                     'selectGoodEvents': False
                     }

    totals = Totals()
    totals.current = 100
    totals.previous = 100
    result_container = AnomalyAuditReportFactory.get_report_result_container(report_config,
                                                                             '2021-12-12', '2021-12-11', totals)

    result = YQLQueryResult([], 'test url')
    result._columns = ['OrderID', 'BannerID', 'current_result', 'previous_result', 'current_result', 'previous_result']
    result._rows = [['1', '2', 12, 12000, 0, 0], ['2', '1', 12, 12, 6, 6], ['3', '3', 12000, 12, 6, 7]]

    result_container.add_result(result)
    result_container.add_value_descriptions({})

    logging.warning(result_container._result_rows)

    assert result_container.get_result() != ''
    assert result_container.output_format == OutputFormat.TXT


def test_get_report_result_html():
    report_config = {'reportId': 'EventShows',
                     'reportName': 'Dummy',
                     'database': Database.ClickHouse,
                     'thresholds': {'default': Threshold(1000, 10, 0.003), 'bmcategoryid': Threshold(10000, 100, 0.3)},
                     'outputFormat': OutputFormat.HTML,
                     'selectGoodEvents': True
                     }

    totals = Totals()
    totals.current = 10
    totals.previous = 10
    result_container = AnomalyAuditReportFactory.get_report_result_container(report_config,
                                                                             '2021-12-12', '2021-12-11', totals)

    result = YQLQueryResult([], 'test url')
    result._columns = ['OrderID', 'BannerID', 'current_result', 'previous_result', 'current_result', 'previous_result']
    result._rows = [['1', '2', 12, 12000, 0, 0], ['2', '1', 0, 0, 6, 6], ['3', '3', 12000, 12, 6, 7]]

    result_container.add_result(result)
    result_container.add_value_descriptions({})

    logging.warning(result_container._result_rows)

    assert result_container.get_result() != ''
    assert result_container.output_format == OutputFormat.HTML
