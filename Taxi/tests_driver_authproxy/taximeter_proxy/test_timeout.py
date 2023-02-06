import pytest


@pytest.mark.driver_session(park_id='db1', session='session1', uuid='uuid1')
async def test_service_timeout(mockserver, request_post, driver_authorizer):
    @mockserver.json_handler('/driver/v1/auth/smth')
    def _504(request):
        raise mockserver.TimeoutError()

    response = await request_post(
        headers={
            'X-Driver-Session': 'session1',
            'X-YaTaxi-Park-Id': 'db1',
            'User-Agent': 'Taximeter 9.13 (1882)',
        },
    )
    assert response.status_code == 504
    assert response.json()['message'] == 'Authproxy upstream timeout'
