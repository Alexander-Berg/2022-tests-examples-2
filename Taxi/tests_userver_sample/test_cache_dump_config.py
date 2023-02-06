import pytest


@pytest.fixture(name='set_dumps_enabled')
def _set_dumps_enabled(taxi_userver_sample, taxi_config, mocked_time):
    async def do_set(cache_name: str, value: bool):
        taxi_config.set(USERVER_DUMPS={cache_name: {'dumps-enabled': value}})
        await taxi_userver_sample.invalidate_caches()
        mocked_time.sleep(1)

    return do_set


async def test_toggle_dumps(taxi_userver_sample, set_dumps_enabled):
    cache_name = 'simple-dumped-cache'

    # Cache dumps are enabled by default for this cache
    await taxi_userver_sample.write_cache_dumps(names=[cache_name])

    # After disabling cache dumps, an attempt to force writing a cache dump
    # should fail
    await set_dumps_enabled(cache_name, False)
    with pytest.raises(AssertionError):
        await taxi_userver_sample.write_cache_dumps(names=[cache_name])

    # ...and cache dumps are working again
    await set_dumps_enabled(cache_name, True)
    await taxi_userver_sample.write_cache_dumps(names=[cache_name])


async def test_dumps_initially_disabled(
        taxi_userver_sample, set_dumps_enabled,
):
    cache_name = 'initially-non-dumped-cache'

    # Cache dumps are disabled by default for this cache
    with pytest.raises(AssertionError):
        await taxi_userver_sample.write_cache_dumps(names=[cache_name])

    # Cache dumps should turn on successfully
    await set_dumps_enabled(cache_name, True)
    await taxi_userver_sample.write_cache_dumps(names=[cache_name])

    # ...and cache dumps are off again
    await set_dumps_enabled(cache_name, False)
    with pytest.raises(AssertionError):
        await taxi_userver_sample.write_cache_dumps(names=[cache_name])
