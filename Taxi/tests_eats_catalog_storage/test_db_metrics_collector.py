import pytest


DISABLE_PERIODIC = pytest.mark.config(
    EATS_CATALOG_STORAGE_ENABLE_METRICS_PERIODIC=False,
)


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_db_metrics_collector(taxi_eats_catalog_storage, testpoint):
    @testpoint('eats_catalog_storage_db_metrics_collected')
    def task_finished(data):
        return data

    await taxi_eats_catalog_storage.invalidate_caches(clean_update=True)
    await taxi_eats_catalog_storage.run_periodic_task(
        'eats_catalog_storage_collect_statistics',
    )

    response = await task_finished.wait_call()
    assert response['data']['place_count'] == 2
    assert response['data']['place_enabled_count'] == 1
    assert response['data']['zone_count'] == 3
    assert response['data']['zone_enabled_count'] == 3
    assert response['data']['place_pg_cache_size'] == 2
    assert response['data']['zone_pg_cache_size'] == 3
    assert response['data']['place_archived_count'] == 1
    assert response['data']['zone_archived_count'] == 1


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_db_metrics_collector_archived(
        taxi_eats_catalog_storage, testpoint,
):
    @testpoint('eats_catalog_storage_db_metrics_collected')
    def task_finished(data):
        return data

    await taxi_eats_catalog_storage.run_periodic_task(
        'eats_catalog_storage_collect_statistics',
    )

    # check pg caches has archived places and zones as well
    response = await task_finished.wait_call()
    assert response['data']['place_pg_cache_size'] == 2
    assert response['data']['zone_pg_cache_size'] == 3


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
@pytest.mark.parametrize(
    'times_called',
    [
        pytest.param(1, id='enabled'),
        pytest.param(0, marks=DISABLE_PERIODIC, id='disabled'),
    ],
)
async def test_db_metrics_collector_control(
        taxi_eats_catalog_storage, testpoint, times_called,
):
    @testpoint('eats_catalog_storage_db_metrics_collected')
    def task_finished(data):
        return data

    await taxi_eats_catalog_storage.invalidate_caches(clean_update=True)
    await taxi_eats_catalog_storage.run_periodic_task(
        'eats_catalog_storage_collect_statistics',
    )

    assert task_finished.times_called == times_called
