CACHE_NAME = 'encrypted-dumped-cache'


async def test_dump_write_read(
        taxi_userver_sample, taxi_userver_sample_monitor, query_cache,
):
    """
    The cache dump directory is left empty by default. The cache should
    perform an update, then write a cache dump, then read it successfully.
    """
    # Check the contents of the cache after update. This check can be
    # omitted for production caches, where there is no special handle
    # for checking the data in the cache.
    assert await query_cache(CACHE_NAME, 'frobnication') == {
        'value': {'foo': 42, 'bar': [True, False], 'baz': 'what'},
    }

    # Write-read cycle
    await taxi_userver_sample.write_cache_dumps(names=[CACHE_NAME])
    await taxi_userver_sample.read_cache_dumps(names=[CACHE_NAME])

    # Check that the cache dump has been loaded successfully
    metrics = await taxi_userver_sample_monitor.get_metric('cache')
    assert metrics[CACHE_NAME]['dump']['is-current-from-dump'] == 1

    # Check the data loaded from the cache dump
    assert await query_cache(CACHE_NAME, 'frobnication') == {
        'value': {'foo': 42, 'bar': [True, False], 'baz': 'what'},
    }
