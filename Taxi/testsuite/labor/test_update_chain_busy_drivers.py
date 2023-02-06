import json

import pytest


@pytest.mark.config(ROUTER_MAPS_ENABLED=False)
def test_update_chain_busy_drivers(taxi_labor, tracker, redis_store, now):
    tracker.set_driver(
        '999012_46037aeff0e942e0a31a17330bd931f0', now, 55.78, 37.56,
    )
    tracker.set_driver(
        '999012_a5709ce56c2740d9a536650f5390de0b', now, 55.783, 37.56,
    )

    taxi_labor.run_workers(['update-chain-busy-drivers'])

    assert len(redis_store.get('chain_busy_drivers:data')) > 0
    meta = json.loads(redis_store.get('chain_busy_drivers:meta'))
    assert meta['count'] == 2
    assert meta['version'] == 1


@pytest.mark.parametrize('busy_drivers_worker_enabled', [True, False])
def test_busy_drivers(
        taxi_labor,
        tracker,
        redis_store,
        now,
        taxi_config,
        busy_drivers_worker_enabled,
):
    taxi_config.set_values(
        dict(LABOR_BUSY_DRIVERS_WORKER_ENABLED=busy_drivers_worker_enabled),
    )
    taxi_labor.run_workers(['update-chain-busy-drivers'])

    if not busy_drivers_worker_enabled:
        assert 'busy_drivers:data' not in redis_store
        assert 'busy_drivers:meta' not in redis_store
        return

    assert len(redis_store.get('busy_drivers:data')) > 0
    meta = json.loads(redis_store.get('busy_drivers:meta'))
    assert meta['version'] == 1
