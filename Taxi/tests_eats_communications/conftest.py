# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from eats_communications_plugins import *  # noqa: F403 F401


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'eats_regions_cache: [eats_regions_cache] '
        'fixture for regions cache',
    )


@pytest.fixture(autouse=True)
def banners(mockserver):
    @mockserver.json_handler('/eda-catalog/v1/_internal/banner-places')
    def _banner_places(request):
        return {}


@pytest.fixture(autouse=True)
def collections(mockserver):
    @mockserver.json_handler('/eats-collections/internal/v1/collections')
    def _collections(request):
        return {}
