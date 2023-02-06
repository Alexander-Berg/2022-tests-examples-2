# pylint: disable=redefined-outer-name
import pytest

import billing_marketplace_api.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301


pytest_plugins = ['billing_marketplace_api.generated.service.pytest_plugins']


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update(
        {
            'MARKETPLACE_BACKEND_KEY': 'qwerty',
            'YT_CONFIG': {
                'hahn': {
                    'token': 'test_token',
                    'prefix': '//home/taxi/',
                    'pickling': {'enable_tmpfs_archive': False},
                    'proxy': {'url': 'test_url'},
                    'api_version': 'v3',
                },
            },
        },
    )
    return simple_secdist
