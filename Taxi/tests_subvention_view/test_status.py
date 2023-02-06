# pylint: disable=too-many-lines
# coding=utf-8
import json
import random

import pytest

from . import common


VEHICLE_BINDING = {
    'profiles': [
        {'park_driver_profile_id': '777_888', 'data': {'car_id': 'vehicle1'}},
    ],
}

DEFAULT_HEADERS = {
    'X-Driver-Session': 'qwerty',
    'Accept-Language': 'en',
    'X-YaTaxi-Park-Id': '777',
    'X-YaTaxi-Driver-Profile-Id': '888',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.77 (456)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}

SELFREG_HEADERS = {
    'Accept-Language': 'en',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.77 (456)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


@pytest.mark.now('1970-01-01T00:00:12Z')
@pytest.mark.parametrize('headers', [DEFAULT_HEADERS, SELFREG_HEADERS])
@pytest.mark.parametrize(
    ('request_arguments', 'expected_status_code'),
    [
        (
            {  # Success. No order_id
                'lon': '37.6',
                'lat': '55.73',
                'subventions_id': '_id/subvention_1',
                'selfreg_token': 'selfreg_token',
            },
            200,
        ),
        (
            {  # Success. Order found by order_id
                'lon': '37.6',
                'lat': '55.73',
                'subventions_id': '_id/subvention_1',
                'order_id': 'order_id_0',
                'selfreg_token': 'selfreg_token',
            },
            200,
        ),
        (
            {  # Success. Order found by alias_id
                'lon': '37.6',
                'lat': '55.73',
                'subventions_id': '_id/subvention_1',
                'order_id': 'alias_id_0',
                'selfreg_token': 'selfreg_token',
            },
            200,
        ),
        (
            {  # Success. Order doesn't exist
                'lon': '37.6',
                'lat': '55.73',
                'subventions_id': '_id/subvention_1',
                'order_id': 'non_existing_order_id',
                'selfreg_token': 'selfreg_token',
            },
            200,
        ),
        (
            {
                'lon': '37.6',
                'subventions_id': '_id/subvention_1',
                'selfreg_token': 'selfreg_token',
            },
            400,
        ),
    ],
)
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
async def test_subvention_geoareas_arguments_validation(
        mockserver,
        now,
        bss,
        taxi_subvention_view,
        load_json,
        request_arguments,
        expected_status_code,
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
        headers,
):
    unique_drivers.add_driver('777', '888', 'udid')
    activity.add_driver('udid', 1)
    driver_authorizer.set_session('777', 'qwerty', '888')
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    for rule in load_json('rules_select_response.json'):
        if rule['subvention_rule_id'] == request_arguments['subventions_id']:
            bss.add_rule(rule)
    for rule_status in load_json('by_driver_response.json'):
        if (
                rule_status['subvention_rule_id']
                == request_arguments['subventions_id']
        ):
            bss.add_by_driver_subvention(rule_status)
    await taxi_subvention_view.invalidate_caches()
    response = await taxi_subvention_view.get(
        '/v1/status?'
        + '&'.join(['='.join(kv) for kv in request_arguments.items()]),
        headers=headers,
        params={'selfreg_token': 'selfreg_token'},
    )
    assert response.status_code == expected_status_code
    bss.clean_rules()
    bss.clean_by_driver_subvention()


@pytest.mark.now('2019-02-24T11:00:00Z')
@pytest.mark.parametrize('headers', [DEFAULT_HEADERS, SELFREG_HEADERS])
@pytest.mark.parametrize(
    (
        'rules_file',
        'rules_status_file',
        'current_point',
        'expected_response_file',
    ),
    [
        (  # guarantee
            'guarantee_rule.json',
            'by_driver_response_empty.json',
            [37.327150, 55.821896],
            'expected_guarantee_response.json',
        ),
        (  # geo guarantee active
            'guarantee_rule_1.json',
            'by_driver_response_empty.json',
            [37.6, 55.75],
            'expected_guarantee_response_active.json',
        ),
    ],
)
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
async def test_active_subvention_geoareas(
        mockserver,
        now,
        bss,
        taxi_subvention_view,
        load_json,
        rules_file,
        rules_status_file,
        current_point,
        expected_response_file,
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
        headers,
):
    unique_drivers.add_driver('777', '888', 'udid')
    activity.add_driver('udid', 90)
    driver_authorizer.set_session('777', 'qwerty', '888')
    candidates_response = load_json('candidates_profiles_response.json')
    candidates_response['point'] = current_point
    candidates.load_profiles(candidates_response)
    rules = load_json(rules_file)
    random.shuffle(rules)
    rules_status = load_json(rules_status_file)
    expected_response = load_json(expected_response_file)
    # Setting up bss
    bss.clean_by_driver_subvention()
    bss.clean_rules()
    for rule in rules_status:
        bss.add_by_driver_subvention(rule)
    subventions_ids = ['some_random_id']
    for rule in rules:
        bss.add_rule(rule)
        subventions_ids.append(rule['subvention_rule_id'])
    await taxi_subvention_view.invalidate_caches()
    assert len(current_point) == 2
    lon, lat = current_point
    await taxi_subvention_view.invalidate_caches()
    response = await taxi_subvention_view.get(
        '/v1/status?'
        'lon={}&lat={}&subventions_id={}{}'.format(
            lon, lat, ','.join(subventions_ids), '&order_id=',
        ),
        headers=headers,
        params={'selfreg_token': 'selfreg_token'},
    )

    assert response.status_code == 200
    response = response.json()
    if 'X-YaTaxi-Driver-Profile-Id' in headers:
        assert response == expected_response
    rules_select_response = json.loads(bss.rules_select_call_params[0])
    rules_select_response['rule_ids'].sort(reverse=True)
    subventions_ids.sort(reverse=True)
    assert rules_select_response == {
        'limit': len(subventions_ids),
        'status': 'enabled',
        'tariff_zone': 'moscow',
        'rule_ids': subventions_ids,
    }
    if bss.by_driver_calls:
        by_driver_request = json.loads(bss.by_driver_call_params[0])
        by_driver_request['subvention_rule_ids'].sort(reverse=True)
        assert by_driver_request == {
            'subvention_rule_ids': ['_id/subvention_2', '_id/subvention_1'],
            'time': '2019-02-24T11:00:00+00:00',
            'unique_driver_id': 'udid',
        }

    bss.clean_rules()
    bss.clean_by_driver_subvention()


TEMPLATE_RULE = {
    'tariff_zones': ['moscow'],
    'status': 'enabled',
    'start': '2019-02-26T21:00:00.000000+00:00',
    'end': '2019-03-28T21:00:00.000000+00:00',
    'type': 'geo_booking',
    'is_personal': False,
    'taxirate': '',
    'subvention_rule_id': '_id/subvention_1',
    'cursor': '2019-03-28T21:00:00.000000+00:00/5c768761254e5eb96aa023b4',
    'tags': [],
    'time_zone': {'id': 'Europe/Moscow', 'offset': '+03:00'},
    'currency': 'RUB',
    'updated': '2019-02-27T12:49:37.835000+00:00',
    'tariff_classes': ['econom'],
    'has_commission': False,
    'week_days': ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
    'geoareas': ['polygon'],
    'workshift': {'start': '14:00', 'end': '14:15'},
    'payment_type': 'add',
    'min_activity_points': 2,
    'min_online_minutes': 2,
    'rate_on_order_per_minute': '1024',
    'rate_free_per_minute': '1024',
    'hours': [],
    'visible_to_driver': True,
    'order_payment_type': None,
    'profile_payment_type_restrictions': 'none',
    'log': [],
    'is_relaxed_order_time_matching': True,
    'is_relaxed_income_matching': True,
}

SATISFY_CRITERIA = {
    'none': {'none': True, 'cash': True, 'online': True, 'any': True},
    'cash': {'none': False, 'cash': True, 'online': False, 'any': True},
    'online': {'none': False, 'cash': False, 'online': True, 'any': True},
}

PAYMENT_TYPE_TO_PAYMENT_METHOD = {
    'none': ['cash', 'card'],
    'cash': ['cash'],
    'online': ['card'],
}


@pytest.mark.now('2020-01-01T00:00:12Z')
@pytest.mark.parametrize('headers', [DEFAULT_HEADERS, SELFREG_HEADERS])
@pytest.mark.parametrize('driver_payment_type', ['none', 'cash', 'online'])
@pytest.mark.parametrize(
    'restriction_payment_type', ['none', 'cash', 'online', 'any'],
)
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
async def test_payment_type_restriction(
        mockserver,
        now,
        bss,
        taxi_subvention_view,
        load_json,
        driver_payment_type,
        restriction_payment_type,
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
        experiments3,
        taxi_config,
        headers,
):
    unique_drivers.add_driver('777', '888', 'udid')
    activity.add_driver('udid', 90)
    driver_authorizer.set_session('777', 'qwerty', '888')
    candidates.load_profiles(
        {
            'drivers': [
                {
                    'classes': ['econom'],
                    'dbid': '777',
                    'position': [37.6, 55.75],
                    'uuid': '889',
                    'payment_methods': PAYMENT_TYPE_TO_PAYMENT_METHOD[
                        driver_payment_type
                    ],
                },
            ],
        },
    )
    rules_status = load_json('by_driver_response.json')
    rule = TEMPLATE_RULE
    rule['profile_payment_type_restrictions'] = restriction_payment_type
    subventions_id = []
    bss.add_rule(rule)
    subventions_id.append(rule['subvention_rule_id'])
    # Setting up bss
    for rule in rules_status:
        if rule['subvention_rule_id'] in subventions_id:
            bss.add_by_driver_subvention(rule)
    await taxi_subvention_view.invalidate_caches()
    response = await taxi_subvention_view.get(
        '/v1/status?'
        'lon={}&lat={}&subventions_id={}{}'.format(
            37.6, 55.75, ','.join(subventions_id), '&order_id=',
        ),
        headers=headers,
        params={'selfreg_token': 'selfreg_token'},
    )
    assert response.status_code == 200
    res = response.json()
    subv = res['subventions_status'][0]
    satisfy = SATISFY_CRITERIA[driver_payment_type][restriction_payment_type]
    if 'X-YaTaxi-Driver-Profile-Id' in headers:
        assert subv['are_restrictions_satisfied'] == satisfy
    if restriction_payment_type != 'any':
        driver_payment_type_loc = {
            'none': 'любой',
            'cash': 'наличные',
            'online': 'картой',
        }
        restriction_payment_type_loc = {
            'none': 'любой',
            'cash': 'наличные',
            'online': 'картой',
        }
        descr_item = {
            'subtitle': (
                'у вас выбрана оплата '
                + driver_payment_type_loc[driver_payment_type]
            ),
            'title': (
                'нужна оплата '
                + restriction_payment_type_loc[restriction_payment_type]
            ),
            'type': 'tip_detail',
        }
        if 'X-YaTaxi-Driver-Profile-Id' in headers:
            if satisfy:
                descr_item['left_tip'] = {
                    'background_color': '#F1F0ED',
                    'form': 'round',
                    'icon': {'icon_type': 'check', 'tint_color': '#0596FA'},
                }
            else:
                descr_item['left_tip'] = {
                    'background_color': '#FA3E2C',
                    'form': 'round',
                    'icon': {'icon_type': 'warning4', 'tint_color': '#FFFFFF'},
                }
            assert descr_item in subv['description_items']
    bss.clean_rules()
    bss.clean_by_driver_subvention()
    if 'X-YaTaxi-Driver-Profile-Id' in headers:
        assert candidates.mock_profiles.times_called == 1


@pytest.mark.now('1970-01-01T00:00:12Z')
@pytest.mark.parametrize('headers', [DEFAULT_HEADERS, SELFREG_HEADERS])
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
async def test_driver_categories(
        mockserver,
        now,
        bss,
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
        headers,
):
    unique_drivers.add_driver('777', '888', 'udid')
    activity.add_driver('udid', 90)
    driver_authorizer.set_session('777', 'qwerty', '888')
    candidates.load_profiles(load_json('candidates_profiles_response.json'))
    driver_authorizer.set_session('777', 'qwerty', '888')
    rules_status = load_json('by_driver_response.json')
    rule = TEMPLATE_RULE
    subventions_id = []
    bss.add_rule(rule)
    subventions_id.append(rule['subvention_rule_id'])

    # Setting up bss
    for rule in rules_status:
        if rule['subvention_rule_id'] in subventions_id:
            bss.add_by_driver_subvention(rule)

    response = await taxi_subvention_view.get(
        '/v1/status?'
        'lon={}&lat={}&subventions_id={}{}'.format(
            37.6, 55.75, ','.join(subventions_id), '&order_id=',
        ),
        headers=headers,
        params={'selfreg_token': 'selfreg_token'},
    )
    assert response.status_code == 200
    if 'X-YaTaxi-Driver-Profile-Id' in headers:
        assert candidates.mock_profiles.times_called == 1
    res = response.json()

    subv = res['subventions_status'][0]
    assert subv['are_restrictions_satisfied']

    bss.clean_rules()
    bss.clean_by_driver_subvention()


@pytest.mark.now('1970-01-01T00:00:12Z')
@pytest.mark.parametrize('headers', [DEFAULT_HEADERS, SELFREG_HEADERS])
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@pytest.mark.config(SUBVENTION_VIEW_MAP_TARIFF_CLASSES=True)
async def test_tariff_classes_mapping(
        mockserver,
        now,
        bss,
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
        headers,
):
    unique_drivers.add_driver('777', '888', 'udid')
    activity.add_driver('udid', 90)
    driver_authorizer.set_session('777', 'qwerty', '888')
    current_point = [37.6, 55.75]

    candidates_response = load_json('candidates_profiles_response.json')
    candidates_response['point'] = current_point
    candidates.load_profiles(candidates_response)

    rules = load_json('rules_select_response_with_uber.json')
    random.shuffle(rules)
    rules_status = load_json('by_driver_response.json')
    expected_response = load_json('expected_response_uber_mapping.json')

    # Setting up bss
    bss.clean_by_driver_subvention()
    bss.clean_rules()
    for rule in rules_status:
        bss.add_by_driver_subvention(rule)

    subventions_ids = ['some_random_id']
    for rule in rules:
        bss.add_rule(rule)
        subventions_ids.append(rule['subvention_rule_id'])

    await taxi_subvention_view.invalidate_caches()

    assert len(current_point) == 2
    lon, lat = current_point

    await taxi_subvention_view.invalidate_caches()
    response = await taxi_subvention_view.get(
        '/v1/status?'
        'lon={}&lat={}&subventions_id={}{}'.format(
            lon, lat, ','.join(subventions_ids), '&order_id=',
        ),
        headers=headers,
        params={'selfreg_token': 'selfreg_token'},
    )

    assert response.status_code == 200
    response = response.json()

    if 'X-YaTaxi-Driver-Profile-Id' in headers:
        assert response == expected_response

    bss.clean_rules()
    bss.clean_by_driver_subvention()


@pytest.mark.now('2020-05-05T00:00:12Z')
@pytest.mark.parametrize('headers', [DEFAULT_HEADERS, SELFREG_HEADERS])
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@pytest.mark.config(
    SUBVENTION_VIEW_MAP_TARIFF_CLASSES=True,
    SUBVENTION_VIEW_STATUS_FETCH_SMART_SUBVENTIONS=True,
    SMART_SUBVENTIONS_SETTINGS={'restrictions': ['activity', 'geoarea']},
)
async def test_fetch_smart_subventions(
        mockserver,
        now,
        bss,
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
        headers,
):
    unique_drivers.add_driver('777', '888', 'udid')
    activity.add_driver('udid', 90)
    driver_authorizer.set_session('777', 'qwerty', '888')
    current_point = [37.6, 55.75]

    candidates_response = load_json('candidates_profiles_response.json')
    candidates_response['point'] = current_point
    candidates.load_profiles(candidates_response)

    bsx_rule = {
        'rule_type': 'single_ride',
        'start': '2020-05-02T21:00:00+00:00',
        'end': '2020-05-30T21:00:00+00:00',
        'rates': [{'week_day': 'mon', 'start': '18:00', 'bonus_amount': '10'}],
        'id': 'cf730f12-c02b-11ea-acc8-ab6ac87f7711',
        'budget_id': 'abcd1234',
        'draft_id': '1234abcd',
        'schedule_ref': '1234abcd',
        'zone': 'moscow',
        'tariff_class': 'comfort',
    }

    @mockserver.json_handler('/billing-subventions-x/v2/rules/get')
    async def _mock_bsx_get(request):
        return {'rule': bsx_rule}

    @mockserver.json_handler('/billing-subventions-x/v2/rules/match')
    async def _mock_bsx_match(request):
        return {
            'matches': (
                [{'rule': bsx_rule, 'type': 'single_ride', 'amount': '100500'}]
                if request.json['tariff_class'] == 'comfort'
                else []
            ),
        }

    subventions_ids = ['bsx/cf730f12-c02b-11ea-acc8-ab6ac87f7711']

    await taxi_subvention_view.invalidate_caches()

    assert len(current_point) == 2
    lon, lat = current_point

    await taxi_subvention_view.invalidate_caches()
    response = await taxi_subvention_view.get(
        '/v1/status?'
        'lon={}&lat={}&subventions_id={}{}'.format(
            lon, lat, ','.join(subventions_ids), '&order_id=',
        ),
        headers=headers,
        params={'selfreg_token': 'selfreg_token'},
    )

    assert response.status_code == 200
    response = response.json()

    assert response == load_json('expected_response_smart_subventions.json')


@pytest.mark.now('1970-01-01T00:00:12Z')
@pytest.mark.parametrize('headers', [DEFAULT_HEADERS, SELFREG_HEADERS])
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@pytest.mark.config(
    POLLING_DELAY={'__default': 600, '/v1/status': 60},
    TAXIMETER_POLLING_SWITCHER={'__default__': 'new'},
    TAXIMETER_POLLING_MANAGER={
        '__default__': {
            'policy_groups': {'__default__': {'full': 600, 'background': 0}},
        },
        '/v1/status': {
            'policy_groups': {
                '__default__': {'full': 60, 'background': 0},
                'with_geobooking': {'full': 30, 'background': 0},
            },
        },
    },
)
@pytest.mark.parametrize(
    'subventions_id,expected_custom_polling_delay',
    [('_id/subvention_1', 30), ('_id/subvention_3', 60)],
)
@pytest.mark.parametrize(
    'use_custom_polling_delay',
    [
        pytest.param(False),
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    POLLING_DELAY_CUSTOM={
                        '/v1/status': {'with_geobooking': 30},
                    },
                ),
            ],
        ),
    ],
)
async def test_polling_headers(
        mockserver,
        now,
        bss,
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
        vehicles,
        subventions_id,
        expected_custom_polling_delay,
        use_custom_polling_delay,
        headers,
):
    unique_drivers.add_driver('777', '888', 'uuid')
    activity.add_driver('uuid', 1)
    driver_authorizer.set_session('777', 'qwerty', '888')
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    for rule in load_json('rules_select_response.json'):
        if rule['subvention_rule_id'] == subventions_id:
            bss.add_rule(rule)

    for rule_status in load_json('by_driver_response.json'):
        if rule_status['subvention_rule_id'] == subventions_id:
            bss.add_by_driver_subvention(rule_status)

    await taxi_subvention_view.invalidate_caches()
    response = await taxi_subvention_view.get(
        '/v1/status?lon=37.327150&lat=55.821896'
        '&subventions_id=' + subventions_id,
        headers=headers,
        params={'selfreg_token': 'selfreg_token'},
    )

    assert response.status_code == 200
    polling_delay = int(response.headers['X-Polling-Delay'])
    polling_policy = response.headers['X-Polling-Power-Policy']
    if use_custom_polling_delay:
        assert polling_delay == expected_custom_polling_delay
        assert polling_policy == common.make_polling_policy(
            expected_custom_polling_delay,
        )
    else:
        assert polling_delay == 60
        assert polling_policy == common.make_polling_policy(60)

    bss.clean_rules()
    bss.clean_by_driver_subvention()


