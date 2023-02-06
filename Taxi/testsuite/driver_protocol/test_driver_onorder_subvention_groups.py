from copy import deepcopy
import json

import pytest

from . import common


DMS_ACTIVITY_VALUES = {
    '59648321ea19f1bacf079756': 89,
    '59648321ea19f1bacf079757': 89,
    '59648321ea19f1bacf079758': 89,
    '59648321ea19f1bacf079759': 89,
    '59648321ea19f1bacf079760': 89,
}


def _prepare_driver_points_in_expected_result(expected_response, dms_context):
    if not dms_context.use_dms_driver_points:
        return expected_response
    response = deepcopy(expected_response)
    driver_points = dms_context.fetch_driver_points('59648321ea19f1bacf079756')
    for item_for_schedule in response['items_for_schedule']:
        if 'rules' not in item_for_schedule:
            continue
        for rule in item_for_schedule['rules']:
            if 'driver_points_current' in rule:
                rule['driver_points_current'] = driver_points
    for item_for_map in response['items_for_map']:
        if 'driver_points_current' in item_for_map:
            item_for_map['driver_points_current'] = driver_points
    return response


def sort_osg_response(respose_json):
    item_for_schedule = respose_json['items_for_schedule']
    for item in item_for_schedule:
        item['rules'].sort(key=lambda x: x['id'])


LRU_CONFIG = [False, True]


def apply_config(config, lru_config):
    if lru_config:
        config.set_values(
            dict(
                BS_CLIENT_LRU_CACHE_ENABLED=lru_config,
                BILLING_SUBVENTIONS_HANDLES_USE_BS_CLIENT=[
                    '/driver/onorder_subvention_groups',
                ],
            ),
        )
    else:
        config.set_values(dict(BS_CLIENT_LRU_CACHE_ENABLED=lru_config))


@pytest.mark.now('2020-06-19T16:05:16+0300')
@pytest.mark.config(
    USE_BILLING_SUBVENTIONS_ONLY=True,
    OSG_FETCH_TARIFF_CLASSES_FROM_MONGO=False,
    USE_PARK_UUID_FOR_CLASSES_IN_SUBVENTIONS=True,
    ENABLE_EXTENDING_SUBVENTION_BY_GEOAREAS=True,
    BILLING_SUBVENTIONS_HANDLES_USE_BS_CLIENT=[
        '/driver/onorder_subvention_groups',
    ],
    MIN_VERSION_FOR_BOOKING_SUBVENTIONS='8.60',
    ENABLE_SUBVENTIONS_SORT_BEFORE_MERGE=True,
)
def test_onorder_merge_bug(
        taxi_driver_protocol,
        load_json,
        driver_authorizer_service,
        bss,
        config,
        mockserver,
):
    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_tracker_categories(request):
        tracker_response = load_json('tracker_response.json')
        return tracker_response

    driver_authorizer_service.set_session(
        'test_db', 'test_session', 'test_uuid',
    )

    all_rules = load_json('billing_rules_bug.json')
    for rule in all_rules:
        bss.add_rule(rule)

    request_params = {
        'db': 'test_db',
        'session': 'test_session',
        'locale': 'ru',
        'lat': '55.733863',
        'lon': '37.590533',
    }

    response = taxi_driver_protocol.get(
        '/driver/onorder-subvention-groups',
        params=request_params,
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.60 (562)',
        },
    )

    assert response.status_code == 200
    assert load_json('expected_moscow_bug.json') == response.json()
    assert mock_tracker_categories.times_called == 1


