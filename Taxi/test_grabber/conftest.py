# pylint: disable=redefined-outer-name
import pytest

import grabber.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['grabber.generated.service.pytest_plugins']


@pytest.fixture  # noqa: F405
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update({'YQL_TOKEN': 'SECRET'})
    return simple_secdist
