import datetime


NOW = datetime.datetime.now(datetime.timezone.utc)


async def test_basic(
        taxi_grocery_delivery_conditions,
        grocery_surge,
        testpoint,
        mocked_time,
):
    mocked_time.set(NOW)

    @testpoint('grocery-delivery-conditions-surge-cache-update')
    def surge_cache_update(data):
        return data

    grocery_surge.add_record(
        legacy_depot_id='1',
        timestamp=(NOW - datetime.timedelta(seconds=10)).isoformat(),
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )
    grocery_surge.add_record(
        legacy_depot_id='1',
        timestamp=NOW.isoformat(),
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )
    grocery_surge.add_record(
        legacy_depot_id='1',
        timestamp=(NOW + datetime.timedelta(seconds=10)).isoformat(),
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )
    await taxi_grocery_delivery_conditions.invalidate_caches()

    surge_info_count = (await surge_cache_update.wait_call())['data']
    assert surge_info_count['surge-info-count'] == 2

    mocked_time.set(NOW + datetime.timedelta(seconds=10))
    await taxi_grocery_delivery_conditions.invalidate_caches()

    surge_info_count = (await surge_cache_update.wait_call())['data']
    assert surge_info_count['surge-info-count'] == 1

    mocked_time.set(NOW + datetime.timedelta(seconds=20))
    grocery_surge.add_record(
        legacy_depot_id='1',
        timestamp=(NOW + datetime.timedelta(seconds=21)).isoformat(),
        pipeline='calc_surge_grocery_v1',
        load_level=0,
    )
    await taxi_grocery_delivery_conditions.invalidate_caches(
        clean_update=False,
    )
    surge_info_count = (await surge_cache_update.wait_call())['data']
    assert surge_info_count['surge-info-count'] == 2

    mocked_time.set(NOW + datetime.timedelta(seconds=40))
    await taxi_grocery_delivery_conditions.invalidate_caches(
        clean_update=False,
    )
    surge_info_count = (await surge_cache_update.wait_call())['data']
    assert surge_info_count['surge-info-count'] == 1
