# pylint: disable=redefined-outer-name, import-only-modules,import-error
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


@pytest.mark.experiments3(
    name='pricing_degradation_config',
    consumers=['pricing-data-preparer/pricing_filter'],
    default_value={'enabled': False, 'ignore_without_parent_link': True},
)
async def test_v2_prepare_filters_enabled(
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
):
    pre_request = utils_request.Request()
    request = pre_request.get()
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 200


@pytest.mark.experiments3(
    name='pricing_degradation_config',
    consumers=['pricing-data-preparer/pricing_filter'],
    is_config=True,
    default_value={
        'enabled': True,
        'ignore_without_parent_link': True,
        'no_user_blocking': {'enabled': False, 'allowed_tvm': []},
    },
)
@pytest.mark.parametrize('has_parent_link', (True, False))
async def test_v2_prepare_filters_parent_link(
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
        has_parent_link,
):
    pre_request = utils_request.Request()
    pre_request.remove_user_info()
    request = pre_request.get()
    surger.set_user_id(None)
    if has_parent_link:
        headers = {'X-YaRequestId': 'parent_link'}
    else:
        headers = {}
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request, headers=headers,
    )
    if has_parent_link:
        assert response.status_code == 200
    else:
        assert response.status_code == 400


@pytest.mark.experiments3(
    name='pricing_degradation_config',
    consumers=['pricing-data-preparer/pricing_filter'],
    is_config=True,
    default_value={
        'enabled': True,
        'ignore_without_parent_link': True,
        'no_user_blocking': {'enabled': True, 'allowed': ['bond_james_bond']},
    },
)
@pytest.mark.parametrize('tvm', (None, '100', '300'))
@pytest.mark.config(
    TVM_SERVICES={
        'pricing-data-preparer': 1,
        'bong_james_bond': 300,
        'somebody': 100,
    },
    TVM_RULES=[
        {'src': 'bong_james_bond', 'dst': 'pricing-data-preparer'},
        {'src': 'somebody', 'dst': 'pricing-data-preparer'},
    ],
)
async def test_v2_prepare_filters_no_user(
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
        tvm,
):
    pre_request = utils_request.Request()
    pre_request.remove_user_info()
    request = pre_request.get()
    surger.set_user_id(None)
    headers = {'X-YaRequestId': 'parent_link'}
    if tvm:
        headers['X-Ya-Service-Ticket'] = tvm
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request, headers=headers,
    )
    if tvm == 300:
        assert response.status_code == 200
    else:
        assert response.status_code == 400


@pytest.mark.experiments3(
    name='pricing_degradation_config',
    consumers=['pricing-data-preparer/pricing_filter'],
    is_config=True,
    default_value={
        'enabled': True,
        'ignore_without_parent_link': True,
        'no_user_blocking': {'enabled': False, 'allowed_tvm': [300]},
        'alt_prices_overrides': {'enabled': True, 'allowed': ['antisurge']},
    },
)
@pytest.mark.parametrize(
    'alt_prices, enabled',
    (
        [[], True],
        [['antisurge'], True],
        [['antisurge', 'plus_promo'], True],
        [['antisurge', 'plus_promo'], False],
    ),
)
async def test_v2_prepare_filters_alt_prices(
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
        alt_prices,
        enabled,
        experiments3,
):
    if not enabled:
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='pricing_degradation_config',
            consumers=['pricing-data-preparer/pricing_filter'],
            clauses=[],
            default_value={
                'enabled': True,
                'ignore_without_parent_link': True,
                'no_user_blocking': {'enabled': False, 'allowed_tvm': [300]},
                'alt_prices_overrides': {
                    'enabled': False,
                    'allowed': ['antisurge'],
                },
            },
        )

    pre_request = utils_request.Request()
    pre_request.set_additional_prices(
        antisurge=('antisurge' in alt_prices),
        plus_promo=('plus_promo' in alt_prices),
    )
    request = pre_request.get()
    surger.set_explicit_antisurge()
    experiments3.add_experiment(
        name='upgraded_tariff_by_plus_promo',
        consumers=['pricing-data-preparer/prepare'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {
                    'enabled': True,
                    'show_rules': {
                        'econom': {
                            'tariff_from': 'business',
                            'change_diff_percent': 20,
                            'max_tariffs_ratio_percent': 150,
                        },
                    },
                },
            },
        ],
    )
    await taxi_pricing_data_preparer.invalidate_caches()

    headers = {'X-YaRequestId': 'parent_link'}
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request, headers=headers,
    )
    assert response.status_code == 200

    data = response.json()
    if enabled:
        assert (
            'plus_promo'
            not in data['categories']['econom']['user']['additional_prices']
        )
        assert (
            'plus_promo'
            not in data['categories']['econom']['driver']['additional_prices']
        )
    elif 'plus_promo' in alt_prices:
        assert (
            'plus_promo'
            in data['categories']['econom']['user']['additional_prices']
        )
        assert (
            'plus_promo'
            in data['categories']['econom']['driver']['additional_prices']
        )

    if 'antisurge' in alt_prices:
        assert (
            'antisurge'
            in data['categories']['econom']['user']['additional_prices']
        )
        assert (
            'antisurge'
            in data['categories']['econom']['driver']['additional_prices']
        )
    else:
        assert (
            'antisurge'
            not in data['categories']['econom']['user']['additional_prices']
        )
        assert (
            'antisurge'
            not in data['categories']['econom']['driver']['additional_prices']
        )


