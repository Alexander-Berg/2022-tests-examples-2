# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

import driver_event_detector.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['driver_event_detector.generated.service.pytest_plugins']


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update(
        {'animals': {'login': 'login', 'password': 'password'}},
    )
    return simple_secdist
