# pylint: disable=C0302
import datetime
import json

import pytest
import pytz

DEFAULT_HEADER = {
    'X-Driver-Session': 'qwerty',
    'User-Agent': 'Taximeter 9.77 (456)',
    'Accept-Language': 'ru',
    'X-YaTaxi-Park-Id': 'dbid1',
    'X-YaTaxi-Driver-Profile-Id': 'driver1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.77 (456)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}

SELFREG_HEADER = {
    'X-Driver-Session': 'qwerty',
    'User-Agent': 'Taximeter 9.77 (456)',
    'Accept-Language': 'ru',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.77 (456)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}

VEHICLE_BINDING = {
    'profiles': [
        {
            'park_driver_profile_id': 'dbid1_driver1',
            'data': {'car_id': 'vehicle1'},
        },
    ],
}

VEHICLE_BINDING_FULL_BRANDING = {
    'profiles': [
        {
            'park_driver_profile_id': 'dbid1_driver1',
            'data': {'car_id': 'vehicle2'},
        },
    ],
}


def make_selfreg_rules_request(expected_request, headers):
    if 'X-YaTaxi-Driver-Profile-Id' not in headers:
        expected_request['profile_tags'] = ['selfreg_v2_profi_unreg']
        expected_request['profile_tariff_classes'] = [
            'courier',
            'econom',
            'express',
        ]
        expected_request['order_tariff_classes'] = [
            'courier',
            'econom',
            'express',
        ]
        expected_request['driver_branding'] = 'no_branding'


@pytest.mark.now('2020-10-31T16:10:00+0300')
@pytest.mark.parametrize(
    'bs_rules_select,bs_by_driver,response_data,lon,lat,tariff_zone,local_tz',
    [
        (
            'bs/rules_select.json',
            'bs/by_driver_commission.json',
            'good_response_no_commission.json',
            37.618423,
            55.751244,
            'moscow',
            'Europe/Moscow',
        ),
        (
            'bs/rules_select_commission.json',
            'bs/by_driver_commission.json',
            'good_response_commission.json',
            37.618423,
            55.751244,
            'moscow',
            'Europe/Moscow',
        ),
        (
            'bs/rules_select.json',
            'bs/by_driver.json',
            'good_response_1.json',
            37.618423,
            55.751244,
            'moscow',
            'Europe/Moscow',
        ),
        (
            'bs/rules_select.json',
            None,
            'good_response_1.json',
            37.618423,
            55.751244,
            'moscow',
            'Europe/Moscow',
        ),
        (
            'bs/rules_select_all_steps.json',
            'bs/by_driver_one_date.json',
            'good_response_2.json',
            37.618423,
            55.751244,
            'moscow',
            'Europe/Moscow',
        ),
        (
            'bs/rules_select.json',
            'bs/by_driver_between_steps.json',
            'good_response_between_steps.json',
            37.618423,
            55.751244,
            'moscow',
            'Europe/Moscow',
        ),
        (
            'bs/rules_select.json',
            'bs/by_driver_all_steps.json',
            'good_response_all_steps.json',
            37.618423,
            55.751244,
            'moscow',
            'Europe/Moscow',
        ),
        (
            'bs/rules_select.json',
            'bs/by_driver_all_steps.json',
            'good_response_all_steps.json',
            37.618423,
            55.751244,
            'moscow',
            'Europe/Moscow',
        ),
        (
            None,
            'bs/by_driver_all_steps.json',
            'good_response_empty.json',
            37.618423,
            55.751244,
            'moscow',
            'Europe/Moscow',
        ),
        (
            'bs/rules_select_with_tags.json',
            'bs/by_driver_with_tags_old_version.json',
            'tags_response_1.json',
            37.618423,
            55.751244,
            'moscow',
            'Europe/Moscow',
        ),
        (
            'bs/rules_select_two_brandings.json',
            None,
            'good_response_two_brandings.json',
            37.618423,
            55.751244,
            'moscow',
            'Europe/Moscow',
        ),
        (
            None,
            None,
            'good_response_empty.json',
            77,
            77,
            'moscow',
            'Europe/Moscow',
        ),
        pytest.param(
            'bs/rules_select.json',
            'bs/by_driver_between_steps.json',
            'good_response_constructor.json',
            37.618423,
            55.751244,
            'moscow',
            'Europe/Moscow',
            marks=[
                pytest.mark.translations(
                    taximeter_backend_driver_messages={
                        'subvention.daily_guarantee.local_sum_prefix': {
                            'ru': 'до',
                        },
                    },
                ),
            ],
        ),
        (
            'bs/rules_select_2.json',
            'bs/by_driver_fully_completed.json',
            'fully_completed_response.json',
            37.618423,
            55.751244,
            'moscow',
            'Europe/Moscow',
        ),
        pytest.param(
            'bs/rules_select_almaty.json',
            'bs/by_driver_almaty.json',
            'good_response_almaty.json',
            76.851250,
            43.222015,
            'almaty',
            'Asia/Almaty',
            marks=[
                pytest.mark.config(
                    CURRENCY_FORMATTING_RULES={
                        '__default__': {'__default__': 1},
                        'KAZ': {'__default__': 0, 'subvention-view': 2},
                    },
                ),
            ],
        ),
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_subvention_rules(
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        bss,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        bs_rules_select,
        bs_by_driver,
        response_data,
        lon,
        lat,
        tariff_zone,
        local_tz,
):
    start = datetime.datetime(2018, 9, 23)
    end = datetime.datetime(2018, 9, 25)
    timezone = pytz.timezone(local_tz)
    start_local = timezone.localize(start).astimezone(pytz.utc).isoformat()
    end_local = timezone.localize(end).astimezone(pytz.utc).isoformat()

    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'uuid')
    activity.add_driver('uuid', 50)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    if bs_rules_select:
        bss.add_rules(load_json(bs_rules_select))
    if bs_by_driver:
        bss.add_by_driver_subventions(load_json(bs_by_driver))

    response = await taxi_subvention_view.post(
        '/v1/nmfg/status',
        json={
            'lon': lon,
            'lat': lat,
            'from': start.strftime('%Y-%m-%d'),
            'to': end.strftime('%Y-%m-%d'),
            'types': ['daily_guarantee'],
        },
        headers=DEFAULT_HEADER,
    )

    assert response.status_code == 200
    data = response.json()
    assert data == load_json(response_data)

    if bs_rules_select is None:
        return

    assert activity.mock_dms.times_called == 1
    assert unique_drivers.mock_retrieve_by_profiles.times_called == 1
    assert candidates.mock_profiles.times_called == 1
    assert vehicles.vehicle_bindings.times_called == 1
    assert vehicles.cars_list.times_called == 1
    assert bss.rules_select.times_called == 1
    assert bss.by_driver.times_called == 1

    assert json.loads(activity.mock_dms.next_call()['request'].get_data()) == {
        'unique_driver_ids': ['uuid'],
    }
    assert json.loads(
        unique_drivers.mock_retrieve_by_profiles.next_call()[
            'request'
        ].get_data(),
    ) == {'profile_id_in_set': ['dbid1_driver1']}
    assert (
        json.loads(candidates.mock_profiles.next_call()['request'].get_data())
        == {
            'data_keys': ['classes', 'payment_methods'],
            'driver_ids': [{'dbid': 'dbid1', 'uuid': 'driver1'}],
        }
    )
    assert json.loads(
        vehicles.vehicle_bindings.next_call()['request'].get_data(),
    ) == {'id_in_set': ['dbid1_driver1']}
    assert (
        json.loads(vehicles.cars_list.next_call()['request'].get_data())
        == {
            'fields': {
                'car': [
                    'sticker_confirmed',
                    'lightbox_confirmed',
                    'amenities',
                    'brand',
                    'model',
                    'color',
                    'year',
                    'number',
                ],
            },
            'query': {'park': {'car': {'id': ['vehicle1']}, 'id': 'dbid1'}},
        }
    )

    assert json.loads(bss.rules_select.next_call()['request'].get_data()) == {
        'is_personal': False,
        'limit': 1000,
        'driver_branding': 'sticker',
        'profile_tags': [],
        'profile_tariff_classes': ['comfort', 'econom', 'vip'],
        'order_tariff_classes': ['comfort', 'econom', 'vip'],
        'status': 'enabled',
        'tariff_zone': tariff_zone,
        'time_range': {'end': end_local, 'start': start_local},
        'types': ['daily_guarantee'],
    }

    bs_by_driver_request = json.loads(
        bss.by_driver.next_call()['request'].get_data(),
    )

    assert bs_by_driver_request['time'] == '2020-10-31T13:10:00+00:00'
    assert bs_by_driver_request['unique_driver_id'] == 'uuid'


@pytest.mark.parametrize(
    'request_data,error',
    [
        (
            {
                'lon': 37.618423,
                'lat': 55.751244,
                'from': '2018-09-23',
                'to': '2018-09-24',
                'types': ['guarantee'],
            },
            400,
        ),
    ],
)
@pytest.mark.parametrize('headers', [DEFAULT_HEADER, SELFREG_HEADER])
@pytest.mark.geoareas(filename='geoareas.json')
async def test_subvention_rules_not_supported_type(
        taxi_subvention_view, driver_authorizer, request_data, error, headers,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')

    response = await taxi_subvention_view.post(
        '/v1/nmfg/status',
        json=request_data,
        headers=headers,
        params={'selfreg_token': 'selfreg_token'},
    )
    assert response.status_code == error


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize('headers', [DEFAULT_HEADER, SELFREG_HEADER])
async def test_subvention_rules_failed_get_by_driver(
        taxi_subvention_view,
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
        vehicles,
        load_json,
        driver_tags_mocks,
        mockserver,
        headers,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'uuid')
    activity.add_driver('uuid', 50)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['tag1', 'tag2'])

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    async def mock_bs_rules_select(request):
        content = json.loads(request.get_data())
        expected_request = {
            'is_personal': False,
            'status': 'enabled',
            'tariff_zone': 'moscow',
            'time_range': {
                'start': '2018-09-22T21:00:00+00:00',
                'end': '2018-09-23T21:00:00+00:00',
            },
            'driver_branding': 'sticker',
            'profile_tariff_classes': ['comfort', 'econom', 'vip'],
            'order_tariff_classes': ['comfort', 'econom', 'vip'],
            'profile_tags': ['tag1', 'tag2'],
            'types': ['daily_guarantee'],
            'limit': 1000,
        }
        make_selfreg_rules_request(expected_request, headers)
        assert content == expected_request
        return {'subventions': load_json('bs/rules_select.json')}

    @mockserver.json_handler('/billing_subventions/v1/by_driver')
    async def mock_bs_by_driver(request):
        return mockserver.make_response('', 500)

    response = await taxi_subvention_view.post(
        '/v1/nmfg/status',
        json={
            'lon': 37.618423,
            'lat': 55.751244,
            'from': '2018-09-23',
            'to': '2018-09-24',
            'types': ['daily_guarantee'],
        },
        headers=headers,
        params={'selfreg_token': 'selfreg_token'},
    )

    if 'X-YaTaxi-Driver-Profile-Id' in headers:
        assert response.status_code == 500
        assert mock_bs_by_driver.times_called != 0
    else:
        assert response.status_code == 200
        assert mock_bs_by_driver.times_called == 0
    assert mock_bs_rules_select.times_called != 0


@pytest.mark.now('2020-10-31T16:10:00+0300')
@pytest.mark.config(SUBVENTION_VIEW_USE_BY_DRIVER_FALLBACK_CACHE=True)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_subvention_rules_by_driver_fallback(
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        bss,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        mockserver,
        statistics,
):
    start = datetime.datetime(2018, 9, 23)
    end = datetime.datetime(2018, 9, 25)
    timezone = pytz.timezone('Europe/Moscow')
    start_local = timezone.localize(start).astimezone(pytz.utc).isoformat()
    end_local = timezone.localize(end).astimezone(pytz.utc).isoformat()
    lon = 37.618423
    lat = 55.751244

    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'uuid')
    activity.add_driver('uuid', 50)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    bss.add_rules(load_json('bs/rules_select.json'))
    bss.add_by_driver_subventions(load_json('bs/by_driver.json'))

    request_json = {
        'lon': lon,
        'lat': lat,
        'from': start.strftime('%Y-%m-%d'),
        'to': end.strftime('%Y-%m-%d'),
        'types': ['daily_guarantee'],
    }

    await taxi_subvention_view.post(
        '/v1/nmfg/status', json=request_json, headers=DEFAULT_HEADER,
    )

    @mockserver.json_handler('/billing_subventions/v1/by_driver')
    async def mock_bs_by_driver(request):
        return mockserver.make_response('', 500)

    statistics.fallbacks = ['subvention_view.bs-by_driver.fallback']

    response = await taxi_subvention_view.post(
        '/v1/nmfg/status', json=request_json, headers=DEFAULT_HEADER,
    )

    assert response.status_code == 200
    data = response.json()
    assert data == load_json('good_response_1.json')

    assert activity.mock_dms.times_called == 2
    assert unique_drivers.mock_retrieve_by_profiles.times_called == 2
    assert candidates.mock_profiles.times_called == 2
    assert vehicles.vehicle_bindings.times_called == 2
    assert vehicles.cars_list.times_called == 2
    assert bss.rules_select.times_called == 2
    assert bss.by_driver.times_called == 1
    assert mock_bs_by_driver.times_called == 0

    assert json.loads(activity.mock_dms.next_call()['request'].get_data()) == {
        'unique_driver_ids': ['uuid'],
    }
    assert json.loads(
        unique_drivers.mock_retrieve_by_profiles.next_call()[
            'request'
        ].get_data(),
    ) == {'profile_id_in_set': ['dbid1_driver1']}
    assert (
        json.loads(candidates.mock_profiles.next_call()['request'].get_data())
        == {
            'data_keys': ['classes', 'payment_methods'],
            'driver_ids': [{'dbid': 'dbid1', 'uuid': 'driver1'}],
        }
    )
    assert json.loads(
        vehicles.vehicle_bindings.next_call()['request'].get_data(),
    ) == {'id_in_set': ['dbid1_driver1']}
    assert (
        json.loads(vehicles.cars_list.next_call()['request'].get_data())
        == {
            'fields': {
                'car': [
                    'sticker_confirmed',
                    'lightbox_confirmed',
                    'amenities',
                    'brand',
                    'model',
                    'color',
                    'year',
                    'number',
                ],
            },
            'query': {'park': {'car': {'id': ['vehicle1']}, 'id': 'dbid1'}},
        }
    )

    assert json.loads(bss.rules_select.next_call()['request'].get_data()) == {
        'is_personal': False,
        'limit': 1000,
        'driver_branding': 'sticker',
        'profile_tags': [],
        'profile_tariff_classes': ['comfort', 'econom', 'vip'],
        'order_tariff_classes': ['comfort', 'econom', 'vip'],
        'status': 'enabled',
        'tariff_zone': 'moscow',
        'time_range': {'end': end_local, 'start': start_local},
        'types': ['daily_guarantee'],
    }

    bs_by_driver_request = json.loads(
        bss.by_driver.next_call()['request'].get_data(),
    )

    assert bs_by_driver_request['time'] == '2020-10-31T13:10:00+00:00'
    assert bs_by_driver_request['unique_driver_id'] == 'uuid'


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize('headers', [DEFAULT_HEADER, SELFREG_HEADER])
async def test_subvention_rules_failed_get_select_rules(
        taxi_subvention_view,
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
        vehicles,
        load_json,
        driver_tags_mocks,
        mockserver,
        headers,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'uuid')
    activity.add_driver('uuid', 50)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['tag1', 'tag2'])

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    async def mock_bs_rules_select(request):
        return mockserver.make_response('', 500)

    response = await taxi_subvention_view.post(
        '/v1/nmfg/status',
        json={
            'lon': 37.618423,
            'lat': 55.751244,
            'from': '2018-09-23',
            'to': '2018-09-24',
            'types': ['daily_guarantee'],
        },
        headers=headers,
        params={'selfreg_token': 'selfreg_token'},
    )
    assert response.status_code == 500
    assert mock_bs_rules_select.times_called != 0


