# pylint: disable=redefined-outer-name
import pytest

import hiring_replica_rabotaru.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'hiring_replica_rabotaru.generated.service.client_rabotaru.pytest_plugin',
    'hiring_replica_rabotaru.generated.service.pytest_plugins',
]


@pytest.fixture  # noqa: F405
def simple_secdist(simple_secdist):
    creds = {'RABOTA_EMAIL': 'login', 'RABOTA_PASSWORD': 'password'}
    simple_secdist.update(creds)
    simple_secdist['settings_override'].update(creds)
    return simple_secdist