def get_modification_name(rule_id, pgsql):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        cursor.execute(
            'SELECT name FROM price_modifications.rules WHERE rule_id={}'.format(
                rule_id,
            ),
        )
        result = cursor.fetchall()
        if not result:
            return None
        return result[0][0]


def lists_compare(num_list, filter_list, pgsql):
    assert len(num_list) == len(filter_list)
    for rule_id, filter_param in zip(num_list, filter_list):
        assert (rule_id == filter_param) or (
            get_modification_name(rule_id, pgsql) == filter_param
        )


@pytest.mark.pgsql(
    'pricing_data_preparer', files=['rules.sql', 'workabilities.sql'],
)
@pytest.mark.parametrize(
    'override, filtered, user, driver, blacklist',
    (
        [False, False, None, None, None],
        [True, False, None, None, None],
        [True, False, [], [], None],
        [True, False, [1, 2, 3], [5, 6, 7], None],
        [
            True,
            False,
            [1, 'yaplus', 'paid_supply'],
            ['surge', 6, 'waiting_in_A'],
            None,
        ],
        [False, True, [1, 2, 3], [5, 6, 7], None],
        [False, True, [1, 2, 3], [5, 6, 7], []],
        [False, True, [1, 2, 3], [5, 6, 7], [1, 2, 3, 4, 5, 6, 7, 8, 9]],
        [
            False,
            True,
            [1, 2, 3],
            [5, 6, 7],
            [
                'coupon',
                'yaplus',
                'paid_supply',
                'requirements',
                'surge',
                'user_discount',
                'waiting_in_A',
                'waiting_in_transit',
                'test_rule_1',
            ],
        ],
        [True, True, [1, 2, 3], [5, 6, 7], [1, 2, 3, 4, 5, 6, 7, 8, 9]],
    ),
)
async def test_v2_prepare_filters_modifications_filter(
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
        override,
        filtered,
        experiments3,
        user,
        driver,
        blacklist,
        pgsql,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='pricing_degradation_config',
        consumers=['pricing-data-preparer/pricing_filter'],
        clauses=[],
        default_value={
            'enabled': True,
            'ignore_without_parent_link': False,
            'no_user_blocking': {'enabled': False, 'allowed_tvm': [300]},
            'modifications_filter': {
                'enabled': filtered,
                'blacklist': blacklist,
            },
            'modifications_overrides': {
                'enabled': override,
                'user': user,
                'driver': driver,
            },
        },
    )
    await taxi_pricing_data_preparer.invalidate_caches()

    pre_request = utils_request.Request()
    request = pre_request.get()

    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 200
    data = response.json()

    if filtered and not override:
        if blacklist == [] or blacklist is None:
            assert data['categories']['econom']['user']['modifications'][
                'for_fixed'
            ] == [1, 2, 3, 5, 6, 7, 8, 9, 11, 13, 15, 16]
            assert data['categories']['econom']['driver']['modifications'][
                'for_fixed'
            ] == [1, 2, 3, 5, 6, 7, 8, 9, 11, 12, 15, 16]
            assert data['categories']['econom']['user']['modifications'][
                'for_taximeter'
            ] == [1, 2, 3, 5, 6, 7, 8, 9, 10, 13, 15, 16]
            assert data['categories']['econom']['driver']['modifications'][
                'for_taximeter'
            ] == [1, 2, 3, 5, 6, 7, 8, 9, 10, 12, 15, 16]
        else:
            assert data['categories']['econom']['user']['modifications'][
                'for_fixed'
            ] == [11, 13, 15, 16]
            assert data['categories']['econom']['driver']['modifications'][
                'for_fixed'
            ] == [11, 12, 15, 16]
            assert data['categories']['econom']['user']['modifications'][
                'for_taximeter'
            ] == [10, 13, 15, 16]
            assert data['categories']['econom']['driver']['modifications'][
                'for_taximeter'
            ] == [10, 12, 15, 16]
    elif override:
        lists_compare(
            data['categories']['econom']['user']['modifications']['for_fixed'],
            user if user else [],
            pgsql,
        )
        lists_compare(
            data['categories']['econom']['driver']['modifications'][
                'for_fixed'
            ],
            driver if driver else [],
            pgsql,
        )
        lists_compare(
            data['categories']['econom']['user']['modifications'][
                'for_taximeter'
            ],
            user if user else [],
            pgsql,
        )
        lists_compare(
            data['categories']['econom']['driver']['modifications'][
                'for_taximeter'
            ],
            driver if driver else [],
            pgsql,
        )
    else:
        assert data['categories']['econom']['user']['modifications'][
            'for_fixed'
        ] == [1, 2, 3, 5, 6, 7, 8, 9, 11, 13, 15, 16]
        assert data['categories']['econom']['driver']['modifications'][
            'for_fixed'
        ] == [1, 2, 3, 5, 6, 7, 8, 9, 11, 12, 15, 16]
        assert data['categories']['econom']['user']['modifications'][
            'for_taximeter'
        ] == [1, 2, 3, 5, 6, 7, 8, 9, 10, 13, 15, 16]
        assert data['categories']['econom']['driver']['modifications'][
            'for_taximeter'
        ] == [1, 2, 3, 5, 6, 7, 8, 9, 10, 12, 15, 16]
