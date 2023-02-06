# pylint: disable=redefined-outer-name
import pytest

import startrack_reports.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['startrack_reports.generated.service.pytest_plugins']


@pytest.fixture  # noqa: F405
def simple_secdist(simple_secdist):
    simple_secdist['client_apikeys'].update(
        {'stq_agent': {'stq_agent': 'secret'}},
    )
    simple_secdist['settings_override'].update(
        {
            'STARTRACK_API_PROFILES': {
                'startrack_reports': {
                    'url': 'https://startrek/',
                    'org_id': 0,
                    'oauth_token': 'secret',
                },
            },
        },
    )
    return simple_secdist
