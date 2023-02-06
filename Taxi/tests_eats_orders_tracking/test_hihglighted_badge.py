# pylint: disable=unused-variable
import pytest

TRACKING_URL = '/eats/v1/eats-orders-tracking/v1/tracking'


@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@pytest.mark.experiments3(filename='exp3_widget_disabled.json')
async def test_widget_disabled_fallback_to_description(
        taxi_eats_orders_tracking, make_tracking_headers,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )
    assert response.status_code == 200
    assert (
        response.json()['payload']['trackedOrders'][0]['description']
        == 'Жёлтая плашка\n\nОписание'
    )
    assert (
        'highlighted_badge'
        not in response.json()['payload']['trackedOrders'][0]
    )
