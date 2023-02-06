import json

import pytest

from . import common

DMS_ACTIVITY_VALUES = {
    '59e8bb4609792ee9bacffd60': 89,
    '59e8bb4609792ee9bacffd61': 89,
}


@pytest.mark.parametrize(
    'bs_rules_select,bs_by_driver,response_data',
    [
        ('bs/rules_select.json', 'bs/by_driver.json', 'good_response_1.json'),
        (
            'bs/rules_select.json',
            'bs/by_driver_empty.json',
            'good_response_1.json',
        ),
        (
            'bs/rules_select_all_steps.json',
            'bs/by_driver_one_date.json',
            'good_response_2.json',
        ),
        (
            'bs/rules_select.json',
            'bs/by_driver_between_steps.json',
            'good_response_between_steps.json',
        ),
        (
            'bs/rules_select.json',
            'bs/by_driver_all_steps.json',
            'good_response_all_steps.json',
        ),
        (
            'bs/rules_select.json',
            'bs/by_driver_all_steps.json',
            'good_response_all_steps.json',
        ),
        (
            'bs/rules_select_empty.json',
            'bs/by_driver_all_steps.json',
            'good_response_empty.json',
        ),
        (
            'bs/rules_select.json',
            'bs/by_driver_more_than_request_dates.json',
            'good_response_all_steps.json',
        ),
    ],
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_subvention_rules(
        taxi_driver_protocol,
        mockserver,
        bs_rules_select,
        bs_by_driver,
        response_data,
        load_json,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/bss/v1/rules/select')
    def mock_bs_rules_select(request):
        return load_json(bs_rules_select)

    @mockserver.json_handler('/bss/v1/by_driver')
    def mock_bs_by_driver(request):
        return load_json(bs_by_driver)

    response = taxi_driver_protocol.post(
        '/driver/subvention-groups?db=1488&session=qwerty',
        json={
            'lon': 37.618423,
            'lat': 55.751244,
            'from': '2018-09-23',
            'to': '2018-09-25',
            'types': ['daily_guarantee'],
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data == load_json(response_data)


@pytest.mark.config(
    CACHE_BILLING_SUBVENTION_RULES_UPDATE_ENABLED=True,
    USE_BILLING_SUBVENTIONS_CACHE_IN_SG=True,
)
@pytest.mark.parametrize(
    'bs_rules_select,bs_by_driver,response_data',
    [
        ('bs/rules_select.json', 'bs/by_driver.json', 'good_response_1.json'),
        (
            'bs/rules_select.json',
            'bs/by_driver_empty.json',
            'good_response_1.json',
        ),
        (
            'bs/rules_select_all_steps.json',
            'bs/by_driver_one_date.json',
            'good_response_2.json',
        ),
        (
            'bs/rules_select.json',
            'bs/by_driver_between_steps.json',
            'good_response_between_steps.json',
        ),
        (
            'bs/rules_select.json',
            'bs/by_driver_all_steps.json',
            'good_response_all_steps.json',
        ),
        (
            'bs/rules_select.json',
            'bs/by_driver_all_steps.json',
            'good_response_all_steps.json',
        ),
        (
            'bs/rules_select_empty.json',
            'bs/by_driver_all_steps.json',
            'good_response_empty.json',
        ),
        (
            'bs/rules_select.json',
            'bs/by_driver_more_than_request_dates.json',
            'good_response_all_steps.json',
        ),
    ],
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_subvention_rules_cached(
        taxi_driver_protocol,
        bs_rules_select,
        bs_by_driver,
        response_data,
        load_json,
        bss,
        driver_authorizer_service,
        mockserver,
        now,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/bss/v1/by_driver')
    def mock_bs_by_driver(request):
        return load_json(bs_by_driver)

    bs_rules = load_json(bs_rules_select)
    for rule in bs_rules['subventions']:
        bss.add_rule(rule)
    taxi_driver_protocol.invalidate_caches(now)

    response = taxi_driver_protocol.post(
        '/driver/subvention-groups?db=1488&session=qwerty',
        json={
            'lon': 37.618423,
            'lat': 55.751244,
            'from': '2018-09-23',
            'to': '2018-09-25',
            'types': ['daily_guarantee'],
        },
        headers={'Accept-Language': 'ru'},
    )
    bss.clean_rules()
    bss.clean_by_driver_subvention()
    data = response.json()

    assert response.status_code == 200
    assert data == load_json(response_data)


@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_subvention_rules_not_supported_type(
        taxi_driver_protocol,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')
    dms_context.set_expect_dms_called(False)

    response = taxi_driver_protocol.post(
        '/driver/subvention-groups?db=1488&session=qwerty',
        json={
            'lon': 37.618423,
            'lat': 55.751244,
            'from': '2018-09-23',
            'to': '2018-09-24',
            'types': ['guarantee'],
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 400


@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_subvention_rules_bad_dates(
        taxi_driver_protocol,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    response = taxi_driver_protocol.post(
        '/driver/subvention-groups?db=1488&session=qwerty',
        json={
            'lon': 37.618423,
            'lat': 55.751244,
            'from': '2018-09-23',
            'to': '2018-09-23',
            'types': ['daily_guarantee'],
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 400


@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_subvention_rules_not_found_zone(
        taxi_driver_protocol,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')
    dms_context.set_expect_dms_called(False)

    response = taxi_driver_protocol.post(
        '/driver/subvention-groups?db=1488&session=qwerty',
        json={
            'lon': 77,
            'lat': 77,
            'from': '2018-09-23',
            'to': '2018-09-24',
            'types': ['daily_guarantee'],
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 404


@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_subvention_rules_not_found_driver(
        taxi_driver_protocol,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverXXX')
    dms_context.set_expect_dms_called(False)

    response = taxi_driver_protocol.post(
        '/driver/subvention-groups?db=1488&session=qwerty',
        json={
            'lon': 37.618423,
            'lat': 55.751244,
            'from': '2018-09-23',
            'to': '2018-09-24',
            'types': ['daily_guarantee'],
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 404


@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_subvention_rules_failed_get_by_driver(
        taxi_driver_protocol,
        mockserver,
        load_json,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/bss/v1/rules/select')
    def mock_bs_rules_select(request):
        content = json.loads(request.get_data())
        assert content == {
            'is_personal': False,
            'status': 'enabled',
            'tariff_zone': 'moscow',
            'time_range': {
                'start': '2018-09-22T21:00:00+00:00',
                'end': '2018-09-23T21:00:00+00:00',
            },
            'types': ['daily_guarantee'],
            'limit': 1000,
        }
        return load_json('bs/rules_select.json')

    @mockserver.json_handler('/bss/v1/by_driver')
    def mock_bs_by_driver(request):
        return mockserver.make_response('', 500)

    response = taxi_driver_protocol.post(
        '/driver/subvention-groups?db=1488&session=qwerty',
        json={
            'lon': 37.618423,
            'lat': 55.751244,
            'from': '2018-09-23',
            'to': '2018-09-24',
            'types': ['daily_guarantee'],
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 500


@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_subvention_rules_failed_get_select_rules(
        taxi_driver_protocol,
        mockserver,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/bss/v1/rules/select')
    def mock_bs_rules_select(request):
        return mockserver.make_response('', 500)

    response = taxi_driver_protocol.post(
        '/driver/subvention-groups?db=1488&session=qwerty',
        json={
            'lon': 37.618423,
            'lat': 55.751244,
            'from': '2018-09-23',
            'to': '2018-09-24',
            'types': ['daily_guarantee'],
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 500


@pytest.mark.parametrize(
    'bs_rules_select,bs_by_driver,bs_rule_ids,response_data,taximeter_version',
    [
        (
            'bs/rules_select_with_tags.json',
            'bs/by_driver_with_tags_old_version.json',
            ['group_id/volgodonsk2_daily_guarantee_2018_09_17'],
            'tags_response_1.json',
            'Taximeter 8.77 (456)',
        ),
        (
            'bs/rules_select_with_tags.json',
            'bs/by_driver_with_tags_new_version.json',
            [
                'group_id/volgodonsk_daily_guarantee_2018_09_17',
                'group_id/volgodonsk2_daily_guarantee_2018_09_17',
            ],
            'tags_response_2.json',
            'Taximeter 9.77 (456)',
        ),
    ],
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_subvention_rules_tags_check(
        bs_rules_select,
        bs_by_driver,
        bs_rule_ids,
        response_data,
        taxi_driver_protocol,
        mockserver,
        taximeter_version,
        load_json,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/bss/v1/rules/select')
    def mock_bs_rules_select(request):
        return load_json(bs_rules_select)

    @mockserver.json_handler('/bss/v1/by_driver')
    def mock_bs_by_driver(request):
        req_json = json.loads(request.get_data())
        assert set(req_json['subvention_rule_ids']) == set(bs_rule_ids)
        return load_json(bs_by_driver)

    response = taxi_driver_protocol.post(
        '/driver/subvention-groups?db=1488&session=qwerty',
        json={
            'lon': 37.618423,
            'lat': 55.751244,
            'from': '2018-09-23',
            'to': '2018-09-25',
            'types': ['daily_guarantee'],
        },
        headers={'Accept-Language': 'ru', 'User-Agent': taximeter_version},
    )
    assert response.status_code == 200
    data = response.json()
    assert data == load_json(response_data)


@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'subvention.daily_guarantee.local_sum_prefix': {'ru': 'от'},
    },
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_subvention_rules_with_prefix(
        taxi_driver_protocol,
        mockserver,
        load_json,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/bss/v1/rules/select')
    def mock_bs_rules_select(request):
        return load_json('bs/rules_select.json')

    @mockserver.json_handler('/bss/v1/by_driver')
    def mock_bs_by_driver(request):
        return load_json('bs/by_driver.json')

    response = taxi_driver_protocol.post(
        '/driver/subvention-groups?db=1488&session=qwerty',
        json={
            'lon': 37.618423,
            'lat': 55.751244,
            'from': '2018-09-23',
            'to': '2018-09-25',
            'types': ['daily_guarantee'],
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data == load_json('good_response_local_sum_prefix.json')


@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_subvention_rules_two_brandings(
        taxi_driver_protocol,
        mockserver,
        load_json,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/bss/v1/rules/select')
    def mock_bs_rules_select(request):
        return load_json('bs/rules_select_two_brandings.json')

    @mockserver.json_handler('/bss/v1/by_driver')
    def mock_bs_by_driver(request):
        return load_json('bs/by_driver_empty.json')

    response = taxi_driver_protocol.post(
        '/driver/subvention-groups?db=1488&session=qwerty',
        json={
            'lon': 37.618423,
            'lat': 55.751244,
            'from': '2018-09-24',
            'to': '2018-09-25',
            'types': ['daily_guarantee'],
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['items_for_day'][0]['subventions']) == 1


@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'subvention.daily_guarantee.local_sum_prefix': {'ru': 'до'},
    },
)
@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'nmfg_ctor': '9.77 (455)'}},
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
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_subvention_rules_constructor(
        taxi_driver_protocol,
        bs_rules_select,
        bs_by_driver,
        response_data,
        load_json,
        bss,
        driver_authorizer_service,
        mockserver,
        now,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/bss/v1/by_driver')
    def mock_bs_by_driver(request):
        return load_json(bs_by_driver)

    bs_rules = load_json(bs_rules_select)
    for rule in bs_rules['subventions']:
        bss.add_rule(rule)
    taxi_driver_protocol.invalidate_caches(now)

    response = taxi_driver_protocol.post(
        '/driver/subvention-groups?db=1488&session=qwerty',
        json={
            'lon': 37.618423,
            'lat': 55.751244,
            'from': '2018-09-23',
            'to': '2018-09-25',
            'types': ['daily_guarantee'],
        },
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 9.77 (456)',
        },
    )
    bss.clean_rules()
    bss.clean_by_driver_subvention()
    data = response.json()

    assert response.status_code == 200
    assert data == load_json(response_data)


@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'subvention.daily_guarantee.local_sum_prefix': {'ru': 'до'},
    },
)
@pytest.mark.config(
    CACHE_BILLING_SUBVENTION_RULES_UPDATE_ENABLED=False,
    FETCH_DRIVER_TAGS_BY_LICENSES_FROM_SERVICE=True,
    FETCH_DRIVER_TAGS_V2_FROM_SERVICE=True,
    FETCH_DRIVER_TAGS_BY_PROFILES_FROM_SERVICE=True,
    BILLING_SUBVENTIONS_HANDLES_USE_BS_CLIENT=['/driver/subvention-groups'],
    FILTER_SUBVENTIONS_BY_TAGS_FOR_NMFG=True,
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'nmfg_ctor': '9.77 (455)'}},
    },
)
@pytest.mark.driver_tags_match(dbid='1488', uuid='driver', tags=['luxary'])
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
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_subvention_rules_constructor_with_tags(
        taxi_driver_protocol,
        bs_rules_select,
        bs_by_driver,
        response_data,
        load_json,
        mockserver,
        bss,
        now,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    @mockserver.json_handler('/bss/v1/by_driver')
    def mock_bs_by_driver(request):
        return load_json(bs_by_driver)

    bs_rules = load_json(bs_rules_select)
    for rule in bs_rules['subventions']:
        bss.add_rule(rule)
    taxi_driver_protocol.invalidate_caches(now)

    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    response = taxi_driver_protocol.post(
        '/driver/subvention-groups?db=1488&session=qwerty',
        json={
            'lon': 37.618423,
            'lat': 55.751244,
            'from': '2018-09-23',
            'to': '2018-09-25',
            'types': ['daily_guarantee'],
        },
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 9.77 (456)',
        },
    )
    bss.clean_rules()
    bss.clean_by_driver_subvention()
    data = response.json()

    assert response.status_code == 200
    assert data == load_json(response_data)

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
            'end': '2018-09-24T21:00:00+00:00',
            'start': '2018-09-22T21:00:00+00:00',
        },
        'types': ['daily_guarantee'],
    }


@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'subvention.daily_guarantee.local_sum_prefix': {'ru': 'до'},
    },
)
@pytest.mark.config(
    CACHE_BILLING_SUBVENTION_RULES_UPDATE_ENABLED=False,
    FETCH_DRIVER_TAGS_BY_LICENSES_FROM_SERVICE=True,
    FETCH_DRIVER_TAGS_V2_FROM_SERVICE=True,
    FETCH_DRIVER_TAGS_BY_PROFILES_FROM_SERVICE=True,
    BILLING_SUBVENTIONS_HANDLES_USE_BS_CLIENT=['/driver/subvention-groups'],
    FILTER_SUBVENTIONS_BY_BRANDING_FOR_NMFG=True,
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'nmfg_ctor': '9.77 (455)'}},
    },
)
@pytest.mark.driver_tags_match(dbid='1488', uuid='driver', tags=['luxary'])
@pytest.mark.parametrize(
    'driver_id,bs_rules_select,bs_by_driver,driver_branding',
    [
        (
            'driver',
            'bs/rules_select_two_brandings.json',
            'bs/by_driver_two_brandings.json',
            'full_branding',
        ),
        (
            'no_full_branding_driver',
            'bs/rules_select_two_brandings_sticker_no_full.json',
            'bs/by_driver_two_brandings.json',
            'sticker',
        ),
        (
            'no_branding_driver',
            'bs/rules_select_two_brandings_no_full_nobranding.json',
            'bs/by_driver_two_brandings_no_full.json',
            'no_branding',
        ),
    ],
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_subvention_rules_constructor_with_branding(
        taxi_driver_protocol,
        driver_id,
        bs_rules_select,
        bs_by_driver,
        driver_branding,
        load_json,
        mockserver,
        bss,
        now,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    @mockserver.json_handler('/bss/v1/by_driver')
    def mock_bs_by_driver(request):
        return load_json(bs_by_driver)

    bs_rules = load_json(bs_rules_select)
    for rule in bs_rules['subventions']:
        bss.add_rule(rule)
    taxi_driver_protocol.invalidate_caches(now)

    driver_authorizer_service.set_session('1488', 'qwerty', driver_id)

    response = taxi_driver_protocol.post(
        '/driver/subvention-groups?db=1488&session=qwerty',
        json={
            'lon': 37.618423,
            'lat': 55.751244,
            'from': '2018-09-23',
            'to': '2018-09-25',
            'types': ['daily_guarantee'],
        },
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 9.77 (456)',
        },
    )
    bss.clean_rules()
    bss.clean_by_driver_subvention()
    data = response.json()

    assert response.status_code == 200
    assert data['items_for_day'][0]['ui_items'][3]['detail'] == '1000 Р.'
    subvention_details = data['items_for_day'][0]['ui_items'][2]['items']
    assert subvention_details[0]['body']['title'] == '10000 Р.'

    bss_requests = bss.rules_select_subventions_call_params
    assert len(bss_requests) == bss.calls
    assert bss.calls == 1

    assert json.loads(bss_requests[0]) == {
        'is_personal': False,
        'limit': 1000,
        'driver_branding': driver_branding,
        'status': 'enabled',
        'tariff_zone': 'moscow',
        'time_range': {
            'end': '2018-09-24T21:00:00+00:00',
            'start': '2018-09-22T21:00:00+00:00',
        },
        'types': ['daily_guarantee'],
    }


@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'subvention.daily_guarantee.local_sum_prefix': {'ru': 'до'},
    },
)
@pytest.mark.config(
    CACHE_BILLING_SUBVENTION_RULES_UPDATE_ENABLED=False,
    FETCH_DRIVER_TAGS_BY_LICENSES_FROM_SERVICE=True,
    FETCH_DRIVER_TAGS_V2_FROM_SERVICE=True,
    FETCH_DRIVER_TAGS_BY_PROFILES_FROM_SERVICE=True,
    BILLING_SUBVENTIONS_HANDLES_USE_BS_CLIENT=['/driver/subvention-groups'],
    FILTER_SUBVENTIONS_BY_BRANDING_FOR_NMFG=True,
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'nmfg_ctor': '9.77 (455)'}},
    },
    USE_DRIVER_TAGS_FOR_MATCH_PROFILE={'__default__': True},
)
@pytest.mark.driver_tags_match(dbid='1488', uuid='driver', tags=['luxary'])
@pytest.mark.match_profile(dbid='1488', uuid='driver', entity_tags=['luxary'])
@pytest.mark.parametrize(
    'driver_id,has_subventions',
    [('driver', False), ('no_branding_driver', True)],
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_subvention_rules_filter_no_full_branding(
        taxi_driver_protocol,
        driver_id,
        has_subventions,
        load_json,
        mockserver,
        bss,
        now,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        experiments3,
        use_dms_driver_points,
):

    # @mockserver.json_handler('/bss/v1/by_driver')
    # def mock_bs_by_driver(request):
    #    return load_json("bs/by_driver_two_brandings_no_full.json")

    bs_rules = load_json('bs/rules_select_no_full_branding.json')
    for rule in bs_rules['subventions']:
        bss.add_rule(rule)
    taxi_driver_protocol.invalidate_caches(now)

    driver_authorizer_service.set_session('1488', 'qwerty', driver_id)

    response = taxi_driver_protocol.post(
        '/driver/subvention-groups?db=1488&session=qwerty',
        json={
            'lon': 37.618423,
            'lat': 55.751244,
            'from': '2018-09-23',
            'to': '2018-09-25',
            'types': ['daily_guarantee'],
        },
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 9.77 (456)',
        },
    )
    bss.clean_rules()
    bss.clean_by_driver_subvention()
    data = response.json()

    assert response.status_code == 200

    if has_subventions:
        subvention_details = data['items_for_day'][0]['ui_items'][2]['items']
        assert subvention_details[0]['body']['title'] == '10000 Р.'
    else:
        assert data is None


@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'subvention.daily_guarantee.local_sum_prefix': {'ru': 'до'},
    },
)
@pytest.mark.config(
    CACHE_BILLING_SUBVENTION_RULES_UPDATE_ENABLED=False,
    BILLING_SUBVENTIONS_HANDLES_USE_BS_CLIENT=['/driver/subvention-groups'],
    FILTER_SUBVENTIONS_BY_CLASSES_FOR_NMFG=True,
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'nmfg_ctor': '9.77 (455)'}},
    },
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'driver_protocol', 'dst': 'billing_subventions'}],
    TVM_SERVICES={'driver_protocol': 1, 'billing_subventions': 2},
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
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_subvention_rules_class_filtering(
        taxi_driver_protocol,
        bs_rules_select,
        bs_by_driver,
        load_json,
        mockserver,
        tvm2_client,
        bss,
        now,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    ticket = 'ticket'
    tvm2_client.set_ticket(json.dumps({'2': {'ticket': ticket}}))

    @mockserver.json_handler('/bss/v1/by_driver')
    def mock_bs_by_driver(request):
        assert 'X-Ya-Service-Ticket' in request.headers
        assert request.headers['X-Ya-Service-Ticket'] == ticket
        return load_json(bs_by_driver)

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_tracker_profile(request):
        tracker_response = load_json('tracker_response.json')
        tracker_response['point'] = [37.6, 55.75]
        return tracker_response

    bs_rules = load_json(bs_rules_select)
    for rule in bs_rules['subventions']:
        bss.add_rule(rule)
    taxi_driver_protocol.invalidate_caches(now)

    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    response = taxi_driver_protocol.post(
        '/driver/subvention-groups?db=1488&session=qwerty',
        json={
            'lon': 37.618423,
            'lat': 55.751244,
            'from': '2018-09-23',
            'to': '2018-09-25',
            'types': ['daily_guarantee'],
        },
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 9.77 (456)',
        },
    )
    bss.clean_rules()
    bss.clean_by_driver_subvention()

    assert response.status_code == 200

    bss_requests = bss.rules_select_subventions_call_params
    assert len(bss_requests) == bss.calls
    assert bss.calls == 1

    request = json.loads(bss_requests[0])
    request['order_tariff_classes'].sort()
    request['profile_tariff_classes'].sort()
    assert request == {
        'is_personal': False,
        'limit': 1000,
        'order_tariff_classes': ['comfort', 'econom', 'vip'],
        'profile_tariff_classes': ['comfort', 'econom', 'vip'],
        'status': 'enabled',
        'tariff_zone': 'moscow',
        'time_range': {
            'end': '2018-09-24T21:00:00+00:00',
            'start': '2018-09-22T21:00:00+00:00',
        },
        'types': ['daily_guarantee'],
    }


@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'subvention.daily_guarantee.local_sum_prefix': {'ru': 'до'},
    },
)
@pytest.mark.config(
    CACHE_BILLING_SUBVENTION_RULES_UPDATE_ENABLED=False,
    BILLING_SUBVENTIONS_HANDLES_USE_BS_CLIENT=['/driver/subvention-groups'],
    FILTER_SUBVENTIONS_BY_CLASSES_FOR_NMFG=True,
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'nmfg_ctor': '9.77 (455)'}},
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
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_subvention_rules_driver_categories_500(
        taxi_driver_protocol,
        bs_rules_select,
        bs_by_driver,
        load_json,
        mockserver,
        bss,
        now,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    @mockserver.json_handler('/bss/v1/by_driver')
    def mock_bs_by_driver(request):
        return load_json(bs_by_driver)

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_tracker_profile(request):
        return mockserver.make_response('Internal Error', 500)

    bs_rules = load_json(bs_rules_select)
    for rule in bs_rules['subventions']:
        bss.add_rule(rule)
    taxi_driver_protocol.invalidate_caches(now)

    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    response = taxi_driver_protocol.post(
        '/driver/subvention-groups?db=1488&session=qwerty',
        json={
            'lon': 37.618423,
            'lat': 55.751244,
            'from': '2018-09-23',
            'to': '2018-09-25',
            'types': ['daily_guarantee'],
        },
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 9.77 (456)',
        },
    )
    bss.clean_rules()
    bss.clean_by_driver_subvention()

    assert response.status_code == 200

    bss_requests = bss.rules_select_subventions_call_params
    assert len(bss_requests) == bss.calls
    assert bss.calls == 1

    assert json.loads(bss_requests[0]) == {
        'is_personal': False,
        'limit': 1000,
        'status': 'enabled',
        'tariff_zone': 'moscow',
        'time_range': {
            'end': '2018-09-24T21:00:00+00:00',
            'start': '2018-09-22T21:00:00+00:00',
        },
        'types': ['daily_guarantee'],
    }


@pytest.mark.config(
    USE_PARK_UUID_FOR_CLASSES_IN_SUBVENTIONS=True,
    FILTER_SUBVENTIONS_BY_CLASSES_FOR_NMFG=True,
)
@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'subvention.daily_guarantee.local_sum_prefix': {'ru': 'от'},
    },
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_subvention_rules_driver_categories(
        taxi_driver_protocol,
        mockserver,
        load_json,
        driver_authorizer_service,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_tracker_categories(request):
        assert json.loads(request.get_data()) == {
            'db_id': '1488',
            'uuid': 'driver',
            'point': [37.6, 55.75],
        }
        tracker_response = load_json('tracker_response.json')
        return tracker_response

    @mockserver.json_handler('/bss/v1/rules/select')
    def mock_bs_rules_select(request):
        return load_json('bs/rules_select.json')

    @mockserver.json_handler('/bss/v1/by_driver')
    def mock_bs_by_driver(request):
        return load_json('bs/by_driver.json')

    response = taxi_driver_protocol.post(
        '/driver/subvention-groups?db=1488&session=qwerty',
        json={
            'lon': 37.6,
            'lat': 55.75,
            'from': '2018-09-23',
            'to': '2018-09-25',
            'types': ['daily_guarantee'],
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data == load_json('good_response_local_sum_prefix.json')
    assert mock_tracker_categories.times_called == 1


REQUEST = {
    'lon': 37.618423,
    'lat': 55.751244,
    'from': '2018-09-23',
    'to': '2018-09-25',
    'types': ['daily_guarantee'],
}

HEADERS = {'Accept-Language': 'ru'}


@common.sv_proxy_decorator(
    experiment_name='subvention_view_proxy_nmfg_status',
    consumer='driver_protocol/driver_subvention_groups',
    url='/subvention_view/v1/nmfg/status',
    result='good_response_1.json',
    expected_args={'park_id': '1488'},
    expected_request=REQUEST,
    expected_headers=HEADERS,
)
def test_subvention_rules_proxy(
        taxi_driver_protocol,
        mockserver,
        load_json,
        driver_authorizer_service,
        experiments3,
        proxy_mode,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/bss/v1/rules/select')
    def mock_bs_rules_select(request):
        return load_json('bs/rules_select.json')

    @mockserver.json_handler('/bss/v1/by_driver')
    def mock_bs_by_driver(request):
        return load_json('bs/by_driver.json')

    response = taxi_driver_protocol.post(
        '/driver/subvention-groups?db=1488&session=qwerty',
        json=REQUEST,
        headers=HEADERS,
    )
    assert response.status_code == 200
    data = response.json()
    assert data == load_json('good_response_1.json')
