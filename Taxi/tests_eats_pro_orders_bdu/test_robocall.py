import pytest

from tests_eats_pro_orders_bdu import models


@pytest.mark.parametrize('cargo', [{'batch': True}], indirect=True)
@pytest.mark.experiments3(filename='tracking_enabled.json')
@models.TIMER_CONFIG_ETA_TEXT
async def test_robocall_actions(
        taxi_eats_pro_orders_bdu,
        default_order_id,
        cargo_orders,
        load_json,
        cargo,
        robocall_actions,
        mock_driver_tags_v1_match_profile,
):
    cargo.waybill['execution']['points'][0]['visit_status'] = 'arrived'
    cargo.waybill['execution']['points'][0]['is_resolved'] = True
    cargo.waybill['execution']['points'][1]['visit_status'] = 'arrived'
    if cargo.batch is True:
        cargo.waybill['execution']['points'][1]['is_resolved'] = True
        cargo.waybill['execution']['points'][2]['visit_status'] = 'arrived'
        cargo.waybill['execution']['segments'][0]['status'] = 'pay_waiting'

    req_json = {
        'cargo_ref_id': 'order/9db1622e-582d-4091-b6fc-4cb2ffdc12c0',
        'performer_params': {
            'driver_profile_id': 'driver_id1',
            'park_id': 'park_id1',
            'app': {
                'version_type': '',
                'version': '10.09 (2147483647)',
                'platform': 'android',
            },
            'remote_ip': '12.34.56.78',
        },
        'point_id': 1,
        'robocall_reason': 'client_not_responding',
    }

    cargo_orders(
        '/cargo-orders/v1/pro-platform/robocall',
        req_json,
        default_order_id,
        200,
        cargo,
    )

    response = await taxi_eats_pro_orders_bdu.post(
        '/driver/v1/eats-pro-orders-bdu/v1/cargo-ui/robocall',
        headers=models.AUTH_HEADERS_V1,
        json={
            'cargo_ref_id': f'order/{default_order_id}',
            'point_id': cargo.waybill['execution']['points'][0][
                'claim_point_id'
            ],
            'robocall_reason': 'client_not_responding',
        },
    )

    assert response.status_code == 200
    assert response.json()['state']['point']['actions'][1] == {
        'free_conditions': [],
        'robocall_reason': 'client_not_responding',
        'title': 'some_title',
        'type': 'robocall',
    }
