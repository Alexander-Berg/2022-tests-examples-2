import pytest


@pytest.mark.uservice_oneshot
async def test_not_loaded_updated(
        taxi_userver_sample, taxi_userver_sample_monitor,
):
    await taxi_userver_sample.write_cache_dumps(names=['non-map-dumped-cache'])

    metrics = await taxi_userver_sample_monitor.get_metric('cache')
    dump_metrics = metrics['non-map-dumped-cache']['dump']

    # The cache started without loading a dump
    assert dump_metrics['is-loaded-from-dump'] == 0
    assert dump_metrics['is-current-from-dump'] == 0
    assert 'load-duration-ms' not in dump_metrics

    # A dump has been written
    assert dump_metrics['last-nontrivial-write']['time-from-start-ms'] > 0
    assert dump_metrics['last-nontrivial-write']['duration-ms'] > 0

    # The dump size is this case is a bit over 1KB, so rounded down to 1
    assert dump_metrics['last-nontrivial-write']['size-kb'] == 1


@pytest.mark.uservice_oneshot(
    config_hooks=['setup_userver_dumps'],
    disable_first_update=['non-map-dumped-cache'],
)
async def test_loaded(taxi_userver_sample, taxi_userver_sample_monitor):
    # No updates have been performed yet
    metrics = await taxi_userver_sample_monitor.get_metric('cache')
    dump_metrics = metrics['non-map-dumped-cache']['dump']

    # The cache started by loading a dump
    assert dump_metrics['is-loaded-from-dump'] == 1
    assert dump_metrics['is-current-from-dump'] == 1
    assert dump_metrics['load-duration-ms'] > 0

    # No new dumps have been written
    assert 'last-nontrivial-write' not in dump_metrics

    # The first update will be performed now
    await taxi_userver_sample.invalidate_caches(
        cache_names=['non-map-dumped-cache'],
    )

    metrics = await taxi_userver_sample_monitor.get_metric('cache')
    dump_metrics = metrics['non-map-dumped-cache']['dump']

    # The cache started by loading a dump, then performed an update
    assert dump_metrics['is-loaded-from-dump'] == 1
    assert dump_metrics['is-current-from-dump'] == 0
    assert dump_metrics['load-duration-ms'] > 0
