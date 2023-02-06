# pylint: disable=redefined-outer-name, import-only-modules, too-many-lines, import-error
# flake8: noqa F401
import uuid

import pytest

from tests_plugins import json_util

from pricing_extended.mock_router import yamaps_router, mock_yamaps_router
from pricing_extended.mocking_base import check_not_called
from pricing_extended.mocking_base import check_called
from pricing_extended.mocking_base import check_called_once
from .plugins import test_utils
from .plugins import utils_request
from .round_values import round_values

from .plugins.mock_user_api import user_api
from .plugins.mock_user_api import mock_user_api_get_phones
from .plugins.mock_user_api import mock_user_api_get_users
from .plugins.mock_surge import surger
from .plugins.mock_surge import mock_surger
from .plugins.mock_umlaas_pricing import mock_umlaas_pricing
from .plugins.mock_umlaas_pricing import umlaas_pricing
from .plugins.mock_ride_discounts import ride_discounts
from .plugins.mock_ride_discounts import mock_ride_discounts
from .plugins.mock_tags import tags
from .plugins.mock_tags import mock_tags
from .plugins.mock_coupons import coupons
from .plugins.mock_coupons import mock_coupons
from .plugins.mock_decoupling import decoupling
from .plugins.mock_decoupling import mock_decoupling_corp_tariffs
from .plugins.utils_response import econom_category
from .plugins.utils_response import econom_response
from .plugins.utils_response import business_category
from .plugins.utils_response import business_response
from .plugins.utils_response import econom_with_additional_prices
from .plugins.utils_response import decoupling_response
from .plugins.utils_response import category_list
from .plugins.utils_response import calc_price

EXPERIMENTS3_CASES = test_utils.BooleanFlagCases(
    [
        'has_user',
        'no_user',
        'other_country',
        'other_zone',
        'other_user',
        'other_app',
        'other_phone',
        'other_yandex_uid',
        'other_payment_type',
    ],
)


@pytest.fixture(name='new_pricing_flow_dry_run', autouse=False)
def new_pricing_flow_dry_run(testpoint, experiments3):
    experiments3.add_experiment(
        clauses=[
            {
                'predicate': {'type': 'true'},
                'enabled': True,
                'title': '',
                'value': {'work_mode': 'dry_run', 'skip_source_load': True},
            },
        ],
        name='new_pricing_data_generator_settings',
        consumers=['pricing-data-preparer/prepare'],
        match={'enabled': True, 'predicate': {'type': 'true'}},
    )

    @testpoint('new_pricing_flow_dry_run')
    def _new_pricing_flow_dry_run(data):
        data['new'].pop('backend_variables_uuids', None)
        data['old'].pop('backend_variables_uuids', None)
        assert data['new'] == data['old']

    return _new_pricing_flow_dry_run


def _check_and_pop_route_id(data):
    assert 'route_id' in data
    try:
        uuid.UUID(data['route_id'])
    except ValueError:
        assert False
    data.pop('route_id')
    return data


@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    PRICING_DATA_PREPARER_ROUTER_ENABLED={'__default__': True},
    PRICING_DATA_PREPARER_SURGER_ENABLED={
        '__default__': {'__default__': True},
    },
    PRICING_DATA_PREPARER_COUPONS_ENABLED=True,
    PRICING_DATA_PREPARER_DISCOUNTS_ENABLED=True,
    PRICING_PASSENGER_TAGS_ENABLED=True,
)
@pytest.mark.experiments3(filename='exp3_config_test.json')
@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize(
    argnames=EXPERIMENTS3_CASES.get_names(),
    argvalues=EXPERIMENTS3_CASES.get_args(),
    ids=EXPERIMENTS3_CASES.get_ids(),
)
async def test_v2_prepare_experiments3(
        taxi_pricing_data_preparer,
        mock_yamaps_router,
        yamaps_router,
        user_api,
        surger,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        mock_surger,
        mock_ride_discounts,
        mock_tags,
        mock_coupons,
        mock_decoupling_corp_tariffs,
        testpoint,
        has_user,
        no_user,
        other_country,
        other_zone,
        other_user,
        other_app,
        other_phone,
        other_yandex_uid,
        other_payment_type,
        new_pricing_flow_dry_run,
):
    experiments_list = ['match_me_always']
    if not no_user and not other_user:
        experiments_list.append('match_by_user')
    if not other_yandex_uid and not no_user:
        experiments_list.append('match_by_yandex_uid')
    if not other_app and not no_user:
        experiments_list.append('match_by_app_and_ver')
    elif other_app:
        experiments_list.append('not_match_by_app')
    experiments_list.append('match_by_zone')
    experiments_list.append('match_by_country')
    if not other_phone and not no_user:
        experiments_list.append('match_by_phone')
    if not other_payment_type and not no_user:
        experiments_list.append('match_by_payment_option')
    if other_payment_type:
        experiments_list.append('match_by_payment_method')
    sorted_experiments = sorted(experiments_list)

    pm_sorted_experiments = []
    for experiment in sorted_experiments:
        pm_sorted_experiments.append('_'.join(['pm', experiment]))

    v2_prepare_exps = sorted(
        sorted_experiments + ['new_pricing_data_generator_settings'],
    )

    @testpoint('experiments3_tp_pricing-data-preparer/prepare')
    def experiments_prepare(data):
        assert data == v2_prepare_exps

    @testpoint('experiments3_tp_pricing-data-preparer/price_modifications')
    def experiments_price_modifications(data):
        assert data == pm_sorted_experiments

    pre_request = utils_request.Request()

    if no_user:
        pre_request.remove_user_info()
        yamaps_router.set_user_id(None)
        surger.set_user_id(None)
    if other_user:
        new_id = 'other_user_id'
        pre_request.set_user_id(new_id)
        user_api.set_user_id(new_id)
        yamaps_router.set_user_id(new_id)
        surger.set_user_id(new_id)
    if other_phone:
        user_api.set_phone_id('other_phone_id')
    if other_app:
        pre_request.set_application(name='taxikomany', version='9.1.1')
    if other_yandex_uid:
        user_api.set_yandex_uid('other_yandex_uid')
    if other_payment_type:
        pre_request.add_decoupling_method()

    request = pre_request.get()
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 200

    assert experiments_prepare.times_called == 1
    assert experiments_price_modifications.times_called == 2

    data = response.json()
    exps = data['categories']['econom']['user']['data']['exps']
    assert sorted(exps) == pm_sorted_experiments
    for exp in exps:
        if exp == 'pm_match_me_always':
            assert exps[exp] == {
                'key1': {'str': 'test_format', 'val': 0.333},
                'key2': {'val': 1.5},
                'key3': {'str': 'only_string'},
                'keyN': None,
            }
        else:
            assert exps[exp] == {}


@pytest.mark.parametrize('force_fallback', [True, False])
@pytest.mark.config(
    SURGE_CLIENT_SMART_FALLBACK_ENABLED=True,
    SURGE_CALCULATOR_CLIENT_QOS={
        '__default__': {'attempts': 1, 'timeout-ms': 100},
    },
)
async def test_v2_prepare_statistics(
        taxi_pricing_data_preparer,
        statistics,
        surger,
        mock_surger,
        mock_yamaps_router,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        testpoint,
        force_fallback,
        new_pricing_flow_dry_run,
):
    @testpoint('surge_calculator_detached_call')
    def calculator_background(data):
        pass

    prefix = 'handler.surge-calculator./v1/calc-surge-post'

    if force_fallback:
        # Will force fallback usage inside smart fallback
        statistics.fallbacks = [f'{prefix}.fallback']
        await taxi_pricing_data_preparer.invalidate_caches()

    request = utils_request.Request().get()
    async with statistics.capture(taxi_pricing_data_preparer) as capture:
        for i in range(10):
            if i > 2:
                surger.must_crack()
            response = await taxi_pricing_data_preparer.post(
                'v2/prepare', json=request,
            )
            if force_fallback:
                # wait for background call to take place,
                # to avoid race around 500 response
                await calculator_background.wait_call()

    assert response.status_code == 200
    assert capture.statistics[f'{prefix}.success'] == 3
    assert capture.statistics[f'{prefix}.error'] == 7
    assert mock_surger.times_called == 10


