import pytest


@pytest.mark.redis_store(
    ['set', 'Order:Driver:CancelRequest:MD5:aaaa:bbbb', 'ETAG'],
    ['sadd', 'Order:Driver:Delayed:Items:aaaa:bbbb', 'delayed_order'],
    ['sadd', 'Order:Driver:Delayed:Items:aaaa:bbbb', 'delayed_order_2'],
)
async def test_delete_delayed(
        taxi_contractor_order_setcar, redis_store, mockserver, taxi_config,
):
    body = {'park_id': 'aaaa', 'profile_id': 'bbbb', 'alias_id': 'cccc'}
    assert (
        redis_store.get('Order:Driver:CancelRequest:MD5:aaaa:bbbb') == b'ETAG'
    )
    response = await taxi_contractor_order_setcar.post(
        '/v1/order/delayed', json=body,
    )
    assert response.status_code == 200
    assert response.json() == {}
    assert (
        redis_store.get('Order:Driver:CancelRequest:MD5:aaaa:bbbb') != b'ETAG'
    )
    assert redis_store.smembers('Order:Driver:Delayed:Items:aaaa:bbbb') == {
        b'delayed_order',
        b'delayed_order_2',
        b'cccc',
    }
