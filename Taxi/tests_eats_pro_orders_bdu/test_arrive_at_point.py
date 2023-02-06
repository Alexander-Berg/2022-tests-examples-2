import datetime

import pytest

from tests_eats_pro_orders_bdu import models


def make_request_json(order_id):
    return {
        'cargo_ref_id': 'order/' + order_id,
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
    }


# cargo-orders handle does not return 400
@pytest.mark.parametrize(
    'cargo_status, expected_status, batch',
    [
        (200, 200, True),
        (403, 403, True),
        (404, 404, True),
        (409, 409, True),
        (500, 500, True),
    ],
)
@pytest.mark.experiments3(filename='tracking_enabled.json')
@models.TIMER_CONFIG_ETA_TEXT
async def test_arrive_at_point(
        taxi_eats_pro_orders_bdu,
        default_order_id,
        cargo_orders,
        cargo_status,
        expected_status,
        cargo,
        batch,
        mock_driver_tags_v1_match_profile,
):
    cargo_orders(
        '/cargo-orders/v1/pro-platform/arrive_at_point',
        make_request_json(default_order_id),
        default_order_id,
        cargo_status,
        cargo,
    )

    response = await taxi_eats_pro_orders_bdu.post(
        '/driver/v1/eats-pro-orders-bdu/v1/cargo-ui/arrive_at_point',
        headers=models.AUTH_HEADERS_V1,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'pickup_confirmation',
            'point_id': 1,
            'location_data': {'a': []},
        },
    )

    assert response.status_code == expected_status
    assert cargo_status == expected_status


@pytest.mark.now('2022-05-27T12:00:00.000000+03:00')
@pytest.mark.parametrize('batch', [False])
@pytest.mark.experiments3(
    filename='eats_pro_orders_bdu_newbie_lessons_by_items.json',
)
@pytest.mark.experiments3(filename='tracking_enabled.json')
@models.TIMER_CONFIG_ETA_TEXT
async def test_send_lesson(
        taxi_eats_pro_orders_bdu,
        default_order_id,
        cargo_orders,
        cargo,
        batch,
        stq,
        mock_driver_tags_v1_match_profile,
):

    cargo.waybill['execution']['points'][0]['visit_status'] = 'arrived'

    cargo_orders(
        '/cargo-orders/v1/pro-platform/arrive_at_point',
        make_request_json(default_order_id),
        default_order_id,
        200,
        cargo,
    )

    response = await taxi_eats_pro_orders_bdu.post(
        '/driver/v1/eats-pro-orders-bdu/v1/cargo-ui/arrive_at_point',
        headers=models.AUTH_HEADERS_V1,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'pickup_confirmation',
            'point_id': 1,
            'location_data': {'a': []},
        },
    )

    assert response.status_code == 200

    assert stq.contractor_statistics_view_trigger_update.times_called == 1
    result = stq.contractor_statistics_view_trigger_update.next_call()

    assert (
        result['id'] == 'driver_id1-some_trigger_name-2022-05-27T09:00:00+0000'
    )
    assert result['eta'] == datetime.datetime(2022, 5, 27, 9, 0, 20)
    assert result['kwargs']['trigger_name'] == 'some_trigger_name'
    assert result['kwargs']['driver_profile_id'] == 'driver_id1'
    assert result['kwargs']['park_id'] == 'park_id1'
