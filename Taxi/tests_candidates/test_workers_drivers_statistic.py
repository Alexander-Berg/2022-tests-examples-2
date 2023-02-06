import asyncio


import pytest


async def wait_workers(taxi_candidates, testpoint):
    @testpoint('statistic_worker_start')
    def worker_start(stats):
        return

    @testpoint('statistic_worker_finish')
    def worker_finished(stats):
        return stats

    await taxi_candidates.enable_testpoints(no_auto_cache_cleanup=True)

    await worker_start.wait_call()
    return (await worker_finished.wait_call())['stats']


async def _check_driver_classes_statistic(redis_store):
    data = None
    for _ in range(20):
        data = redis_store.get('candidates:driver_classes_statistic:data')
        if data:
            break
        await asyncio.sleep(0.05)

    assert data


@pytest.mark.config(CANDIDATES_DRIVER_STATISTIC_ZONES=[])
async def test_fallback_and_worker(
        taxi_candidates, testpoint, driver_positions, redis_store,
):
    # dbid1_uuid3 drivers park(clid1) deactivated
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.195, 55.5]},
            {'dbid_uuid': 'dbid1_uuid3', 'position': [35, 55]},
        ],
    )

    # initialize taxi_candidates by request
    response = await taxi_candidates.get('ping')
    assert response.status_code == 200

    stats = await wait_workers(taxi_candidates, testpoint)
    total = stats['total']
    assert total
    assert total['total'] == 2
    assert total['allowed'] == 1
    assert total['disallows']['infra/deactivated_park_v2'] == 1
    assert 'classes' in total

    assert 'zones' in stats
    assert 'moscow' in stats['zones']
    assert '' in stats['zones']

    await _check_driver_classes_statistic(redis_store)


async def test_zone_config(
        taxi_candidates, testpoint, driver_positions, redis_store,
):
    # dbid1_uuid3 drivers park(clid1) deactivated
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.195, 55.5]},
            {'dbid_uuid': 'dbid1_uuid3', 'position': [35, 55]},
        ],
    )

    # initialize taxi_candidates by request
    response = await taxi_candidates.get('ping')
    assert response.status_code == 200

    stats = await wait_workers(taxi_candidates, testpoint)
    total = stats['total']
    assert total
    assert total['total'] == 2
    assert total['allowed'] == 1
    assert total['disallows']['infra/deactivated_park_v2'] == 1
    assert 'classes' in total

    assert 'zones' in stats
    assert 'moscow' in stats['zones']
    assert '' not in stats['zones']

    await _check_driver_classes_statistic(redis_store)
