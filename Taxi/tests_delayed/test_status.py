import json

import pytest


@pytest.mark.pgsql('delayed_orders', files=['delayed_orders.sql'])
@pytest.mark.parametrize(
    'request_body,response_status,response_body',
    [
        (
            {'order_id': 'dispatched_order_id'},
            200,
            {
                'dispatched': True,
                'due': '2019-02-04T00:00:00+00:00',
                'dispatch_time': '2019-02-05T00:00:00+00:00',
            },
        ),
        (
            {'order_id': 'delayed_order_id'},
            200,
            {
                'dispatched': False,
                'due': '2019-02-02T00:00:00+00:00',
                'last_update_time': '2019-02-03T00:00:00+00:00',
            },
        ),
        ({'order_id': 'non_existing_order_id'}, 404, None),
        ({'some_wrong_key': 123}, 400, None),
    ],
)
async def test_status(
        taxi_delayed, request_body, response_status, response_body,
):
    response = await taxi_delayed.post('v1/status', request_body)

    assert response.status_code == response_status, response.content
    if response.status_code == 200:
        data = json.loads(response.content)
        assert data == response_body
