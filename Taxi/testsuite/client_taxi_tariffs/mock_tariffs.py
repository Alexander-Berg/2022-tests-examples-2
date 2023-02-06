import urllib

import pytest


@pytest.fixture
def mock_tariffs(mockserver, tariffs, load_json):
    @mockserver.json_handler('/taxi-tariffs/v1/tariffs')
    def mock_tariffs_list(request):
        return {'tariffs': tariffs.get_list()}

    return mock_tariffs_list


@pytest.fixture(name='tariff_settings')
def _tariff_settings(request, load_json):
    """
    For default tariff_settings:
    @pytest.mark.tariff_settings
    async def my_test(...)

    For custom tariff_settings:
    @pytest.mark.tariff_settings(filename='your_file.json')
    async def my_test(...)
    """
    context = TariffSettingsContext(load_json)

    for marker in request.node.iter_markers('tariff_settings'):
        context.add_by_marker(marker)

    return context


@pytest.fixture
def mock_tariff_settings(tariff_settings, mockserver):
    @mockserver.json_handler('/taxi-tariffs/v1/tariff_settings/list')
    def _mock_tariff_setting_list(request):
        params = urllib.parse.parse_qs(request.query_string.decode())
        cursor = params.get('cursor', [''])[0]
        if cursor == 'final':
            return {'zones': [], 'next_cursor': 'final'}
        return {'zones': tariff_settings.data, 'next_cursor': 'final'}


class TariffSettingsContext:
    data: dict = {}

    def __init__(self, load_json):
        self.load_json_func = load_json
        self.fill_data(filename='tariff_settings.json')

    def add_by_marker(self, marker):
        if 'filename' in marker.kwargs:
            self.fill_data(filename=marker.kwargs['filename'])
        if 'visibility_overrides' in marker.kwargs:
            home_zones = marker.kwargs['visibility_overrides']
            for zone in self.data:
                home_zone = zone['home_zone']
                if home_zone not in home_zones:
                    continue
                overrides = home_zones[home_zone]
                self._apply_visibility_overrides(zone, overrides)

    def fill_data(self, filename=None):
        self.data = self.load_json_func(filename)

    def _apply_visibility_overrides(self, zone_doc, overrides):
        categories = zone_doc['categories']
        for category in categories:
            category_name = category['name']
            if category_name not in overrides:
                continue
            override = overrides[category_name]
            category['visibility_settings'] = override


def pytest_configure(config):
    config.addinivalue_line('markers', 'tariff_settings: tariff settings')
