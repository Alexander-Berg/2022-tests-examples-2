# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

import example_library.generated.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['example_library.generated.pytest_plugins']


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update({'YAS_TOKEN': 'HELLO_YAS'})
    return simple_secdist
