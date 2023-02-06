import pytest

# pylint: disable=redefined-outer-name
import supportai_models.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['supportai_models.generated.service.pytest_plugins']


@pytest.fixture(autouse=True)
def turn_on_setup_ml_app(setup_ml_app):
    pass