FIXED_PRICE_CASES_DISCARD_REASONS = {
    'normal_fixed_price': None,
    'one_point_in_waypoints': 'NO_POINT_B',
    'router_turned_off': 'NO_ROUTE',
    'router_breaks': 'NO_ROUTE',
    # 'route_blocked': 'BLOCKED_ROUTE',
    'empty_route': 'NO_ROUTE',
    'too_big_line_distance_1': 'NO_ROUTE',
    'too_big_line_distance_2': 'NO_ROUTE',
    'fix_price_not_enabled': 'DISABLED_FOR_CATEGORY',
    'fix_price_disabled': 'DISABLED_BY_CORP',
    'long_distance_ride': 'LONG_TRIP',
    'preorder_with_due_changed_config': None,
    'preorder_with_due': 'DELAYED_ORDER_DUE',
    'preorder_with_is_delayed_and_with_due': 'DELAYED_ORDER_FLAG',
    'preorder_with_is_delayed_and_without_due': 'DELAYED_ORDER_FLAG',
}


@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    PRICING_DATA_PREPARER_ROUTER_ENABLED={'__default__': True},
    PRICING_DATA_PREPARER_SURGER_ENABLED={
        '__default__': {'__default__': True},
    },
    PRICING_DATA_PREPARER_COUPONS_ENABLED=True,
    PRICING_DATA_PREPARER_DISCOUNTS_ENABLED=True,
    PRICING_PASSENGER_TAGS_ENABLED=True,
    ROUTE_RETRIES=1,
    FIXED_PRICE_MAX_ALLOWED_DISTANCE_ENABLED=True,
    DELAYED_ORDER_DETECTION_THRESHOLD_MIN=11,
    PRICING_DATA_PREPARER_MAX_ALLOWED_LINEAR_DISTANCE_KM=4000,
)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize(
    argnames='case, discard_reason',
    argvalues=list(
        (k, v) for k, v in FIXED_PRICE_CASES_DISCARD_REASONS.items()
    ),
    ids=list(FIXED_PRICE_CASES_DISCARD_REASONS.keys()),
)
@pytest.mark.parametrize(
    'use_fallback_router',
    [None, False, True],
    ids=[
        'fallback_router_is_none',
        'fallback_router_disabled',
        'fallback_router_enabled',
    ],
)
@pytest.mark.parametrize(
    'preorder_configs_enabled',
    (
        pytest.param(
            True,
            marks=pytest.mark.experiments3(
                filename='exp3_config_preorder.json',
            ),
            id='preorder_configs_enabled',
        ),
        pytest.param(False, id='preorder_configs_disabled'),
    ),
)
@pytest.mark.parametrize('new_pricing_data_flow', ['dry_run', 'disable'])
async def test_v2_prepare_fixed_price(
        taxi_pricing_data_preparer,
        yamaps_router,
        mock_yamaps_router,
        surger,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        mock_surger,
        mock_ride_discounts,
        mock_tags,
        mock_coupons,
        decoupling,
        mock_decoupling_corp_tariffs,
        case,
        discard_reason,
        use_fallback_router,
        preorder_configs_enabled,
        taxi_config,
        testpoint,
        new_pricing_data_flow,
        experiments3,
        new_pricing_flow_dry_run,
):
    pre_request = utils_request.Request()
    preorder_with_fixprice = False
    experiments3.add_experiment(
        clauses=[
            {
                'predicate': {'type': 'true'},
                'enabled': True,
                'title': '',
                'value': {
                    'work_mode': new_pricing_data_flow,
                    'skip_source_load': True,
                },
            },
        ],
        name='new_pricing_data_generator_settings',
        consumers=['pricing-data-preparer/prepare'],
        match={'enabled': True, 'predicate': {'type': 'true'}},
    )

    if case == 'one_point_in_waypoints':
        pre_request.set_one_point_route()
    if case == 'router_turned_off':
        taxi_config.set(
            PRICING_DATA_PREPARER_ROUTER_ENABLED={'__default__': False},
        )
    if case == 'router_breaks':
        yamaps_router.must_crack(always=True)
    if case == 'route_blocked':
        yamaps_router.set_blocked()
    if case == 'fix_price_disabled':
        decoupling.disable_fix_price()
        pre_request.add_decoupling_method()
    if case == 'long_distance_ride':
        yamaps_router.set_long_route()
    if case == 'fix_price_not_enabled':
        pre_request.set_categories(['business'])
    if case == 'empty_route':
        yamaps_router.set_empty()
    if case == 'too_big_line_distance_1':
        pre_request.set_waypoints([[37.683, 55.774], [0.0, 0.0]])
    if case == 'too_big_line_distance_2':
        pre_request.set_waypoints(
            [[37.683, 55.774], [0.0, 0.0], [37.683, 55.774]],
        )
    if 'with_due' in case:
        pre_request.set_due('2019-02-01T14:25:00Z')
    if 'with_is_delayed' in case:
        pre_request.set_is_delayed(True)
    if preorder_configs_enabled and case in [
            'preorder_with_due',
            'preorder_with_is_delayed_and_with_due',
    ]:
        preorder_with_fixprice = True
        yamaps_router.set_dtm(1549031100)
        surger.set_due('2019-02-01T14:25:00+00:00')
        discard_reason = None
    if case == 'preorder_with_due_changed_config':
        taxi_config.set(DELAYED_ORDER_DETECTION_THRESHOLD_MIN=30)
    if use_fallback_router is not None:
        pre_request.set_use_fallback_router(use_fallback_router)

    total_waypoints = len(pre_request.get_waypoints())
    request = pre_request.get()
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 200
    data = response.json()

    if case == 'fix_price_not_enabled':
        category = data['categories']['business']
    else:
        category = data['categories']['econom']
    fix_flag = category['fixed_price']
    bv_fix_flag = category['user']['data']['category_data']['fixed_price']
    assert fix_flag == bv_fix_flag
    assert 'for_taximeter' in category['driver']['modifications']
    assert 'for_taximeter' in category['user']['modifications']
    if (
            case in ['normal_fixed_price', 'preorder_with_due_changed_config']
            or (
                case in ['router_breaks', 'empty_route', 'long_distance_ride']
                and use_fallback_router
            )
            or preorder_with_fixprice
    ):
        assert fix_flag
        assert 'for_fixed' in category['driver']['modifications']
        assert 'for_fixed' in category['user']['modifications']
    else:
        assert not fix_flag
        assert not 'for_fixed' in category['driver']['modifications']
        assert not 'for_fixed' in category['user']['modifications']

    if (
            case in ['too_big_line_distance_1', 'too_big_line_distance_2']
            or use_fallback_router
    ):
        assert not mock_yamaps_router.has_calls

    if not discard_reason or (
            case in ['router_breaks', 'empty_route', 'long_distance_ride']
            and use_fallback_router
    ):
        assert 'fixed_price_discard_reason' not in category
    else:
        assert category['fixed_price_discard_reason'] == discard_reason

    assert category['user']['data']['waypoints_count'] == total_waypoints

    if new_pricing_data_flow == 'dry_run':
        assert new_pricing_flow_dry_run.times_called == 1
    else:
        assert new_pricing_flow_dry_run.times_called == 0


CORP_FLAGS_CASES = test_utils.BooleanFlagCases(
    [
        'all_enabled',
        'disable_fix_price',
        'disable_surge',
        'disable_paid_supply',
    ],
)


