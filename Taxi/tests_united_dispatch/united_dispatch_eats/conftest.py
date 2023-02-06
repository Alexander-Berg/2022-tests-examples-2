# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest
from united_dispatch_eats_plugins import *  # noqa: F403 F401


@pytest.fixture(name='united_dispatch_unit')
def _united_dispatch_unit(taxi_united_dispatch_eats):
    return taxi_united_dispatch_eats