@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'subvention.daily_guarantee.local_sum_prefix': {'ru': 'до'},
    },
)
@pytest.mark.parametrize(
    'bs_rules_select,bs_by_driver,response_data',
    [
        (
            'bs/rules_select.json',
            'bs/by_driver_between_steps.json',
            'good_response_constructor.json',
        ),
    ],
)
@pytest.mark.parametrize('headers', [DEFAULT_HEADER, SELFREG_HEADER])
@pytest.mark.geoareas(filename='geoareas.json')
async def test_subvention_rules_constructor_with_tags(
        taxi_subvention_view,
        driver_authorizer,
        unique_drivers,
        bss,
        activity,
        candidates,
        vehicles,
        load_json,
        driver_tags_mocks,
        bs_rules_select,
        bs_by_driver,
        response_data,
        headers,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'uuid')
    activity.add_driver('uuid', 50)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['luxary'])

    bss.add_rules(load_json(bs_rules_select))
    bss.add_by_driver_subventions(load_json(bs_by_driver))
    await taxi_subvention_view.invalidate_caches()

    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')

    response = await taxi_subvention_view.post(
        '/v1/nmfg/status',
        json={
            'lon': 37.618423,
            'lat': 55.751244,
            'from': '2018-09-23',
            'to': '2018-09-25',
            'types': ['daily_guarantee'],
        },
        headers=headers,
        params={'selfreg_token': 'selfreg_token'},
    )
    bss.clean_rules()
    bss.clean_by_driver_subvention()
    data = response.json()

    assert response.status_code == 200
    if 'X-YaTaxi-Driver-Profile-Id' in headers:
        assert data == load_json(response_data)

    assert bss.rules_select.times_called == 1
    expected_request = {
        'is_personal': False,
        'limit': 1000,
        'driver_branding': 'sticker',
        'profile_tags': ['luxary'],
        'profile_tariff_classes': ['comfort', 'econom', 'vip'],
        'order_tariff_classes': ['comfort', 'econom', 'vip'],
        'status': 'enabled',
        'tariff_zone': 'moscow',
        'time_range': {
            'end': '2018-09-24T21:00:00+00:00',
            'start': '2018-09-22T21:00:00+00:00',
        },
        'types': ['daily_guarantee'],
    }
    make_selfreg_rules_request(expected_request, headers)
    assert (
        json.loads(bss.rules_select.next_call()['request'].get_data())
        == expected_request
    )


