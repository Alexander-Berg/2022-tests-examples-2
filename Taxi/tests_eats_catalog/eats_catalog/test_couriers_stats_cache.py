import copy
import random

import pytest

VEHICLE_TYPES = (
    'pedestrian',
    'bicycle',
    'electric_bicycle',
    'motorcycle',
    'vehicle',
)
LOCATION_TYPES = ('nearby', 'near', 'far', 'faraway')
STATS_FIELDS = ('distance', 'tempo', 'fixTime')


def mangle_couriers_stats(data):
    data = copy.deepcopy(data)
    vehicle = random.choice(VEHICLE_TYPES)
    location = random.choice(LOCATION_TYPES)
    field = random.choice(STATS_FIELDS)
    data['payload'][vehicle][location][field] = round(random.uniform(0, 1), 5)
    return data


async def test_successful_update(taxi_eats_catalog, mockserver, load_json):
    core_response = load_json('couriers_stats_expected_response.json')

    @mockserver.json_handler('/eats-core/v1/export/settings/couriers-stats')
    def eats_core(_):
        return core_response

    response = await taxi_eats_catalog.get('ping')
    assert response.status_code == 200

    assert eats_core.times_called == 1


async def test_successive_cache_updates(
        taxi_eats_catalog, mockserver, load_json,
):
    core_response = load_json('couriers_stats_expected_response.json')
    responses = [mangle_couriers_stats(core_response) for _ in range(10)]
    updates_count = 0

    @mockserver.json_handler('/eats-core/v1/export/settings/couriers-stats')
    def eats_core(_):
        return responses[updates_count]

    for _ in range(len(responses)):
        await taxi_eats_catalog.invalidate_caches()
        updates_count += 1
        assert eats_core.times_called == updates_count


async def test_successive_updates_with_initial_failure(
        taxi_eats_catalog, mockserver, testpoint, taxi_config, load_json,
):
    await taxi_eats_catalog.invalidate_caches()

    default_stats = load_json('couriers_stats_expected_response.json')
    taxi_config.set_values({'EATS_CATALOG_COURIERS_STATS': default_stats})

    responses = [default_stats] + [
        mangle_couriers_stats(default_stats) for _ in range(2)
    ]
    updates_count = 0

    @mockserver.json_handler('/eats-core/v1/export/settings/couriers-stats')
    def eats_core(_):
        if updates_count == 0:
            return mockserver.make_response('bad request', status=400)
        return responses[updates_count]

    @testpoint('eats-eta-couriers-stats-cache-finish')
    def couriers_cache_testpoint(data):
        assert data == responses[updates_count]['payload']

    for _ in responses:
        await taxi_eats_catalog.invalidate_caches()
        updates_count += 1
        assert eats_core.times_called == updates_count

    assert couriers_cache_testpoint.times_called == updates_count


@pytest.mark.parametrize(
    'total_updates,failures', [(2, [1]), (5, [1, 2]), (10, [1, 3, 4, 7])],
)
async def test_failure_at_intermediary_update(
        taxi_eats_catalog,
        mockserver,
        testpoint,
        load_json,
        total_updates,
        failures,
):
    core_response = load_json('couriers_stats_expected_response.json')
    responses = [
        mangle_couriers_stats(core_response) for _ in range(total_updates)
    ]
    updates_count = 0
    last_success = 0

    @mockserver.json_handler('/eats-core/v1/export/settings/couriers-stats')
    def _eats_core(_):
        if updates_count in failures:
            return mockserver.make_response('bad request', status=400)
        return mockserver.make_response(
            json=responses[updates_count], status=200,
        )

    @testpoint('eats-eta-couriers-stats-cache-finish')
    def couriers_cache_testpoint(data):
        nonlocal last_success
        if updates_count in failures:
            assert data == responses[last_success]['payload']
        else:
            assert data == responses[updates_count]['payload']
            last_success = updates_count

    for _ in range(total_updates):
        await taxi_eats_catalog.invalidate_caches()
        updates_count += 1

    assert couriers_cache_testpoint.times_called == updates_count
