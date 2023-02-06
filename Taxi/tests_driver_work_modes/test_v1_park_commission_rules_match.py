import pytest

from tests_driver_work_modes import utils

ENDPOINT = 'v1/park-commission-rules/match'


@pytest.mark.parametrize(
    'request_body,expected_response',
    [
        (
            {
                'park_id': 'park1',
                'driver_profile_id': 'driver1',
                'matching_at': '2019-01-01T00:00:00+0000',
                'payment_type': 'card',
                'order_status': 'normal',
            },
            'expected_response_null_calc_table.json',
        ),
        (
            {
                'park_id': 'park1',
                'driver_profile_id': 'driver9',
                'matching_at': '2019-01-01T00:00:00+0000',
                'payment_type': 'prepaid',
                'order_status': 'normal',
            },
            'expected_response_no_matching_rule_type.json',
        ),
        (
            {
                'park_id': 'park1',
                'driver_profile_id': 'driver2',
                'matching_at': '2019-01-01T00:00:00+0000',
                'payment_type': 'prepaid',
                'order_status': 'normal',
            },
            'expected_response_rule_type_disabled.json',
        ),
        (
            {
                'park_id': 'park1',
                'driver_profile_id': 'driver2',
                'matching_at': '2019-01-01T00:00:00+0000',
            },
            'expected_response_no_order.json',
        ),
        (
            {
                'park_id': 'park1',
                'driver_profile_id': 'driver2',
                'matching_at': '2019-01-01T00:00:00+0000',
                'payment_type': 'unknown',
                'order_status': 'normal',
            },
            'expected_response_unknown_payment_type.json',
        ),
        (
            {
                'park_id': 'park1',
                'driver_profile_id': 'driver3',
                'matching_at': '2019-01-01T00:00:00+0000',
                'payment_type': 'cash',
                'order_status': 'normal',
            },
            'expected_response_disabled.json',
        ),
        (
            {
                'park_id': 'park1',
                'driver_profile_id': 'driver2',
                'matching_at': '2019-01-01T00:00:00+0000',
                'payment_type': 'card',
                'order_status': 'normal',
            },
            'expected_response_with_fixed.json',
        ),
        (
            {
                'park_id': 'park1',
                'driver_profile_id': 'driver2',
                'matching_at': '2019-01-01T00:00:00+0000',
                'payment_type': 'card',
                'order_status': 'cancel',
            },
            'expected_response_is_zero.json',
        ),
        (
            {
                'park_id': 'park1',
                'driver_profile_id': 'driver4',
                'matching_at': '2019-01-01T00:00:00+0000',
                'payment_type': 'card',
                'order_status': 'normal',
            },
            'expected_response_with_subvention_amnesty.json',
        ),
        (
            {
                'park_id': 'park1',
                'driver_profile_id': 'driver9',
                'matching_at': '2019-01-01T00:00:00+0000',
                'payment_type': 'cash',
                'order_status': 'normal',
            },
            'expected_response_aggregator_platform_enabled.json',
        ),
        (
            {
                'park_id': 'park1',
                'driver_profile_id': 'driver10',
                'matching_at': '2019-01-01T00:00:00+0000',
                'payment_type': 'cash',
                'order_status': 'normal',
            },
            'expected_response_aggregator_platform_disabled.json',
        ),
        (
            {
                'park_id': 'park3',
                'driver_profile_id': 'driver6',
                'matching_at': '2019-01-01T00:00:00+0000',
                'payment_type': 'card',
                'order_status': 'normal',
            },
            'expected_response_not_found.json',
        ),
        (
            {
                'park_id': 'park3',
                'driver_profile_id': 'driver8',
                'matching_at': '2019-01-01T00:00:00+0000',
                'payment_type': 'card',
                'order_status': 'normal',
            },
            'expected_response_not_found.json',
        ),
        (
            {
                'park_id': 'park4',
                'driver_profile_id': 'driver11',
                'matching_at': '2019-01-01T00:00:00+0000',
                'payment_type': 'card',
                'order_status': 'normal',
            },
            'expected_response_billing_disabled.json',
        ),
        (
            {
                'park_id': 'park5',
                'driver_profile_id': 'driver12',
                'matching_at': '2019-01-01T00:00:00+0000',
                'payment_type': 'card',
                'order_status': 'normal',
            },
            'expected_response_driver_selfemployed.json',
        ),
    ],
)
async def test_ok(
        taxi_driver_work_modes,
        driver_profiles,
        driver_work_rules,
        mock_fleet_parks_list,
        load_json,
        request_body,
        expected_response,
):
    response = await taxi_driver_work_modes.post(ENDPOINT, json=request_body)

    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.parametrize(
    'request_body,expected_response',
    [
        (
            {
                'park_id': 'not_existed_park_id',
                'driver_profile_id': 'not_existed_driver_id',
                'matching_at': '2019-01-01T00:00:00+0000',
                'payment_type': 'card',
                'order_status': 'cancel',
            },
            {'code': 'driver_not_found', 'message': 'Driver not found'},
        ),
    ],
)
async def test_not_found(
        taxi_driver_work_modes,
        mockserver,
        driver_profiles,
        driver_work_rules,
        request_body,
        expected_response,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_parks_list(_):
        return {'parks': [utils.NICE_PARK]}

    response = await taxi_driver_work_modes.post(ENDPOINT, json=request_body)

    assert response.status_code == 404
    assert response.json() == expected_response
