"""Tests for NonMapDumpedCache

We test 3 scenarios:
1. the cache has successfully loaded a cache dump, then performed an update
2. the cache has failed to load a cache dump, then performed an update
3. the cache has loaded a cache dump, then failed to update
"""
import pytest


@pytest.fixture(name='check_has_updated_contents')
async def _check_has_updated_contents(
        taxi_userver_sample, taxi_userver_sample_monitor, query_cache,
):
    # Check the contents of the cache after update
    assert await query_cache('non-map-dumped-cache', 'qux') == {
        'value': 5,
        'foo': 42,
        'bar': ['hai', 'bai'],
    }

    # Compare the dumped contents with the ground truth
    await taxi_userver_sample.write_cache_dumps(names=['non-map-dumped-cache'])
    await taxi_userver_sample.read_cache_dumps(names=['non-map-dumped-cache'])

    metrics = await taxi_userver_sample_monitor.get_metric('cache')
    assert metrics['non-map-dumped-cache']['dump']['is-current-from-dump'] == 1


@pytest.mark.uservice_oneshot(config_hooks=['setup_userver_dumps'])
def test_loaded_updated(check_has_updated_contents):
    """
    We copy the contents of `static/test_cache_dump_simple/dumps` to the cache
    dump directory, then restart the service. The cache should load the dump,
    then perform an update, discarding the loaded contents.
    """


@pytest.mark.uservice_oneshot
def test_not_loaded_updated(check_has_updated_contents):
    """
    We use the main uservice instance. When the uservice started
    along with testsuite, the cache did not find any cache dumps, because
    the cache dump directory is left empty by default. Now it should perform
    an update.
    """


@pytest.mark.uservice_oneshot(
    config_hooks=['setup_userver_dumps'],
    disable_first_update=['non-map-dumped-cache'],
)
async def test_loaded_not_updated(taxi_userver_sample_monitor, query_cache):
    """
    We copy the contents of `static/test_cache_dump_simple/dumps` to the cache
    dump directory, then disable updates for our cache, then restart
    the service. The cache should load the dump, then fail to update, keeping
    the loaded contents.
    """
    # Check that the cache has the contents loaded from our cache dump
    assert await query_cache('non-map-dumped-cache', 'qux') == {
        'value': 5,
        'foo': 42,
        'bar': ['hai', 'bai'],
    }

    # Check that the data has come from the dump
    metrics = await taxi_userver_sample_monitor.get_metric('cache')
    assert metrics['non-map-dumped-cache']['dump']['is-current-from-dump'] == 1