@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    PRICING_DATA_PREPARER_ROUTER_ENABLED={'__default__': True},
    PRICING_DATA_PREPARER_SURGER_ENABLED={
        '__default__': {'__default__': True},
    },
    PRICING_DATA_PREPARER_COUPONS_ENABLED=True,
    PRICING_DATA_PREPARER_DISCOUNTS_ENABLED=True,
    PRICING_PASSENGER_TAGS_ENABLED=True,
)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize(
    argnames=CORP_FLAGS_CASES.get_names(),
    argvalues=CORP_FLAGS_CASES.get_args(),
    ids=CORP_FLAGS_CASES.get_ids(),
)
async def test_v2_prepare_corp_flags(
        taxi_pricing_data_preparer,
        mock_yamaps_router,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        mock_surger,
        mock_ride_discounts,
        mock_tags,
        mock_coupons,
        decoupling,
        mock_decoupling_corp_tariffs,
        all_enabled,
        disable_fix_price,
        disable_surge,
        disable_paid_supply,
        new_pricing_flow_dry_run,
):
    if disable_fix_price:
        decoupling.disable_fix_price()
    if disable_surge:
        decoupling.disable_surge()
    if disable_paid_supply:
        decoupling.disable_paid_supply()

    request = utils_request.Request().add_decoupling_method().get()

    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 200
    data = response.json()

    assert mock_decoupling_corp_tariffs.handler_client_tariff.times_called == 1
    corp_req = mock_decoupling_corp_tariffs.handler_client_tariff.next_call()
    assert (
        corp_req['request'].query['application']
        == request['user_info']['application']['name']
    )

    assert data['categories']['econom']['corp_decoupling']
    cat = data['categories']['econom']['user']['data']['category_data']
    assert cat['decoupling']

    assert data['categories']['econom']['fixed_price'] is not disable_fix_price
    assert cat['fixed_price'] is not disable_fix_price

    assert cat['disable_surge'] is disable_surge

    assert cat['disable_paid_supply'] is disable_paid_supply


TRIP_INFORMATION_CASES = test_utils.BooleanFlagCases(
    [
        'msk_route',
        'empty_route',
        'long_route',
        'one_point',
        'zero_delta_route',
        'has_toll_roads',
    ],
)


@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    PRICING_DATA_PREPARER_ROUTER_ENABLED={'__default__': True},
    PRICING_DATA_PREPARER_SURGER_ENABLED={
        '__default__': {'__default__': True},
    },
    PRICING_DATA_PREPARER_COUPONS_ENABLED=True,
    PRICING_DATA_PREPARER_DISCOUNTS_ENABLED=True,
    PRICING_PASSENGER_TAGS_ENABLED=True,
    FIXED_PRICE_MAX_ALLOWED_DISTANCE_ENABLED=True,
)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize(
    argnames=TRIP_INFORMATION_CASES.get_names(),
    argvalues=TRIP_INFORMATION_CASES.get_args(),
    ids=TRIP_INFORMATION_CASES.get_ids(),
)
async def test_v2_prepare_trip_information(
        taxi_pricing_data_preparer,
        yamaps_router,
        mock_yamaps_router,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        mock_surger,
        mock_ride_discounts,
        mock_tags,
        mock_coupons,
        mock_decoupling_corp_tariffs,
        msk_route,
        empty_route,
        long_route,
        one_point,
        zero_delta_route,
        has_toll_roads,
        new_pricing_flow_dry_run,
):
    if empty_route:
        yamaps_router.set_empty()
    if long_route:
        yamaps_router.set_long_route()
    if zero_delta_route:
        yamaps_router.set_zero_delta_route()
    if has_toll_roads:
        yamaps_router.set_with_toll_roads()

    pre_request = utils_request.Request().set_categories(['ubernight'])
    if one_point:
        pre_request.set_one_point_route()
    request = pre_request.get()

    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 200
    data = response.json()

    if empty_route or one_point:
        assert (
            'trip_information' not in data['categories']['ubernight']['driver']
        )
        assert (
            'trip_information' not in data['categories']['ubernight']['user']
        )
    else:
        assert 'trip_information' in data['categories']['ubernight']['driver']
        assert 'trip_information' in data['categories']['ubernight']['user']
        driver_trip = round_values(
            data['categories']['ubernight']['driver']['trip_information'],
        )
        driver_trip = _check_and_pop_route_id(driver_trip)
        user_trip = round_values(
            data['categories']['ubernight']['user']['trip_information'],
        )
        user_trip = _check_and_pop_route_id(user_trip)

        if msk_route or has_toll_roads:
            assert driver_trip == round_values(
                {
                    'distance': 2046.0000000000002,
                    'has_toll_roads': has_toll_roads,
                    'jams': True,
                    'time': 307.0,
                },
            )
            assert user_trip == round_values(
                {
                    'distance': 2046.0000000000002,
                    'has_toll_roads': has_toll_roads,
                    'jams': True,
                    'time': 307.0,
                },
            )
        elif long_route:
            assert driver_trip == {
                'distance': 634907.0,
                'has_toll_roads': False,
                'jams': True,
                'time': 16500.0,
            }
            assert user_trip == {
                'distance': 634907.0,
                'has_toll_roads': False,
                'jams': True,
                'time': 16500.0,
            }

    should_use_router = not one_point
    assert mock_yamaps_router.has_calls == should_use_router


TAXIMETER_METADATA_CASES = test_utils.BooleanFlagCases(
    ['max_distance_from_config', 'max_distance_from_tariff_settings'],
)


@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    PRICING_DATA_PREPARER_ROUTER_ENABLED={'__default__': True},
    PRICING_DATA_PREPARER_SURGER_ENABLED={
        '__default__': {'__default__': True},
    },
    PRICING_DATA_PREPARER_COUPONS_ENABLED=True,
    PRICING_DATA_PREPARER_DISCOUNTS_ENABLED=True,
    PRICING_PASSENGER_TAGS_ENABLED=True,
    FIXED_PRICE_MAX_DISTANCE_FROM_B=700,
)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize(
    'case',
    [
        'get_normal_db',
        pytest.param(
            'get_other_db', marks=pytest.mark.filldb(tariff_settings='other'),
        ),
    ],
    ids=TAXIMETER_METADATA_CASES.get_ids(),
)
async def test_v2_prepare_taximeter_metadata(
        taxi_pricing_data_preparer,
        mock_yamaps_router,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        mock_surger,
        mock_ride_discounts,
        mock_tags,
        mock_coupons,
        mock_decoupling_corp_tariffs,
        case,
        new_pricing_flow_dry_run,
):
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=utils_request.Request().get(),
    )
    assert response.status_code == 200
    data = response.json()
    metadata = data['categories']['econom']['taximeter_metadata']

    if case == 'get_normal_db':
        assert metadata['max_distance_from_point_b'] == 700
        assert not metadata['show_price_in_taximeter']

    if case == 'get_other_db':
        assert metadata['max_distance_from_point_b'] == 150
        assert metadata['show_price_in_taximeter']


@pytest.mark.config(ROUTER_MAPS_ENABLED=True)
@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.filldb(tariffs='without_tariff_settings')
@pytest.mark.experiments3(filename='exp3_config.json')
async def test_v2_prepare_empty_tariff_settings_flags(
        taxi_pricing_data_preparer,
        mock_yamaps_router,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        mock_surger,
        mock_ride_discounts,
        mock_tags,
        mock_coupons,
        mock_decoupling_corp_tariffs,
):
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=utils_request.Request().get(),
    )
    assert response.status_code == 200


CLIENT_LOGIC_CASES = test_utils.BooleanFlagCases(
    ['zuser', 'tolls_on', 'tolls_off'],
)


