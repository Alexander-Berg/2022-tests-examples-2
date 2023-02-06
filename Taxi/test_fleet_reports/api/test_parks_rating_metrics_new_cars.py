import aiohttp.web
import pytest

ENDPOINT = '/reports-api/v1/parks-rating/metrics/new-cars'

DISTANCE = 5


@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=DISTANCE)
@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
@pytest.mark.now('2021-05-04T12:48:44.477345+03:00')
async def test_success(
        web_app_client, headers, mock_fleet_vehicles, load_json,
):
    fleet_vehicles_stub = load_json('fleet_vehicles.json')

    @mock_fleet_vehicles('/v1/vehicles/cache-retrieve')
    async def _v1_vehicles_cache_retrieve(request):
        assert request.query == {'consumer': 'fleet-reports'}
        assert request.json == fleet_vehicles_stub['request']
        return aiohttp.web.json_response(fleet_vehicles_stub['response'])

    response = await web_app_client.get(
        ENDPOINT, headers=headers, params={'period': '2021-03'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == {
        'items': [
            {
                'id': '91a8158bcd9e4123969c17864b8ec037',
                'is_new': True,
                'status': 'working',
                'callsign': 'B8250P77',
                'brand': 'BMW',
                'model': 'i8',
                'year': 2020,
                'number': 'B8250P77',
                'color': 'Серый',
                'price': 566672.0,
            },
            {
                'id': '91a94d67fc8941d5a97be3b6ebd34889',
                'is_new': False,
                'year': 2010,
            },
            {
                'id': '91866ddc70f74a94a0ff570ea9a08f42',
                'is_new': False,
                'status': 'working',
                'callsign': 'И324КА',
                'brand': 'BMW',
                'model': 'X6',
                'year': 2019,
                'number': 'A354TX777',
                'color': 'Красный',
            },
        ],
        'pagination': {'total': 3, 'page': 1, 'limit': 25},
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
    assert data == {
        'items': [],
        'pagination': {'limit': 25, 'page': 1, 'total': 0},
    }


@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=DISTANCE)
@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
@pytest.mark.now('2021-05-04T12:48:44.477345+03:00')
async def test_period_validator(web_app_client, headers):
    response = await web_app_client.get(
        ENDPOINT, headers=headers, params={'period': '2021-02'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == {
        'items': [],
        'pagination': {'limit': 25, 'page': 1, 'total': 0},
    }