@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'subvention.daily_guarantee.local_sum_prefix': {'ru': 'до'},
    },
)
@pytest.mark.parametrize(
    'bs_rules_select,bs_by_driver',
    [
        (
            'bs/rules_select_two_brandings.json',
            'bs/by_driver_two_brandings.json',
        ),
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize('headers', [DEFAULT_HEADER, SELFREG_HEADER])
async def test_subvention_rules_constructor_with_branding(
        taxi_subvention_view,
        driver_authorizer,
        unique_drivers,
        bss,
        activity,
        candidates,
        vehicles,
        load_json,
        driver_tags_mocks,
        bs_rules_select,
        bs_by_driver,
        headers,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'uuid')
    activity.add_driver('uuid', 50)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING_FULL_BRANDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['luxary'])

    bss.add_rules(load_json(bs_rules_select))
    bss.add_by_driver_subventions(load_json(bs_by_driver))
    await taxi_subvention_view.invalidate_caches()

    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')

    response = await taxi_subvention_view.post(
        '/v1/nmfg/status',
        json={
            'lon': 37.618423,
            'lat': 55.751244,
            'from': '2018-09-23',
            'to': '2018-09-25',
            'types': ['daily_guarantee'],
        },
        headers=headers,
        params={'selfreg_token': 'selfreg_token'},
    )

    bss.clean_rules()
    bss.clean_by_driver_subvention()

    assert response.status_code == 200
    data = response.json()
    if 'X-YaTaxi-Driver-Profile-Id' in headers:
        assert data['items_for_day'][0]['ui_items'][3]['detail'] == '1000_₽'
    else:
        assert not data

    assert bss.rules_select.times_called == 1
    expected_request = {
        'is_personal': False,
        'limit': 1000,
        'driver_branding': 'full_branding',
        'profile_tags': ['luxary'],
        'profile_tariff_classes': ['comfort', 'econom', 'vip'],
        'order_tariff_classes': ['comfort', 'econom', 'vip'],
        'status': 'enabled',
        'tariff_zone': 'moscow',
        'time_range': {
            'end': '2018-09-24T21:00:00+00:00',
            'start': '2018-09-22T21:00:00+00:00',
        },
        'types': ['daily_guarantee'],
    }
    make_selfreg_rules_request(expected_request, headers)
    assert (
        json.loads(bss.rules_select.next_call()['request'].get_data())
        == expected_request
    )


@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'subvention.daily_guarantee.local_sum_prefix': {'ru': 'до'},
    },
)
@pytest.mark.parametrize(
    'bs_rules_select,bs_by_driver',
    [
        (
            'bs/rules_select_two_brandings.json',
            'bs/by_driver_two_brandings.json',
        ),
    ],
)
@pytest.mark.parametrize('headers', [DEFAULT_HEADER, SELFREG_HEADER])
@pytest.mark.geoareas(filename='geoareas.json')
async def test_subvention_rules_class_filtering(
        taxi_subvention_view,
        driver_authorizer,
        unique_drivers,
        bss,
        activity,
        vehicles,
        load_json,
        driver_tags_mocks,
        bs_rules_select,
        bs_by_driver,
        mockserver,
        headers,
        candidates,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'uuid')
    activity.add_driver('uuid', 50)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING_FULL_BRANDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['luxary'])
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    bss.add_rules(load_json(bs_rules_select))
    bss.add_by_driver_subventions(load_json(bs_by_driver))
    await taxi_subvention_view.invalidate_caches()

    response = await taxi_subvention_view.post(
        '/v1/nmfg/status',
        json={
            'lon': 37.618423,
            'lat': 55.751244,
            'from': '2018-09-23',
            'to': '2018-09-25',
            'types': ['daily_guarantee'],
        },
        headers=headers,
        params={'selfreg_token': 'selfreg_token'},
    )
    bss.clean_rules()
    bss.clean_by_driver_subvention()

    assert response.status_code == 200

    assert bss.rules_select.times_called == 1
    bss_request = json.loads(
        bss.rules_select.next_call()['request'].get_data(),
    )

    bss_request['order_tariff_classes'].sort()
    bss_request['profile_tariff_classes'].sort()
    expected_request = {
        'is_personal': False,
        'limit': 1000,
        'driver_branding': 'full_branding',
        'profile_tariff_classes': ['comfort', 'econom', 'vip'],
        'order_tariff_classes': ['comfort', 'econom', 'vip'],
        'profile_tags': ['luxary'],
        'status': 'enabled',
        'tariff_zone': 'moscow',
        'time_range': {
            'end': '2018-09-24T21:00:00+00:00',
            'start': '2018-09-22T21:00:00+00:00',
        },
        'types': ['daily_guarantee'],
    }
    make_selfreg_rules_request(expected_request, headers)
    assert bss_request == expected_request