@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    PRICING_DATA_PREPARER_ROUTER_ENABLED={'__default__': True},
    PRICING_DATA_PREPARER_SURGER_ENABLED={
        '__default__': {'__default__': True},
    },
    PRICING_DATA_PREPARER_COUPONS_ENABLED=True,
    PRICING_DATA_PREPARER_DISCOUNTS_ENABLED=True,
    PRICING_PASSENGER_TAGS_ENABLED=True,
)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize(
    argnames=CLIENT_LOGIC_CASES.get_names(),
    argvalues=CLIENT_LOGIC_CASES.get_args(),
    ids=CLIENT_LOGIC_CASES.get_ids(),
)
async def test_v2_prepare_client_logic(
        taxi_pricing_data_preparer,
        load_json,
        yamaps_router,
        mock_yamaps_router,
        surger,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        mock_surger,
        mock_ride_discounts,
        mock_tags,
        mock_coupons,
        mock_decoupling_corp_tariffs,
        zuser,
        tolls_on,
        tolls_off,
        new_pricing_flow_dry_run,
):
    pre_request = utils_request.Request()
    if zuser:
        pre_request.set_user_id('zuser_code')
        surger.set_user_id('zuser_code')
        surger.set_phone_id(None)
    if tolls_on:
        pre_request.set_tolls('ALLOW')
        yamaps_router.set_tolls(True)
    if tolls_off:
        yamaps_router.set_tolls(False)
        pre_request.set_tolls('DENY')

    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=pre_request.get(),
    )
    assert response.status_code == 200

    if zuser:
        check_not_called(mock_user_api_get_users)
        check_not_called(mock_user_api_get_phones)


@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    PRICING_DATA_PREPARER_ROUTER_ENABLED={'__default__': True},
    PRICING_DATA_PREPARER_SURGER_ENABLED={
        '__default__': {'__default__': True},
    },
    PRICING_DATA_PREPARER_COUPONS_ENABLED=True,
    PRICING_DATA_PREPARER_DISCOUNTS_ENABLED=True,
    PRICING_PASSENGER_TAGS_ENABLED=True,
    APPLICATION_MAP_PLATFORM={
        '__default__': 'web',
        'call_center': 'callcenter',
    },
)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize(
    'order_type, econom_price',
    [('APPLICATION', 131), ('CALL_CENTER', 199)],
    ids=['application', 'call_center'],
)
async def test_v2_prepare_match_categories(
        taxi_pricing_data_preparer,
        mock_yamaps_router,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        mock_surger,
        mock_ride_discounts,
        mock_tags,
        mock_coupons,
        mock_decoupling_corp_tariffs,
        order_type,
        econom_price,
        new_pricing_flow_dry_run,
):
    big_list_of_categories = [
        'ultimate',
        'ubervan',
        'mkk',
        'uberselect',
        'minivan',
        'business',
        'demostand',
        'child_tariff',
        'econom',
        'uberselectplus',
        'ubernight',
        'mkk_antifraud',
        'selfdriving',
        'personal_driver',
        'comfortplus',
        'uberlux',
        'uberstart',
        'vip',
        'maybach',
        'uberkids',
        'uberx',
        'uberblack',
        'premium_van',
        'cargo',
        'not-existing',  # will not match
    ]

    pre_request = (
        utils_request.Request()
        .set_order_type(order_type)
        .set_categories(big_list_of_categories)
    )
    if order_type == 'CALL_CENTER':
        pre_request.set_application(name='call_center')

    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=pre_request.get(),
    )
    assert response.status_code == 200
    data = response.json()

    assert sorted(category_list(data)) == sorted(big_list_of_categories[:-1])
    user_price = calc_price(data['categories']['econom']['user']['price'])
    assert user_price == econom_price


@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    PRICING_DATA_PREPARER_ROUTER_ENABLED={'__default__': True},
    PRICING_DATA_PREPARER_SURGER_ENABLED={
        '__default__': {'__default__': True},
    },
    PRICING_DATA_PREPARER_COUPONS_ENABLED=True,
    PRICING_DATA_PREPARER_DISCOUNTS_ENABLED=True,
    PRICING_PASSENGER_TAGS_ENABLED=True,
    PRICING_DATA_PREPARER_RESPONSE_SUMMARY_ENABLED={'__default__': False},
)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.pgsql(
    'pricing_data_preparer', files=['rules.sql', 'workabilities.sql'],
)
@pytest.mark.parametrize(
    'request_categories, calculation_order, calculate_deps, expected_previous',
    [
        # no_calculation_order
        (
            [
                'econom',
                'business',
                'comfortplus',
                'vip',
                'ultimate',
                'maybach',
                'minivan',
                'child_tariff',
            ],
            [],
            False,
            {},
        ),
        # only_one_category_in_calculation_order
        (
            [
                'econom',
                'business',
                'comfortplus',
                'vip',
                'ultimate',
                'maybach',
                'minivan',
                'child_tariff',
            ],
            ['econom'],
            False,
            {},
        ),
        # two_categories_in_calculation_order
        (
            [
                'econom',
                'business',
                'comfortplus',
                'vip',
                'ultimate',
                'maybach',
                'minivan',
                'child_tariff',
            ],
            ['econom', 'business'],
            False,
            {'business': {'list': ['econom'], 'category': 'econom'}},
        ),
        # calculating_only_business_no_deps
        (['business'], ['econom', 'business'], False, {}),
        # calculating_business_with_deps
        (
            ['business'],
            ['econom', 'business'],
            True,
            {'business': {'list': ['econom'], 'category': 'econom'}},
        ),
        # three_categories_in_calculation_order
        (
            [
                'econom',
                'business',
                'comfortplus',
                'vip',
                'ultimate',
                'maybach',
                'minivan',
                'child_tariff',
            ],
            ['econom', 'business', 'vip'],
            False,
            {
                'business': {'list': ['econom'], 'category': 'econom'},
                'vip': {
                    'list': ['econom', 'business'],
                    'category': 'business',
                },
            },
        ),
        # vip_no_deps
        (
            ['vip', 'ultimate', 'maybach', 'minivan', 'child_tariff'],
            ['econom', 'business', 'vip'],
            False,
            {},
        ),
        # vip_with_two_deps
        (
            ['vip', 'ultimate', 'maybach', 'minivan', 'child_tariff'],
            ['econom', 'business', 'vip'],
            True,
            {'vip': {'list': ['econom', 'business'], 'category': 'business'}},
        ),
        # calculating_business_twice
        (
            [
                'econom',
                'business',
                'comfortplus',
                'vip',
                'ultimate',
                'maybach',
                'minivan',
                'child_tariff',
            ],
            ['econom', 'business', 'business'],
            False,
            {
                'business': {
                    'list': ['econom', 'business'],
                    'category': 'econom',
                },
            },
        ),
        # calculating_business_twice_and_vip_after
        (
            [
                'econom',
                'business',
                'comfortplus',
                'vip',
                'ultimate',
                'maybach',
                'minivan',
                'child_tariff',
            ],
            ['econom', 'business', 'business', 'vip'],
            False,
            {
                'business': {
                    'list': ['econom', 'business'],
                    'category': 'econom',
                },
                'vip': {
                    'list': ['econom', 'business'],
                    'category': 'business',
                },
            },
        ),
        # unneeded_category_in_calculation_order
        (
            [
                'econom',
                'business',
                'comfortplus',
                'vip',
                'ultimate',
                'maybach',
                'minivan',
                'child_tariff',
            ],
            ['econom', 'uberx', 'business', 'business', 'vip'],
            False,
            {
                'business': {
                    'list': ['econom', 'business'],
                    'category': 'econom',
                },
                'vip': {
                    'list': ['econom', 'business'],
                    'category': 'business',
                },
            },
        ),
    ],
    ids=[
        'no_calculation_order',
        'only_one_category_in_calculation_order',
        'two_categories_in_calculation_order',
        'calculating_only_business_no_deps',
        'calculating_business_with_deps',
        'three_categories_in_calculation_order',
        'vip_no_deps',
        'vip_with_two_deps',
        'calculating_business_twice',
        'calculating_business_twice_and_vip_after',
        'unneeded_category_in_calculation_order',
    ],
)
async def test_v2_prepare_previously_calculated_categories(
        taxi_pricing_data_preparer,
        mock_yamaps_router,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        mock_surger,
        mock_ride_discounts,
        mock_tags,
        mock_coupons,
        mock_decoupling_corp_tariffs,
        load_json,
        experiments3,
        request_categories,
        calculation_order,
        calculate_deps,
        expected_previous,
):
    experiments3.add_config(
        consumers=['pricing-data-preparer/prepare'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Setup by zone',
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'value': 'moscow',
                        'arg_name': 'zone',
                        'arg_type': 'string',
                    },
                },
                'value': {'categories_order': calculation_order},
            },
        ],
        name='pricing_data_preparer_categories_calculation_order',
        default_value={'categories_order': []},
    )

    if calculate_deps:
        experiments3.add_experiments_json(
            load_json('exp3_calculate_category_dependencies.json'),
        )

    pre_request = (
        utils_request.Request()
        .set_categories(request_categories)
        .set_additional_prices(
            antisurge=True,
            strikeout=True,
            combo_order=False,
            combo_inner=False,
            combo_outer=False,
        )
    )
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=pre_request.get(),
    )
    assert response.status_code == 200
    data = response.json()
    assert sorted(category_list(data)) == sorted(request_categories)

    for category in request_categories:
        category_data = data['categories'][category]
        assert 'data' not in category_data['driver']  # no decoupling here
        assert 'data' in category_data['user']

    expected_values = {
        'econom': {
            'driver': {
                'base_total': 130.05,
                'main_total': 131,
                'main_meta': {},
            },
            'user': {
                'base_total': 130.05,
                'main_total': 105,
                'main_strikeout': 131,
                'main_meta': {'discount_percent': 20},
            },
        },
        'business': {
            'driver': {
                'base_total': 199.552,
                'main_total': 200,
                'main_meta': {},
            },
            'user': {
                'base_total': 199.552,
                'main_total': 180,
                'main_strikeout': 200,
                'main_meta': {'discount_percent': 10},
            },
        },
    }

    for category, previous_info in expected_previous.items():
        user_data = data['categories'][category]['user']['data']
        assert 'previously_calculated_categories' in user_data
        assert 'previous_different_category' in user_data
        assert (
            user_data['previous_different_category']
            == previous_info['category']
        )
        pcc = user_data['previously_calculated_categories']
        assert sorted(pcc.keys()) == sorted(previous_info['list'])
        for previous in previous_info['list']:
            for subject in ['driver', 'user']:
                pcc_cat = pcc[previous][subject]
                assert set(pcc_cat['final_prices'].keys()) == set(['main'])
                exp_cat = expected_values[previous][subject]
                if previous in request_categories:
                    data_cat = data['categories'][previous][subject]
                    assert (
                        pcc_cat['base_price_total']
                        == sum(data_cat['base_price'].values())
                        == exp_cat['base_total']
                    )
                    assert (
                        pcc_cat['final_prices']['main']['total']
                        == data_cat['price']['total']
                        == exp_cat['main_total']
                    )
                    if 'main_strikeout' in exp_cat:
                        assert (
                            pcc_cat['final_prices']['main']['strikeout']
                            == data_cat['price']['strikeout']
                            == exp_cat['main_strikeout']
                        )
                    else:
                        assert (
                            'strikeout' not in pcc_cat['final_prices']['main']
                        )
                        assert 'strikeout' not in data_cat['price']
                    assert (
                        pcc_cat['final_prices']['main']['meta']
                        == data_cat['meta']
                        == exp_cat['main_meta']
                    )
                else:
                    assert previous not in data['categories']
                    assert pcc_cat['base_price_total'] == exp_cat['base_total']
                    assert (
                        pcc_cat['final_prices']['main']['total']
                        == exp_cat['main_total']
                    )
                    if 'main_strikeout' in exp_cat:
                        assert (
                            pcc_cat['final_prices']['main']['strikeout']
                            == exp_cat['main_strikeout']
                        )
                    else:
                        assert (
                            'strikeout' not in pcc_cat['final_prices']['main']
                        )
                    assert (
                        pcc_cat['final_prices']['main']['meta']
                        == exp_cat['main_meta']
                    )

    other_categories = set(request_categories) - set(expected_previous.keys())
    for category in other_categories:
        user_data = data['categories'][category]['user']['data']
        assert 'previously_calculated_categories' not in user_data
        assert 'previous_different_category' not in user_data


