# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

import taxi_teamcity_monitoring.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['taxi_teamcity_monitoring.generated.service.pytest_plugins']

SETTINGS_OVERRIDE = {
    'STARTRACK_API_PROFILES': {
        'teamcity-monitoring': {
            'url': 'https://test-startrack-url/',
            'org_id': 0,
            'oauth_token': 'some_startrack_token',
        },
    },
    'TEAMCITY_MDS_S3_COMMON': {
        'url': 's3.mds.yandex.net',
        'bucket': 'common',
        'access_key_id': 'key_to_access',
        'secret_key': 'very_secret',
    },
    'TEAMCITY_OAUTH': 'foobar',
}


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update(SETTINGS_OVERRIDE)
    return simple_secdist
