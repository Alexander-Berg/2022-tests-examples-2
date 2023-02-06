import json

import pytest

from tests_contractor_order_setcar import utils


@pytest.mark.parametrize(
    'client_events_enabled', [{'enable': True}, {'enable': False}],
)
@pytest.mark.redis_store(
    ['set', 'Order:Driver:CancelRequest:MD5:aaaa:bbbb', 'ETAG'],
    ['rpush', 'Order:Driver:CancelRequest:Items:aaaa:bbbb', 'Hello1'],
    ['rpush', 'Order:Driver:CancelRequest:Items:aaaa:bbbb', 'Hello2'],
    ['rpush', 'Order:Driver:CancelRequest:Items:aaaa:bbbb', 'Hello3'],
    ['rpush', 'Order:Driver:CancelRequest:Items:aaaa:bbbb', 'Hello4'],
    ['rpush', 'Order:Driver:CancelRequest:Items:aaaa:bbbb', 'Hello5'],
    ['rpush', 'Order:Driver:CancelRequest:Items:aaaa:bbbb', 'Hello6'],
    ['rpush', 'Order:Driver:CancelRequest:Items:aaaa:bbbb', 'Hello7'],
    ['rpush', 'Order:Driver:CancelRequest:Items:aaaa:bbbb', 'Hello8'],
    ['rpush', 'Order:Driver:CancelRequest:Items:aaaa:bbbb', 'Hello9'],
    ['rpush', 'Order:Driver:CancelRequest:Items:aaaa:bbbb', 'Hello10'],
    ['rpush', 'Order:Driver:CancelRequest:Items:aaaa:bbbb', 'Hello11'],
    ['rpush', 'Order:Driver:CancelRequest:Items:aaaa:bbbb', 'Hello12'],
    [
        'rpush',
        'Order:Driver:CancelReason:Items:aaaa:bbbb',
        '{"alias_id": "Hello", "message": "some text", "category": "unknown"}',
    ],
    ['sadd', 'Order:Driver:Delayed:Items:aaaa:bbbb', 'delayed_order'],
)
async def test_cancel_request(
        experiments3,
        taxi_contractor_order_setcar,
        redis_store,
        mockserver,
        taxi_config,
        client_events_enabled,
):
    taxi_config.set_values(
        {
            'CONTRACTOR_ORDER_SETCAR_ENABLE_CLIENT_EVENTS': (
                client_events_enabled
            ),
        },
    )
    experiments3.add_config(
        name='driver_orders_common_use_client_events_for_send_fields',
        match={'predicate': {'type': 'true'}, 'enabled': True},
        consumers=['driver-orders-common/contractor_park'],
        clauses=[],
        default_value={'enabled': True, 'fields': ['setcar_statuses']},
    )

    @mockserver.json_handler('/client-events/push')
    def push(request):
        return {'version': '123'}

    body = {
        'park_id': 'aaaa',
        'profile_id': 'bbbb',
        'alias_id': 'cccc',
        'cancel_reason': {'message': 'YA-message', 'category': 'unknown'},
    }
    assert (
        redis_store.get('Order:Driver:CancelRequest:MD5:aaaa:bbbb') == b'ETAG'
    )
    response = await taxi_contractor_order_setcar.post(
        '/v1/order/cancel', json=body, headers=utils.HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {}
    assert (
        redis_store.lrange('Order:Driver:CancelRequest:Items:aaaa:bbbb', 0, -1)
        == [
            b'Hello4',
            b'Hello5',
            b'Hello6',
            b'Hello7',
            b'Hello8',
            b'Hello9',
            b'Hello10',
            b'Hello11',
            b'Hello12',
            b'cccc',
        ]
    )
    reasons_content = redis_store.lrange(
        'Order:Driver:CancelReason:Items:aaaa:bbbb', 0, -1,
    )
    assert len(reasons_content) == 2
    actually_inserted = json.loads(reasons_content[1])
    assert actually_inserted['alias_id'] == 'cccc'
    assert actually_inserted['message'] == body['cancel_reason']['message']
    assert actually_inserted['category'] == body['cancel_reason']['category']
    assert (
        redis_store.get('Order:Driver:CancelRequest:MD5:aaaa:bbbb') != b'ETAG'
    )
    assert (
        redis_store.smembers('Order:Driver:Delayed:Items:aaaa:bbbb') == set()
    )
    assert not push.has_calls
