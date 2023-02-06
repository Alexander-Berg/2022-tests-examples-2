# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from contractor_profiles_manager_plugins import *  # noqa: F403 F401


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