@pytest.mark.now('1970-01-01T00:00:12Z')
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@pytest.mark.config(SUBVENTION_VIEW_USE_BY_DRIVER_FALLBACK_CACHE=True)
async def test_by_driver_fallback_cache(
        mockserver,
        now,
        bss,
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
        statistics,
):
    unique_drivers.add_driver('777', '888', 'udid')
    activity.add_driver('udid', 90)
    driver_authorizer.set_session('777', 'qwerty', '888')
    current_point = [37.6, 55.75]

    candidates_response = load_json('candidates_profiles_response.json')
    candidates_response['point'] = current_point
    candidates.load_profiles(candidates_response)

    rules = load_json('rules_select_response.json')
    random.shuffle(rules)
    rules_status = load_json('by_driver_response.json')
    expected_response = load_json('expected_response.json')

    # Setting up bss
    bss.clean_by_driver_subvention()
    bss.clean_rules()
    for rule in rules_status:
        bss.add_by_driver_subvention(rule)

    subventions_ids = ['some_random_id']
    for rule in rules:
        bss.add_rule(rule)
        subventions_ids.append(rule['subvention_rule_id'])

    await taxi_subvention_view.invalidate_caches()

    assert len(current_point) == 2
    lon, lat = current_point

    endpoint = '/v1/status?' 'lon={}&lat={}&subventions_id={}{}'.format(
        lon, lat, ','.join(subventions_ids), '&order_id=',
    )

    await taxi_subvention_view.invalidate_caches()

    await taxi_subvention_view.get(
        endpoint,
        headers=DEFAULT_HEADERS,
        params={'selfreg_token': 'selfreg_token'},
    )

    @mockserver.json_handler('/billing_subventions/v1/by_driver')
    async def mock_bs_by_driver(request):
        return mockserver.make_response('', 500)

    statistics.fallbacks = ['subvention_view.bs-by_driver.fallback']

    response = await taxi_subvention_view.get(
        endpoint,
        headers=DEFAULT_HEADERS,
        params={'selfreg_token': 'selfreg_token'},
    )

    assert response.status_code == 200
    response = response.json()

    assert response == expected_response
    rules_select_response = json.loads(bss.rules_select_call_params[0])
    rules_select_response['rule_ids'].sort(reverse=True)
    subventions_ids.sort(reverse=True)
    assert rules_select_response == {
        'limit': len(subventions_ids),
        'status': 'enabled',
        'tariff_zone': 'moscow',
        'rule_ids': subventions_ids,
    }

    assert mock_bs_by_driver.times_called == 0
    by_driver_request = json.loads(bss.by_driver_call_params[0])
    by_driver_request['subvention_rule_ids'].sort(reverse=True)
    assert by_driver_request == {
        'subvention_rule_ids': ['_id/subvention_2', '_id/subvention_1'],
        'time': '1970-01-01T00:00:12+00:00',
        'unique_driver_id': 'udid',
    }

    bss.clean_rules()
    bss.clean_by_driver_subvention()


