# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

from taxi.clients import personal

import fleet_drivers_scoring_reports.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'fleet_drivers_scoring_reports.generated.service.pytest_plugins',
]


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
def mock_personal_single_license(monkeypatch):
    def mock_single_personal(license_: str, license_pd_id: str):
        async def response_patch(*args, **kwargs):
            return {'license': license_, 'id': license_pd_id}

        monkeypatch.setattr(personal.PersonalApiClient, 'find', response_patch)

    return mock_single_personal
