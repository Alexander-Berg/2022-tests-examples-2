import pytest

from taxi.clients import juggler_api


@pytest.fixture(name='mock_juggler_checks_remove_check')
def _mock_juggler_checks_remove_check(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session(
        juggler_api.JUGGLER_API_URL + '/api/checks/remove_check', 'POST',
    )
    def _checks_remove_check(method, url, **kwargs):
        assert 'Authorization' in kwargs['headers']
        assert kwargs['params']['do'] == 1
        params = kwargs['params']
        assert params['service_name'] == 'hejmdal'
        assert params['host_name'] == 'hejmdal_stable'

        return response_mock(json={'status': 200})

    return _checks_remove_check


async def test_alerts(web_app_client, mock_juggler_checks_remove_check):
    response = await web_app_client.post(
        '/v1/alerts/remove/',
        params={
            'service_id': 139,
            'branch_id': 1,
            'juggler_service': 'hejmdal',
        },
    )
    assert response.status == 200
