# pylint: disable=redefined-outer-name
import pytest

import eats_startrek_notifications.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'eats_startrek_notifications.generated.service.pytest_plugins',
]


@pytest.fixture
def patch_get_startrack_tickets(patch_aiohttp_session, response_mock):
    def wrapper(tickets):
        @patch_aiohttp_session(
            'https://st-api.test.yandex-team.ru/v2/issues/_search', 'POST',
        )
        def get_tickets(*args, **kwargs):
            return response_mock(json=tickets)

        return get_tickets

    return wrapper
