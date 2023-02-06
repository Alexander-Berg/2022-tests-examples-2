import aiohttp.web
import pytest

from taxi.clients import personal

ENDPOINT = '/reports-api/v1/parks-rating/metrics/bad-marks'

DISTANCE = 5

RESPONSE = {
    'items': [
        {
            'id': 'feddb2299044aaa654e2e4851ed43ed4',
            'rating_end': 4.76,
            'rating_trend': -0.01,
            'orders': 14,
            'cancel_orders': 2,
            'cancel_orders_percent': 14.29,
            'trips': 12,
            'trips_percent': 85.71,
            'bad_rated_trips': 0,
            'bad_rated_trips_percent': 0.0,
            'bad_driving_orders': 0,
            'car_condition_orders': 0,
            'no_trip_orders': 3,
            'rude_driver_orders': 0,
            'smell_car_orders': 1,
            'perfect_trips': 2,
            'perfect_trips_percent': 14.29,
            'full_name': 'Имярек Алексеев',
            'phone': '+79115553322',
        },
        {
            'id': 'a57d409d08a044fc9faab63aca100145',
            'rating_end': 4.83,
            'rating_trend': 0.01,
            'orders': 48,
            'cancel_orders': 0,
            'cancel_orders_percent': 0.0,
            'trips': 44,
            'trips_percent': 91.67,
            'bad_rated_trips': 0,
            'bad_rated_trips_percent': 0.0,
            'bad_driving_orders': 0,
            'car_condition_orders': 1,
            'no_trip_orders': 0,
            'rude_driver_orders': 0,
            'smell_car_orders': 0,
            'perfect_trips': 9,
            'perfect_trips_percent': 18.75,
        },
        {
            'id': 'f760b273bd63a89fa835527d63cf1615',
            'rating_end': 4.88,
            'rating_trend': -0.08,
            'orders': 118,
            'cancel_orders': 0,
            'cancel_orders_percent': 0.0,
            'trips': 108,
            'trips_percent': 91.53,
            'bad_rated_trips': 1,
            'bad_rated_trips_percent': 0.85,
            'bad_driving_orders': 0,
            'car_condition_orders': 0,
            'no_trip_orders': 0,
            'rude_driver_orders': 1,
            'smell_car_orders': 0,
            'perfect_trips': 27,
            'perfect_trips_percent': 22.88,
            'full_name': 'G G Yast',
            'phone': '+70006811011',
        },
    ],
    'pagination': {'total': 3, 'page': 1, 'limit': 25},
}


@pytest.mark.config(FLEET_REPORTS_PARKS_RATING_PERIOD_DISTANCE=DISTANCE)
@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
@pytest.mark.now('2021-05-04T12:48:44.477345+03:00')
async def test_success(
        web_app_client, headers, mock_driver_profiles, patch, load_json,
):
    driver_profiles_stub = load_json('driver_profiles.json')

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _v1_driver_profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-reports'}
        assert request.json == driver_profiles_stub['request']
        return aiohttp.web.json_response(driver_profiles_stub['response'])

    @patch('taxi.clients.personal.PersonalApiClient.bulk_retrieve')
    async def _bulk_retrieve(data_type, request_ids, log_extra=None):
        assert data_type == personal.PERSONAL_TYPE_PHONES
        return [
            {
                'id': 'fa866b5c515a48a8b0dee01a7d74b477',
                'phone': '+79115553322',
            },
            {
                'id': '7da1236a76e0405eb1307e1bffc07491',
                'phone': '+70006811011',
            },
        ]

    response = await web_app_client.get(
        ENDPOINT, headers=headers, params={'period': '2021-03'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == RESPONSE


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
async def test_success_support_mode(
        web_app_client,
        headers_support,
        mock_driver_profiles,
        patch,
        load_json,
):
    driver_profiles_stub = load_json('driver_profiles.json')

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _v1_driver_profiles_retrieve(request):
        assert request.query == {'consumer': 'fleet-reports'}
        assert request.json == driver_profiles_stub['request']
        return aiohttp.web.json_response(driver_profiles_stub['response'])

    @patch('taxi.clients.personal.PersonalApiClient.bulk_retrieve')
    async def _bulk_retrieve(data_type, request_ids, log_extra=None):
        assert data_type == personal.PERSONAL_TYPE_PHONES
        return [
            {
                'id': 'fa866b5c515a48a8b0dee01a7d74b477',
                'phone': '+79115553322',
            },
            {
                'id': '7da1236a76e0405eb1307e1bffc07491',
                'phone': '+70006811011',
            },
        ]

    items = []
    for item in RESPONSE['items']:
        if 'phone' in item:
            del item['phone']
        items.append(item)
    RESPONSE['items'] = items

    response = await web_app_client.get(
        ENDPOINT, headers=headers_support, params={'period': '2021-03'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == RESPONSE


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
