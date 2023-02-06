import aiohttp.web
import pytest

ENDPOINT = '/reports-api/v1/parks-rating/metrics/chart-data'

DISTANCE = 5


@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=DISTANCE)
@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
@pytest.mark.now('2021-05-04T12:48:44.477345+03:00')
async def test_success(web_app_client, headers, mock_fleet_parks, load_json):
    fleet_parks_stub = load_json('fleet_parks.json')

    @mock_fleet_parks('/v1/parks/list')
    async def _v1_parks_list(request):
        assert request.json == fleet_parks_stub['request']
        return aiohttp.web.json_response(fleet_parks_stub['response'])

    response = await web_app_client.get(
        ENDPOINT,
        headers=headers,
        params={'period': '2021-04', 'metric': 'bad_marks'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == {
        'items': [
            {'compared': 8.0, 'own': 135.71, 'date_at': '2021-04-01'},
            {'compared': 7.0, 'own': 1.71, 'date_at': '2021-04-02'},
            {'compared': 6.0, 'own': 2.71, 'date_at': '2021-04-03'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-04'},
            {'compared': 5.0, 'own': 3.71, 'date_at': '2021-04-05'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-06'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-07'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-08'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-09'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-10'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-11'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-12'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-13'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-14'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-15'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-16'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-17'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-18'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-19'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-20'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-21'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-22'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-23'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-24'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-25'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-26'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-27'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-28'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-29'},
            {'compared': 0.0, 'own': 0.0, 'date_at': '2021-04-30'},
        ],
        'parks': {
            'compared': {
                'name': 'новыйпарк3',
                'rank': 79,
                'tier': 'bronze',
                'priority': 'second',
            },
            'own': {'name': 'Sea bream', 'rank': 33, 'tier': 'bronze'},
        },
    }


@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=DISTANCE)
@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
@pytest.mark.now('2021-05-04T12:48:44.477345+03:00')
async def test_empty(web_app_client, headers):
    response = await web_app_client.get(
        ENDPOINT,
        headers={**headers, 'X-Park-Id': '7ad36bc7560449998acbe2c57a75c292'},
        params={'period': '2021-04', 'metric': 'churn_rate'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == {'items': []}


@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=DISTANCE)
@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
@pytest.mark.now('2021-05-04T12:48:44.477345+03:00')
async def test_period_validator(web_app_client, headers):
    response = await web_app_client.get(
        ENDPOINT,
        headers=headers,
        params={'period': '2021-02', 'metric': 'bad_marks'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == {'items': []}
