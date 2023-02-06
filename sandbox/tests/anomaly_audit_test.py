from library.python import resource
import json
from sandbox.projects.yabs.AnomalyAuditReport.lib.anomaly_audit import AnomalyAudit
from sandbox.projects.yabs.AnomalyAuditReport.lib.config_reader import AnomalyAuditConfigReader
from sandbox.projects.yabs.AnomalyAuditReport.lib.query_builder import ColumnType


def test_get_columns():
    report_configs = _get_test_config()

    for report_config in report_configs:
        table_columns = _get_table_columns(report_config)
        columns = AnomalyAudit._get_report_columns(report_config, table_columns)

        if report_config['reportId'] == 'eventLogShows':
            assert len(columns) == 5, columns
            assert columns[0][0] == 'WideFraudBits'
            assert columns[0][1] == ColumnType.WideBits
            assert columns[1][0] == 'FraudBits'
            assert columns[1][1] == ColumnType.Bits
            assert columns[2][0] == 'RegionID'
            assert columns[2][1] == ColumnType.Other
            assert columns[3][0] == 'Rules'
            assert columns[3][1] == ColumnType.Array
            assert columns[4][0] == "dictGet('BMCategoryDict', 'ParentBMCategoryID', toUInt64(BMCategoryID)) as BMCategoryID"
            assert columns[4][1] == ColumnType.Dictionary
        elif report_config['reportId'] == 'eventLogClicks':
            assert len(columns) == 6, columns
            assert columns[0][0] == 'WideFraudBits'
            assert columns[0][1] == ColumnType.WideBits
            assert columns[1][0] == 'FraudBits'
            assert columns[1][1] == ColumnType.Bits
            assert columns[2][0] == 'RegionID'
            assert columns[2][1] == ColumnType.Other
            assert columns[3][0] == 'Rules'
            assert columns[3][1] == ColumnType.Array
            assert columns[4][0] == "dictGet('BMCategoryDict', 'ParentBMCategoryID', toUInt64(BMCategoryID)) as BMCategoryID"
            assert columns[4][1] == ColumnType.Dictionary
            assert columns[5][0] == 'PageID, ImpID'
            assert columns[5][1] == ColumnType.Group
        elif report_config['reportId'] == 'anomalyActionLogReport':
            assert len(columns) == 5, columns
            assert columns[0][0] == 'fraudbits'
            assert columns[0][1] == ColumnType.Bits
            assert columns[1][0] == 'widefraudbits'
            assert columns[1][1] == ColumnType.WideBits
            assert columns[2][0] == 'statisticoptions'
            assert columns[2][1] == ColumnType.Array
            assert columns[3][0] == 'options'
            assert columns[3][1] == ColumnType.Array
            assert columns[4][0] == 'autobudgetavgcpa'
            assert columns[4][1] == ColumnType.Other


def test_get_columns_custom():
    report_configs = _get_test_config()

    for report_config in report_configs:
        table_columns = _get_table_columns(report_config)

        if report_config['reportId'] == 'eventLogShows' or report_config['reportId'] == 'eventLogClicks':
            report_config['manualColumns'] = {'widefraudbits'}
        else:
            report_config['manualColumns'] = {'fraudbits', 'options'}

        columns = AnomalyAudit._get_report_columns(report_config, table_columns)

        if report_config['reportId'] == 'eventLogShows':
            assert len(columns) == 1, report_config['manualColumns']
            assert columns[0][0] == 'WideFraudBits'
            assert columns[0][1] == ColumnType.WideBits
        elif report_config['reportId'] == 'eventLogClicks':
            assert len(columns) == 2, report_config['manualColumns']
            assert columns[0][0] == 'WideFraudBits'
            assert columns[0][1] == ColumnType.WideBits
            assert columns[1][0] == 'PageID, ImpID'
            assert columns[1][1] == ColumnType.Group
        elif report_config['reportId'] == 'anomalyActionLogReport':
            assert len(columns) == 2, report_config['manualColumns']
            assert columns[0][0] == 'fraudbits'
            assert columns[0][1] == ColumnType.Bits
            assert columns[1][0] == 'options'
            assert columns[1][1] == ColumnType.Array


def _get_test_config():
    resource_content = resource.find('sandbox/projects/yabs/AnomalyAuditReport/lib/tests/config_for_test.json')
    if resource_content is None:
        raise ValueError('Resource query_builder_test_results.yaml is not found')

    report_configs = json.loads(resource_content)
    return AnomalyAuditConfigReader.get_config(report_configs)


def _get_table_columns(report_config: dict):
    if report_config['reportId'] == 'eventLogShows' or report_config['reportId'] == 'eventLogClicks':
        return [('WideFraudBits', 'String'), ('FraudBits', 'UInt64'), ('RegionID', 'Int32'),
                ('Rules', 'String'), ('PageID', 'Int64'), ('ImpID', 'Int64'), ('BMCategoryID', 'Int64')]
    else:
        return [('fraudbits', 'Nullable(UInt64)'), ('widefraudbits', 'Nullable(String)'), ('pageid', 'Nullable(Int64)'),
                ('statisticoptions', 'String'), ('options', 'String'), ('autobudgetavgcpa', 'Nullable(Int64)')]