@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    PRICING_DATA_PREPARER_ROUTER_ENABLED={'__default__': True},
    PRICING_DATA_PREPARER_SURGER_ENABLED={
        '__default__': {'__default__': True},
    },
    PRICING_DATA_PREPARER_COUPONS_ENABLED=True,
    PRICING_DATA_PREPARER_DISCOUNTS_ENABLED=True,
    PRICING_PASSENGER_TAGS_ENABLED=True,
    PRICING_DATA_PREPARER_RESPONSE_SUMMARY_ENABLED={'__default__': False},
)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.pgsql(
    'pricing_data_preparer',
    files=[
        # Code of price modification is important for this test, see sql file
        'rules_modification_uses_previous_calc_of_same_category.sql',
        'workabilities.sql',
    ],
)
@pytest.mark.parametrize(
    'calculation_order, expected_user_meta_on_business',
    [
        ([], {'no_pcc': 1}),
        (['econom'], {'no_pcc': 1}),
        (['business'], {'no_pcc': 1}),
        (['econom', 'business'], {'business_not_in_pcc': 1}),
        (['business', 'business'], {'business_in_pcc': 1}),
        (['econom', 'business', 'business'], {'business_in_pcc': 1}),
    ],
)
async def test_v2_prepare_modification_uses_previous_calc_of_same_category(
        taxi_pricing_data_preparer,
        mock_yamaps_router,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        mock_surger,
        mock_ride_discounts,
        mock_tags,
        mock_coupons,
        mock_decoupling_corp_tariffs,
        taxi_config,
        calculation_order,
        expected_user_meta_on_business,
        experiments3,
):
    experiments3.add_config(
        consumers=['pricing-data-preparer/prepare'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Setup by zone',
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'value': 'moscow',
                        'arg_name': 'zone',
                        'arg_type': 'string',
                    },
                },
                'value': {'categories_order': calculation_order},
            },
        ],
        name='pricing_data_preparer_categories_calculation_order',
        default_value={'categories_order': []},
    )

    pre_request = (
        utils_request.Request()
        .set_categories(['econom', 'business'])
        .set_additional_prices(
            antisurge=True,
            strikeout=True,
            combo_order=False,
            combo_inner=False,
            combo_outer=False,
        )
    )

    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=pre_request.get(),
    )
    assert response.status_code == 200
    data = response.json()

    user_meta_on_business = data['categories']['business']['user']['meta']
    assert user_meta_on_business == expected_user_meta_on_business


TARIFF_INFO_CASES = test_utils.BooleanFlagCases(
    ['max_free_waiting_time_from_tariff', 'max_free_waiting_time_from_config'],
)


