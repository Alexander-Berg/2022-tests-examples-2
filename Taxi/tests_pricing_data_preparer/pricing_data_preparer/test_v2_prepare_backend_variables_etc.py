# pylint: disable=redefined-outer-name, import-only-modules, import-error
# flake8: noqa F401
import pytest

from pricing_extended.mock_router import yamaps_router, mock_yamaps_router
from pricing_extended.mocking_base import check_called_once
from pricing_extended.mocking_base import check_not_called
from pricing_extended.mocking_base import check_called

from .plugins import test_utils
from .plugins import utils_request


from .plugins.mock_cashback_rates import cashback_rates_fixture
from .plugins.mock_cashback_rates import mock_cashback_rates
from .plugins.mock_user_api import user_api
from .plugins.mock_user_api import mock_user_api_get_phones
from .plugins.mock_user_api import mock_user_api_get_users
from .plugins.mock_surge import surger
from .plugins.mock_surge import mock_surger
from .plugins.mock_ride_discounts import ride_discounts
from .plugins.mock_ride_discounts import mock_ride_discounts
from .plugins.mock_tags import tags
from .plugins.mock_tags import mock_tags
from .plugins.mock_combo_contractors import combo_contractors
from .plugins.mock_combo_contractors import mock_combo_contractors
from .plugins.mock_alt_offer_discount import alt_offer_discount
from .plugins.mock_alt_offer_discount import mock_alt_offer_discount
from .plugins.mock_coupons import coupons
from .plugins.mock_coupons import mock_coupons
from .plugins.mock_decoupling import decoupling
from .plugins.mock_decoupling import mock_decoupling_corp_tariffs
from .plugins.mock_decoupling import decoupling_tariff
from .plugins.utils_response import econom_tariff
from .plugins.utils_response import business_tariff
from .plugins.utils_response import econom_category_callcenter
from .plugins.utils_response import callcenter_tariff
from .plugins.utils_response import econom_category
from .plugins.utils_response import business_category

BACKEND_VARIABLES_CASES = test_utils.BooleanFlagCases(
    [
        'decoupling_success',
        'decoupling_failed',
        'fill_surge',
        'fill_coupons',
        'ya_plus',
        'cashback_plus',
        'add_business',
        'tags_list',
        'combo_discount',
        'perfect_chain_discount',
        'alt_offer_discount_empty',
        'requirements',
        'cashback_discount',
        'personal_wallet',
        'callcenter',
        'preorder_multiplier',
        'plus_promo',
    ],
)

PLUS_PROMO_PARAMS = {
    'enabled': True,
    'show_rules': {
        'econom': {
            'tariff_from': 'business',
            'change_diff_percent': 20,
            'max_tariffs_ratio_percent': 150,
        },
    },
}

COMBO_PARAMS = {'enabled': True, 'available_categories': ['econom']}


def set_new_data_work_mode(
        experiments3, mode='dry_run', skip_source_load=True,
):
    experiments3.add_experiment(
        clauses=[
            {
                'predicate': {'type': 'true'},
                'enabled': True,
                'title': '',
                'value': {
                    'work_mode': mode,
                    'skip_source_load': skip_source_load,
                },
            },
        ],
        name='new_pricing_data_generator_settings',
        consumers=['pricing-data-preparer/prepare'],
        match={'enabled': True, 'predicate': {'type': 'true'}},
    )


@pytest.fixture(name='new_pricing_flow_dry_run', autouse=False)
def new_pricing_flow_dry_run(testpoint, experiments3):
    @testpoint('new_pricing_flow_dry_run')
    def _new_pricing_flow_dry_run(data):
        data['new'].pop('backend_variables_uuids', None)
        data['old'].pop('backend_variables_uuids', None)
        assert data['new'] == data['old']

    return _new_pricing_flow_dry_run


