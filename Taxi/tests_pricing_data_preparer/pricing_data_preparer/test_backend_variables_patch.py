# pylint: disable=redefined-outer-name, import-only-modules, too-many-lines, import-error
# flake8: noqa F401
import uuid

import copy
import pytest

from typing import Dict
from typing import Any

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
from .plugins.mock_cashback_rates import cashback_rates_fixture
from .plugins.mock_cashback_rates import mock_cashback_rates
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
from .plugins.mock_order_core import mock_order_core
from .plugins.mock_order_core import OrderIdRequestType
from .plugins.mock_order_core import order_core

from testsuite.utils import matching

COUPON_SECTION = {
    'currency_code': 'RUB',
    'descr': 'Testsuite promocode',
    'details': [],
    'format_currency': False,
    'series': 'karc',
    'valid': True,
    'value': 150,
}

DISCOUNT_BACKEND_VARIABLES = {
    'calc_data_table_data': [
        {'coeff': 7, 'price': 15},
        {'coeff': 3, 'price': 20},
    ],
    'description': '1',
    'discount_class': 'default',
    'id': '100',
    'is_cashback': False,
    'is_price_strikethrough': True,
    'limited_rides': False,
    'method': 'subvention-fix',
    'restrictions': {
        'driver_less_coeff': 1,
        'max_discount_coeff': 1,
        'min_discount_coeff': 0,
    },
    'with_restriction_by_usages': False,
}

CASHBACK_DISCOUNT_BACKEND_VARIABLES = {
    'calc_data_table_data': [
        {'coeff': 10, 'price': 10},
        {'coeff': 5, 'price': 20},
    ],
    'description': '1',
    'discount_class': 'default',
    'id': '100',
    'is_cashback': False,
    'is_price_strikethrough': True,
    'limited_rides': False,
    'method': 'subvention-fix',
    'restrictions': {
        'driver_less_coeff': 1,
        'max_discount_coeff': 1,
        'min_discount_coeff': 0,
    },
    'with_restriction_by_usages': False,
}

BASE_ORDER_CORE_UPDATE = {
    'unset': {
        'pricing_data_updates': {
            'order.pricing_data.user.data.cashback_discount': True,
            'order.pricing_data.user.data.discount': True,
            'order.pricing_data.user.data.complements': True,
        },
    },
    'set': {
        'pricing_data_updates': {
            'order.pricing_data.user.price.total': 450,
            'order.pricing_data.user.data.cashback_rates': [
                {'rate': 0.4, 'sponsor': 'fintech', 'max_value': 100},
                {'rate': 0.05, 'sponsor': 'portal'},
            ],
            'order.pricing_data.user.data.previous_payment_type': 'card',
            'order.pricing_data.user.data.payment_type': 'cash',
            'order.pricing_data.driver.price.total': 450,
            'order.pricing_data.user.meta': {
                'waiting_in_destination_time': 0,
                'waiting_in_transit_time': 0,
                'total_distance': 4900,
                'waiting_time': 70,
                'total_time': 540,
            },
            'order.pricing_data.driver.meta': {
                'total_distance': 4900,
                'waiting_time': 70,
                'total_time': 540,
                'waiting_in_destination_time': 0,
                'waiting_in_transit_time': 0,
            },
            'order.pricing_data.backend_variables_uuids': {
                'user': matching.uuid_string,
            },
        },
        'fixed_price_updates': {
            'order.fixed_price.driver_price': 450,
            'order.fixed_price.price': 450,
        },
    },
}


class MergeDictCommand:
    def __init__(self):
        pass

    def do_command(self, target_dict: Dict[str, Any], key: str):
        raise NotImplementedError


class ReplaceFieldCommand(MergeDictCommand):
    def __init__(self, value):
        super().__init__()
        self._value = value

    def do_command(self, target_dict: Dict[str, Any], key: str):
        target_dict[key] = self._value


def merge_dicts(left, right):
    left = copy.deepcopy(left)
    for key in right:
        if key in left:
            if isinstance(right[key], MergeDictCommand):
                right[key].do_command(left, key)
            elif isinstance(left[key], dict) and isinstance(right[key], dict):
                left[key] = merge_dicts(left[key], right[key])
            else:
                left[key] = right[key]
        else:
            left[key] = right[key]
    return left


