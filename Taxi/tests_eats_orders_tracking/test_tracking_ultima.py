# pylint: disable=unused-variable
import pytest

TRACKING_URL = '/eats/v1/eats-orders-tracking/v1/tracking'


@pytest.mark.now('2020-10-28T18:20:00.00+00:00')
@pytest.mark.pgsql('eats_orders_tracking', files=['green_flow_payload.sql'])
async def test_ultima(taxi_eats_orders_tracking, make_tracking_headers):
    headers = make_tracking_headers(eater_id='eater1')
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=headers,
    )
    assert response.status_code == 200
    order = response.json()['payload']['trackedOrders'][0]

    assert order['color_scheme'] == 'ultima'
