import pytest

ENDPOINT = '/reports-api/v1/parks-rating/period-distance'


@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=5)
@pytest.mark.now('2021-07-10T13:04:49+03:00')
async def test_success(web_app_client, headers):
    response = await web_app_client.get(ENDPOINT, headers=headers)

    assert response.status == 200

    data = await response.json()
    assert data == {'from': '2021-02'}