def add_enabled_experiment(experiments3, name, value, is_config=False):
    (experiments3.add_config if is_config else experiments3.add_experiment)(
        name=name,
        consumers=['pricing-data-preparer/prepare'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': value,
            },
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
    APPLICATION_MAP_PLATFORM={
        '__default__': 'web',
        'call_center': 'callcenter',
    },
)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.experiments3(filename='exp3_combo_order_config.json')
@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize(
    argnames=BACKEND_VARIABLES_CASES.get_names(),
    argvalues=BACKEND_VARIABLES_CASES.get_args(),
    ids=BACKEND_VARIABLES_CASES.get_ids(),
)
@pytest.mark.parametrize(
    'discounts_enabled',
    [None, True, False],
    ids=[
        'discounts_enabled_because_none',
        'discounts_enabled',
        'discounts_disabled',
    ],
)
@pytest.mark.parametrize(
    'surge_enabled',
    [None, True, False],
    ids=['surge_enabled_because_none', 'surge_enabled', 'surge_disabled'],
)
@pytest.mark.parametrize('new_pricing_data_skip_source', [True, False])
async def test_v2_prepare_backend_variables_etc(
        taxi_pricing_data_preparer,
        yamaps_router,
        mock_yamaps_router,
        user_api,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        surger,
        mock_surger,
        ride_discounts,
        mock_ride_discounts,
        tags,
        mock_tags,
        combo_contractors,
        mock_combo_contractors,
        coupons,
        mock_coupons,
        decoupling,
        mock_decoupling_corp_tariffs,
        mock_cashback_rates,
        business_tariff,
        econom_tariff,
        decoupling_success,
        decoupling_failed,
        fill_surge,
        fill_coupons,
        ya_plus,
        cashback_plus,
        add_business,
        tags_list,
        combo_discount,
        perfect_chain_discount,
        alt_offer_discount_empty,
        alt_offer_discount,
        mock_alt_offer_discount,
        requirements,
        cashback_discount,
        personal_wallet,
        callcenter,
        callcenter_tariff,
        preorder_multiplier,
        plus_promo,
        discounts_enabled,
        surge_enabled,
        experiments3,
        new_pricing_flow_dry_run,
        new_pricing_data_skip_source,
):
    set_new_data_work_mode(
        experiments3, skip_source_load=new_pricing_data_skip_source,
    )
    is_decoupling = decoupling_success or decoupling_failed
    request_additional_prices = {}

    pre_request = utils_request.Request()
    if preorder_multiplier:
        pre_request.set_due('2019-02-01T14:25:00Z')

        # seconds from epoch of the above date
        dtm = 1549031100
        yamaps_router.set_dtm(dtm)
        surger.set_due('2019-02-01T14:25:00+00:00')

        add_enabled_experiment(
            experiments3, 'preorder_multiplier', {'value': 123.45},
        )
        add_enabled_experiment(
            experiments3, 'preorder_predict_surge', {'available': True},
        )
        add_enabled_experiment(
            experiments3, 'preorder_predict_route', {'available': True},
        )

    combo_contractors.add_tariff('econom')
    if combo_discount:
        request_additional_prices['combo_inner'] = True
        request_additional_prices['combo_outer'] = True

    if plus_promo:
        request_additional_prices['plus_promo'] = True
        add_enabled_experiment(
            experiments3, 'upgraded_tariff_by_plus_promo', PLUS_PROMO_PARAMS,
        )
    if fill_coupons:
        pre_request.add_coupon()
    if is_decoupling:
        pre_request.add_decoupling_method()
        decoupling.disable_surge()
    if add_business:
        pre_request.set_categories(['econom', 'business'])
    if requirements:
        pre_request.set_requirements(
            {'econom': {'childchair': [3, 7], 'conditioner': True}},
        )
    if cashback_discount:
        pre_request.enable_cashback()
    if personal_wallet:
        pre_request.set_personal_wallet('PERSONAL_WALLET_ID', balance=123.45)

    pre_request.set_discounts_enabled(discounts_enabled)
    pre_request.set_surge_enabled(surge_enabled)

    if fill_surge:
        surger.set_surge(5, surcharge=10, alpha=15, beta=20)
    if fill_coupons:
        coupons.set_value(35)
        coupons.set_locale('ru')
    if ya_plus:
        user_api.set_yaplus(True)
    if cashback_plus:
        user_api.set_cashback_plus(True)
    if decoupling_failed:
        decoupling.tariffs_crack(
            expected_requests=1 if new_pricing_data_skip_source else 2,
        )
    if tags_list:
        tags.set_tags(['one_tag', 'two_tag', 'four_tag'])
    if perfect_chain_discount:
        request_additional_prices['alt_offer_discount'] = True
        add_enabled_experiment(
            experiments3,
            'alt_offer_discount_pricing_enabled',
            COMBO_PARAMS,
            is_config=True,
        )
        alt_offer_discount.set_param('kekw', 1337.0)
    if alt_offer_discount_empty:
        request_additional_prices['alt_offer_discount'] = True
        add_enabled_experiment(
            experiments3,
            'alt_offer_discount_pricing_enabled',
            COMBO_PARAMS,
            is_config=True,
        )
        alt_offer_discount.clear_offers()

    ride_discounts.add_table_discount(
        'econom', [(0, 10), (2, 20)], is_cashback=cashback_discount,
    )

    if callcenter:
        pre_request.set_application(name='call_center')

    pre_request.set_additional_prices(**request_additional_prices)
    request = pre_request.get()

    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request, headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200

    data = response.json()

    assert 'categories' in data
    assert 'econom' in data['categories']
    if add_business:
        assert len(data['categories']) == 2
        assert 'business' in data['categories']
    else:
        assert len(data['categories']) == 1
    econom = data['categories']['econom']
    assert 'user' in econom and 'driver' in econom

    additional_prices = {}

    if plus_promo:
        additional_prices['plus_promo'] = {
            'meta': {},
            'modifications': {'for_fixed': [], 'for_taximeter': []},
            'price': {'total': 131.0},
        }

    if combo_discount:
        additional_prices['combo_inner'] = {
            'meta': {},
            'modifications': {'for_fixed': [], 'for_taximeter': []},
            'price': {'total': 131.0},
        }
        additional_prices['combo_outer'] = {
            'meta': {},
            'modifications': {'for_fixed': [], 'for_taximeter': []},
            'price': {'total': 131.0},
        }
        check_called(mock_combo_contractors)
    else:
        check_not_called(mock_combo_contractors)

    if perfect_chain_discount:
        additional_prices['alt_offer_discount'] = [
            {
                'alternative_type': 'perfect_chain',
                'price_data': {
                    'meta': {},
                    'modifications': {'for_fixed': [], 'for_taximeter': []},
                    'price': {'total': 131.0},
                },
            },
        ]

    assert econom['user']['additional_prices'] == additional_prices
    assert econom['driver']['additional_prices'] == additional_prices

    assert 'data' in econom['user']
    backend_variables = econom['user']['data']

    expected_surge_params = {
        'value': 1.0,
        'value_raw': 1.0,
        'value_smooth': 1.0,
    }
    if surge_enabled is None or surge_enabled:
        assert mock_surger.times_called == 1 + (
            0 if new_pricing_data_skip_source else 1
        )
        if not is_decoupling or not decoupling_success:
            expected_surge_params.update(
                {
                    'value_b': 1,
                    'pins': 0,
                    'free_drivers': 6,
                    'free_drivers_chain': 0,
                    'total_drivers': 6,
                    'radius': 3000,
                },
            )
        if fill_surge:
            expected_surge_params.update(
                {
                    'value': 5,
                    'value_raw': 5,
                    'value_smooth': 5,
                    'surcharge': 10,
                    'surcharge_alpha': 15,
                    'surcharge_beta': 20,
                },
            )
        assert backend_variables['surge_params'] == expected_surge_params
    else:
        check_not_called(mock_surger)
        assert backend_variables['surge_params'] == expected_surge_params

    if fill_coupons:
        assert 'coupon' in backend_variables
        assert backend_variables['coupon']['value'] == 35

    assert 'cashback_rates' in backend_variables
    if personal_wallet:
        assert len(backend_variables['cashback_rates']) == 3
        assert backend_variables['cashback_rates'] == [
            {'rate': 0.4, 'max_value': 100, 'sponsor': 'fintech'},
            {'rate': 0.05, 'sponsor': 'portal'},
            {
                'sponsor': 'PERSONAL_WALLET_ID',
                'rate': 0.1,
                'max_value': 123.45,
            },
        ]
    else:
        assert len(backend_variables['cashback_rates']) == 2
        assert backend_variables['cashback_rates'] == [
            {'rate': 0.4, 'max_value': 100, 'sponsor': 'fintech'},
            {'rate': 0.05, 'sponsor': 'portal'},
        ]

    assert 'user_data' in backend_variables
    assert 'has_yaplus' in backend_variables['user_data']
    assert backend_variables['user_data']['has_yaplus'] == ya_plus
    assert 'has_cashback_plus' in backend_variables['user_data']
    assert backend_variables['user_data']['has_cashback_plus'] == cashback_plus

    assert econom['corp_decoupling'] == is_decoupling
    if is_decoupling:
        assert (
            backend_variables['category_data']['corp_decoupling']
            == is_decoupling
        )
    if is_decoupling and not decoupling_failed:
        assert 'data' in econom['driver']
        assert (
            econom['driver']['data']['category_data']['corp_decoupling']
            == is_decoupling
        )

    if decoupling_success:
        assert backend_variables['category_data']['decoupling']
    else:
        assert not backend_variables['category_data']['decoupling']

    assert backend_variables['category_data']['fixed_price']
    if decoupling_success:
        assert backend_variables['category_data']['disable_surge']
    else:
        assert not 'disable_surge' in backend_variables['category_data']
    if decoupling_success:
        assert not backend_variables['category_data']['disable_paid_supply']
    else:
        assert not 'disable_paid_supply' in backend_variables['category_data']

    # tariff
    if decoupling_success:
        assert 'data' in econom['driver']
        driver_backend_variables = econom['driver']['data']
        assert driver_backend_variables['tariff'] == econom_tariff
        assert backend_variables['tariff'] == decoupling_tariff()
        if add_business:
            business_backend_variables = data['categories']['business'][
                'user'
            ]['data']
            assert business_backend_variables['tariff'] == decoupling_tariff()
            assert 'data' in data['categories']['business']['driver']
            driver_backend_variables = data['categories']['business'][
                'driver'
            ]['data']
            assert driver_backend_variables['tariff'] == business_tariff
    elif callcenter:
        assert backend_variables['tariff'] == callcenter_tariff
    else:
        assert backend_variables['tariff'] == econom_tariff
        if add_business:
            business_backend_variables = data['categories']['business'][
                'user'
            ]['data']
            assert business_backend_variables['tariff'] == business_tariff

    # category_prices_id
    if not callcenter:
        assert (
            econom['driver']['category_prices_id']
            == 'c/ed3b2fe5c51f4a4da7bee86349259dda'
        )

    if add_business:
        assert (
            data['categories']['business']['driver']['category_prices_id']
            == 'c/465adfd1acb34724b7825bf6a2e663d4'
        )
    if decoupling_success:
        assert (
            econom['user']['category_prices_id']
            == 'd/corp_tariff_id/decoupling_category_id'
        )
        if add_business:
            assert (
                data['categories']['business']['user']['category_prices_id']
                == 'd/corp_tariff_id/decoupling_category_id'
            )
    elif callcenter:
        assert (
            econom['driver']['category_prices_id']
            == 'c/290b95c29f04495998c686e87eb77851'
        )
        assert (
            econom['user']['category_prices_id']
            == 'c/290b95c29f04495998c686e87eb77851'
        )
    else:
        assert (
            econom['user']['category_prices_id']
            == 'c/ed3b2fe5c51f4a4da7bee86349259dda'
        )
        if add_business:
            assert (
                data['categories']['business']['user']['category_prices_id']
                == 'c/465adfd1acb34724b7825bf6a2e663d4'
            )

    assert 'user_tags' in backend_variables
    if tags_list:
        user_tags = backend_variables['user_tags']
        assert 'one_tag' in user_tags
        assert 'two_tag' in user_tags
        assert not 'three tag' in user_tags
        assert not '' in user_tags
        assert 'four_tag' in user_tags
    else:
        assert backend_variables['user_tags'] == []

    # test combo
    if combo_discount:
        assert 'combo_offers_data' in backend_variables
        assert 'combo_inner_settings' in backend_variables['combo_offers_data']
        assert (
            backend_variables['combo_offers_data']['combo_inner_settings'][
                'discount_function'
            ]
            == 'default_formula'
        )

        assert 'combo_outer_settings' in backend_variables['combo_offers_data']
        assert (
            backend_variables['combo_offers_data']['combo_outer_settings'][
                'discount_function'
            ]
            == 'default_formula'
        )
    else:
        assert (
            'combo_offers_data' not in backend_variables
            or 'combo_inner_settings'
            not in backend_variables['combo_offers_data']
            or 'combo_outer_settings'
            not in backend_variables['combo_offers_data']
        )

    if perfect_chain_discount:
        assert backend_variables['alt_offer_discount'] == {
            'type': 'perfect_chain',
            'params': {'kekw': 1337.0},
        }

        if add_business:
            assert (
                not 'alt_offer_discount'
                in data['categories']['business']['user']['data']
            )
    else:
        assert 'alt_offer_discount' not in backend_variables

    if alt_offer_discount_empty:
        assert 'alt_offer_discount' not in backend_variables

    if is_decoupling:
        assert backend_variables['payment_type'] == 'corp'
    else:
        assert backend_variables['payment_type'] == 'SOME_PAYMENT_TYPE'

    if requirements:
        assert backend_variables['requirements'] == {
            'select': {
                'childchair': [{'independent': False, 'name': 'only_booster'}],
            },
            'simple': ['conditioner'],
        }
    else:
        assert backend_variables['requirements'] == {
            'select': {},
            'simple': [],
        }

    if discounts_enabled is None or discounts_enabled:
        assert mock_ride_discounts.times_called == 1 + (
            0 if new_pricing_data_skip_source else 1
        )
        if cashback_discount:
            assert 'cashback_discount' in backend_variables
            discount = backend_variables['cashback_discount']
        else:
            assert 'discount' in backend_variables
            discount = backend_variables['discount']
        assert 'calc_data_table_data' in discount
        assert discount['calc_data_table_data'] == [
            {'coeff': 10.0, 'price': 0.0},
            {'coeff': 20.0, 'price': 2.0},
        ]
        assert discount.get('with_restriction_by_usages') is False
    else:
        assert 'discount' not in backend_variables
        assert 'cashback_discount' not in backend_variables
        check_not_called(mock_ride_discounts)

    experiment_list = [
        'pm_match_by_phone',
        'pm_match_by_country',
        'pm_match_by_user',
        'pm_match_by_app_and_ver',
        'pm_match_by_zone',
        'pm_match_by_yandex_uid',
        'pm_match_me_always',
    ]

    if not is_decoupling:
        experiment_list.append('pm_match_by_payment_option')
    else:
        experiment_list.append('pm_match_by_payment_method')

    assert sorted(backend_variables['exps'].keys()) == sorted(experiment_list)

    if personal_wallet:
        assert 'complements' in backend_variables
        assert 'personal_wallet' in backend_variables['complements']
        personal_wallet = backend_variables['complements']['personal_wallet']
        assert 'balance' in personal_wallet
        assert personal_wallet['balance'] == 123.45

    if callcenter:
        assert (
            backend_variables['category_data']['callcenter_extra_percents']
            == 3
        )
        assert (
            backend_variables['category_data']['callcenter_discount_percents']
            == 4
        )
        assert backend_variables['category_data']['callcenter_fix_charge'] == 5
    else:
        assert (
            'callcenter_extra_percents'
            not in backend_variables['category_data']
        )
        assert (
            'callcenter_discount_percents'
            not in backend_variables['category_data']
        )
        assert (
            'callcenter_fix_charge' not in backend_variables['category_data']
        )

    if preorder_multiplier:
        assert backend_variables['preorder_multiplier'] == 123.45
    else:
        assert 'preorder_multiplier' not in backend_variables

    if plus_promo:
        assert (
            backend_variables['plus_promo']
            == PLUS_PROMO_PARAMS['show_rules']['econom']
        )
    else:
        assert 'plus_promo' not in backend_variables

    assert new_pricing_flow_dry_run.times_called > 0
