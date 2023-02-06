import pytest

# this handler is just a proxy to /internal/maas/v1/check-trip-requirements
# so we just check that it can correctly proxy its ok and fail response
@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
@pytest.mark.parametrize(
    'request_json, phone_id, expected_response',
    [
        pytest.param(
            {
                'coupon_id': 'maas30000002',
                'payload': {'waypoints': [[37.467, 55.736], [37.5, 55.5]]},
            },
            'active_phone_id',
            {'valid': True},
            id='valid',
        ),
        pytest.param(
            {
                'coupon_id': 'maas30000002',
                'payload': {'waypoints': [[37.5, 55.5]]},
            },
            'active_phone_id',
            {'valid': False, 'error_code': 'route_without_point_b'},
            id='invalid',
        ),
        pytest.param(
            {'coupon_id': 'maas30000002'},
            'active_phone_id',
            {'valid': False, 'error_code': 'no_route'},
            id='invalid_no_payload',
        ),
        pytest.param(
            {'coupon_id': 'maas30000002', 'payload': {}},
            'active_phone_id',
            {'valid': False, 'error_code': 'no_route'},
            id='invalid_no_waypoints',
        ),
    ],
)
async def test_validation(
        taxi_maas,
        mockserver,
        load_json,
        request_json,
        phone_id,
        expected_response,
):
    @mockserver.json_handler('/persuggest/internal/persuggest/v2/stops_nearby')
    def _stops_nearby(request):
        return mockserver.make_response(
            json=load_json('stops_nearby_response.json'),
        )

    await taxi_maas.invalidate_caches()

    response = await taxi_maas.post(
        '/internal/maas/v1/validate-maas-coupon',
        headers={
            'X-Yandex-Uid': 'user_uid',
            'X-YaTaxi-UserId': 'user_id',
            'X-YaTaxi-PhoneId': phone_id,
        },
        json=request_json,
    )
    assert response.status_code == 200
    assert response.json() == expected_response
