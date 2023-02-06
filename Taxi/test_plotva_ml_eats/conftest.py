# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

import plotva_ml_eats.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from plotva_ml_eats.generated.web.grocery_products_cache import (
    plugin as cache_plugin,
)  # noqa: E402

pytest_plugins = ['plotva_ml_eats.generated.service.pytest_plugins']


@pytest.fixture(autouse=True)
def turn_on_setup_ml_app(setup_ml_app):
    pass


@pytest.fixture(autouse=True)
def _patch_wait(monkeypatch):
    cache_plugin.MAX_SLEEP_STARTUP_SECONDS = 0
