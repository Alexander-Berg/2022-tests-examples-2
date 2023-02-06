# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

import taxi_plotva_ml.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['taxi_plotva_ml.generated.service.pytest_plugins']


@pytest.fixture(autouse=True)
def turn_on_setup_ml_app(setup_ml_app):
    pass
