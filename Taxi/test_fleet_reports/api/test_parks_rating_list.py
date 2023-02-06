import aiohttp.web
import pytest

ENDPOINT = '/reports-api/v1/parks-rating/list'

DISTANCE = 3


@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=DISTANCE)
@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
@pytest.mark.now('2021-07-04T12:48:44.477345+03:00')
async def test_success(web_app_client, headers, mock_fleet_parks, load_json):
    fleet_parks_stub = load_json('fleet_parks.json')

    @mock_fleet_parks('/v1/parks/list')
    async def _v1_parks_list(request):
        assert request.json == fleet_parks_stub['request']
        return aiohttp.web.json_response(fleet_parks_stub['response'])

    response = await web_app_client.get(
        ENDPOINT, headers=headers, params={'period': '2021-07'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == {
        'items': [
            {
                'name': 'новыйпарк3',
                'rank': 3,
                'tier': 'gold',
                'points': {
                    'bad_marks': 4.0,
                    'new_cars': 0.0,
                    'supply_hours': 0.0,
                    'churn_rate': 0.0,
                    'total': 0.0,
                },
            },
            {
                'id': '7ad36bc7560449998acbe2c57a75c293',
                'name': 'Sea bream',
                'rank': 33,
                'tier': 'silver',
                'points': {
                    'bad_marks': 5.0,
                    'new_cars': 64.29,
                    'supply_hours': 35.71,
                    'churn_rate': 50.0,
                    'total': 285.71,
                },
            },
            {
                'name': 'Berlin bream',
                'rank': 79,
                'tier': 'bronze',
                'points': {
                    'bad_marks': 3.0,
                    'new_cars': 0.0,
                    'supply_hours': 0.0,
                    'churn_rate': 0.0,
                    'total': 0.0,
                },
            },
        ],
    }


@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=DISTANCE)
@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
@pytest.mark.now('2021-07-04T12:48:44.477345+03:00')
async def test_empty(web_app_client, headers):
    response = await web_app_client.get(
        ENDPOINT, headers=headers, params={'period': '2021-06'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == {'items': []}


@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=DISTANCE)
@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
@pytest.mark.now('2021-07-04T12:48:44.477345+03:00')
async def test_period_validator(web_app_client, headers):
    response = await web_app_client.get(
        ENDPOINT, headers=headers, params={'period': '2021-02'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == {'items': []}