# @pytest.mark.parametrize('lru_config', LRU_CONFIG)
@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(
    SUBVENTION_SCHEDULE_TAXIMETER_DISPLAYING_DAYS={'__default__': 4},
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_onorder_subvention_groups(
        taxi_driver_protocol,
        load_json,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    # apply_config(config, lru_config)
    driver_authorizer_service.set_session(
        'test_db', 'test_session', 'test_uuid',
    )

    request_params = {
        'db': 'test_db',
        'session': 'test_session',
        'locale': 'ru',
        'lat': '55.733863',
        'lon': '37.590533',
    }

    response = taxi_driver_protocol.get(
        '/driver/onorder-subvention-groups', params=request_params,
    )

    assert response.status_code == 200
    response_data = response.json()

    expected_data = load_json('expected_moscow.json')
    assert response_data == _prepare_driver_points_in_expected_result(
        expected_data, dms_context,
    )


@pytest.mark.parametrize('lru_config', LRU_CONFIG)
@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(
    ENABLE_NEW_LOGIC_RESOLVE_CONFLICT_BETWEEN_SUBVENTION_RULES=True,
    SUBVENTION_SCHEDULE_TAXIMETER_DISPLAYING_DAYS={'__default__': 4},
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_onorder_subvention_groups_with_merging(
        taxi_driver_protocol,
        load_json,
        driver_authorizer_service,
        config,
        lru_config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    apply_config(config, lru_config)

    driver_authorizer_service.set_session(
        'test_db', 'test_session', 'test_uuid',
    )

    request_params = {
        'db': 'test_db',
        'session': 'test_session',
        'locale': 'ru',
        'lat': '55.733863',
        'lon': '37.590533',
    }

    response = taxi_driver_protocol.get(
        '/driver/onorder-subvention-groups', params=request_params,
    )

    assert response.status_code == 200
    response_data = response.json()

    expected_data = load_json('expected_moscow_with_merging.json')
    assert response_data == _prepare_driver_points_in_expected_result(
        expected_data, dms_context,
    )


@pytest.mark.parametrize('lru_config', LRU_CONFIG)
@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(
    ENABLE_EXTENDING_SUBVENTION_BY_GEOAREAS=True,
    SUBVENTION_SCHEDULE_TAXIMETER_DISPLAYING_DAYS={
        '__default__': 7,
        'almaty': 4,
    },
    # 590 minutes = 9 hours, 50 minutes
    # now + ~10 hours is the next day (2017-07-07)
    SUBVENTION_FOR_MAP_DISPLAYING_START_LIMIT=590,
    FETCH_DRIVER_TAGS_BY_PROFILES_FROM_SERVICE=True,
)
@pytest.mark.driver_tags_match(
    dbid='test_db', uuid='almaty_uuid', tags=['almaty_tag'],
)
@pytest.mark.match_profile(
    dbid='test_db', uuid='almaty_uuid', entity_tags=['almaty_tag'],
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_onorder_subvention_groups_almaty(
        taxi_driver_protocol,
        load_json,
        driver_authorizer_service,
        config,
        lru_config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    apply_config(config, lru_config)

    driver_authorizer_service.set_session(
        'test_db', 'test_session', 'almaty_uuid',
    )

    request_params = {
        'db': 'test_db',
        'session': 'test_session',
        'locale': 'ru',
        'lat': '43.238286',
        'lon': '76.945456',
    }

    response = taxi_driver_protocol.get(
        '/driver/onorder-subvention-groups', params=request_params,
    )

    assert response.status_code == 200

    response_data = response.json()
    expected_data = load_json('expected_almaty.json')
    assert response_data == _prepare_driver_points_in_expected_result(
        expected_data, dms_context,
    )


@pytest.mark.parametrize('lru_config', LRU_CONFIG)
@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(
    ENABLE_EXTENDING_SUBVENTION_BY_GEOAREAS=True,
    SUBVENTION_SCHEDULE_TAXIMETER_DISPLAYING_DAYS={'__default__': 1},
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_onorder_subvention_groups_empty(
        taxi_driver_protocol,
        driver_authorizer_service,
        config,
        lru_config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    apply_config(config, lru_config)

    driver_authorizer_service.set_session(
        'test_db', 'test_session', 'almaty_uuid',
    )

    request_params = {
        'db': 'test_db',
        'session': 'test_session',
        'locale': 'ru',
        'lat': '55.733863',
        'lon': '37.590533',
    }

    response = taxi_driver_protocol.get(
        '/driver/onorder-subvention-groups', params=request_params,
    )

    assert response.status_code == 200
    response_data = response.json()
    expected_data = {
        'items_for_map': [],
        'items_for_schedule': [
            {
                'date': '2017-07-06',
                'localized_date': 'Ближайшие сутки',
                'localized_price': '600 Р.',
                'rules': [
                    {
                        'driver_points_current': 90.0,
                        'driver_points_required': 70.0,
                        'from': '00:00',
                        'from_utc': '2017-07-05T21:00:00+0000',
                        'id': '_id/57def69d3d11433ca46fa4c8',
                        'is_active': True,
                        'localized_driver_points': 'Карма',
                        'localized_geo_description': 'По всему городу',
                        'localized_requirements_status': 'выполнено',
                        'localized_time': 'Круглосуточно',
                        'steps': [{'localized_sum': '600 Р.', 'sum': 600.0}],
                        'to': '00:00',
                        'to_utc': '2017-07-06T21:00:00+0000',
                        'type': 'add',
                    },
                ],
                'slider_from_utc': '2017-07-06T11:00:00+0000',
                'slider_to_utc': '2017-07-07T11:00:00+0000',
            },
        ],
        'localized_required_for_bonuses': 'Требуется для получения доплат:',
        'localized_requirements': 'Требования',
        'localized_steps': 'Этапы получения бонуса',
        'localized_title': 'Гарантированные бонусы в Москве',
        'subvention_descriptions': [
            {
                'text': (
                    'Необходимо быть в синей зоне ... Пусть гарантия '
                    '800 Р., заработок 600 Р., бонус - 200 Р. '
                    '(200 Р. + 600 Р. = 800 Р.)'
                ),
                'title': 'Подробнее о гарантии',
                'type': 'geo_booking',
            },
        ],
    }
    assert response_data == _prepare_driver_points_in_expected_result(
        expected_data, dms_context,
    )


@pytest.mark.parametrize('lru_config', LRU_CONFIG)
@pytest.mark.now('2017-07-07T14:15:16+0300')
@pytest.mark.config(
    ENABLE_EXTENDING_SUBVENTION_BY_GEOAREAS=True,
    SUBVENTION_SCHEDULE_TAXIMETER_DISPLAYING_DAYS={'__default__': 3},
    FETCH_DRIVER_TAGS_BY_PROFILES_FROM_SERVICE=True,
)
@pytest.mark.driver_tags_match(
    dbid='test_db', uuid='almaty_uuid', tags=['almaty_tag'],
)
@pytest.mark.match_profile(
    dbid='test_db', uuid='almaty_uuid', entity_tags=['almaty_tag'],
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_onorder_subvention_groups_almaty_friday(
        taxi_driver_protocol,
        load_json,
        driver_authorizer_service,
        config,
        lru_config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    apply_config(config, lru_config)

    driver_authorizer_service.set_session(
        'test_db', 'test_session', 'almaty_uuid',
    )

    request_params = {
        'db': 'test_db',
        'session': 'test_session',
        'locale': 'ru',
        'lat': '43.238286',
        'lon': '76.945456',
    }

    response = taxi_driver_protocol.get(
        '/driver/onorder-subvention-groups', params=request_params,
    )

    assert response.status_code == 200

    response_data = response.json()
    expected_data = load_json('expected_almaty_friday.json')
    assert response_data == _prepare_driver_points_in_expected_result(
        expected_data, dms_context,
    )


@pytest.mark.parametrize('lru_config', LRU_CONFIG)
@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(
    SUBVENTION_SCHEDULE_TAXIMETER_DISPLAYING_DAYS={'__default__': 4},
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_enabled_subventions_by_driver_points_default(
        taxi_driver_protocol,
        load_json,
        driver_authorizer_service,
        config,
        lru_config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    apply_config(config, lru_config)

    driver_authorizer_service.set_session(
        'test_db', 'test_session', 'test_uuid',
    )

    request_params = {
        'db': 'test_db',
        'session': 'test_session',
        'locale': 'ru',
        'lat': '55.733863',
        'lon': '37.590533',
    }

    response = taxi_driver_protocol.get(
        '/driver/onorder-subvention-groups',
        params=request_params,
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.60 (562)',
        },
    )

    assert response.status_code == 200
    response_data = response.json()

    expected_data = load_json('expected_moscow_driver_points.json')
    assert response_data == _prepare_driver_points_in_expected_result(
        expected_data, dms_context,
    )


@pytest.mark.parametrize('lru_config', LRU_CONFIG)
@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(
    SUBVENTION_SCHEDULE_TAXIMETER_DISPLAYING_DAYS={'__default__': 4},
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_enabled_subventions_by_driver_points_city(
        taxi_driver_protocol,
        load_json,
        driver_authorizer_service,
        config,
        lru_config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    apply_config(config, lru_config)

    driver_authorizer_service.set_session(
        'test_db', 'test_session', 'test_uuid',
    )

    request_params = {
        'db': 'test_db',
        'session': 'test_session',
        'locale': 'ru',
        'lat': '55.733863',
        'lon': '37.590533',
    }

    response = taxi_driver_protocol.get(
        '/driver/onorder-subvention-groups',
        params=request_params,
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.60 (562)',
        },
    )

    assert response.status_code == 200
    response_data = response.json()

    expected_data = load_json('expected_moscow_driver_points.json')
    assert response_data == _prepare_driver_points_in_expected_result(
        expected_data, dms_context,
    )


@pytest.mark.parametrize('lru_config', LRU_CONFIG)
@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(
    SUBVENTION_SCHEDULE_TAXIMETER_DISPLAYING_DAYS={'__default__': 4},
    CACHE_BILLING_SUBVENTION_RULES_UPDATE_ENABLED=True,
    MIN_VERSION_FOR_BOOKING_SUBVENTIONS='8.60',
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_billing_subvention_rules(
        now,
        taxi_driver_protocol,
        load_json,
        bss,
        driver_authorizer_service,
        config,
        lru_config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    apply_config(config, lru_config)

    bss.add_rule(load_json('geobooking_rule_moscow.json'))
    bss.add_rule(load_json('geobooking_rule_moscow_with_tags.json'))
    taxi_driver_protocol.invalidate_caches(now)

    driver_authorizer_service.set_session(
        'test_db', 'test_session', 'test_uuid',
    )

    request_params = {
        'db': 'test_db',
        'session': 'test_session',
        'locale': 'ru',
        'lat': '55.733863',
        'lon': '37.590533',
    }

    response = taxi_driver_protocol.get(
        '/driver/onorder-subvention-groups',
        params=request_params,
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.60 (562)',
        },
    )

    assert response.status_code == 200
    response_data = response.json()

    expected_data = load_json('expected_moscow_booking.json')
    assert response_data == _prepare_driver_points_in_expected_result(
        expected_data, dms_context,
    )
    bss.clean_rules()


@pytest.mark.parametrize('lru_config', LRU_CONFIG)
@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(
    SUBVENTION_SCHEDULE_TAXIMETER_DISPLAYING_DAYS={'__default__': 4},
    USE_BILLING_SUBVENTIONS_ONLY=True,
    CACHE_BILLING_SUBVENTION_RULES_UPDATE_ENABLED=True,
    MIN_VERSION_FOR_BOOKING_SUBVENTIONS='8.60',
    MIN_VERSION_FOR_SUBVENTION_REQUIREMENT_STATUS='999.99',
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_onorder_subvention_groups_billing(
        lru_config,
        taxi_driver_protocol,
        load_json,
        bss,
        now,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    apply_config(config, lru_config)

    if lru_config:
        all_rules = load_json('billing_rules_moscow.json')
    else:
        all_rules = load_json('billing_rules.json')
    for rule in all_rules:
        bss.add_rule(rule)

    taxi_driver_protocol.invalidate_caches(now)
    driver_authorizer_service.set_session(
        'test_db', 'test_session', 'test_uuid',
    )

    request_params = {
        'db': 'test_db',
        'session': 'test_session',
        'locale': 'ru',
        'lat': '55.733863',
        'lon': '37.590533',
    }

    response = taxi_driver_protocol.get(
        '/driver/onorder-subvention-groups',
        params=request_params,
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.60 (562)',
        },
    )

    assert response.status_code == 200
    response_data = response.json()

    expected_data = load_json('expected_moscow_billing.json')
    sort_osg_response(expected_data)
    sort_osg_response(response_data)
    assert response_data == _prepare_driver_points_in_expected_result(
        expected_data, dms_context,
    )
    bss.clean_rules()


@pytest.mark.parametrize('lru_config', LRU_CONFIG)
@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(
    SUBVENTION_SCHEDULE_TAXIMETER_DISPLAYING_DAYS={'__default__': 4},
    USE_BILLING_SUBVENTIONS_ONLY=True,
    CACHE_BILLING_SUBVENTION_RULES_UPDATE_ENABLED=True,
    MIN_VERSION_FOR_BOOKING_SUBVENTIONS='8.60',
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_enabled_subventions_by_driver_points_city_billing(
        taxi_driver_protocol,
        load_json,
        bss,
        now,
        driver_authorizer_service,
        config,
        lru_config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):

    all_rules = load_json('billing_rules.json')
    for rule in all_rules:
        bss.add_rule(rule)
    taxi_driver_protocol.invalidate_caches(now)
    driver_authorizer_service.set_session(
        'test_db', 'test_session', 'test_uuid',
    )

    request_params = {
        'db': 'test_db',
        'session': 'test_session',
        'locale': 'ru',
        'lat': '55.733863',
        'lon': '37.590533',
    }

    response = taxi_driver_protocol.get(
        '/driver/onorder-subvention-groups',
        params=request_params,
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.60 (562)',
        },
    )

    assert response.status_code == 200
    response_data = response.json()

    expected_data = load_json('expected_moscow_driver_points_billing.json')
    sort_osg_response(expected_data)
    sort_osg_response(response_data)
    assert response_data == _prepare_driver_points_in_expected_result(
        expected_data, dms_context,
    )
    bss.clean_rules()


@pytest.mark.parametrize('lru_config', LRU_CONFIG)
@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(
    SUBVENTION_SCHEDULE_TAXIMETER_DISPLAYING_DAYS={'__default__': 4},
    GEOBOOKING_DESCRIPTION_PARAMS={
        '__default__': {'__default__': {'orders_sum': 15.1, 'bonus': 1.7}},
    },
    CURRENCY_FORMATTING_RULES={'__default__': {'__default__': 1}},
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_dynamic_description_decimals(
        taxi_driver_protocol,
        load_json,
        driver_authorizer_service,
        config,
        lru_config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    apply_config(config, lru_config)

    driver_authorizer_service.set_session(
        'test_db', 'test_session', 'test_uuid',
    )

    request_params = {
        'db': 'test_db',
        'session': 'test_session',
        'locale': 'ru',
        'lat': '55.733863',
        'lon': '37.590533',
    }

    response = taxi_driver_protocol.get(
        '/driver/onorder-subvention-groups', params=request_params,
    )

    assert response.status_code == 200
    response_data = response.json()

    expected_data = load_json('expected_moscow_decimals.json')
    assert response_data == _prepare_driver_points_in_expected_result(
        expected_data, dms_context,
    )


@pytest.mark.parametrize('lru_config', LRU_CONFIG)
@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(CACHE_BILLING_SUBVENTION_RULES_UPDATE_ENABLED=True)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_error_when_no_cache_available(
        now,
        taxi_driver_protocol,
        load_json,
        driver_authorizer_service,
        mockserver,
        config,
        lru_config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    @mockserver.json_handler('/bss/v1/rules/select')
    def mock_external(request):
        return mockserver.make_response('', 500)

    taxi_driver_protocol.invalidate_caches(now)

    driver_authorizer_service.set_session(
        'test_db', 'test_session', 'test_uuid',
    )
    request_params = {
        'db': 'test_db',
        'session': 'test_session',
        'locale': 'ru',
        'lat': '55.733863',
        'lon': '37.590533',
    }
    response = taxi_driver_protocol.get(
        '/driver/onorder-subvention-groups',
        params=request_params,
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 99.00 (9900)',
        },
    )
    assert response.status_code == 500


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(
    SUBVENTION_SCHEDULE_TAXIMETER_DISPLAYING_DAYS={'__default__': 4},
    USE_BILLING_SUBVENTIONS_ONLY=True,
    CACHE_BILLING_SUBVENTION_RULES_UPDATE_ENABLED=False,
    MIN_VERSION_FOR_BOOKING_SUBVENTIONS='8.60',
    MIN_VERSION_FOR_SUBVENTION_REQUIREMENT_STATUS='999.99',
    BS_CLIENT_LRU_CACHE_ENABLED=True,
    BILLING_SUBVENTIONS_HANDLES_USE_BS_CLIENT=[
        '/driver/onorder_subvention_groups',
    ],
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_billing_subvention_cache_metrics(
        taxi_driver_protocol,
        load_json,
        bss,
        now,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):

    all_rules = load_json('billing_rules_moscow.json')
    for rule in all_rules:
        bss.add_rule(rule)

    taxi_driver_protocol.invalidate_caches(now)
    driver_authorizer_service.set_session(
        'test_db', 'test_session', 'test_uuid',
    )

    request_params = {
        'db': 'test_db',
        'session': 'test_session',
        'locale': 'ru',
        'lat': '55.733863',
        'lon': '37.590533',
    }

    assert (
        taxi_driver_protocol.get(
            '/driver/onorder-subvention-groups',
            params=request_params,
            headers={
                'Accept-Language': 'ru',
                'User-Agent': 'Taximeter 8.60 (562)',
            },
        ).status_code
        == 200
    )

    bss.clean_rules()

    metrics = taxi_driver_protocol.get('/service/statistics').json()
    bcc = metrics['billing_client']['cache']
    assert bcc
    bss.clean_rules()


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(
    SUBVENTION_SCHEDULE_TAXIMETER_DISPLAYING_DAYS={'__default__': 4},
    CACHE_BILLING_SUBVENTION_RULES_UPDATE_ENABLED=False,
    FETCH_DRIVER_TAGS_BY_LICENSES_FROM_SERVICE=True,
    FETCH_DRIVER_TAGS_V2_FROM_SERVICE=True,
    FETCH_DRIVER_TAGS_BY_PROFILES_FROM_SERVICE=True,
    USE_BILLING_SUBVENTIONS_ONLY=True,
    ENABLE_TAG_FILTERING_BY_BILLLING=True,
    BS_CLIENT_LRU_CACHE_ENABLED=False,
    BILLING_SUBVENTIONS_HANDLES_USE_BS_CLIENT=[
        '/driver/onorder_subvention_groups',
    ],
    MIN_VERSION_FOR_BOOKING_SUBVENTIONS='8.60',
)
@pytest.mark.driver_tags_match(
    dbid='test_db', uuid='test_uuid', tags=['luxary'],
)
@pytest.mark.match_profile(
    dbid='test_db', uuid='test_uuid', entity_tags=['luxary'],
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_billing_subvention_rules_request_body(
        now,
        taxi_driver_protocol,
        load_json,
        bss,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    bss.add_rule(load_json('geobooking_rule_moscow_with_tags.json'))
    taxi_driver_protocol.invalidate_caches(now)

    driver_authorizer_service.set_session(
        'test_db', 'test_session', 'test_uuid',
    )

    request_params = {
        'db': 'test_db',
        'session': 'test_session',
        'locale': 'ru',
        'lat': '55.733863',
        'lon': '37.590533',
    }

    response = taxi_driver_protocol.get(
        '/driver/onorder-subvention-groups',
        params=request_params,
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.60 (562)',
        },
    )

    assert response.status_code == 200
    bss_requests = bss.rules_select_subventions_call_params
    assert len(bss_requests) == bss.calls
    assert bss.calls == 1

    assert json.loads(bss_requests[0]) == {
        'is_personal': False,
        'limit': 1000,
        'profile_tags': ['luxary'],
        'status': 'enabled',
        'tariff_zone': 'moscow',
        'time_range': {
            'end': '2017-07-13T11:15:16+00:00',
            'start': '2017-07-06T11:15:16+00:00',
        },
    }
    bss.clean_rules()


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(
    SUBVENTION_SCHEDULE_TAXIMETER_DISPLAYING_DAYS={'__default__': 4},
    CACHE_BILLING_SUBVENTION_RULES_UPDATE_ENABLED=False,
    FETCH_DRIVER_TAGS_BY_LICENSES_FROM_SERVICE=True,
    FETCH_DRIVER_TAGS_V2_FROM_SERVICE=True,
    FETCH_DRIVER_TAGS_BY_PROFILES_FROM_SERVICE=True,
    USE_BILLING_SUBVENTIONS_ONLY=True,
    ENABLE_TAG_FILTERING_BY_BILLLING=True,
    BS_CLIENT_LRU_CACHE_ENABLED=False,
    BILLING_SUBVENTIONS_HANDLES_USE_BS_CLIENT=[
        '/driver/onorder_subvention_groups',
    ],
    MIN_VERSION_FOR_BOOKING_SUBVENTIONS='8.60',
    REQUST_ONLY_REQUIRED_SUBVENTION_TYPES=True,
)
@pytest.mark.driver_tags_match(
    dbid='test_db', uuid='test_uuid', tags=['luxary'],
)
@pytest.mark.match_profile(
    dbid='test_db', uuid='test_uuid', entity_tags=['luxary'],
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_billing_subvention_rules_request_body_required_types(
        now,
        taxi_driver_protocol,
        load_json,
        bss,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    bss.add_rule(load_json('geobooking_rule_moscow_with_tags.json'))
    taxi_driver_protocol.invalidate_caches(now)

    driver_authorizer_service.set_session(
        'test_db', 'test_session', 'test_uuid',
    )

    request_params = {
        'db': 'test_db',
        'session': 'test_session',
        'locale': 'ru',
        'lat': '55.733863',
        'lon': '37.590533',
    }

    response = taxi_driver_protocol.get(
        '/driver/onorder-subvention-groups',
        params=request_params,
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.60 (562)',
        },
    )

    assert response.status_code == 200
    bss_requests = bss.rules_select_subventions_call_params
    assert len(bss_requests) == bss.calls
    assert bss.calls == 1

    assert json.loads(bss_requests[0]) == {
        'is_personal': False,
        'limit': 1000,
        'types': ['goal', 'guarantee', 'add', 'geo_booking'],
        'profile_tags': ['luxary'],
        'status': 'enabled',
        'tariff_zone': 'moscow',
        'time_range': {
            'end': '2017-07-13T11:15:16+00:00',
            'start': '2017-07-06T11:15:16+00:00',
        },
    }
    bss.clean_rules()


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(
    BS_CLIENT_THROW_EXCEPTIONS_FURTHER=True,
    MIN_VERSION_FOR_BOOKING_SUBVENTIONS='8.60',
    MIN_VERSION_FOR_SUBVENTION_REQUIREMENT_STATUS='999.99',
    BILLING_SUBVENTIONS_HANDLES_USE_BS_CLIENT=[
        '/driver/onorder_subvention_groups',
    ],
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_billing_subvention_500_on_bad_subvention(
        now,
        taxi_driver_protocol,
        load_json,
        bss,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):

    taxi_driver_protocol.invalidate_caches(now)
    bss.add_rule(load_json('bad_rule.json'))

    driver_authorizer_service.set_session(
        'test_db', 'test_session', 'test_uuid',
    )

    request_params = {
        'db': 'test_db',
        'session': 'test_session',
        'locale': 'ru',
        'lat': '55.733863',
        'lon': '37.590533',
    }

    response = taxi_driver_protocol.get(
        '/driver/onorder-subvention-groups',
        params=request_params,
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.60 (562)',
        },
    )

    assert response.status_code == 500
    bss.clean_rules()


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.parametrize(
    'rules_select_limit, bss_calls', [(2, 3), (3, 2), (4, 2), (5, 1)],
)
@pytest.mark.config(
    MIN_VERSION_FOR_BOOKING_SUBVENTIONS='8.60',
    MIN_VERSION_FOR_SUBVENTION_REQUIREMENT_STATUS='999.99',
    BILLING_SUBVENTIONS_HANDLES_USE_BS_CLIENT=[
        '/driver/onorder_subvention_groups',
    ],
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_billing_subvention_get_with_different_limits(
        now,
        taxi_driver_protocol,
        load_json,
        bss,
        driver_authorizer_service,
        rules_select_limit,
        bss_calls,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    config.set_values({'BS_CLIENT_RULES_SELECT_LIMIT': rules_select_limit})
    taxi_driver_protocol.invalidate_caches(now)
    bss.set_rules_select_limit(rules_select_limit)
    all_rules = load_json('billing_rules_moscow.json')
    for rule in all_rules:
        bss.add_rule(rule)

    driver_authorizer_service.set_session(
        'test_db', 'test_session', 'test_uuid',
    )

    request_params = {
        'db': 'test_db',
        'session': 'test_session',
        'locale': 'ru',
        'lat': '55.733863',
        'lon': '37.590533',
    }

    assert (
        taxi_driver_protocol.get(
            '/driver/onorder-subvention-groups',
            params=request_params,
            headers={
                'Accept-Language': 'ru',
                'User-Agent': 'Taximeter 8.60 (562)',
            },
        ).status_code
        == 200
    )

    bss_requests = bss.rules_select_subventions_call_params
    assert len(bss_requests) == bss.calls

    assert bss.calls == bss_calls

    for i in range(len(bss_requests)):
        request = json.loads(bss_requests[i])
        assert request['limit'] == rules_select_limit
        if i > 0:
            if i * rules_select_limit < len(all_rules):
                request['cursor'] == all_rules[i * rules_select_limit][
                    'cursor'
                ]

    bss.clean_rules()
    bss.set_rules_select_limit(-1)


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(
    SUBVENTION_SCHEDULE_TAXIMETER_DISPLAYING_DAYS={'__default__': 4},
    MIN_VERSION_FOR_BOOKING_SUBVENTIONS='8.60',
    MIN_VERSION_FOR_SUBVENTION_REQUIREMENT_STATUS='999.99',
    BILLING_SUBVENTIONS_HANDLES_USE_BS_CLIENT=[
        '/driver/onorder_subvention_groups',
    ],
    CACHE_BILLING_SUBVENTION_RULES_UPDATE_ENABLED=False,
    ENABLE_FILTER_SUBVENTION_RULES_BY_BRANDING_TYPE=True,
    USE_BILLING_SUBVENTIONS_ONLY=True,
    BS_CLIENT_LRU_CACHE_ENABLED=True,
    API_OVER_DATA_WORK_MODE={
        '__default__': {'__default__': 'oldway'},
        'driver-protocol': {
            '__default__': 'oldway',
            'onorder_subvention_group': 'newway',
        },
    },
)
@pytest.mark.parametrize(
    'dbid,uuid,expected_branding',
    [
        ('test_db', 'test_uuid', 'no_branding'),
        ('test_db', 'test_uuid1', 'sticker'),
        ('test_db', 'test_uuid2', 'full_branding'),
    ],
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_billing_subvention_branding_filtering(
        now,
        taxi_driver_protocol,
        load_json,
        bss,
        dbid,
        uuid,
        expected_branding,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    taxi_driver_protocol.invalidate_caches(now)

    rule_template = load_json('billing_rules_moscow_branding.json')[0]
    rule = deepcopy(rule_template)
    rule['branding_type'] = expected_branding
    bss.add_rule(rule)

    session = 'session' + uuid
    driver_authorizer_service.set_session(dbid, session, uuid)

    request_params = {
        'db': dbid,
        'session': session,
        'locale': 'ru',
        'lat': '55.733863',
        'lon': '37.590533',
    }

    response = taxi_driver_protocol.get(
        '/driver/onorder-subvention-groups',
        params=request_params,
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.60 (562)',
        },
    )

    assert response.status_code == 200
    bss_requests = bss.rules_select_subventions_call_params
    assert len(bss_requests) == bss.calls
    assert bss.calls == 1
    assert json.loads(bss_requests[0])['driver_branding'] == expected_branding
    bss.clean_rules()


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(
    SUBVENTION_SCHEDULE_TAXIMETER_DISPLAYING_DAYS={'__default__': 4},
    OSG_FETCH_TARIFF_CLASSES_FROM_MONGO=False,
    USE_PARK_UUID_FOR_CLASSES_IN_SUBVENTIONS=True,
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_onorder_subvention_groups_driver_categories(
        taxi_driver_protocol,
        load_json,
        driver_authorizer_service,
        config,
        mockserver,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_tracker_categories(request):
        assert json.loads(request.get_data()) == {
            'db_id': 'test_db',
            'uuid': 'test_uuid',
            'point': [37.590533, 55.733863],
        }
        tracker_response = load_json('tracker_response.json')
        return tracker_response

    driver_authorizer_service.set_session(
        'test_db', 'test_session', 'test_uuid',
    )

    request_params = {
        'db': 'test_db',
        'session': 'test_session',
        'locale': 'ru',
        'lat': '55.733863',
        'lon': '37.590533',
    }

    response = taxi_driver_protocol.get(
        '/driver/onorder-subvention-groups', params=request_params,
    )

    assert response.status_code == 200
    assert mock_tracker_categories.times_called == 1
    response_data = response.json()

    expected_data = load_json('expected_moscow.json')
    assert response_data == _prepare_driver_points_in_expected_result(
        expected_data, dms_context,
    )


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(
    SUBVENTION_SCHEDULE_TAXIMETER_DISPLAYING_DAYS={'__default__': 4},
    CACHE_BILLING_SUBVENTION_RULES_UPDATE_ENABLED=True,
    MIN_VERSION_FOR_BOOKING_SUBVENTIONS='8.60',
    BS_CLIENT_LRU_CACHE_ENABLED=True,
    BILLING_SUBVENTIONS_HANDLES_USE_BS_CLIENT=[
        '/driver/onorder_subvention_groups',
    ],
    ENABLE_EXTENDING_SUBVENTION_BY_GEOAREAS=True,
    USE_BILLING_SUBVENTIONS_ONLY=True,
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_billing_subvention_rules_multiple_geoareas(
        now,
        taxi_driver_protocol,
        load_json,
        bss,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    bss.add_rule(load_json('geobooking_rule_moscow_multiple_geoareas.json'))
    taxi_driver_protocol.invalidate_caches(now)

    driver_authorizer_service.set_session(
        'test_db', 'test_session', 'test_uuid',
    )

    request_params = {
        'db': 'test_db',
        'session': 'test_session',
        'locale': 'ru',
        'lat': '55.733863',
        'lon': '37.590533',
    }

    response = taxi_driver_protocol.get(
        '/driver/onorder-subvention-groups',
        params=request_params,
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.60 (562)',
        },
    )

    assert response.status_code == 200
    response_data = response.json()
    expected_data = load_json('expected_moscow_multiple_geoareas.json')
    assert response_data == _prepare_driver_points_in_expected_result(
        expected_data, dms_context,
    )

    response2 = taxi_driver_protocol.get(
        '/driver/onorder-subvention-groups',
        params=request_params,
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.60 (562)',
        },
    )

    assert response2.status_code == 200
    response_data2 = response.json()

    assert response_data == _prepare_driver_points_in_expected_result(
        response_data2, dms_context,
    )
    bss.clean_rules()


HEADERS = {'Accept-Language': 'ru', 'User-Agent': 'Taximeter 8.60 (562)'}
ARGS = {'park_id': 'test_db', 'lat': '55.733863', 'lon': '37.590533'}


@pytest.mark.now('2017-07-06T14:15:16+0300')
@pytest.mark.config(
    SUBVENTION_SCHEDULE_TAXIMETER_DISPLAYING_DAYS={'__default__': 4},
    MIN_VERSION_FOR_SUBVENTION_REQUIREMENT_STATUS='999.99',
)
@common.sv_proxy_decorator(
    experiment_name='subvention_view_proxy_schedule',
    consumer='driver_protocol/driver_onorder_subvention_groups',
    url='/subvention_view/v1/schedule',
    result='expected_moscow.json',
    expected_args=ARGS,
    expected_headers=HEADERS,
)
def test_onorder_subvention_groups_sv_proxy(
        taxi_driver_protocol,
        mockserver,
        load_json,
        driver_authorizer_service,
        config,
        experiments3,
        proxy_mode,
):
    # apply_config(config, lru_config)
    driver_authorizer_service.set_session(
        'test_db', 'test_session', 'test_uuid',
    )

    response = taxi_driver_protocol.get(
        '/driver/onorder-subvention-groups',
        params={
            'db': 'test_db',
            'session': 'test_session',
            'locale': 'ru',
            'lat': '55.733863',
            'lon': '37.590533',
        },
        headers=HEADERS,
    )

    assert response.status_code == 200
    response_data = response.json()

    expected_data = load_json('expected_moscow.json')
    assert response_data == expected_data
