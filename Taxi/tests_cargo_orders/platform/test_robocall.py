import pytest

from testsuite.utils import matching

TEST_SIMPLE_JSON_PERFORMER_RESULT = {
    'car_id': 'car_id1',
    'car_model': 'some_car_model',
    'car_number': 'some_car_number',
    'driver_id': 'driver_id1',
    'is_deaf': False,
    'lookup_version': 1,
    'name': 'Kostya',
    'order_alias_id': '1234',
    'order_id': '9db1622e-582d-4091-b6fc-4cb2ffdc12c0',
    'park_clid': 'park_clid1',
    'park_id': 'park_id1',
    'park_name': 'some_park_name',
    'park_org_name': 'some_park_org_name',
    'phone_pd_id': 'phone_pd_id',
    'revision': 1,
    'tariff_class': 'cargo',
    'transport_type': 'electric_bicycle',
}


DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


async def call_and_check_robocall(
        taxi_cargo_orders,
        stq,
        my_waybill_info,
        default_order_id,
        fetch_order_client_robocall,
):
    response = await taxi_cargo_orders.post(
        'v1/pro-platform/robocall',
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'point_id': my_waybill_info['execution']['points'][0][
                'claim_point_id'
            ],
            'robocall_reason': 'client_not_responding',
        },
        headers=DEFAULT_HEADERS,
    )

    assert response.json() == {
        'performer': TEST_SIMPLE_JSON_PERFORMER_RESULT,
        'waybill': my_waybill_info,
        'status': matching.AnyString(),
    }

    assert response.status_code == 200

    point_id = my_waybill_info['execution']['points'][0]['point_id']

    assert stq.cargo_orders_client_robocall.times_called == 1
    stq_call = stq.cargo_orders_client_robocall.next_call()
    assert stq_call['id'] == f'{default_order_id}_{point_id}'

    kwargs = stq_call['kwargs']
    assert kwargs['cargo_order_id'] == default_order_id
    assert kwargs['point_id'] == point_id

    order_client_robocall = fetch_order_client_robocall(
        default_order_id, point_id,
    )
    assert order_client_robocall.status == 'calling'


@pytest.mark.parametrize(
    'driver_profile_id, park_id, expected_status',
    [
        ('driver_id1', 'park_id1', 409),
        ('driver_id1', '', 403),
        ('driver', 'park_id1', 403),
    ],
)
async def test_simple(
        taxi_cargo_orders,
        default_order_id,
        driver_profile_id,
        park_id,
        expected_status,
        mock_waybill_info,
        my_waybill_info,
):
    await taxi_cargo_orders.invalidate_caches()

    response = await taxi_cargo_orders.post(
        '/v1/pro-platform/robocall',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'point_id': my_waybill_info['execution']['points'][0][
                'claim_point_id'
            ],
            'performer_params': {
                'driver_profile_id': driver_profile_id,
                'park_id': park_id,
                'app': {
                    'version_type': '',
                    'version': '9.40',
                    'platform': 'android',
                },
                'remote_ip': '12.34.56.78',
            },
            'robocall_reason': 'client_not_responding',
        },
    )

    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.json() == {
            'performer': TEST_SIMPLE_JSON_PERFORMER_RESULT,
            'waybill': my_waybill_info,
            'status': matching.AnyString(),
        }
