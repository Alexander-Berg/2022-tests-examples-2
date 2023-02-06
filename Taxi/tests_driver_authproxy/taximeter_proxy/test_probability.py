import pytest


@pytest.mark.driver_session(park_id='db1', session='session1', uuid='uuid1')
async def test_probability_percent_30_70(
        driver_authorizer, request_post, mockserver,
):
    """Very simple test to test if it works"""

    @mockserver.json_handler('/30/driver/v1/probability_percent/30_70')
    def _test_30(request):
        return {'id': 30}

    @mockserver.json_handler('/70/driver/v1/probability_percent/30_70')
    def _test_70(request):
        return {'id': 70}

    response = await request_post(
        'driver/v1/probability_percent/30_70',
        headers={
            'X-Driver-Session': 'session1',
            'X-YaTaxi-Park-Id': 'db1',
            'User-Agent': 'Taximeter 9.13 (1882)',
        },
    )
    assert response.status_code == 200
    assert response.json()['id'] in [30, 70]
