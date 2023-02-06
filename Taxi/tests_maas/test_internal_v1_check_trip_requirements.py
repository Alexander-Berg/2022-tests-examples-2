import pytest

import common


@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
async def test_ok(taxi_maas, load_json, mockserver):
    @mockserver.json_handler('/persuggest/internal/persuggest/v2/stops_nearby')
    def _stops_nearby(request):
        return mockserver.make_response(
            json=load_json('stops_nearby_response.json'),
        )

    await taxi_maas.invalidate_caches()

    response = await taxi_maas.post(
        '/internal/maas/v1/check-trip-requirements',
        headers={
            'X-Yandex-Uid': 'user_uid',
            'X-YaTaxi-UserId': 'user_id',
            'X-YaTaxi-PhoneId': 'active_phone_id',
        },
        json={
            'waypoints': [[37.5, 55.5], [37.467, 55.736]],
            'coupon': 'maas30000002',
        },
    )
    assert response.status_code == 200

    response_body = response.json()

    assert response_body['valid']
    assert 'failed_check_id' not in response_body


@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
@pytest.mark.parametrize(
    'waypoints, coupon, phone_id, expected_response',
    [
        pytest.param(
            [[37.5, 55.5], [37.467, 55.736]],
            'maas30000002',
            'active_phone_id',
            {'valid': True},
            id='valid',
        ),
        pytest.param(
            [[37.5, 55.5]],
            'maas30000002',
            'active_phone_id',
            {'valid': False, 'failed_check_id': 'route_without_point_b'},
            id='route_without_point_b',
        ),
        pytest.param(
            None,
            'maas30000002',
            'active_phone_id',
            {'valid': False, 'failed_check_id': 'no_route'},
            id='no_route',
        ),
        pytest.param(
            [[37.5, 55.5], [37.51, 55.52], [37.52, 55.53]],
            'maas30000002',
            'active_phone_id',
            {
                'valid': False,
                'failed_check_id': 'route_with_intermediate_stop',
            },
            id='route_with_intermediate_stop',
        ),
        pytest.param(
            [[37.467, 55.736], [38, 56]],
            'maas30000002',
            'active_phone_id',
            {'valid': True},
            id='valid_from_metro',  # we don't check route length
        ),
        pytest.param(
            [[38, 56], [37.467, 55.736]],
            'maas30000002',
            'active_phone_id',
            {'valid': True},
            id='valid_to_metro',  # we don't check route length
        ),
        pytest.param(
            [[38, 56], [38, 56]],
            'maas30000002',
            'active_phone_id',
            {
                'valid': False,
                'failed_check_id': 'route_points_too_far_from_metro',
            },
            id='route_points_too_far_from_metro',
        ),
        pytest.param(
            [[37.5, 55.5], [37.467, 55.736]],
            'invalid_coupon',
            'active_phone_id',
            {'valid': False, 'failed_check_id': 'subscription_unavailable'},
            id='coupon_in_subscription_!=_coupon_in_request',
        ),
        pytest.param(
            [[37.5, 55.5]],
            'invalid_coupon',
            'active_phone_id',
            {'valid': False, 'failed_check_id': 'subscription_unavailable'},
            id='route_without_point_b_and_invalid_coupon',
        ),
        pytest.param(
            [[37.5, 55.5], [37.467, 55.736]],
            'maas30000002',
            'active_phone_id_no_coupon',
            {'valid': False, 'failed_check_id': 'subscription_unavailable'},
            id='subscription_without_coupon',
        ),
        pytest.param(
            [[37.5, 55.5], [37.467, 55.736]],
            'maas30000002',
            'some_phone_id',
            {'valid': False, 'failed_check_id': 'subscription_unavailable'},
            id='user_without_subscription',
        ),
        pytest.param(
            [[37.5, 55.5], [37.467, 55.736]],
            'maas30000001',
            'reserved_phone_id',
            {'valid': False, 'failed_check_id': 'subscription_unavailable'},
            id='user_with_inactive_subscription',
        ),
    ],
)
async def test_checks(
        taxi_maas,
        load_json,
        mockserver,
        waypoints,
        coupon,
        phone_id,
        expected_response,
):
    @mockserver.json_handler('/persuggest/internal/persuggest/v2/stops_nearby')
    def _stops_nearby(request):
        response_file = 'stops_nearby_response.json'
        return mockserver.make_response(json=load_json(response_file))

    await taxi_maas.invalidate_caches()

    response = await taxi_maas.post(
        '/internal/maas/v1/check-trip-requirements',
        headers={
            'X-Yandex-Uid': 'user_uid',
            'X-YaTaxi-UserId': 'user_id',
            'X-YaTaxi-PhoneId': phone_id,
        },
        json={'waypoints': waypoints, 'coupon': coupon},
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
async def test_geo_checks_disabled(taxi_maas, taxi_config, load_json):
    taxi_config.set(
        MAAS_GEO_HELPER_SETTINGS={
            'geo_client_qos': {
                'validate_route': {'timeout-ms': 50, 'attempts': 1},
            },
            'route_validation_settings': {
                'enable_geo_checks': False,
                'ignore_geo_errors': False,
            },
            'geo_settings': load_json('geo_settings.json'),
        },
    )

    await taxi_maas.invalidate_caches()

    response = await taxi_maas.post(
        '/internal/maas/v1/check-trip-requirements',
        headers={
            'X-Yandex-Uid': 'user_uid',
            'X-YaTaxi-UserId': 'user_id',
            'X-YaTaxi-PhoneId': 'active_phone_id',
        },
        json={
            'waypoints': [[37.5, 55.5], [37.51, 55.52]],
            'coupon': 'maas30000002',
        },
    )

    assert response.status_code == 200

    response_body = response.json()

    assert response_body['valid']
    assert 'failed_check_id' not in response_body


@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
@pytest.mark.parametrize(
    'waypoints, expected_response',
    [
        pytest.param(
            [[37.5, 55.5], [37.467, 55.736]],
            {'valid': True},
            id='valid_metro',
        ),
        pytest.param(
            [[37.5, 55.5], [37.472, 55.730]],
            {'valid': True},
            id='valid_railway',
        ),
        pytest.param(
            [[38, 56], [37.48, 55.75]],
            {
                'valid': False,
                'failed_check_id': 'route_points_too_far_from_metro',
            },
            id='route_points_too_far_from_metro',
        ),
        pytest.param(
            [[37.449, 55.726], [38, 56]],
            {
                'valid': False,
                'failed_check_id': 'route_points_too_far_from_metro',
            },
            id='route_points_too_far_from_railway',
        ),
    ],
)
async def test_checks_with_railway(
        taxi_maas,
        load_json,
        mockserver,
        taxi_config,
        waypoints,
        expected_response,
):
    taxi_config.set(
        MAAS_GEO_HELPER_SETTINGS={
            'geo_client_qos': {},
            'route_validation_settings': {
                'enable_geo_checks': True,
                'ignore_geo_errors': False,
            },
            'geo_settings': load_json('geo_settings_with_railway.json'),
        },
    )

    @mockserver.json_handler('/persuggest/internal/persuggest/v2/stops_nearby')
    def _stops_nearby(request):
        request_json = request.json
        assert len(request_json['transport_types']) == 1
        assert request_json['transport_types'][0] in {'underground', 'railway'}
        assert request_json == common.create_stops_nearby_request(
            position=[37.62, 55.75],
            distance_meters=30000,
            pickup_points_type='identical',
            transfer_type='from_mt',
            routers={'bee': {'type': 'bee_line'}},
            transport_types=request_json['transport_types'],
            fetch_lines=False,
        )

        response_file = 'stops_nearby_response.json'
        if request_json['transport_types'] == ['railway']:
            response_file = 'stops_nearby_railway_response.json'

        return mockserver.make_response(json=load_json(response_file))

    await taxi_maas.invalidate_caches()

    assert _stops_nearby.times_called == 2

    response = await taxi_maas.post(
        '/internal/maas/v1/check-trip-requirements',
        headers={
            'X-Yandex-Uid': 'user_uid',
            'X-YaTaxi-UserId': 'user_id',
            'X-YaTaxi-PhoneId': 'active_phone_id',
        },
        json={'waypoints': waypoints, 'coupon': 'maas30000002'},
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
async def test_ok_with_cache_with_no_successfull_updates(
        taxi_maas, load_json, mockserver,
):
    response = await taxi_maas.post(
        '/internal/maas/v1/check-trip-requirements',
        headers={
            'X-Yandex-Uid': 'user_uid',
            'X-YaTaxi-UserId': 'user_id',
            'X-YaTaxi-PhoneId': 'active_phone_id',
        },
        json={
            'waypoints': [[37.5, 55.5], [37.467, 55.736]],
            'coupon': 'maas30000002',
        },
    )
    assert response.status_code == 200

    response_body = response.json()

    assert response_body['valid']
    assert 'failed_check_id' not in response_body


@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
async def test_ok_with_empty_cache(taxi_maas, load_json, mockserver):
    @mockserver.json_handler('/persuggest/internal/persuggest/v2/stops_nearby')
    def _stops_nearby(request):
        return mockserver.make_response(
            json=load_json('stops_nearby_empty_response.json'),
        )

    await taxi_maas.invalidate_caches()

    response = await taxi_maas.post(
        '/internal/maas/v1/check-trip-requirements',
        headers={
            'X-Yandex-Uid': 'user_uid',
            'X-YaTaxi-UserId': 'user_id',
            'X-YaTaxi-PhoneId': 'active_phone_id',
        },
        json={
            'waypoints': [[37.5, 55.5], [37.467, 55.736]],
            'coupon': 'maas30000002',
        },
    )
    assert response.status_code == 200

    response_body = response.json()

    assert response_body['valid']
    assert 'failed_check_id' not in response_body
