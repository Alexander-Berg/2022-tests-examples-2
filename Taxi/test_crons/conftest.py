# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

import crons.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['crons.generated.service.pytest_plugins']


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update(
        {
            'STARTRACK_API_PROFILES': {
                'crons': {
                    'url': 'https://st-api.test.yandex-team.ru/v2/',
                    'org_id': 0,
                    'oauth_token': '',
                },
            },
        },
    )
    return simple_secdist
