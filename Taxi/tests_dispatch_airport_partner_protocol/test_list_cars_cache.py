import pytest

import tests_dispatch_airport_partner_protocol.utils as utils


@pytest.mark.now('2020-02-02T00:00:00+00:00')
@pytest.mark.config(
    DISPATCH_AIRPORT_PARTNER_PROTOCOL_LIST_CARS={
        'enabled': True,
        'data_ttl': 300,
        'updated_parkings': ['parking_lot1', 'parking_lot_fake'],
    },
)
async def test_list_cars_cache_update(
        taxi_dispatch_airport_partner_protocol,
        taxi_config,
        testpoint,
        mockserver,
        load_json,
):
    list_cars_response = load_json('list_cars_response.json')

    @mockserver.json_handler(
        '/sintegro-list-cars/YANDEX_SH_D/hs/parkings/list_cars',
    )
    def _list_cars(request):
        assert request.headers['X-API-Key'] == 'some_api_key'
        assert (
            request.headers['Authorization']
            == 'Basic c29tZV9sb2dpbjpzb21lX3Bhc3N3b3Jk'
        )
        return utils.form_list_cars_response(request, list_cars_response)

    @testpoint('list-cars-cache-finished')
    def list_cars_cache_finished(data):
        return data

    taxi_config.set_values(
        {'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json')},
    )

    await taxi_dispatch_airport_partner_protocol.enable_testpoints()
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    expected_data = load_json('expected_cache_data.json')

    cache_data = (await list_cars_cache_finished.wait_call())['data']
    assert cache_data == expected_data


@pytest.mark.config(
    DISPATCH_AIRPORT_PARTNER_PROTOCOL_LIST_CARS={
        'enabled': False,
        'data_ttl': 300,
        'updated_parkings': ['parking_lot1'],
    },
)
async def test_sintegro_disabled(
        taxi_dispatch_airport_partner_protocol,
        taxi_config,
        testpoint,
        mockserver,
        load_json,
):
    @mockserver.json_handler(
        '/sintegro-list-cars/YANDEX_SH_D/hs/parkings/list_cars',
    )
    def list_cars(request):
        assert False

    @testpoint('list-cars-cache-ignored')
    def list_cars_cache_ignored(data):
        return {}

    taxi_config.set_values(
        {'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json')},
    )

    await taxi_dispatch_airport_partner_protocol.enable_testpoints()
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    await list_cars_cache_ignored.wait_call()

    assert list_cars.times_called == 0


@pytest.mark.now('2020-02-02T00:00:00+00:00')
@pytest.mark.config(
    DISPATCH_AIRPORT_PARTNER_PROTOCOL_LIST_CARS={
        'enabled': True,
        'data_ttl': 300,
        'updated_parkings': ['parking_lot1'],
    },
)
@pytest.mark.parametrize('error_code', [400, 401, 403, 409, 429, 500])
async def test_sintegro_error_codes(
        taxi_dispatch_airport_partner_protocol,
        taxi_config,
        testpoint,
        mockserver,
        load_json,
        error_code,
):
    list_cars_response = load_json('list_cars_response.json')

    @mockserver.json_handler(
        '/sintegro-list-cars/YANDEX_SH_D/hs/parkings/list_cars',
    )
    def _list_cars(request):
        if request.json['parking_id'] == 'parking_lot1':
            return utils.form_list_cars_response(request, list_cars_response)
        return mockserver.make_response(json={}, status=error_code)

    @testpoint('list-cars-cache-finished')
    def list_cars_cache_finished(data):
        return data

    taxi_config.set_values(
        {'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json')},
    )

    await taxi_dispatch_airport_partner_protocol.enable_testpoints()
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    expected_data = load_json('expected_cache_data.json')

    cache_data = (await list_cars_cache_finished.wait_call())['data']
    assert cache_data == expected_data


@pytest.mark.now('2020-02-02T00:00:00+00:00')
@pytest.mark.config(
    DISPATCH_AIRPORT_PARTNER_PROTOCOL_LIST_CARS={
        'enabled': True,
        'data_ttl': 300,
        'updated_parkings': ['parking_lot1'],
    },
)
async def test_list_cars_cache_ttl(
        taxi_dispatch_airport_partner_protocol,
        taxi_config,
        testpoint,
        mockserver,
        load_json,
        mocked_time,
):
    list_cars_response = load_json('list_cars_response.json')

    @mockserver.json_handler(
        '/sintegro-list-cars/YANDEX_SH_D/hs/parkings/list_cars',
    )
    def _list_cars(request):
        #   Return data for first call only
        if _list_cars.times_called == 0:
            return utils.form_list_cars_response(request, list_cars_response)
        return {}

    @testpoint('list-cars-cache-finished')
    def list_cars_cache_finished(data):
        return data

    taxi_config.set_values(
        {'PARTNER_PARKING_AREAS': load_json('list_cars_parking_areas.json')},
    )

    await taxi_dispatch_airport_partner_protocol.enable_testpoints()
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()

    expected_data = load_json('expected_cache_data.json')
    #   Cache is updated twice at the start, remove one call
    list_cars_cache_finished.next_call()
    cache_data = (await list_cars_cache_finished.wait_call())['data']
    assert cache_data == expected_data

    #   Cache not expired, keep it
    mocked_time.sleep(4 * 60)
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    cache_data = (await list_cars_cache_finished.wait_call())['data']
    assert cache_data == expected_data

    #   Cache expired, remove it
    mocked_time.sleep(2 * 60)
    await taxi_dispatch_airport_partner_protocol.invalidate_caches()
    cache_data = (await list_cars_cache_finished.wait_call())['data']
    assert cache_data is None


@pytest.mark.now('2020-02-02T00:00:00+00:00')
@pytest.mark.config(
    DISPATCH_AIRPORT_PARTNER_PROTOCOL_LIST_CARS={
        'enabled': True,
        'data_ttl': 300,
        'updated_parkings': ['parking_lot1'],
    },
)
async def test_metrics(
        taxi_dispatch_airport_partner_protocol,
        taxi_dispatch_airport_partner_protocol_monitor,
        taxi_config,
        mockserver,
        load_json,
        mocked_time,
):
    list_cars_response = load_json('list_cars_response.json')

    @mockserver.json_handler(
        '/sintegro-list-cars/YANDEX_SH_D/hs/parkings/list_cars',
    )
    def _list_cars(request):
        return utils.form_list_cars_response(request, list_cars_response)

    taxi_config.set_values(
        {'PARTNER_PARKING_AREAS': load_json('partner_parking_areas.json')},
    )

    await taxi_dispatch_airport_partner_protocol.invalidate_caches(
        cache_names=['list-cars-cache'],
    )
    mocked_time.sleep(15)
    await taxi_dispatch_airport_partner_protocol.tests_control(
        invalidate_caches=False,
    )
    metrics = await taxi_dispatch_airport_partner_protocol_monitor.get_metric(
        'dispatch_airport_partner_protocol_metrics',
    )

    assert metrics['partner_driver_count']['parking_lot1'] == 2
