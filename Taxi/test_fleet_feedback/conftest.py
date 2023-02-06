# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import aiohttp.web
import pytest

import fleet_feedback.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['fleet_feedback.generated.service.pytest_plugins']


@pytest.fixture
def headers() -> dict:
    return {
        'X-Ya-User-Ticket': 'user_ticket',
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-Login': 'tarasalk',
        'X-Yandex-UID': '123',
        'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
        'X-Real-IP': '127.0.0.1',
        'Accept-Language': 'ru, ru',
    }


@pytest.fixture
def headers_support() -> dict:
    return {
        'X-Ya-User-Ticket': 'user_ticket',
        'X-Ya-User-Ticket-Provider': 'yandex_team',
        'X-Yandex-Login': 'tarasalk',
        'X-Yandex-UID': '123',
        'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
        'X-Real-IP': '127.0.0.1',
        'Accept-Language': 'ru, ru',
    }


@pytest.fixture
def mock_parks(mock_fleet_parks):
    park = {
        'parks': [
            {
                'id': '7ad36bc7560449998acbe2c57a75c293',
                'name': 'park_name',
                'login': 'park_login',
                'is_active': True,
                'city_id': 'Москва',
                'tz_offset': 3,
                'locale': 'ru',
                'is_billing_enabled': True,
                'is_franchising_enabled': True,
                'country_id': 'rus',
                'demo_mode': False,
                'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
            },
        ],
    }

    @mock_fleet_parks('/v1/parks/list')
    async def _parks(request):
        return aiohttp.web.json_response(park)

    return park


@pytest.fixture
def mock_dac_users(mock_dispatcher_access_control):
    @mock_dispatcher_access_control('/v1/parks/users/list')
    async def _users(request):
        return aiohttp.web.json_response(
            {
                'limit': 1,
                'offset': 0,
                'users': [
                    {
                        'created_at': '2018-01-01T00:00+00:00',
                        'id': '123',
                        'is_confirmed': True,
                        'is_enabled': True,
                        'is_superuser': True,
                        'is_usage_consent_accepted': True,
                        'park_id': '7ad36bc7560449998acbe2c57a75c293',
                        'passport_uid': '123',
                        'email': 'tarasalk@yandex.ru',
                        'group_name': 'Администратор',
                    },
                ],
            },
        )
