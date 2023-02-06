import json


import pytest


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.parametrize(
    'use_driver_status,driver_status,free,busy_drivers,order',
    (
        (True, 'online', False, False, None),
        (True, 'offline', True, True, None),
        (True, 'busy', True, True, None),
        (False, None, True, False, None),
        (False, None, False, True, None),
        (True, 'online', True, True, [{'id': '123', 'status': 'waiting'}]),
        (True, 'online', False, False, []),
    ),
)
def test_totw_driver_status(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        use_driver_status,
        driver_status,
        free,
        busy_drivers,
        order,
        db,
        config,
):
    @mockserver.json_handler('/driver_status/v2/statuses')
    def driver_status_handler(request):
        answer = {
            'statuses': [
                {
                    'park_id': 'ffff',
                    'driver_id': 'a5709ce56c2740d9a536650f5390de0b',
                    'status': driver_status,
                },
            ],
        }
        if driver_status != 'offline':
            answer['statuses'][0]['updated_ts'] = int(now.timestamp()) * 1000
        if order:
            answer['statuses'][0]['orders'] = order
        return mockserver.make_response(json.dumps(answer), status=200)

    config.set_values(dict(TAXIONTHEWAY_USE_DRIVER_STATUS=use_driver_status))
    tracker.set_driver(
        '999012_a5709ce56c2740d9a536650f5390de0b',
        now,
        55.73341076871702,
        37.58917997300821,
        free=free,
    )
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {
            '$set': {
                'order._type': 'soon',
                'order.status': 'pending',
                'order.taxi_status': 'assigned',
            },
        },
    )
    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content['status'] == 'search'
    if use_driver_status:
        assert driver_status_handler.has_calls
    else:
        assert not driver_status_handler.has_calls

    if busy_drivers:
        assert content['busycars']
        assert not content['freecars']
    else:
        assert not content['busycars']
        assert content['freecars']
