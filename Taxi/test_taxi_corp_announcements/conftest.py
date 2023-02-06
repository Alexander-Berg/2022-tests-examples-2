# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

import taxi_corp_announcements.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['taxi_corp_announcements.generated.service.pytest_plugins']


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update(
        {
            'API_ADMIN_SERVICES_TOKENS': {
                'taxi_corp_announcements_web': 'test_api_key',
            },
        },
    )
    return simple_secdist