@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    PRICING_DATA_PREPARER_ROUTER_ENABLED={'__default__': True},
    PRICING_DATA_PREPARER_SURGER_ENABLED={
        '__default__': {'__default__': True},
    },
    PRICING_DATA_PREPARER_COUPONS_ENABLED=True,
    PRICING_DATA_PREPARER_DISCOUNTS_ENABLED=True,
    PRICING_PASSENGER_TAGS_ENABLED=True,
    FIXED_PRICE_MAX_ALLOWED_DISTANCE_ENABLED=True,
    UNLOADING_CONFIG_BY_ZONE_AND_CATEGORY={
        'moscow': {
            'econom': {
                'free_time': 234.0,
                'max_distance_to_destination': 500.0,
            },
        },
    },
)
@pytest.mark.filldb(tariff_settings='other')
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize(
    argnames=TARIFF_INFO_CASES.get_names(),
    argvalues=TARIFF_INFO_CASES.get_args(),
    ids=TARIFF_INFO_CASES.get_ids(),
)
async def test_v2_prepare_tariff_info(
        taxi_pricing_data_preparer,
        yamaps_router,
        mock_yamaps_router,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        mock_surger,
        mock_ride_discounts,
        mock_tags,
        mock_coupons,
        mock_decoupling_corp_tariffs,
        max_free_waiting_time_from_tariff,
        max_free_waiting_time_from_config,
        new_pricing_flow_dry_run,
):
    pre_request = utils_request.Request()

    pre_request.set_moscow_route()

    if max_free_waiting_time_from_tariff:
        pre_request.set_categories(['econom'])
    else:
        pre_request.set_categories(['ubernight'])

    request = pre_request.get()

    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 200
    data = response.json()

    if max_free_waiting_time_from_tariff:
        assert data['categories']['econom']['tariff_info'] == {
            'distance': {
                'included_kilometers': 3,
                'price_per_kilometer': 10.0,
            },
            'time': {'included_minutes': 5, 'price_per_minute': 9.0},
            'max_free_waiting_time': 120,
            'point_a_free_waiting_time': 180,
            'point_b_free_waiting_time': 234,
        }
    else:
        assert data['categories']['ubernight']['tariff_info'] == {
            'distance': {'included_kilometers': 3, 'price_per_kilometer': 7.0},
            'time': {'included_minutes': 8, 'price_per_minute': 7.0},
            'max_free_waiting_time': 600,
            'point_a_free_waiting_time': 180,
        }


PREORDER_CASES = test_utils.BooleanFlagCases(
    ['experiment_match', 'experiment_default', 'experiment_invalid'],
)


@pytest.mark.experiments3(filename='exp3_config_preorder.json')
@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize(
    argnames=PREORDER_CASES.get_names(),
    argvalues=PREORDER_CASES.get_args(),
    ids=PREORDER_CASES.get_ids(),
)
async def test_v2_prepare_preorder(
        taxi_pricing_data_preparer,
        yamaps_router,
        mock_yamaps_router,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        user_api,
        mock_surger,
        surger,
        experiment_match,
        experiment_default,
        experiment_invalid,
        new_pricing_flow_dry_run,
):
    pre_request = utils_request.Request()

    # +25 min from current time
    pre_request.set_due('2019-02-01T14:25:00Z')

    if experiment_match:
        surger.set_due('2019-02-01T14:25:00+00:00')
        # seconds from epoch of the above date
        dtm = 1549031100
        yamaps_router.set_dtm(dtm)

    if experiment_default:
        new_id = 'unknown_user_id'
    elif experiment_invalid:
        new_id = 'wrong_user_id'
    else:
        # by default in mock_user_api
        new_id = 'some_user_id'
    pre_request.set_user_id(new_id)
    user_api.set_user_id(new_id)
    surger.set_user_id(new_id)
    surger.set_user_app(pre_request.request['user_info']['application'])

    request = pre_request.get()
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'multiple_routes_params',
    [
        {'enabled': False},
        {'enabled': True},
        {'enabled': True, 'results_count': 5},
        {'enabled': True, 'intent': 'helloworld'},
        {'enabled': True, 'pass_user_id': True},
        {'enabled': True, 'vehicle': {'type': 'car'}},
        {'enabled': True, 'use_manoeuvres': True},
        {
            'enabled': True,
            'results_count': 5,
            'intent': 'helloworld',
            'pass_user_id': True,
            'vehicle': {'type': 'car'},
        },
    ],
    ids=[
        'disabled',
        'enabled',
        'results_count',
        'intent',
        'pass_user_id',
        'vehicle',
        'use_manoeuvres',
        'all',
    ],
)
async def test_v2_prepare_alternative_routes_params(
        taxi_pricing_data_preparer,
        load_json,
        yamaps_router,
        experiments3,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        mock_surger,
        mock_yamaps_router,
        multiple_routes_params,
):
    experiments3.add_experiments_json(
        load_json(
            'exp3_use_multiple_routes.json',
            object_hook=json_util.VarHook(multiple_routes_params),
        ),
    )

    if 'results_count' in multiple_routes_params:
        yamaps_router.set_easy_msk_nojams(
            multiple_routes_params['results_count'],
        )
    else:
        yamaps_router.set_easy_msk_nojams()
    if 'intent' in multiple_routes_params:
        yamaps_router.set_intent(multiple_routes_params['intent'])
    else:
        yamaps_router.set_intent('ROUTESTATS')
    if (
            'pass_user_id' in multiple_routes_params
            and not multiple_routes_params['pass_user_id']
    ):
        yamaps_router.set_user_id(None)
    if 'vehicle' in multiple_routes_params:
        yamaps_router.set_vehicle_type(
            multiple_routes_params['vehicle']['type'],
        )
    if 'use_manoeuvres' in multiple_routes_params:
        yamaps_router.set_use_manoeuvres('1')

    pre_request = utils_request.Request()
    request = pre_request.get()
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 200

    check_called_once(mock_yamaps_router)


@pytest.mark.parametrize(
    'is_decoupling', [False, True], ids=['no_decoupling', 'decoupling'],
)
@pytest.mark.parametrize(
    'routes_blocks, time_diff, available_alternatives, '
    'tolls, expected_distance, expected_time, waypoints',
    [
        ([True], None, 5, False, 2046.0, 307, None),
        ([True, False, True, False, True], None, 2, False, 2066.46, 310, None),
        ([False], None, 5, False, 2046.0, 307, None),
        (
            [False],
            {'absolute': 30, 'relative': 0.1},
            5,
            False,
            2046.0,
            307,
            None,
        ),
        (
            [False],
            {'absolute': 7, 'relative': 0.02},
            3,
            False,
            2046.0,
            307,
            None,
        ),
        (
            [False],
            {'absolute': 1, 'relative': 0.005},
            1,
            False,
            2046.0,
            307,
            None,
        ),
        (
            [True, False, True, False, True],
            {'absolute': 7, 'relative': 0.02},
            2,
            False,
            2066.46,
            310,
            None,
        ),
        ([True, False, True, False, True], None, 2, True, 2066.46, 310, None),
        ([False], None, 5, True, 2046.0, 307, None),
        (
            [False],
            {'absolute': 900, 'relative': 0.1},
            2,
            False,
            6474.137065649033,
            923,
            [[38.726549, 55.343154], [38.658536, 55.325139]],
        ),
    ],
    ids=[
        'all_blocked',
        'some_blocked',
        'no_blocked',
        'all_allowed_by_time',
        'some_allowed_by_time',
        'only_fastest_allowed_by_time',
        'some_blocked_and_some_allowed_by_time',
        'some_blocked_tolls_allowed',
        'no_blocked_tolls_allowed',
        'one_of_the_conditions_is_bad',
    ],
)
@pytest.mark.usefixtures(
    'mock_yamaps_router',
    'mock_user_api_get_users',
    'mock_user_api_get_phones',
    'mock_surger',
    'mock_decoupling_corp_tariffs',
)
async def test_v2_prepare_alternative_routes_usings(
        taxi_pricing_data_preparer,
        load_json,
        experiments3,
        testpoint,
        yamaps_router,
        routes_blocks,
        time_diff,
        available_alternatives,
        tolls,
        expected_distance,
        expected_time,
        waypoints,
        is_decoupling,
):
    @testpoint('use_multiple_routes')
    def tp_use_multiple_routes(data):
        assert data['count'] == available_alternatives
        assert data['kind'] == 'fastest' if tolls else 'cheapest'

    variables = {'enabled': True, 'results_count': 5, 'pass_user_id': True}
    if time_diff:
        variables['max_allowed_time_diff'] = time_diff
    experiments3.add_experiments_json(
        load_json(
            'exp3_use_multiple_routes.json',
            object_hook=json_util.VarHook(variables),
        ),
    )

    yamaps_router.set_intent('ROUTESTATS')
    yamaps_router.set_tolls(tolls)
    if waypoints:
        yamaps_router.set_voskresensks_custom_routes()
    else:
        yamaps_router.set_blocked(variables['results_count'], routes_blocks)

    pre_request = utils_request.Request()

    if waypoints:
        pre_request.set_waypoints(waypoints)

    if is_decoupling:
        experiments3.add_experiments_json(
            load_json('exp3_plugin_decoupling.json'),
        )
        pre_request.add_decoupling_method()
    pre_request.set_tolls('ALLOW' if tolls else 'DENY')
    request = pre_request.get()
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 200

    assert tp_use_multiple_routes.times_called == 2 if is_decoupling else 1

    data = response.json()
    assert 'categories' in data and 'econom' in data['categories']
    category = data['categories']['econom']
    assert 'user' in category and 'trip_information' in category['user']
    trip_information = category['user']['trip_information']
    assert round_values(trip_information['distance']) == round_values(
        expected_distance,
    )
    assert round_values(trip_information['time']) == round_values(
        expected_time,
    )


