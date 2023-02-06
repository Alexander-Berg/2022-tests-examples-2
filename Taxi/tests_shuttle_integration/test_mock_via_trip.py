import pytest


TEST_SERVICE_AREAS_RESPONSE = {
    'service_area': [
        {
            'service_polygon_id': 'polygon_id0',
            'service_polygon': {
                'type': 'polygon',
                'coordinates': [
                    [[37.6425, 55.7349]],
                    [[37.2425, 55.8349]],
                    [[37.7425, 55.9349]],
                ],
            },
        },
    ],
}

TEST_DETAILS_RESPONSE = {
    'trip_id': 'trip_id0',
    'trip_details': {
        'trip_status': 'PENDING',
        'cancel_reason': 'System',
        'pickup': {'lat': 37.6425, 'lng': 55.7349},
        'dropoff': {'lat': 37.8425, 'lng': 50.7349},
        'pickup_eta': 1234567890,
        'dropoff_eta': 1234567890,
        'vehicle_info': {
            'license_plate': 'license_plate_0',
            'color': 'color_0',
            'model': 'model_0',
            'vfh_id': 'vfh_id_0',
            'current_location': {'lat': 37.8425, 'lng': 50.7349},
        },
        'driver_info': {
            'id': 'dbid0_uuid0',
            'first_name': 'name',
            'last_name': 'surname',
            'phone_number': '+12001001',
        },
        'trip_properties': ['trip_properties_0', 'trip_properties_1'],
    },
}

TEST_BOOK_RESPONSE = {'trip_id': 'trip_id0', 'trip_status': 'PENDING'}

TEST_CANCEL_RESPONSE = {'trip_id': 'trip_id0', 'trip_status': 'ARRIVED'}

TEST_BOARD_RESPONSE = None

TEST_QUOTA_RESPONSE = {
    'service_available': True,
    'unavailability_cause': 'OutOfServiceHours',
    'trip_quotes': [{'quote_trip_type': 'shared', 'pickup_eta_min': 56}],
}

TEST_REQUEST_RESPONSE = {
    'trips': [
        {
            'trip_id': 'trip_id_0',
            'trip_type': 'private',
            'pickup': {'lat': 37.8425, 'lng': 50.7349},
            'pickup_eta': 1289192,
            'pickup_distance': 12322,
            'pickup_walking_time_sec': 1800,
            'dropoff': {'lat': 38.8425, 'lng': 59.7349},
            'dropoff_eta': 213,
            'cost': 2132,
        },
    ],
}

MT_TST_API_KEY = 'mt_tst_api_key'
MT_API_KEY = 'mt_api_key'


@pytest.mark.parametrize(
    'method, url, client_name, body_or_get_params, expected_response',
    [
        (
            'get',
            '/via-trip/v1/service_areas/get',
            'mt',
            None,
            TEST_SERVICE_AREAS_RESPONSE,
        ),
        (
            'get',
            '/via-trip/v1/trips/details',
            None,
            '?trip_id=trip_id_0',
            TEST_DETAILS_RESPONSE,
        ),
        (
            'post',
            '/via-trip/v1/trips/book',
            'mt',
            {'trip_id': 'trip_id_0'},
            TEST_BOOK_RESPONSE,
        ),
        (
            'post',
            '/via-trip/v1/trips/cancel',
            'mt_tst',
            {'trip_id': 'trip_id_0'},
            TEST_CANCEL_RESPONSE,
        ),
        (
            'post',
            '/via-trip/v1/trips/board',
            'mt_tst',
            {'trip_id': 'trip_id_0'},
            TEST_BOARD_RESPONSE,
        ),
        (
            'post',
            '/via-trip/v1/trips/quote',
            'mt_tst',
            {
                'origin': {'lat': 37.8425, 'lng': 50.7349},
                'destination': {'lat': 37.8225, 'lng': 50.7349},
            },
            TEST_QUOTA_RESPONSE,
        ),
        (
            'post',
            '/via-trip/v1/trips/request',
            'mt_tst',
            {
                'origin': {'lat': 37.8425, 'lng': 50.7349},
                'destination': {'lat': 37.8225, 'lng': 50.7349},
                'passenger_info': {
                    'first_name': '111111',
                    'passenger_id': 'd1cf6a92-26ef-11ea-979b-02426df27c46',
                },
                'passenger_count': 2,
                'trip_properties': ['trip_properties_0'],
            },
            TEST_REQUEST_RESPONSE,
        ),
    ],
)
async def test_via_trip_mock(
        taxi_shuttle_integration,
        taxi_config,
        method,
        url,
        client_name,
        body_or_get_params,
        expected_response,
):
    api_keys = {'mt_tst': MT_TST_API_KEY, 'mt': MT_API_KEY}

    config_client = client_name or '__default__'
    taxi_config.set_values(
        {
            'SHUTTLE_INTEGRATION_VIA_TRIP_RESPONSES_TMP': {
                url: {config_client: expected_response or dict()},
            },
        },
    )

    request_api_key = api_keys.get(client_name) if client_name else MT_API_KEY
    headers = {'X-API-Key': request_api_key}
    if method == 'get':
        response = await taxi_shuttle_integration.get(
            url + (body_or_get_params or ''), headers=headers,
        )
    else:  # method == 'post'
        response = await taxi_shuttle_integration.post(
            url, body_or_get_params or {}, headers=headers,
        )

    assert response.status_code == 200
    if expected_response is not None:
        assert response.json() == expected_response


@pytest.mark.parametrize(
    'api_key, config_value, expected_code',
    [
        (MT_API_KEY, None, 500),
        (MT_TST_API_KEY, {}, 500),
        ('bla-bla', None, 401),
    ],
)
async def test_via_trip_error(
        taxi_shuttle_integration,
        taxi_config,
        api_key,
        config_value,
        expected_code,
):
    url = '/via-trip/v1/service_areas/get'

    if config_value is not None:
        taxi_config.set_values(
            {
                'SHUTTLE_INTEGRATION_VIA_TRIP_RESPONSES_TMP': {
                    url: config_value,
                },
            },
        )

    response = await taxi_shuttle_integration.get(
        url, headers={'X-API-Key': api_key},
    )
    assert response.status_code == expected_code
