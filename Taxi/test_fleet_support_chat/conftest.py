# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import aiohttp.web
import pytest

from taxi.clients import personal

import fleet_support_chat.generated.service.pytest_init  # noqa: F401, E501 pylint: disable=C0301

pytest_plugins = ['fleet_support_chat.generated.service.pytest_plugins']


@pytest.fixture
def headers() -> dict:
    return {
        'Accept-Language': 'ru, ru',
        'X-Ya-User-Ticket': 'user_ticket',
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-Login': 'tarasalk',
        'X-Yandex-UID': '123',
        'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
        'X-Real-IP': '127.0.0.1',
    }


@pytest.fixture
def headers_support() -> dict:
    return {
        'Accept-Language': 'ru, ru',
        'X-Ya-User-Ticket': 'user_ticket',
        'X-Ya-User-Ticket-Provider': 'yandex_team',
        'X-Yandex-Login': 'tarasalk',
        'X-Yandex-UID': '123',
        'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
        'X-Real-IP': '127.0.0.1',
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
                'provider_config': {'clid': '111111', 'type': 'production'},
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
                        'id': 'dc7e031f6dd94512989d8c17dc6f2163',
                        'is_confirmed': True,
                        'is_enabled': True,
                        'is_superuser': True,
                        'is_usage_consent_accepted': True,
                        'park_id': '7ad36bc7560449998acbe2c57a75c293',
                        'passport_uid': '123',
                        'email': 'vasya@yandex.ru',
                        'group_id': '9330ae2ecbc646bab446b936b3048d11',
                        'group_name': 'Администратор',
                        'phone': '71112223344',
                        'display_name': 'vasya',
                    },
                ],
            },
        )


@pytest.fixture
def mock_personal_email_store(monkeypatch):
    def mock_email_store(email: str, email_pd_id: str):
        async def response_patch(*args, **kwargs):
            return {'email': email, 'id': email_pd_id}

        monkeypatch.setattr(
            personal.PersonalApiClient, 'store', response_patch,
        )

    return mock_email_store


@pytest.fixture
def mock_personal_single_license(monkeypatch):
    def mock_single_personal(license_: str, license_pd_id: str):
        async def response_patch(*args, **kwargs):
            return {'license': license_, 'id': license_pd_id}

        monkeypatch.setattr(personal.PersonalApiClient, 'find', response_patch)

    return mock_single_personal
