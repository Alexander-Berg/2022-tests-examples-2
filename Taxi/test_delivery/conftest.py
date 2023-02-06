# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

import delivery.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['delivery.generated.service.pytest_plugins']


@pytest.fixture(autouse=True)
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update(
        {
            'AVITO_USER_ID': 123456789,
            'AVITO_CLIENT_ID': 'secret_client_id',
            'AVITO_CLIENT_SECRET': 'secret_client_secret',
        },
    )
    return simple_secdist
