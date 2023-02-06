# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import aiohttp.web
import pytest

import fleet_dashboard.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['fleet_dashboard.generated.service.pytest_plugins']


@pytest.fixture
def headers() -> dict:
    return {
        'X-Ya-User-Ticket': 'user_ticket',
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-Login': 'tarasalk',
        'X-Yandex-UID': '123',
        'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
        'X-Real-IP': '127.0.0.1',
    }


@pytest.fixture
def mock_parks(mock_fleet_parks):
    @mock_fleet_parks('/v1/parks/list')
    async def _parks(request):
        if request.json['query']['park']['ids'] == [
                '7ad36bc7560449998acbe2c57a75c293',
        ]:
            return aiohttp.web.json_response(
                {
                    'parks': [
                        {
                            'id': '7ad36bc7560449998acbe2c57a75c293',
                            'name': 'park_name',
                            'login': 'park_login',
                            'is_active': True,
                            'city_id': 'Moscow',
                            'tz_offset': 3,
                            'locale': 'ru',
                            'is_billing_enabled': True,
                            'is_franchising_enabled': True,
                            'country_id': 'rus',
                            'demo_mode': False,
                            'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                        },
                    ],
                },
            )
        if request.json['query']['park']['ids'] == [
                'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
        ]:
            return aiohttp.web.json_response(
                {
                    'parks': [
                        {
                            'id': 'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
                            'name': 'park_name',
                            'login': 'park_login',
                            'is_active': True,
                            'city_id': 'Moscow',
                            'tz_offset': 3,
                            'locale': 'ru',
                            'is_billing_enabled': True,
                            'is_franchising_enabled': True,
                            'country_id': 'rus',
                            'demo_mode': False,
                            'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                            'specifications': ['taxi', 'saas'],
                        },
                    ],
                },
            )
        return aiohttp.web.json_response({'parks': []})


@pytest.fixture
def mock_territories_api(mockserver):
    @mockserver.json_handler('/territories/v1/countries/list')
    async def _territories(request, **kwargs):
        return {'countries': [{'_id': 'rus', 'currency': 'RUB'}]}