@pytest.mark.parametrize(
    'bs_rules_select,bs_by_driver',
    [
        (
            'bs/rules_select_two_brandings.json',
            'bs/by_driver_two_brandings.json',
        ),
    ],
)
@pytest.mark.parametrize('headers', [DEFAULT_HEADER, SELFREG_HEADER])
@pytest.mark.geoareas(filename='geoareas.json')
async def test_subvention_rules_driver_categories_500(
        taxi_subvention_view,
        driver_authorizer,
        unique_drivers,
        activity,
        vehicles,
        load_json,
        driver_tags_mocks,
        bs_rules_select,
        bs_by_driver,
        mockserver,
        headers,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'uuid')
    activity.add_driver('uuid', 50)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING_FULL_BRANDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['luxary'])

    @mockserver.json_handler('/candidates/profiles')
    async def _mock_candidates_profile(request):
        return mockserver.make_response('Internal Error', 500)

    response = await taxi_subvention_view.post(
        '/v1/nmfg/status',
        json={
            'lon': 37.618423,
            'lat': 55.751244,
            'from': '2018-09-23',
            'to': '2018-09-25',
            'types': ['daily_guarantee'],
        },
        headers=headers,
        params={'selfreg_token': 'selfreg_token'},
    )
    if 'X-YaTaxi-Driver-Profile-Id' in headers:
        assert response.status_code == 500
    else:
        assert response.status_code == 200


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize('headers', [DEFAULT_HEADER, SELFREG_HEADER])
async def test_subvention_rules_driver_categories(
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        unique_drivers,
        bss,
        activity,
        vehicles,
        driver_tags_mocks,
        headers,
        candidates,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'uuid')
    activity.add_driver('uuid', 50)
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING_FULL_BRANDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    driver_tags_mocks.set_tags_info('dbid1', 'driver1', ['luxary'])
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    bss.add_rules(load_json('bs/rules_select.json'))
    bss.add_by_driver_subventions(load_json('bs/by_driver.json'))
    await taxi_subvention_view.invalidate_caches()

    response = await taxi_subvention_view.post(
        '/v1/nmfg/status',
        json={
            'lon': 37.6,
            'lat': 55.75,
            'from': '2018-09-23',
            'to': '2018-09-25',
            'types': ['daily_guarantee'],
        },
        headers=headers,
        params={'selfreg_token': 'selfreg_token'},
    )
    assert response.status_code == 200
    data = response.json()
    if 'X-YaTaxi-Driver-Profile-Id' in headers:
        assert data == load_json('good_response_local_sum_prefix.json')
        assert candidates.mock_profiles.times_called == 1