@pytest.mark.parametrize(
    'with_coupon, with_some_discount_response, disable_cashback_rates, expected_order_core_update',
    [
        pytest.param(False, False, False, {}, id='simple_order'),
        pytest.param(
            False,
            True,
            False,
            {
                'set': {
                    'pricing_data_updates': {
                        'order.pricing_data.user.data.cashback_discount': (
                            CASHBACK_DISCOUNT_BACKEND_VARIABLES
                        ),
                        'order.pricing_data.user.data.discount': (
                            DISCOUNT_BACKEND_VARIABLES
                        ),
                        'order.pricing_data.user.data.cashback_rates': [
                            {
                                'max_value': 100,
                                'rate': 0.4,
                                'sponsor': 'fintech',
                            },
                            {'rate': 0.05, 'sponsor': 'portal'},
                        ],
                    },
                },
                'unset': {
                    'pricing_data_updates': ReplaceFieldCommand(
                        {'order.pricing_data.user.data.complements': True},
                    ),
                },
            },
            id='simple_discount',
        ),
        pytest.param(
            True,
            False,
            False,
            {
                'set': {
                    'pricing_data_updates': {
                        'order.pricing_data.user.data.coupon.valid': True,
                    },
                },
            },
            id='simple_coupon',
        ),
        pytest.param(
            False,
            False,
            True,
            {
                'set': {
                    'pricing_data_updates': {
                        'order.pricing_data.user.data.cashback_rates': [],
                    },
                },
            },
            id='disabled_cashback',
        ),
    ],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
async def test_payment_type_update(
        taxi_pricing_data_preparer,
        order_core,
        mock_order_core,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        mock_ride_discounts,
        mock_cashback_rates,
        ride_discounts,
        mock_coupons,
        user_api,
        coupons,
        with_coupon,
        expected_order_core_update,
        with_some_discount_response,
        disable_cashback_rates,
        cashback_rates_fixture,
        mongodb,
):
    order_id = 'fix_price_order'
    if with_coupon:
        result = mongodb.order_proc.update_one(
            {'_id': order_id},
            {
                '$set': {
                    'order.pricing_data.user.data.coupon': COUPON_SECTION,
                    'order.coupon': {'id': 'someid'},
                },
            },
        )
        assert result.matched_count == 1
        coupons.set_valid(True)
        coupons.set_locale('ru')
        coupons.set_expected_order_id(order_id)

    expected_order_core_update = merge_dicts(
        BASE_ORDER_CORE_UPDATE, expected_order_core_update,
    )

    if with_some_discount_response:
        ride_discounts.add_table_discount(
            category_name='econom',
            table=[(15, 7), (20, 3)],
            is_cashback=False,
        )
        ride_discounts.add_table_discount(
            category_name='econom',
            table=[(10, 10), (20, 5)],
            is_cashback=True,
        )

    if disable_cashback_rates:
        cashback_rates_fixture.set_response_rate('econom', {'rates': []})

    user_api.set_user_id('a57210cd2aa942d39bdce67170051326')

    result = await taxi_pricing_data_preparer.patch(
        '/internal/v1/backend_variables/',
        json={
            'order_id': order_id,
            'reason': 'payment_type_changed',
            'new_value': {
                'variable_id': 'payment_type',
                'payment_type': 'cash',
            },
        },
    )
    assert result.status_code == 200
    assert mock_order_core.get_fields.times_called == 1
    assert result.json() == expected_order_core_update


DEFAULT_META = {
    'total_distance': 4900.0,
    'total_time': 540.0,
    'waiting_in_destination_time': 0.0,
    'waiting_in_transit_time': 0.0,
    'waiting_time': 70.0,
}


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
async def test_extra_price_update(
        taxi_pricing_data_preparer,
        order_core,
        mock_order_core,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        mock_ride_discounts,
        mock_cashback_rates,
        ride_discounts,
        mock_coupons,
        user_api,
        coupons,
        cashback_rates_fixture,
        mongodb,
):
    order_core.set_expected_update_fields(
        {'order.pricing_data.user.data.extra_price': 42.42},
    )
    result = await taxi_pricing_data_preparer.patch(
        '/internal/v1/backend_variables/',
        json={
            'order_id': 'fix_price_order',
            'reason': 'user_increase_price',
            'new_value': {
                'variable_id': 'extra_price',
                'extra_price_value': 42.42,
            },
        },
    )
    assert result.status_code == 200
    assert mock_order_core.get_fields.times_called == 1
    assert result.json() == {
        'set': {
            'fixed_price_updates': {
                'order.fixed_price.driver_price': 450.0,
                'order.fixed_price.price': 450.0,
            },
            'pricing_data_updates': {
                'order.pricing_data.driver.meta': DEFAULT_META,
                'order.pricing_data.driver.price.total': 450.0,
                'order.pricing_data.user.data.extra_price': 42.42,
                'order.pricing_data.user.meta': DEFAULT_META,
                'order.pricing_data.user.price.total': 450.0,
                'order.pricing_data.backend_variables_uuids': {
                    'user': matching.uuid_string,
                },
            },
        },
        'unset': {'pricing_data_updates': {}},
    }


@pytest.mark.parametrize(
    'fallback_enabled_v1_backend_variables_patch',
    [pytest.param(True), pytest.param(False)],
)
@pytest.mark.parametrize('fixed_price_value', [True, False])
@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
async def test_waypoints_count_update(
        taxi_pricing_data_preparer,
        order_core,
        mock_order_core,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        mock_ride_discounts,
        mock_cashback_rates,
        ride_discounts,
        mock_coupons,
        user_api,
        coupons,
        cashback_rates_fixture,
        fallback_enabled_v1_backend_variables_patch,
        fixed_price_value,
        experiments3,
        mongodb,
):
    order_core.set_expected_update_fields(
        {'order.pricing_data.user.data.waypoints_count': 2},
    )
    experiments3.add_config(
        consumers=['pricing-data-preparer/patch'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        name='switch_v1_backend_variables_patch',
        default_value={
            'fallback_enabled': fallback_enabled_v1_backend_variables_patch,
        },
    )
    order_id = 'fix_price_order'
    mongodb.order_proc.update_one(
        {'_id': order_id},
        {'$set': {'order.pricing_data.fixed_price': fixed_price_value}},
    )
    result = await taxi_pricing_data_preparer.patch(
        '/internal/v1/backend_variables/',
        json={
            'order_id': 'fix_price_order',
            'reason': 'change_destinations',
            'new_value': {
                'variable_id': 'waypoints_count',
                'waypoints_count': 2,
            },
        },
    )
    assert result.status_code == 200
    assert mock_order_core.get_fields.times_called == int(
        not fallback_enabled_v1_backend_variables_patch,
    )
    correct_result = {
        'set': {
            'pricing_data_updates': {
                'order.pricing_data.user.data.waypoints_count': 2,
            },
        },
        'unset': {'pricing_data_updates': {}},
    }
    if fixed_price_value:
        correct_result['set']['fixed_price_updates'] = {
            'order.fixed_price.driver_price': 450.0,
            'order.fixed_price.price': 450.0,
        }
        correct_result['set']['pricing_data_updates'] = {
            'order.pricing_data.driver.meta': DEFAULT_META,
            'order.pricing_data.driver.price.total': 450.0,
            'order.pricing_data.user.meta': DEFAULT_META,
            'order.pricing_data.user.price.total': 450.0,
            'order.pricing_data.backend_variables_uuids': {
                'user': matching.uuid_string,
            },
            'order.pricing_data.user.data.waypoints_count': 2,
        }
    if not fallback_enabled_v1_backend_variables_patch:
        assert result.json() == correct_result
    else:
        assert result.json() == {
            'set': {'pricing_data_updates': {}},
            'unset': {'pricing_data_updates': {}},
        }


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
async def test_extra_price_update_with_paid_supply(
        taxi_pricing_data_preparer,
        order_core,
        mock_order_core,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        mock_ride_discounts,
        mock_cashback_rates,
        ride_discounts,
        mock_coupons,
        user_api,
        coupons,
        cashback_rates_fixture,
        mongodb,
):
    order_core.set_expected_update_fields(
        {'order.pricing_data.user.data.extra_price': 42.42},
    )
    result = await taxi_pricing_data_preparer.patch(
        '/internal/v1/backend_variables/',
        json={
            'order_id': 'order_with_paid_supply',
            'reason': 'user_increase_price',
            'new_value': {
                'variable_id': 'extra_price',
                'extra_price_value': 42.42,
            },
        },
    )
    assert result.status_code == 200
    assert mock_order_core.get_fields.times_called == 1
    assert result.json() == {
        'set': {
            'fixed_price_updates': {
                'order.fixed_price.driver_price': 450.0,
                'order.fixed_price.price': 450.0,
                'order.fixed_price.paid_supply_price': 100500,
            },
            'pricing_data_updates': {
                'order.pricing_data.driver.meta': DEFAULT_META,
                'order.pricing_data.driver.price.total': 450.0,
                'order.pricing_data.user.data.extra_price': 42.42,
                'order.pricing_data.user.meta': DEFAULT_META,
                'order.pricing_data.user.price.total': 450.0,
                'order.pricing_data.driver.additional_prices.paid_supply.meta': {},
                'order.pricing_data.driver.additional_prices.paid_supply.price.total': (
                    100950
                ),
                'order.pricing_data.user.additional_prices.paid_supply.meta': {},
                'order.pricing_data.user.additional_prices.paid_supply.price.total': (
                    100950
                ),
                'order.pricing_data.backend_variables_uuids': {
                    'user': matching.uuid_string,
                },
            },
        },
        'unset': {'pricing_data_updates': {}},
    }


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
async def test_extra_price_update_decoupling(
        taxi_pricing_data_preparer,
        order_core,
        mock_order_core,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        mock_ride_discounts,
        mock_cashback_rates,
        ride_discounts,
        mock_coupons,
        user_api,
        coupons,
        cashback_rates_fixture,
        mongodb,
):
    order_core.set_expected_update_fields(
        {'order.pricing_data.user.data.extra_price': 42.42},
    )
    result = await taxi_pricing_data_preparer.patch(
        '/internal/v1/backend_variables/',
        json={
            'order_id': 'fix_price_order_decoupling',
            'reason': 'user_increase_price',
            'new_value': {
                'variable_id': 'extra_price',
                'extra_price_value': 42.42,
            },
        },
    )
    assert result.status_code == 200
    assert mock_order_core.get_fields.times_called == 1
    assert result.json() == {
        'set': {
            'fixed_price_updates': {
                'order.fixed_price.driver_price': 450.0,
                'order.fixed_price.price': 450.0,
            },
            'pricing_data_updates': {
                'order.pricing_data.driver.meta': DEFAULT_META,
                'order.pricing_data.driver.price.total': 450.0,
                'order.pricing_data.user.data.extra_price': 42.42,
                'order.pricing_data.user.meta': DEFAULT_META,
                'order.pricing_data.user.price.total': 450.0,
                'order.pricing_data.driver.data.extra_price': 42.42,
                'order.pricing_data.backend_variables_uuids': {
                    'user': matching.uuid_string,
                    'driver': matching.uuid_string,
                },
            },
            'decoupling_updates': {
                'order.decoupling.driver_price_info.fixed_price': 450,
                'order.decoupling.user_price_info.fixed_price': 450,
            },
        },
        'unset': {'pricing_data_updates': {}},
    }


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
async def test_extra_price_update_non_fixed_price(
        taxi_pricing_data_preparer,
        order_core,
        mock_order_core,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        mock_ride_discounts,
        mock_cashback_rates,
        ride_discounts,
        mock_coupons,
        user_api,
        coupons,
        cashback_rates_fixture,
        mongodb,
):
    order_core.set_expected_update_fields(
        {'order.pricing_data.user.data.extra_price': 42.42},
    )
    result = await taxi_pricing_data_preparer.patch(
        '/internal/v1/backend_variables/',
        json={
            'order_id': 'non_fix_price_order',
            'reason': 'user_increase_price',
            'new_value': {
                'variable_id': 'extra_price',
                'extra_price_value': 42.42,
            },
        },
    )
    assert result.status_code == 200
    assert mock_order_core.get_fields.times_called == 1
    assert result.json() == {
        'set': {
            'pricing_data_updates': {
                'order.pricing_data.user.data.extra_price': 42.42,
            },
        },
        'unset': {'pricing_data_updates': {}},
    }


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
async def test_accepted_driver_price_update(
        taxi_pricing_data_preparer,
        order_core,
        mock_order_core,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        mock_ride_discounts,
        mock_cashback_rates,
        ride_discounts,
        mock_coupons,
        user_api,
        coupons,
        cashback_rates_fixture,
        mongodb,
):
    order_core.set_expected_update_fields(
        {'order.pricing_data.user.data.extra_price': 42.42},
    )
    result = await taxi_pricing_data_preparer.patch(
        '/internal/v1/backend_variables/',
        json={
            'order_id': 'fix_price_order',
            'reason': 'user_accept_bid',
            'new_value': {
                'variable_id': 'accepted_driver_price',
                'accepted_driver_price_value': 42.42,
            },
        },
    )
    assert result.status_code == 200
    assert mock_order_core.get_fields.times_called == 1
    assert result.json() == {
        'set': {
            'fixed_price_updates': {
                'order.fixed_price.driver_price': 450.0,
                'order.fixed_price.price': 450.0,
            },
            'pricing_data_updates': {
                'order.pricing_data.driver.meta': DEFAULT_META,
                'order.pricing_data.driver.price.total': 450.0,
                'order.pricing_data.user.data.accepted_driver_price': 42.42,
                'order.pricing_data.user.meta': DEFAULT_META,
                'order.pricing_data.user.price.total': 450.0,
                'order.pricing_data.backend_variables_uuids': {
                    'user': matching.uuid_string,
                },
            },
        },
        'unset': {'pricing_data_updates': {}},
    }