@pytest.mark.parametrize(
    'alternatives_enabled',
    [True, False],
    ids=['alternatives_enabled', 'alternatives_disabled'],
)
@pytest.mark.parametrize(
    'yamaps_success',
    [True, False],
    ids=['answer_by_yamaps', 'answer_by_tigraph'],
)
@pytest.mark.usefixtures(
    'mock_user_api_get_users', 'mock_user_api_get_phones', 'mock_surger',
)
@pytest.mark.config(
    ROUTER_SELECT=[{'routers': ['yamaps', 'tigraph']}],
    ROUTER_TIGRAPH_USERVICES_ENABLED=True,
)
async def test_v2_prepare_alternative_routes_fallbacks(
        taxi_pricing_data_preparer,
        experiments3,
        load_json,
        testpoint,
        yamaps_router,
        tigraph_router,
        mock_yamaps_router,
        mock_tigraph_router,
        alternatives_enabled,
        yamaps_success,
):
    available_alternatives = 5

    @testpoint('use_multiple_routes')
    def tp_use_multiple_routes(data):
        assert data['count'] == available_alternatives
        assert data['kind'] == 'cheapest'

    variables = {
        'enabled': alternatives_enabled,
        'results_count': available_alternatives,
        'vehicle': {'type': 'taxi'},
    }
    experiments3.add_experiments_json(
        load_json(
            'exp3_use_multiple_routes.json',
            object_hook=json_util.VarHook(variables),
        ),
    )

    yamaps_router.set_intent('ROUTESTATS')
    yamaps_router.set_vehicle_type('taxi')

    yamaps_router.set_easy_msk_nojams(
        results_count=available_alternatives if alternatives_enabled else 1,
    )

    if not yamaps_success:
        yamaps_router.must_crack(always=True)

    pre_request = utils_request.Request()
    request = pre_request.get()
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 200

    data = response.json()
    assert 'categories' in data and 'econom' in data['categories']
    category = data['categories']['econom']
    assert 'user' in category

    if not yamaps_success:
        assert mock_tigraph_router.has_calls
        assert not tp_use_multiple_routes.has_calls
        assert 'trip_information' not in category['user']
        assert category.get('fixed_price_discard_reason') == 'NO_ROUTE'
    else:
        assert mock_yamaps_router.has_calls
        assert tp_use_multiple_routes.has_calls == alternatives_enabled
        assert 'trip_information' in category['user']
        trip_information = category['user']['trip_information']
        assert round_values(trip_information['distance']) == round_values(
            2046.0,
        )
        assert round_values(trip_information['time']) == round_values(307)


@pytest.mark.parametrize(
    'experiment_enabled',
    [True, False],
    ids=['config_enabled', 'config_disabled'],
)
@pytest.mark.parametrize('run_draft_on_prestable', [True, False])
@pytest.mark.usefixtures(
    'mock_user_api_get_users',
    'mock_user_api_get_phones',
    'mock_surger',
    'mock_yamaps_router',
)
@pytest.mark.pgsql(
    'pricing_data_preparer', files=['rules.sql', 'workabilities.sql'],
)
@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_update_rule_draft_timestamp(
        taxi_pricing_data_preparer,
        experiment_enabled,
        run_draft_on_prestable,
        pgsql,
        testpoint,
        experiments3,
):
    draft_id = 2
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        cursor.execute(
            'UPDATE price_modifications.rules_drafts '
            f'SET evaluate_on_prestable={"true" if run_draft_on_prestable else "false"}, '
            'prestable_evaluation_begin_time=null'
            f' WHERE rule_id = {draft_id}',
        )

    experiments3.add_config(
        consumers=['pricing-data-preparer/caches'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        name='enable_drafts_prestable_evaluation',
        default_value={'enabled': experiment_enabled},
    )

    @testpoint('calculate_fix_prestable_drafts')
    def calc_fix_pre_drafts_tp(data):
        if experiment_enabled and run_draft_on_prestable:
            assert data == ['test draft']
        else:
            assert data == []

    pre_request = utils_request.Request()
    request = pre_request.get()
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 200
    assert calc_fix_pre_drafts_tp.times_called == 1

    with pgsql['pricing_data_preparer'].cursor() as cursor:
        cursor.execute(
            'SELECT prestable_evaluation_begin_time '
            'FROM price_modifications.rules_drafts '
            f'WHERE rule_id = {draft_id}',
        )
        begin_time = cursor.fetchone()[0]
        if experiment_enabled and run_draft_on_prestable:
            assert begin_time.isoformat() == '2019-02-01T17:00:00+03:00'
        else:
            assert not begin_time


@pytest.mark.parametrize(
    'forced_use_pricing_fallback_enabled',
    [False, True],
    ids=[
        'forced_use_pricing_fallback_disabled',
        'forced_use_pricing_fallback_enabled',
    ],
)
@pytest.mark.usefixtures(
    'mock_user_api_get_users',
    'mock_user_api_get_phones',
    'mock_surger',
    'mock_yamaps_router',
)
@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_forced_use_pricing_fallback(
        taxi_pricing_data_preparer,
        experiments3,
        load_json,
        forced_use_pricing_fallback_enabled,
):
    if forced_use_pricing_fallback_enabled:
        experiments3.add_experiments_json(
            load_json('exp3_forced_use_pricing_fallback.json'),
        )

    pre_request = utils_request.Request()
    request = pre_request.get()
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == (
        500 if forced_use_pricing_fallback_enabled else 200
    )


UMLAAS_PRICING_CASES = test_utils.BooleanFlagCases(
    [
        'disabled_request',
        'enabled_simple_two_points',
        'enabled_simple_one_point',
        'umlaas_pricing_error',
    ],
)


@pytest.mark.usefixtures(
    'mock_user_api_get_users',
    'mock_user_api_get_phones',
    'mock_yamaps_router',
    'mock_surger',
)
async def test_forced_fixprice_and_expected_prices(
        taxi_pricing_data_preparer, new_pricing_flow_dry_run,
):
    expected_prices = {'la': 1, 'lala': 2, 'lalala': 3}
    pre_request = utils_request.Request()
    pre_request = pre_request.set_forced_fixprice(1337)
    pre_request = pre_request.set_expected_prices(expected_prices)
    request = pre_request.get()
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )

    assert response.status_code == 200
    data = response.json()
    assert (
        data['categories']['econom']['user']['data']['forced_fixprice'] == 1337
    )
    assert (
        data['categories']['econom']['user']['data']['expected_prices']
        == expected_prices
    )


