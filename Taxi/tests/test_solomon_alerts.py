from typing import List

import jsonschema
import pytest
import scripts.common as common


ALERT_DEF_SCHEMA = 'solomon_alert_def.yaml'
JUGGLER_SERVICE_AND_HOST_CHANNEL = 'juggler_service_and_host_from_annotations'


@pytest.fixture(scope='session', name='solomon_alert_validator')
def _solomon_alert_validator():
    return common.get_validator(ALERT_DEF_SCHEMA)


@pytest.mark.parametrize('config_path', common.get_all_solomon_alert_paths())
def test_solomon_alerts(config_path, solomon_alert_validator):
    alerts = common.try_load_yaml(config_path)
    errors = []
    for alert in alerts:
        try:
            solomon_alert_validator.validate(alert)
            errors.extend(_check_juggler_channel(alert))
        except jsonschema.exceptions.ValidationError as exc:
            raise Exception(
                f'Validation of {config_path} failed: {exc.message}',
            )
    if errors:
        raise Exception(
           f'config {config_path} has errors: {errors}'
        )


def _check_juggler_channel(alert: dict) -> List[str]:
    errors = []
    notification_channels = alert.get('notificationChannels', [])
    req_channel = JUGGLER_SERVICE_AND_HOST_CHANNEL
    host = alert.get('host')
    if req_channel in notification_channels and not host:
        errors.append(
            f'{alert["service"]}: \'host\' is required field for use '
            f'notificationChannels.{req_channel}'
        )
    return errors
