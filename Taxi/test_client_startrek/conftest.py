# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

import client_startrek.generated.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['client_startrek.generated.pytest_plugins']


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update(
        {
            'STARTRACK_API_PROFILES': {
                'client-startrek-test': {
                    'url': 'http://startrek/',
                    'org_id': 0,
                    'oauth_token': 'secret',
                },
            },
        },
    )
    return simple_secdist
