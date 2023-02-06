import pytest

ENDPOINT = '/reports-api/v1/parks-rating/thresholds'

DISTANCE = 4


@pytest.mark.now('2021-07-10T13:04:49+03:00')
@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=DISTANCE)
@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
async def test_success(web_app_client, headers):
    response = await web_app_client.get(
        ENDPOINT, headers=headers, params={'period': '2021-05'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == {
        'cars': {'current': 50, 'threshold': 20},
        'supply_hours': {'current': 3460.8, 'threshold': 2400},
    }


@pytest.mark.now('2021-07-10T13:04:49+03:00')
@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=DISTANCE)
@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
async def test_no_thresholds(web_app_client, headers):
    response = await web_app_client.get(
        ENDPOINT,
        headers={**headers, 'X-Park-Id': '7ad36bc7560449998acbe2c57a75c292'},
        params={'period': '2021-05'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == {}


@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=DISTANCE)
@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
async def test_park_not_found(web_app_client, headers):
    response = await web_app_client.get(
        ENDPOINT, headers=headers, params={'period': '2021-04'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == {}
