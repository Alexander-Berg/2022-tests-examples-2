# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

import client_yt.generated.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['client_yt.generated.pytest_plugins']


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override']['YT_CONFIG'] = {
        'genghis': {'prefix': 'genghis', 'proxy': {'url': 'genghis'}},
    }
    return simple_secdist
