import pytest

from tests_eats_pro_orders_bdu import models


@pytest.mark.parametrize(
    'cargo_status, expected_status, batch',
    [
        (200, 200, True),
        (400, 400, True),
        (403, 403, True),
        (404, 404, True),
        (409, 409, True),
        (410, 410, True),
        (429, 429, True),
    ],
)
@pytest.mark.experiments3(filename='tracking_enabled.json')
@models.TIMER_CONFIG_ETA_TEXT
async def test_confirm(
        taxi_eats_pro_orders_bdu,
        default_order_id,
        cargo_orders,
        cargo_status,
        expected_status,
        cargo,
        batch,
        mock_driver_tags_v1_match_profile,
):

    req_json = {
        'cargo_ref_id': 'order/9db1622e-582d-4091-b6fc-4cb2ffdc12c0',
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
    }

    cargo_orders(
        '/cargo-orders/v1/pro-platform/exchange/confirm',
        req_json,
        default_order_id,
        cargo_status,
        cargo,
    )

    response = await taxi_eats_pro_orders_bdu.post(
        '/driver/v1/eats-pro-orders-bdu/v1/cargo-ui/exchange/confirm',
        headers=models.AUTH_HEADERS_V1,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'pickup_confirmation',
            'point_id': 1,
        },
    )

    assert response.status_code == expected_status
    assert cargo_status == expected_status
