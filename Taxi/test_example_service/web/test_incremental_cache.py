INCREMENTAL_CACHE_GET_URI = '/incremental_cache_value'


async def test_incremental_cache(taxi_example_service_web):
    await taxi_example_service_web.invalidate_caches()
    res = await taxi_example_service_web.get(INCREMENTAL_CACHE_GET_URI)
    assert res.status == 200
    assert (await res.json())['value'] == 1  # refresh_cache were called

    await taxi_example_service_web.invalidate_caches(clean_update=False)
    res = await taxi_example_service_web.get(INCREMENTAL_CACHE_GET_URI)
    assert res.status == 200
    assert (await res.json())['value'] == 2

    await taxi_example_service_web.invalidate_caches(clean_update=False)
    res = await taxi_example_service_web.get(INCREMENTAL_CACHE_GET_URI)
    assert res.status == 200
    assert (await res.json())['value'] == 3

    await taxi_example_service_web.invalidate_caches()
    res = await taxi_example_service_web.get(INCREMENTAL_CACHE_GET_URI)
    assert res.status == 200
    assert (await res.json())['value'] == 1