@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'subvention.daily_guarantee.local_sum_prefix': {'ru': 'до'},
    },
)
@pytest.mark.parametrize(
    'driver_tags, rules_select, expected_result',
    [
        (
            ['test_tag'],
            'bs/rules_select_one_rule_with_tag.json',
            'good_response_rule_with_tag.json',
        ),
        (
            ['wrong_tag'],
            'bs/rules_select_one_rule_with_tag.json',
            'good_response_rule_without_tag.json',
        ),
        (['wrong_tag'], 'bs/rules_select_all_rules_with_tag.json', None),
        (
            None,
            'bs/rules_select_one_rule_with_tag.json',
            'good_response_rule_without_tag.json',
        ),
        pytest.param(
            ['test_tag'],
            'bs/rules_select_one_rule_with_tag.json',
            'good_response_rule_with_tag.json',
            marks=[
                pytest.mark.config(
                    SUBVENTION_VIEW_USE_BSX_NMFG_MATCHING_LOGIC=True,
                ),
            ],
        ),
        pytest.param(
            ['wrong_tag'],
            'bs/rules_select_one_rule_with_tag.json',
            None,
            marks=[
                pytest.mark.config(
                    SUBVENTION_VIEW_USE_BSX_NMFG_MATCHING_LOGIC=True,
                ),
            ],
        ),
        pytest.param(
            ['wrong_tag'],
            'bs/rules_select_all_rules_with_tag.json',
            None,
            marks=[
                pytest.mark.config(
                    SUBVENTION_VIEW_USE_BSX_NMFG_MATCHING_LOGIC=True,
                ),
            ],
        ),
        pytest.param(
            None,
            'bs/rules_select_one_rule_with_tag.json',
            None,
            marks=[
                pytest.mark.config(
                    SUBVENTION_VIEW_USE_BSX_NMFG_MATCHING_LOGIC=True,
                ),
            ],
        ),
        pytest.param(
            ['test_tag'],
            'bs/rules_select_one_rule_tariffs_dont_intersect.json',
            None,
            marks=[
                pytest.mark.config(
                    SUBVENTION_VIEW_USE_BSX_NMFG_MATCHING_LOGIC=True,
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize('headers', [DEFAULT_HEADER, SELFREG_HEADER])
@pytest.mark.geoareas(filename='geoareas.json')
async def test_subvention_rules_rule_tags(
        taxi_subvention_view,
        driver_authorizer,
        unique_drivers,
        bss,
        activity,
        candidates,
        vehicles,
        load_json,
        driver_tags_mocks,
        driver_tags,
        expected_result,
        rules_select,
        headers,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'uuid')
    activity.add_driver('uuid', 50)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING_FULL_BRANDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    if driver_tags:
        driver_tags_mocks.set_tags_info('dbid1', 'driver1', driver_tags)

    bss.add_rules(load_json(rules_select))
    bss.add_by_driver_subventions(
        load_json('bs/by_driver_rule_with_tags.json'),
    )
    await taxi_subvention_view.invalidate_caches()

    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')

    response = await taxi_subvention_view.post(
        '/v1/nmfg/status',
        json={
            'lon': 37.618423,
            'lat': 55.751244,
            'from': '2018-09-23',
            'to': '2018-09-25',
            'types': ['daily_guarantee'],
        },
        headers=headers,
        params={'selfreg_token': 'selfreg_token'},
    )

    bss.clean_rules()
    bss.clean_by_driver_subvention()

    assert response.status_code == 200
    data = response.json()
    if expected_result and 'X-YaTaxi-Driver-Profile-Id' in headers:
        assert data == load_json(expected_result)
    else:
        assert data == {}

    assert bss.rules_select.times_called == 1


@pytest.mark.now('2020-10-31T16:10:00+0300')
@pytest.mark.config(SUBVENTION_VIEW_SHOW_DETAILED_NMFG_INFO=True)
@pytest.mark.parametrize(
    'bs_rules_select,bs_by_driver,response_data,lon,lat,tariff_zone,local_tz',
    [
        pytest.param(
            'bs/rules_select_all_steps_split_week.json',
            'bs/by_driver_one_date.json',
            'good_response_2_detailed_not_filtered.json',
            37.618423,
            55.751244,
            'moscow',
            'Europe/Moscow',
            marks=[
                pytest.mark.config(SUBVENTION_VIEW_FILTER_NMFG_BY_TODAY=False),
            ],
        ),
        pytest.param(
            'bs/rules_select_all_steps_split_week.json',
            'bs/by_driver_one_date.json',
            'good_response_2_detailed_filtered.json',
            37.618423,
            55.751244,
            'moscow',
            'Europe/Moscow',
            marks=[
                pytest.mark.config(SUBVENTION_VIEW_FILTER_NMFG_BY_TODAY=True),
            ],
        ),
        pytest.param(
            'bs/rules_select_all_steps_whole_week.json',
            'bs/by_driver_one_date.json',
            'good_response_2_detailed_whole_week.json',
            37.618423,
            55.751244,
            'moscow',
            'Europe/Moscow',
            marks=[
                pytest.mark.config(SUBVENTION_VIEW_FILTER_NMFG_BY_TODAY=False),
            ],
        ),
    ],
)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_subvention_rules_filter_by_day(
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        bss,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        bs_rules_select,
        bs_by_driver,
        response_data,
        lon,
        lat,
        tariff_zone,
        local_tz,
):
    start = datetime.datetime(2018, 9, 23)
    end = datetime.datetime(2018, 9, 25)

    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'uuid')
    activity.add_driver('uuid', 50)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    if bs_rules_select:
        bss.add_rules(load_json(bs_rules_select))
    if bs_by_driver:
        bss.add_by_driver_subventions(load_json(bs_by_driver))

    response = await taxi_subvention_view.post(
        '/v1/nmfg/status',
        json={
            'lon': lon,
            'lat': lat,
            'from': start.strftime('%Y-%m-%d'),
            'to': end.strftime('%Y-%m-%d'),
            'types': ['daily_guarantee'],
        },
        headers=DEFAULT_HEADER,
    )

    assert response.status_code == 200
    data = response.json()
    assert data == load_json(response_data)


@pytest.mark.now('2020-10-31T16:10:00+0300')
@pytest.mark.config(SUBVENTION_VIEW_SHOW_DETAILED_NMFG_INFO=True)
@pytest.mark.parametrize(
    'bs_rules_select,bs_by_driver,response_data,lon,lat,tariff_zone,local_tz',
    [
        pytest.param(
            'bs/rules_select_all_steps_split_week.json',
            'bs/by_driver_one_date.json',
            'good_response_2_detailed_not_filtered.json',
            37.618423,
            55.751244,
            'moscow',
            'Europe/Moscow',
            marks=[
                pytest.mark.config(SUBVENTION_VIEW_FILTER_NMFG_BY_TODAY=False),
            ],
        ),
    ],
)
@pytest.mark.parametrize('switch_to_by_time', [False, True])
@pytest.mark.geoareas(filename='geoareas.json')
async def test_subvention_rules_switch_to_by_time(
        taxi_subvention_view,
        taxi_config,
        load_json,
        driver_authorizer,
        bss,
        unique_drivers,
        activity,
        driver_tags_mocks,
        candidates,
        vehicles,
        bs_rules_select,
        bs_by_driver,
        response_data,
        lon,
        lat,
        tariff_zone,
        local_tz,
        switch_to_by_time,
):
    if switch_to_by_time:
        taxi_config.set_values(
            dict(
                SUBVENTION_VIEW_BY_DRIVER_REQUEST_AS_BY_TIME={
                    'nfmg': True,
                    'status': False,
                },
            ),
        )
    start = datetime.datetime(2018, 9, 23)
    end = datetime.datetime(2018, 9, 25)

    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'uuid')
    activity.add_driver('uuid', 50)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    bss.add_rules(load_json(bs_rules_select))
    bss.add_by_driver_subventions(load_json(bs_by_driver))

    response = await taxi_subvention_view.post(
        '/v1/nmfg/status',
        json={
            'lon': lon,
            'lat': lat,
            'from': start.strftime('%Y-%m-%d'),
            'to': end.strftime('%Y-%m-%d'),
            'types': ['daily_guarantee'],
        },
        headers=DEFAULT_HEADER,
    )

    assert response.status_code == 200
    data = response.json()
    assert data == load_json(response_data)

    if switch_to_by_time:
        by_driver_params = json.loads(bss.by_driver_call_params[0])
        assert by_driver_params['time'] == '2020-10-31T13:10:00+00:00'


@pytest.mark.now('2018-09-24T16:10:00+0300')
@pytest.mark.config(
    SUBVENTION_VIEW_SHOW_DETAILED_NMFG_INFO=True,
    SUBVENTION_VIEW_FILTER_NMFG_BY_TODAY=True,
)
@pytest.mark.parametrize(
    'is_nmfg_today,response_data', [(True, 'good_response_only_nmfg.json')],
)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_non_personal_goals_in_nmfg(
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
        vehicles,
        response_data,
        mockserver,
        experiments3,
        is_nmfg_today,
):
    start = datetime.datetime(2018, 9, 23)
    end = datetime.datetime(2018, 9, 25)

    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'uuid')
    activity.add_driver('uuid', 50)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_rules_select(request):
        data = json.loads(request.get_data())
        types = data['types']
        assert len(types) == 1
        subv_type = types[0]
        if subv_type == 'daily_guarantee':
            if is_nmfg_today:
                return {
                    'subventions': load_json(
                        'bs/rules_select_all_steps_split_week.json',
                    ),
                }
            return {'subventions': []}
        if subv_type == 'goal':
            return {'subventions': load_json('bs/rs_response_goals.json')}
        raise RuntimeError(f'Unknown subvention type: {subv_type}')

    @mockserver.json_handler('/billing_subventions/v1/by_driver')
    def _get_by_driver(request):
        data = json.loads(request.get_data())
        rule_ids = data['subvention_rule_ids']
        rule_ids.sort()

        if rule_ids == ['group_id/volgodonsk_daily_guarantee_2018_09_17']:
            return {'subventions': load_json('bs/by_driver_one_date.json')}

        goal_rule_ids = [
            'group_id/85f2a91d6ec1e1af020ff34a6eeafd30f9b2b3e8',
            'group_id/85f2a91d6ec1e1af020ff34a6eeafd30f9b2b3e9',
            'group_id/85f2a91d6ec1e1af020ff34a6eeafd30f9b2b3f1',
            'group_id/85f2a91d6ec1e1af020ff34a6eeafd30f9b2b3f2',
        ]
        if rule_ids == goal_rule_ids:
            return {
                'subventions': load_json('bs/by_driver_response_goals.json'),
            }
        raise RuntimeError(f'Got no nmfg or goals in request: {rule_ids}')

    response = await taxi_subvention_view.post(
        '/v1/nmfg/status',
        json={
            'lon': 37.618423,
            'lat': 55.751244,
            'from': start.strftime('%Y-%m-%d'),
            'to': end.strftime('%Y-%m-%d'),
            'types': ['daily_guarantee'],
        },
        headers=DEFAULT_HEADER,
    )

    assert response.status_code == 200
    data = response.json()
    assert data == load_json(response_data)


@pytest.mark.config(SUBVENTION_VIEW_PASS_503_ON_429=True)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_got_429(
        taxi_subvention_view,
        driver_authorizer,
        unique_drivers,
        bss,
        mockserver,
        activity,
        candidates,
        vehicles,
        load_json,
):
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')
    unique_drivers.add_driver('dbid1', 'driver1', 'uuid')
    activity.add_driver('uuid', 50)
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING_FULL_BRANDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    driver_authorizer.set_session('dbid1', 'qwerty', 'driver1')

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_rules_select(request):
        return mockserver.make_response(status=429)

    response = await taxi_subvention_view.post(
        '/v1/nmfg/status',
        json={
            'lon': 37.618423,
            'lat': 55.751244,
            'from': '2020-01-13',
            'to': '2020-01-20',
            'types': ['daily_guarantee'],
        },
        headers=DEFAULT_HEADER,
        params={'selfreg_token': 'selfreg_token'},
    )
    assert response.status_code == 503
