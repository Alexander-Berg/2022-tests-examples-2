import datetime

import pytest
import pytz

from . import utils


@pytest.mark.parametrize(
    'orders,expected_ids',
    [
        pytest.param(
            {
                'e0001': {
                    'picker_id': 'p0001',
                    'place_id': 1,
                    'state': 'new',
                    'estimated_picking_time': 100,
                },
                'e0002': {
                    'picker_id': 'p0002',
                    'place_id': 2,
                    'state': 'assigned',
                    'estimated_picking_time': 200,
                },
            },
            {'e0001', 'e0002'},
            id='not picked up',
        ),
        pytest.param(
            {
                'e0001': {
                    'picker_id': 'p0001',
                    'place_id': 1,
                    'state': 'cancelled',
                },
                'e0002': {
                    'picker_id': 'p0002',
                    'place_id': 2,
                    'state': 'complete',
                },
            },
            set(),
            id='finished orders',
        ),
        pytest.param(
            {
                'e0001': {
                    'picker_id': 'p0001',
                    'place_id': 1,
                    'state': 'packing',
                    'time_delta': datetime.timedelta(seconds=50),
                    'estimated_picking_time': 100,
                },
                'e0002': {
                    'picker_id': 'p0002',
                    'place_id': 2,
                    'state': 'paid',
                    'time_delta': datetime.timedelta(seconds=50),
                    'estimated_picking_time': 200,
                },
            },
            {'e0001', 'e0002'},
            id='time spent',
        ),
        pytest.param(
            {
                'e0001': {
                    'picker_id': 'p0001',
                    'place_id': 1,
                    'state': 'picked_up',
                    'time_delta': datetime.timedelta(seconds=150),
                    'estimated_picking_time': 100,
                },
                'e0002': {
                    'picker_id': 'p0002',
                    'place_id': 3,
                    'state': 'handing',
                    'time_delta': datetime.timedelta(seconds=0),
                    'estimated_picking_time': 200,
                },
                'e0003': {
                    'picker_id': 'p0003',
                    'place_id': 1,
                    'state': 'handing',
                    'time_delta': datetime.timedelta(seconds=350),
                    'estimated_picking_time': 300,
                },
            },
            {'e0001', 'e0003'},
            id='overflow',
        ),
    ],
)
@pytest.mark.parametrize('place_ids', [['1', '2']])
async def test_places_queue_length(
        orders,
        place_ids,
        expected_ids,
        taxi_eats_picker_orders,
        mocked_time,
        create_order,
        create_order_status,
        get_order_by_eats_id,
        get_last_order_status,
):
    def is_picking(state):
        return state not in {
            'new',
            'waiting_dispatch',
            'dispatching',
            'dispatch_failed',
            'assigned',
            'complete',
            'cancelled',
        }

    now = mocked_time.now().replace(tzinfo=pytz.utc)
    for eats_id, params in orders.items():
        order_id = create_order(
            eats_id=eats_id,
            picker_id=params['picker_id'],
            place_id=params['place_id'],
            state=params['state'],
            estimated_picking_time=params['estimated_picking_time']
            if 'estimated_picking_time' in params
            else None,
        )
        if is_picking(params['state']) and params['state'] != 'picking':
            create_order_status(
                order_id, 'picking', 0, created_at=now - params['time_delta'],
            )
            create_order_status(order_id, params['state'], 0)

    response = await taxi_eats_picker_orders.post(
        '/api/v1/places/queue-length', json={'place_ids': place_ids},
    )
    payload = response.json()['orders']

    assert response.status_code == 200
    assert expected_ids == {order['eats_id'] for order in payload}

    for resp_order in payload:
        eats_id = resp_order['eats_id']
        order_id = get_order_by_eats_id(eats_id)['id']
        orig_order = orders[eats_id]

        assert resp_order['place_id'] in place_ids
        assert int(resp_order['place_id']) == orig_order['place_id']
        assert resp_order['status'] == orig_order['state']
        assert (
            utils.parse_datetime(resp_order['status_created_at'])
            == get_last_order_status(order_id)['created_at']
        )

        assert 'estimated_picking_time' in resp_order
        assert 'remaining_picking_time' in resp_order
        assert 'estimated_dispatch_attempt_time' in resp_order

        if is_picking(resp_order['status']):
            started_picking_at = now - orig_order['time_delta']
            time_spent = now - started_picking_at
            time_left = (
                datetime.timedelta(
                    seconds=resp_order['estimated_picking_time'],
                )
                - time_spent
            )
            assert time_left == datetime.timedelta(
                seconds=resp_order['remaining_picking_time'],
            )
        else:
            assert (
                resp_order['remaining_picking_time']
                == resp_order['estimated_picking_time']
            )
