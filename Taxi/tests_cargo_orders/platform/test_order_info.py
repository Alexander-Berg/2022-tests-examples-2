import pytest

from testsuite.utils import matching

DEFAULT_HEADERS = {'Accept-Language': 'en'}

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


@pytest.mark.parametrize(
    'driver_profile_id, park_id, expected_status',
    [
        ('driver_id1', 'park_id1', 200),
        ('driver_id1', '', 404),
        ('driver', 'park_id1', 404),
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
        '/v1/pro-platform/order-info',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
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
        },
    )

    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.json() == {
            'performer': TEST_SIMPLE_JSON_PERFORMER_RESULT,
            'waybill': my_waybill_info,
            'status': matching.AnyString(),
        }
