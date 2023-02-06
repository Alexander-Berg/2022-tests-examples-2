import urllib

import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from subvention_communications_plugins import *  # noqa: F403 F401


@pytest.fixture(autouse=True)
def mock_tariff_settings(mockserver):
    @mockserver.json_handler('/taxi-tariffs/v1/tariff_settings/list')
    def _mock_tariff_setting_list(request):
        params = urllib.parse.parse_qs(request.query_string.decode())
        cursor = params.get('cursor', [''])[0]
        if cursor == 'final':
            return {'zones': [], 'next_cursor': 'final'}
        return {
            'zones': [
                {'home_zone': 'moscow', 'timezone': 'Europe/Moscow'},
                {'home_zone': 'boryasvo', 'timezone': 'Europe/Moscow'},
                {'home_zone': 'vko', 'timezone': 'Europe/Moscow'},
                {'home_zone': 'svo', 'timezone': 'Europe/Moscow'},
                {'home_zone': 'spb', 'timezone': 'Europe/Moscow'},
                {'home_zone': 'samara', 'timezone': 'Europe/Samara'},
                {'home_zone': 'minsk', 'timezone': 'Europe/Minsk'},
            ],
            'next_cursor': 'final',
        }
