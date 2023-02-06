from sandbox.projects.yabs.AnomalyAuditReport.lib.config_reader import AnomalyAuditConfigReader
from library.python import resource
import pytest
import json
from jsonschema.exceptions import ValidationError


def test_validate_test_config():
    resource_content = resource.find('sandbox/projects/yabs/AnomalyAuditReport/lib/tests/config_for_test.json')
    if resource_content is None:
        raise ValueError('Resource query_builder_test_results.yaml is not found')

    report_configs = json.loads(resource_content)

    report_configs = AnomalyAuditConfigReader.get_config(report_configs)
    assert len(report_configs) == 4


def test_validate_config_error():

    resource_content = """
        [
            {
                "reportId": "anomalyActionLogReport",
                "reportName": "Action Log Anomaly Report"
            }
        ]
    """

    report_configs = json.loads(resource_content)

    with pytest.raises(ValidationError):
        AnomalyAuditConfigReader.get_config(report_configs)
