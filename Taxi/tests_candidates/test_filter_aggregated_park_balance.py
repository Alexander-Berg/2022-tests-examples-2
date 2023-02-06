import pytest


@pytest.mark.config(
    CANDIDATES_AGGREGATED_PARK_BALANCE_CACHE={
        'enabled': True,
        'close_to_limit_delta': 10000,
        'update_balance_sec': 60,
        'update_close_to_limit_sec': 5,
    },
)
@pytest.mark.redis_store(
    ['hset', 'Aggregator:YandexClid', 'clid0', 'agg0'],
    ['sadd', 'Aggregator:Disable', 'agg1'],
    ['hset', 'Aggregator:agg0', 'BalanceLimitAlert', 20000.0],
    ['hset', 'Aggregator:Balance:agg0', 'dbid0', 30000.0],
)
async def test_aggregated_park_balance(taxi_candidates, driver_positions):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['partners/aggregated_park_balance'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 1
    assert drivers[0]['dbid'] == 'dbid0'
    assert drivers[0]['uuid'] == 'uuid0'
