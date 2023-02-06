# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from blender_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture(autouse=True)
def _promotions(mockserver):
    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        return {
            'stories': [],
            'fullscreens': [],
            'cards': [],
            'notifications': [],
            'promos_on_map': [],
            'eda_banners': [],
            'deeplink_shortcuts': [],
            'promos_on_summary': [],
            'showcases': [],
        }
