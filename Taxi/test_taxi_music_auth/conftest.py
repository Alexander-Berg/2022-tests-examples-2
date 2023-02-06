# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
# noqa: E501 pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name, duplicate-code
import pytest

from taxi.clients import driver_authorizer

from taxi_music_auth.generated.service.client_taxi_music import (
    plugin as taxi_music_plugin,
)  # noqa: F403 F401 E501 pylint: disable=C0301
from taxi_music_auth.generated.service.client_yandex_music import (
    plugin as yandex_music_plugin,
)  # noqa: F403 F401 E501 pylint: disable=C0301
import taxi_music_auth.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['taxi_music_auth.generated.service.pytest_plugins']


@pytest.fixture
def yandex_music_200_mock(patch, mock):
    @patch(
        'taxi_music_auth.generated.service.client_yandex_music.'
        'plugin.YandexMusicClient.make_api_request',
    )
    async def _make_request(*args, **kwargs):
        return yandex_music_plugin.APIResponse(
            status=200, data='{"key": "value"}', headers={},
        )


@pytest.fixture
def taxi_music_userinfo_200_mock(patch, mock):
    @patch(
        'taxi_music_auth.generated.service.client_taxi_music.'
        'plugin.TaxiMusicClient.get_userinfo',
    )
    async def _get_userinfo(*args, **kwargs):
        return taxi_music_plugin.APIResponse(
            status=200,
            data={
                'yandex_uid': 'test_yandex_uid',
                'order_id': 'test_order_id',
                'alias_id': 'test_alias_id',
            },
            headers={},
        )


@pytest.fixture
def mock_authorize_for_driver(monkeypatch):
    def authorize_for_driver(uuid='uuid', authorized=True):
        async def fake_session_check(*_, **__):
            if authorized:
                return {'uuid': uuid}
            raise driver_authorizer.AuthError()

        monkeypatch.setattr(
            'taxi.clients.driver_authorizer.'
            'DriverAuthorizerClient.check_driver_sessions',
            fake_session_check,
        )

    return authorize_for_driver
