"""
Mock for configs service.
"""

import datetime

import pytest

TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


@pytest.fixture(autouse=True)
def mock_configs_service(mockserver, taxi_config):
    @mockserver.json_handler('/configs-service/configs/values')
    def _mock_configs(request):
        values = taxi_config.get_values()
        if request.json.get('ids'):
            values = {
                name: values[name]
                for name in request.json['ids']
                if name in values
            }
        return {'configs': values, 'updated_at': _service_timestamp()}

    @mockserver.json_handler('/configs-service/configs/status')
    def _mock_configs_status(request):
        return {'updated_at': _service_timestamp()}


def _service_timestamp(now=None):
    if now is None:
        now = datetime.datetime.now()
    return now.strftime(format=TIMESTAMP_FORMAT)
