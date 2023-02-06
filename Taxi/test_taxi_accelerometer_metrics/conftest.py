# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

import taxi_accelerometer_metrics.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'taxi_accelerometer_metrics.generated.service.pytest_plugins',
]


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update(
        {'GEOTRACKS_API_KEY': 'supersecret'},
    )
    return simple_secdist
