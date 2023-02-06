import pytest

from taxi.clients import juggler_api

from test_clowny_alert_manager.helpers import juggler as juggler_helpers


@pytest.fixture(name='mock_juggler_context')
def _mock_juggler_context(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session(
        juggler_api.JUGGLER_API_URL + '/api/system/config_tree', 'GET',
    )
    def _juggler_system_config_tree(method, url, **kwargs):
        return response_mock(
            json={
                'jctl': {'new_check_downtime': 1200},
                'main': {
                    'default_check_ttl': 900,
                    'default_check_refresh_time': 90,
                },
            },
        )


@pytest.fixture(name='mock_juggler_get_checks')
def _mock_juggler_get_checks(load_json, patch_aiohttp_session, response_mock):
    def _wrapper(data, ignore_filters=False):
        @patch_aiohttp_session(
            juggler_api.JUGGLER_API_URL + '/api/checks/checks', 'GET',
        )
        def get_checks(method, url, **kwargs):
            assert 'Authorization' in kwargs['headers']
            assert kwargs['params']['do'] == 1
            return response_mock(
                json=juggler_helpers.apply_filters(
                    data, kwargs['params'], ignore_filters=ignore_filters,
                ),
            )

        return get_checks

    return _wrapper
