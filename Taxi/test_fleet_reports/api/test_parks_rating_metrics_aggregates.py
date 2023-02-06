import pytest

ENDPOINT = '/reports-api/v1/parks-rating/metrics/aggregates'

DISTANCE = 5


@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=DISTANCE)
@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
@pytest.mark.now('2021-05-04T12:48:44.477345+03:00')
async def test_success(web_app_client, headers):
    response = await web_app_client.get(
        ENDPOINT, headers=headers, params={'period': '2021-03'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == {
        'aggregates': {
            'bad_marks': {'value': 10.0, 'max_value': 250.0},
            'new_cars': {'value': 20.0, 'max_value': 250.0},
            'supply_hours': {'value': 30.0, 'max_value': 250.0},
            'churn_rate': {'value': 0.4, 'max_value': 250.0},
        },
        'total': {'value': 0.0, 'max_value': 1000.0},
    }


@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=DISTANCE)
@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
@pytest.mark.now('2021-05-04T12:48:44.477345+03:00')
async def test_empty(web_app_client, headers):
    response = await web_app_client.get(
        ENDPOINT, headers=headers, params={'period': '2021-04'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == {}


@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=DISTANCE)
@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
@pytest.mark.now('2021-05-04T12:48:44.477345+03:00')
async def test_period_validator(web_app_client, headers):
    response = await web_app_client.get(
        ENDPOINT, headers=headers, params={'period': '2021-02'},
    )

    data = await response.json()
    assert data == {}
