# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import typing as tp

import aiohttp.web
import pytest

from taxi.clients import personal

import taxi_fleet.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301


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
        'X-YaTaxi-Fleet-Permissions': 'kis_art_drivers_column_view',
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
        'X-YaTaxi-Fleet-Permissions': 'kis_art_drivers_column_view',
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
                'specifications': ['taxi', 'delivery'],
            },
        ],
    }

    @mock_fleet_parks('/v1/parks/list')
    async def _parks(request):
        return aiohttp.web.json_response(park)

    return park


@pytest.fixture
def mock_parks_deu(mock_fleet_parks):
    park = {
        'parks': [
            {
                'id': '7ad36bc7560449998acbe2c57a75c293',
                'name': 'park_name',
                'login': 'park_login',
                'is_active': True,
                'city_id': 'Berlin',
                'tz_offset': 1,
                'locale': 'de',
                'is_billing_enabled': True,
                'is_franchising_enabled': True,
                'country_id': 'deu',
                'demo_mode': False,
                'provider_config': {'clid': '111111', 'type': 'production'},
                'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                'specifications': ['saas', 'taxi'],
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


@pytest.fixture
def mock_territories_countries_list(mockserver):
    @mockserver.json_handler('/territories/v1/countries/list')
    async def _territories(request, **kwargs):
        return {
            'countries': [{'_id': 'rus', 'currency': 'RUB', 'name': 'Россия'}],
        }


@pytest.fixture
def mock_personal_single_license(monkeypatch):
    def mock_single_personal(license_: str, license_pd_id: str):
        async def response_patch(*args, **kwargs):
            return {'license': license_, 'id': license_pd_id}

        monkeypatch.setattr(personal.PersonalApiClient, 'find', response_patch)

    return mock_single_personal


@pytest.fixture
def mock_personal_bulk_phones(monkeypatch):
    def mock_bulk_personal(pds_and_phones: tp.List[tp.Tuple[str, str]]):
        async def response_patch(*args, **kwargs):
            return [{'id': x[0], 'phone': x[1]} for x in pds_and_phones]

        monkeypatch.setattr(
            personal.PersonalApiClient, 'bulk_retrieve', response_patch,
        )

    return mock_bulk_personal


@pytest.fixture
def mock_personal_single_phone(monkeypatch):
    def mock_single_personal(phone_: str, phone_pd_id: str):
        async def response_patch(*args, **kwargs):
            return {'phone': phone_, 'id': phone_pd_id}

        monkeypatch.setattr(personal.PersonalApiClient, 'find', response_patch)

    return mock_single_personal