@pytest.mark.now('2020-11-11T18:00:12Z')
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
@pytest.mark.parametrize('switch_to_by_time', [False, True])
async def test_subvention_rules_switch_to_by_time(
        mockserver,
        taxi_config,
        now,
        bss,
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
        switch_to_by_time,
):
    if switch_to_by_time:
        taxi_config.set_values(
            dict(
                SUBVENTION_VIEW_BY_DRIVER_REQUEST_AS_BY_TIME={
                    'nfmg': False,
                    'status': True,
                },
            ),
        )

    unique_drivers.add_driver('777', '888', 'udid')
    activity.add_driver('udid', 90)
    driver_authorizer.set_session('777', 'qwerty', '888')
    current_point = [37.6, 55.75]

    candidates_response = load_json('candidates_profiles_response.json')
    candidates_response['point'] = current_point
    candidates.load_profiles(candidates_response)

    rules = load_json('rules_select_response.json')
    random.shuffle(rules)
    rules_status = load_json('by_driver_response.json')
    expected_response = load_json('expected_response.json')

    # Setting up bss
    bss.clean_by_driver_subvention()
    bss.clean_rules()
    for rule in rules_status:
        bss.add_by_driver_subvention(rule)

    subventions_ids = ['some_random_id']
    for rule in rules:
        bss.add_rule(rule)
        subventions_ids.append(rule['subvention_rule_id'])

    await taxi_subvention_view.invalidate_caches()

    assert len(current_point) == 2
    lon, lat = current_point

    endpoint = '/v1/status?' 'lon={}&lat={}&subventions_id={}{}'.format(
        lon, lat, ','.join(subventions_ids), '&order_id=',
    )

    await taxi_subvention_view.invalidate_caches()

    response = await taxi_subvention_view.get(
        endpoint,
        headers=DEFAULT_HEADERS,
        params={'selfreg_token': 'selfreg_token'},
    )

    assert response.status_code == 200
    response = response.json()

    assert response == expected_response

    if switch_to_by_time:
        by_driver_params = json.loads(bss.by_driver_call_params[0])
        assert by_driver_params['time'] == '2020-11-11T18:00:12+00:00'


