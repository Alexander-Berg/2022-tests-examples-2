# pylint: disable=redefined-outer-name
import pytest

import fleet_fines.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['fleet_fines.generated.service.pytest_plugins']


@pytest.fixture  # noqa: F405
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update(
        {'YAMONEY_FINES_TOKEN': 'SECRET'},
    )
    return simple_secdist
