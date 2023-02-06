# pylint: disable=redefined-outer-name, import-only-modules, import-error
# flake8: noqa F401
import pytest

from pricing_extended.mock_router import yamaps_router, mock_yamaps_router
from pricing_extended.mocking_base import check_not_called
from pricing_extended.mocking_base import check_called
from testsuite.utils import matching

from .plugins import test_utils
from .plugins import utils_request
from .round_values import round_values

from .plugins.mock_user_api import user_api
from .plugins.mock_user_api import mock_user_api_get_phones
from .plugins.mock_user_api import mock_user_api_get_users
from .plugins.mock_surge import surger
from .plugins.mock_surge import mock_surger
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


RESPONSE_CASES = test_utils.BooleanFlagCases(
    ['econom', 'with_decoupling', 'business', 'all_additional_prices'],
)


def _reset_prepare_link(response):
    for category in response['categories'].values():
        if 'links' in category and 'prepare' in category['links']:
            category['links']['prepare'] = '__default__'
    return response


def _reset_route_id(response):
    if 'categories' in response:
        for category in response['categories'].values():
            category['driver'] = _reset_route_id(category['driver'])
            category['user'] = _reset_route_id(category['user'])
    else:
        if (
                'trip_information' in response
                and 'route_id' in response['trip_information']
        ):
            response['trip_information']['route_id'] = '__default__'
    return response


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
    argnames=RESPONSE_CASES.get_names(),
    argvalues=RESPONSE_CASES.get_args(),
    ids=RESPONSE_CASES.get_ids(),
)
@pytest.mark.parametrize('response_summary', ['on', 'off', 'prepare_only'])
async def test_v2_prepare_full_response(
        taxi_pricing_data_preparer,
        taxi_config,
        mock_yamaps_router,
        mock_user_api_get_users,
        mock_user_api_get_phones,
        surger,
        mock_surger,
        mock_ride_discounts,
        mock_tags,
        mock_coupons,
        mock_decoupling_corp_tariffs,
        econom_response,
        business_response,
        decoupling_response,
        econom_with_additional_prices,
        econom,
        with_decoupling,
        business,
        all_additional_prices,
        testpoint,
        response_summary,
):
    if response_summary == 'on':
        taxi_config.set(
            PRICING_DATA_PREPARER_RESPONSE_SUMMARY_ENABLED={
                '__default__': True,
            },
        )
    elif response_summary == 'off':
        taxi_config.set(
            PRICING_DATA_PREPARER_RESPONSE_SUMMARY_ENABLED={
                '__default__': False,
            },
        )
    elif utils_request == 'prepare_only':
        taxi_config.set(
            PRICING_DATA_PREPARER_RESPONSE_SUMMARY_ENABLED={
                '__default__': False,
                'handler-v2_prepare-post': True,
            },
        )

    pre_request = utils_request.Request()
    if econom:
        log = {
            'categories': {
                'econom': {
                    'fixed': True,
                    'decoupling': False,
                    'success': False,
                    'user': {
                        'price': 131.0,
                        'category_prices_id': (
                            'c/ed3b2fe5c51f4a4da7bee86349259dda'
                        ),
                        'base_price': {
                            'boarding': 129.0,
                            'distance': 0.0,
                            'time': 1.05,
                        },
                        'trip_details': {'distance': 2046.0, 'time': 307.0},
                    },
                    'driver': {
                        'price': 131.0,
                        'category_prices_id': (
                            'c/ed3b2fe5c51f4a4da7bee86349259dda'
                        ),
                        'base_price': {
                            'boarding': 129.0,
                            'distance': 0.0,
                            'time': 1.05,
                        },
                        'trip_details': {'distance': 2046.0, 'time': 307.0},
                    },
                },
            },
            'surge_calculation_id': '012345678901234567890123',
        }
    elif with_decoupling:
        pre_request.add_decoupling_method()
        log = {
            'categories': {
                'econom': {
                    'fixed': True,
                    'decoupling': True,
                    'success': True,
                    'user': {
                        'price': 56.0,
                        'category_prices_id': (
                            'd/corp_tariff_id/decoupling_category_id'
                        ),
                        'base_price': {
                            'boarding': 49.0,
                            'distance': 4.0920000000000005,
                            'time': 2.558333333333333,
                        },
                        'trip_details': {'distance': 2046.0, 'time': 307.0},
                    },
                    'driver': {
                        'price': 131.0,
                        'category_prices_id': (
                            'c/ed3b2fe5c51f4a4da7bee86349259dda'
                        ),
                        'base_price': {
                            'boarding': 129.0,
                            'distance': 0.0,
                            'time': 1.05,
                        },
                        'trip_details': {'distance': 2046.0, 'time': 307.0},
                    },
                },
            },
            'surge_calculation_id': '012345678901234567890123',
        }
    elif business:
        pre_request.set_categories(['econom', 'business'])
        log = {
            'categories': {
                'econom': {
                    'fixed': True,
                    'decoupling': False,
                    'success': False,
                    'user': {
                        'price': 131.0,
                        'category_prices_id': (
                            'c/ed3b2fe5c51f4a4da7bee86349259dda'
                        ),
                        'base_price': {
                            'boarding': 129.0,
                            'distance': 0.0,
                            'time': 1.05,
                        },
                        'trip_details': {'distance': 2046.0, 'time': 307.0},
                    },
                    'driver': {
                        'price': 131.0,
                        'category_prices_id': (
                            'c/ed3b2fe5c51f4a4da7bee86349259dda'
                        ),
                        'base_price': {
                            'boarding': 129.0,
                            'distance': 0.0,
                            'time': 1.05,
                        },
                        'trip_details': {'distance': 2046.0, 'time': 307.0},
                    },
                },
                'business': {
                    'fixed': False,
                    'reason': 'DISABLED_FOR_CATEGORY',
                    'decoupling': False,
                    'success': False,
                    'user': {
                        'price': 200.0,
                        'category_prices_id': (
                            'c/465adfd1acb34724b7825bf6a2e663d4'
                        ),
                        'base_price': {
                            'boarding': 199.0,
                            'distance': 0.552,
                            'time': 0.0,
                        },
                        'trip_details': {'distance': 2046.0, 'time': 307.0},
                    },
                    'driver': {
                        'price': 200.0,
                        'category_prices_id': (
                            'c/465adfd1acb34724b7825bf6a2e663d4'
                        ),
                        'base_price': {
                            'boarding': 199.0,
                            'distance': 0.552,
                            'time': 0.0,
                        },
                        'trip_details': {'distance': 2046.0, 'time': 307.0},
                    },
                },
            },
            'surge_calculation_id': '012345678901234567890123',
        }
    elif all_additional_prices:
        pre_request.set_additional_prices(
            antisurge=True,
            strikeout=True,
            combo_order=False,
            combo_inner=False,
            combo_outer=False,
        )
        surger.set_explicit_antisurge()
        log = {
            'categories': {
                'econom': {
                    'fixed': True,
                    'decoupling': False,
                    'success': False,
                    'user': {
                        'category_prices_id': (
                            'c/ed3b2fe5c51f4a4da7bee86349259dda'
                        ),
                        'price': 131.0,
                        'strikeout': 131.0,
                        'antisurge': 131.0,
                        'antisurge_strikeout': 131.0,
                        'base_price': {
                            'boarding': 129.0,
                            'distance': 0.0,
                            'time': 1.05,
                        },
                        'trip_details': {'distance': 2046.0, 'time': 307.0},
                    },
                    'driver': {
                        'category_prices_id': (
                            'c/ed3b2fe5c51f4a4da7bee86349259dda'
                        ),
                        'price': 131.0,
                        'antisurge': 131.0,
                        'base_price': {
                            'boarding': 129.0,
                            'distance': 0.0,
                            'time': 1.05,
                        },
                        'trip_details': {'distance': 2046.0, 'time': 307.0},
                    },
                },
            },
            'surge_calculation_id': '012345678901234567890123',
        }

    @testpoint('v2_prepare_response_log')
    def v2_prepare_response_log(data):
        assert round_values(data) == round_values(log)

    request = pre_request.get()
    response = await taxi_pricing_data_preparer.post(
        'v2/prepare', json=request,
    )
    assert response.status_code == 200
    data = round_values(response.json())
    data = _reset_prepare_link(data)
    data = _reset_route_id(data)
    del data['categories']['econom']['backend_variables_uuids']

    if econom:
        assert data == round_values(econom_response)
    if with_decoupling:
        assert data == round_values(decoupling_response)
    if business:
        del data['categories']['business']['backend_variables_uuids']
        assert data == round_values(business_response)
    if all_additional_prices:
        assert data == round_values(econom_with_additional_prices)

    if response_summary == 'off':
        assert v2_prepare_response_log.times_called == 0
    else:
        assert v2_prepare_response_log.times_called == 1
