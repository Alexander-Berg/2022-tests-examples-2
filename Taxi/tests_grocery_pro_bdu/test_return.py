import pytest

from tests_grocery_pro_bdu import models


@pytest.mark.parametrize(
    'cargo_status, expected_status',
    [(200, 200), (403, 403), (403, 403), (404, 404), (409, 409)],
)
@models.TIMER_CONFIG_ETA_TEXT
@models.COMMON_CONFIG
async def test_simple(
        taxi_grocery_pro_bdu,
        default_order_id,
        cargo_status,
        expected_status,
        mockserver,
        my_waybill_pickup,
        load_json,
):
    @mockserver.json_handler('/cargo-orders/v1/pro-platform/return')
    def _mock_order_info(request):
        assert request.json == {
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'pickup_confirmation',
            'performer_params': {
                'app': {
                    'platform': 'android',
                    'version': '10.09 (2147483647)',
                    'version_type': '',
                },
                'driver_profile_id': 'driver_id1',
                'park_id': 'park_id1',
                'remote_ip': '12.34.56.78',
            },
            'point_id': 1,
            'location_data': {'a': []},
            'comment': 'комент 1',
            'reasons': ['reason1', 'reason2'],
        }
        if cargo_status == 200:
            return {
                'performer': models.TEST_SIMPLE_JSON_PERFORMER_RESULT,
                'waybill': my_waybill_pickup,
            }
        return mockserver.make_response(
            status=cargo_status,
            json={
                'code': 'state_mismatch',
                'message': 'confirmation conflict',
            },
        )

    response = await taxi_grocery_pro_bdu.post(
        '/driver/v1/grocery-pro-bdu/v1/cargo-ui/return',
        headers=models.AUTH_HEADERS_V1,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'pickup_confirmation',
            'point_id': 1,
            'location_data': {'a': []},
            'comment': 'комент 1',
            'reasons': ['reason1', 'reason2'],
        },
    )

    assert response.status_code == expected_status
    assert cargo_status == expected_status
    if expected_status == 200:
        example_ui = load_json('pickup_screen.json')
        assert response.json()['state']['ui'] == example_ui