@pytest.mark.config(SUBVENTION_VIEW_PASS_503_ON_429=True)
@pytest.mark.geoareas(
    filename='geoareas.json', sg_filename='subvention_geoareas.json',
)
async def test_got_429(
        mockserver,
        now,
        bss,
        taxi_subvention_view,
        load_json,
        driver_authorizer,
        unique_drivers,
        activity,
        candidates,
        vehicles,
):
    unique_drivers.add_driver('777', '888', 'uuid')
    activity.add_driver('uuid', 1)
    driver_authorizer.set_session('777', 'qwerty', '888')
    vehicles.set_vehicle_bindings_response(VEHICLE_BINDING)
    vehicles.set_cars_list_response(load_json('parks_cars_list.json'))
    candidates.load_profiles(load_json('candidates_profiles_response.json'))

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _mock_rules_select(request):
        return mockserver.make_response(status=429)

    response = await taxi_subvention_view.get(
        '/v1/status?lon=37.327150&lat=55.821896'
        '&subventions_id=_id/subvention_1',
        headers=DEFAULT_HEADERS,
        params={'selfreg_token': 'selfreg_token'},
    )
    assert response.status_code == 503

    response = await taxi_subvention_view.post(
        '/driver/v1/subvention_view/v2/status'
        '?park_id=dbid1&lat=55.821896&lon=37.327150',
        headers=DEFAULT_HEADERS,
        json={
            'subventions_id': ['_id/subvention_1'],
            'order_id': 'non_existing_order_id',
        },
    )

    assert response.status_code == 503