@pytest.mark.parametrize('is_street_hail_booking', [True, False])
@pytest.mark.usefixtures(
    'mock_user_api_get_users',
    'mock_user_api_get_phones',
    'mock_yamaps_router',
    'mock_surger',
)
async def test_shuttle_params_extra(
        taxi_pricing_data_preparer,
        is_street_hail_booking,
        new_pricing_flow_dry_run,
):
    pre_request = utils_request.Request()
    pre_request = pre_request.set_shuttle_params(is_street_hail_booking)
    request = pre_request.get()
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )

    assert response.status_code == 200
    data = response.json()
    assert data['categories']['econom']['user']['data']['shuttle_params'] == {
        'is_street_hail_booking': is_street_hail_booking,
    }


@pytest.mark.parametrize('order_id', [None, '1234'])
@pytest.mark.usefixtures(
    'mock_coupons',
    'mock_user_api_get_users',
    'mock_user_api_get_phones',
    'mock_yamaps_router',
    'mock_surger',
)
@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_coupons_order_id(
        taxi_pricing_data_preparer,
        coupons,
        order_id,
        new_pricing_flow_dry_run,
):
    pre_request = utils_request.Request()
    if order_id:
        pre_request.set_coupons_order_id(order_id)
        coupons.set_expected_order_id(order_id)
    request = pre_request.get()
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 200


@pytest.mark.experiments3(filename='exp3_test_price_modifications_kwargs.json')
@pytest.mark.parametrize(
    'due,timezone,point_a,expected_pricing_exp_val,required_category',
    [
        (
            '2019-02-01T11:25:00Z',
            'Europe/Moscow',
            [37.683, 55.774],
            None,
            'econom',
        ),
        (
            '2019-02-01T11:25:00Z',
            'Europe/Moscow',
            [42, 43],
            'point_a == (42,43)',
            'econom',
        ),
        (
            '2019-02-01T12:25:00Z',
            'Europe/Moscow',
            [37.683, 55.774],
            'due_hour == 15',
            'econom',
        ),
        (
            '2019-02-01T11:25:00Z',
            'Europe/Samara',
            [37.683, 55.774],
            'due_hour == 15',
            'econom',
        ),
        (None, 'Europe/Moscow', [37.683, 55.774], 'due_hour == 17', 'econom'),
        (
            '2019-02-04T11:25:00Z',
            'Europe/Moscow',
            [37.683, 55.774],
            'due_weekday == 1',
            'econom',
        ),
        (
            '2022-01-25T11:25:00Z',
            'Europe/Moscow',
            [37.683, 55.774],
            'business_category',
            'business',
        ),
    ],
)
@pytest.mark.usefixtures(
    'mock_coupons',
    'mock_user_api_get_users',
    'mock_user_api_get_phones',
    'mock_yamaps_router',
    'mock_surger',
)
@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_price_modifications_kwargs(
        taxi_pricing_data_preparer,
        due,
        timezone,
        point_a,
        expected_pricing_exp_val,
        required_category,
        mongodb,
):
    pre_request = utils_request.Request()
    if due:
        pre_request.set_due(due)
        pre_request.set_categories([required_category])
    pre_request.set_waypoints([point_a, [0, 0]])

    result = mongodb.tariff_settings.update_one(
        {'hz': 'moscow'}, {'$set': {'tz': timezone}},
    )
    assert result.matched_count == 1

    request = pre_request.get()
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 200
    data = response.json()
    exps = data['categories'][required_category]['user']['data']['exps']
    if expected_pricing_exp_val is not None:
        assert (
            exps['test_price_modifications_exp']['main']['str']
            == expected_pricing_exp_val
        )
    else:
        assert 'test_price_modifications_exp' not in exps


@pytest.mark.parametrize(
    'user_id, expected_antisurge_settings',
    [
        (
            '42',
            {
                'apply_discount': True,
                'apply_to_boarding': False,
                'max_abs_discount': 1,
                'min_abs_gain': 2,
                'min_rel_gain': 3,
            },
        ),
        ('some_other_userid', None),
    ],
)
@pytest.mark.experiments3(
    filename='exp3_config_pricing_antisurge_settings.json',
)
@pytest.mark.usefixtures(
    'mock_user_api_get_users',
    'mock_user_api_get_phones',
    'mock_surger',
    'mock_yamaps_router',
)
@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_pricing_antisurge_settings(
        taxi_pricing_data_preparer,
        user_id,
        expected_antisurge_settings,
        surger,
        user_api,
        yamaps_router,
        new_pricing_flow_dry_run,
):
    pre_request = utils_request.Request()
    pre_request.set_user_id(user_id)
    user_api.set_user_id(user_id)
    yamaps_router.set_user_id(user_id)
    surger.set_user_id(user_id)
    request = pre_request.get()
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 200
    for category in response.json()['categories'].values():
        backend_variables = category['user']['data']
        if expected_antisurge_settings is not None:
            assert (
                backend_variables['pricing_antisurge_settings']
                == expected_antisurge_settings
            )
        else:
            assert 'pricing_antisurge_settings' not in backend_variables


@pytest.mark.parametrize(
    argnames=UMLAAS_PRICING_CASES.get_names(),
    argvalues=UMLAAS_PRICING_CASES.get_args(),
    ids=UMLAAS_PRICING_CASES.get_ids(),
)
@pytest.mark.usefixtures(
    'mock_user_api_get_users',
    'mock_user_api_get_phones',
    'mock_yamaps_router',
    'mock_surger',
)
@pytest.mark.config(
    UMLAAS_PRICING_CLIENT_QOS={
        '__default__': {'attempts': 1, 'timeout-ms': 10000},
    },
)
@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_umlaas_pricing_offer_statistics(
        taxi_pricing_data_preparer,
        experiments3,
        load_json,
        disabled_request,
        enabled_simple_two_points,
        enabled_simple_one_point,
        umlaas_pricing_error,
        umlaas_pricing,
        mock_umlaas_pricing,
        new_pricing_flow_dry_run,
):
    if disabled_request:
        experiments3.add_experiments_json(
            load_json(
                'umlaas_pricing_offer_statistic_disabled_exp3_config.json',
            ),
        )
    else:
        experiments3.add_experiments_json(
            load_json(
                'umlaas_pricing_offer_statistic_enabled_exp3_config.json',
            ),
        )

    pre_request = utils_request.Request()
    if enabled_simple_two_points:
        pre_request.set_moscow_route()
    elif enabled_simple_one_point:
        pre_request.set_one_point_route()

    if umlaas_pricing_error:
        umlaas_pricing.must_crack()

    request = pre_request.get()
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )

    must_have_umlaas_pricing_stat = enabled_simple_two_points
    must_request_umlaas_pricing = (
        enabled_simple_two_points or umlaas_pricing_error
    )

    if must_request_umlaas_pricing:
        assert mock_umlaas_pricing.times_called == 1
    else:
        assert mock_umlaas_pricing.times_called == 0

    assert response.status_code == 200
    for category in response.json()['categories'].values():
        backend_variables = category['user']['data']
        if must_have_umlaas_pricing_stat:
            assert (
                backend_variables['offer_statistics']
                == umlaas_pricing.get_offer_statistics()
            )
        else:
            assert 'offer_statistics' not in backend_variables


@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    PRICING_DATA_PREPARER_ROUTER_ENABLED={'__default__': True},
    PRICING_DATA_PREPARER_SURGER_ENABLED={
        '__default__': {'__default__': True},
    },
    PRICING_DATA_PREPARER_COUPONS_ENABLED=True,
    PRICING_DATA_PREPARER_DISCOUNTS_ENABLED=True,
    PRICING_PASSENGER_TAGS_ENABLED=True,
)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_v2_prepare_propagate_corp_tariffs_429(
        taxi_pricing_data_preparer,
        mockserver,
        mock_yamaps_router,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        mock_surger,
        mock_ride_discounts,
        mock_tags,
        mock_coupons,
):
    @mockserver.handler('/corp-tariffs/v1/client_tariff/current')
    async def _mock_client_tariff(request):
        return mockserver.make_response(
            '429', status=429, content_type='text/plain',
        )

    request = utils_request.Request().add_decoupling_method().get()

    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 429
