import pytest


@pytest.mark.redis_store(
    ['set', 'Order:Driver:CompleteRequest:MD5:aaaa:bbbb', 'ETAG'],
    ['rpush', 'Order:Driver:CompleteRequest:Items:aaaa:bbbb', 'Hello1'],
    ['rpush', 'Order:Driver:CompleteRequest:Items:aaaa:bbbb', 'Hello2'],
    ['rpush', 'Order:Driver:CompleteRequest:Items:aaaa:bbbb', 'Hello3'],
    ['rpush', 'Order:Driver:CompleteRequest:Items:aaaa:bbbb', 'Hello4'],
    ['rpush', 'Order:Driver:CompleteRequest:Items:aaaa:bbbb', 'Hello5'],
    ['rpush', 'Order:Driver:CompleteRequest:Items:aaaa:bbbb', 'Hello6'],
    ['rpush', 'Order:Driver:CompleteRequest:Items:aaaa:bbbb', 'Hello7'],
    ['rpush', 'Order:Driver:CompleteRequest:Items:aaaa:bbbb', 'Hello8'],
    ['rpush', 'Order:Driver:CompleteRequest:Items:aaaa:bbbb', 'Hello9'],
    ['rpush', 'Order:Driver:CompleteRequest:Items:aaaa:bbbb', 'Hello10'],
    ['rpush', 'Order:Driver:CompleteRequest:Items:aaaa:bbbb', 'Hello11'],
    ['rpush', 'Order:Driver:CompleteRequest:Items:aaaa:bbbb', 'Hello12'],
)
async def test_complete_request(
        experiments3,
        taxi_contractor_order_setcar,
        redis_store,
        mockserver,
        taxi_config,
):
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

    assert (
        redis_store.get('Order:Driver:CompleteRequest:MD5:aaaa:bbbb')
        == b'ETAG'
    )
    response = await taxi_contractor_order_setcar.post(
        '/v1/order/complete',
        json={'park_id': 'aaaa', 'profile_id': 'bbbb', 'alias_id': 'cccc'},
    )
    assert response.json() == {}
    assert response.status_code == 200
    assert (
        redis_store.lrange(
            'Order:Driver:CompleteRequest:Items:aaaa:bbbb', 0, -1,
        )
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
    assert (
        redis_store.get('Order:Driver:CompleteRequest:MD5:aaaa:bbbb')
        != b'ETAG'
    )

    assert not push.has_calls
