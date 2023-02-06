import pytest


@pytest.mark.config(
    ORDER_CORE_MONGO_SHARD_POOL_LIMIT={
        'enabled': True,
        'pool_limit_per_shard': 1,
        'timeout': 0,
    },
)
@pytest.mark.experiments3(filename='exp3_order_shards.json')
async def test_shard_pool_limit(taxi_order_core, testpoint):
    @testpoint('lock-taken')
    async def testpoint_lock_taken(data):
        result2 = await taxi_order_core.post(
            '/v1/tc/order-fields', json=params,
        )
        assert result2.status_code == 500

    params = {'order_id': 'order_1', 'fields': ['_id']}
    result = await taxi_order_core.post('/v1/tc/order-fields', json=params)
    assert result.status_code == 200
    assert result.json()['order_id'] == 'order_1'
    assert testpoint_lock_taken.times_called == 1
