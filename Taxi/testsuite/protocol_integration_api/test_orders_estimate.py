# flake8: noqa: F401, F811

import copy
import datetime
import json
from urllib import request

import bson
import pytest

from taxi_tests import utils
from taxi_tests.utils import ordered_object
from tests_plugins.daemons import service_client

from order_offers_switch_parametrize import ORDER_OFFERS_SAVE_SWITCH
from protocol.routestats import utils as rs_utils
from protocol_integration_api.estimate import utils as es_utils
from protocol_integration_api.estimate.utils import test_fixtures
from replica_dbusers_switch_parametrize import (
    PROTOCOL_SWITCH_TO_REPLICA_DBUSERS,
)


def make_afs_is_spammer_response_builder(add_sec_to_block_time):
    def response_builder(now):
        if add_sec_to_block_time is None:
            return {'is_spammer': False}
        blocked_until = now + datetime.timedelta(seconds=add_sec_to_block_time)
        return {
            'is_spammer': True,
            'blocked_until': utils.timestring(blocked_until),
        }

    return response_builder


CALLCENTER_PRICE_MODIFIERS = {
    'items': [
        {
            'value': '1.020000',
            'type': 'multiplier',
            'reason': 'call_center',
            'tariff_categories': ['econom', 'child_tariff'],
            'pay_subventions': False,
        },
    ],
}
YAPLUS_PRICE_MODIFIERS = {
    'items': [
        {
            'value': '0.900000',
            'type': 'multiplier',
            'reason': 'ya_plus',
            'tariff_categories': ['econom'],
            'pay_subventions': True,
        },
    ],
}


DETAILS_NO_MODIFIERS = [
    {'type': 'price', 'value': 'from 99 rub'},
    {'type': 'comment', 'value': '5 min included thereafter 9 rub/min'},
    {'type': 'comment', 'value': '2 km included thereafter 9 rub/km'},
]

DETAILS_NO_MODIFIERS_NEW_PRICING = [{'type': 'price', 'value': 'from 99 rub'}]

DETAILS_APPLICATION_CATEGORY_CALLCENTER_SOURCE = [
    {'type': 'price', 'value': 'from 101 rub'},
    {'type': 'comment', 'value': '5 min included thereafter 9 rub/min'},
    {'type': 'comment', 'value': '2 km included thereafter 9 rub/km'},
]


DETAILS_CALLCENTER_CATEGORY_CALLCENTER_SOURCE = [
    {'type': 'price', 'value': 'from 111 rub'},
    {'type': 'comment', 'value': '5 min included thereafter 9 rub/min'},
    {'type': 'comment', 'value': '2 km included thereafter 9 rub/km'},
]

DETAILS_CALLCENTER_CATEGORY_CALLCENTER_SOURCE_NEW_PRICING = [
    {'type': 'price', 'value': 'from 111 rub'},
]

DETAILS_YAPLUS_SOURCE = [
    {'type': 'price', 'value': 'from 89 rub'},
    {'type': 'comment', 'value': '5 min included thereafter 8 rub/min'},
    {'type': 'comment', 'value': '2 km included thereafter 8 rub/km'},
]

RESPONSE_DETAILS_TARIFF_CHILD_RU_SURGE = [
    {'type': 'price', 'value': 'от 131 руб.'},
    {'type': 'comment', 'value': 'включено 5 мин далее 12 руб./мин'},
    {'type': 'comment', 'value': 'включено 2 км далее 11 руб./км'},
]


RESPONSE_DETAILS_TARIFF_CHILD_EN_SURGE = [
    {'type': 'price', 'value': 'from 131 rub'},
    {'type': 'comment', 'value': '5 min included thereafter 12 rub/min'},
    {'type': 'comment', 'value': '2 km included thereafter 11 rub/km'},
]


COMMON_DISCOUNTS_RESPONSE = {
    'discounts': [
        {
            'class': 'econom',
            'discount': {
                'value': 0.11,
                'price': 943.0,
                'original_value': 0.12,
                'reason': 'for_all',
                'method': 'full-driver-less',
            },
        },
    ],
    'discount_offer_id': '123456',
}


ONLY_BASE_DISCOUNT_COST_BREAKDOWN = [
    {'display_amount': 'Ride 814 rub, ~49 min', 'display_name': 'cost'},
    {'display_amount': '915 rub', 'display_name': 'cost_without_discount'},
    {'display_amount': '11%', 'display_name': 'discount'},
    {'display_amount': '11%', 'display_name': 'total_discount'},
]
PLUS_COST_BREAKDOWN = [
    {'display_amount': 'Ride 733 rub, ~49 min', 'display_name': 'cost'},
    {'display_amount': '915 rub', 'display_name': 'cost_without_discount'},
    {'display_amount': '20%', 'display_name': 'discount'},
    {'display_amount': '20%', 'display_name': 'total_discount'},
    {'display_amount': '10%', 'display_name': 'ya_plus_discount'},
    {'display_amount': '11%', 'display_name': 'base_discount'},
]
CALLCENTER_COST_830_BREAKDOWN = [
    {'display_amount': 'Ride 830 rub, ~49 min', 'display_name': 'cost'},
    {'display_amount': '1,097 rub', 'display_name': 'cost_without_discount'},
    {'display_amount': '24%', 'display_name': 'discount'},
    {'display_amount': '24%', 'display_name': 'total_discount'},
    {'display_amount': '15%', 'display_name': 'call_center_discount'},
    {'display_amount': '11%', 'display_name': 'base_discount'},
]
CALLCENTER_COST_839_BREAKDOWN = [
    {'display_amount': 'Ride 839 rub, ~49 min', 'display_name': 'cost'},
    {'display_amount': '1,109 rub', 'display_name': 'cost_without_discount'},
    {'display_amount': '24%', 'display_name': 'discount'},
    {'display_amount': '24%', 'display_name': 'total_discount'},
    {'display_amount': '15%', 'display_name': 'call_center_discount'},
    {'display_amount': '11%', 'display_name': 'base_discount'},
]

DETAILS_DECOUPLING = [
    {'type': 'price', 'value': 'from 198 rub'},
    {'type': 'comment', 'value': '5 min included thereafter 18 rub/min'},
    {'type': 'comment', 'value': '2 km included thereafter 18 rub/km'},
]

DETAILS_DECOUPLING_FROM_NEW_PRICING_RESPONSE = [
    {'type': 'price', 'value': 'from 198 rub'},
]

PDP_COST_BREAKDOWN_FIELDS = [
    'total_discount',
    'discount',
    'cost',
    'cost_without_discount',
]

CC_HEADERS = {'User-Agent': 'call_center'}


OFFER_EXTRA_DATA_SUCCESS_PDP_PRICES_CALL_CENTER = {
    'decoupling': {
        'success': True,
        'user': {
            'tariff': 'driver_corp_tariff_id-user_corp_tariff_id',
            'prices': [
                {
                    'cls': 'econom',
                    'cat_type': 'call_center',
                    'category_id': 'user_decoupling_category_id',
                    'price': 123.0,
                    'sp': 2.0,
                    'is_fixed_price': True,
                    'using_new_pricing': True,
                },
            ],
        },
        'driver': {
            'tariff': 'driver_corp_tariff_id',
            'prices': [
                {
                    'cls': 'econom',
                    'cat_type': 'call_center',
                    'category_id': 'driver_decoupling_category_id',
                    'price': 321.0,
                    'sp': 4.0,
                    'is_fixed_price': True,
                    'using_new_pricing': True,
                },
            ],
        },
    },
}

OFFER_EXTRA_DATA_SUCCESS_PDP_PRICES_CORP_CABINET = {
    'decoupling': {
        'success': True,
        'user': {
            'tariff': 'driver_corp_tariff_id-user_corp_tariff_id',
            'prices': [
                {
                    'cls': 'econom',
                    'cat_type': 'application',
                    'category_id': 'user_decoupling_category_id',
                    'price': 123.0,
                    'sp': 2.0,
                    'is_fixed_price': True,
                    'using_new_pricing': True,
                },
            ],
        },
        'driver': {
            'tariff': 'driver_corp_tariff_id',
            'prices': [
                {
                    'cls': 'econom',
                    'cat_type': 'application',
                    'category_id': 'driver_decoupling_category_id',
                    'price': 321.0,
                    'sp': 4.0,
                    'is_fixed_price': True,
                    'using_new_pricing': True,
                },
            ],
        },
    },
}

OFFER_EXTRA_DATA_PDP_NO_FIX_PRICES = {
    'decoupling': {
        'success': True,
        'user': {
            'tariff': 'driver_corp_tariff_id-user_corp_tariff_id',
            'prices': [
                {
                    'cls': 'econom',
                    'cat_type': 'application',
                    'category_id': 'user_decoupling_category_id',
                    'price': 123.0,
                    'sp': 2.0,
                    'is_fixed_price': False,
                    'using_new_pricing': True,
                },
            ],
        },
        'driver': {
            'tariff': 'driver_corp_tariff_id',
            'prices': [
                {
                    'cls': 'econom',
                    'cat_type': 'application',
                    'category_id': 'driver_decoupling_category_id',
                    'price': 321.0,
                    'sp': 4.0,
                    'is_fixed_price': False,
                    'using_new_pricing': True,
                },
            ],
        },
    },
}

CORP_CABINET_WITH_DECOUPLING_REQUEST = {
    'user': {
        'personal_phone_id': 'p00000000000000000000008',
        'phone': '+79061112288',
        'user_id': 'e4707fc6e79e4562b4f0af20a8e877a8',
    },
    'payment': {'type': 'corp', 'payment_method_id': 'corp-decoupled-client'},
    'requirements': {'nosmoking': True},
    'route': [[37.1946401739712, 55.478983901730004], [37.56521, 55.734434]],
    'selected_class': 'econom',
    'sourceid': 'corp_cabinet',
}

CALLCENTER_WITH_DECOUPLING_REQUEST = {
    'user': {
        'personal_phone_id': 'p00000000000000000000008',
        'phone': '+79061112288',
        'user_id': 'e4707fc6e79e4562b4f0af20a8e877a8',
    },
    'payment': {'type': 'corp', 'payment_method_id': 'corp-decoupled-client'},
    'requirements': {'nosmoking': True},
    'route': [[37.1946401739712, 55.478983901730004], [37.56521, 55.734434]],
    'selected_class': 'econom',
    'sourceid': 'corp_cabinet',
}

DECOUPLING_USER_CATEGORY_PRICES_ID = (
    'd/driver_corp_tariff_id'
    '-user_corp_tariff_id'
    '/user_decoupling_category_id'
)

PDP_TARIFF_CATEGORY_INFO = {
    'user_category_prices_id': DECOUPLING_USER_CATEGORY_PRICES_ID,
    'user_category_id': 'user_decoupling_category_id',
    'user_tariff_id': 'user_corp_tariff_id',
    'driver_category_prices_id': 'c/driver_decoupling_category_id',
    'driver_category_id': 'driver_decoupling_category_id',
    'driver_tariff_id': 'driver_corp_tariff_id',
}


def filter_pdp_cost_breakdown(cost_breakdown):
    return [
        value
        for value in cost_breakdown
        if value['display_name'] in PDP_COST_BREAKDOWN_FIELDS
    ]


def filter_pdp_details_tariff(detail_tariffs):
    return [
        value
        for value in detail_tariffs
        if value['type'] != 'comment' and value['type'] != 'icon'
    ]


@pytest.fixture()
def test_fixture_surge(mockserver, load_json):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_getsurge(request):
        input_json = json.loads(request.get_data())
        mocks = {
            'econom': 'get_surge_econom.json',
            'child_tariff': 'get_surge_child.json',
        }
        key = '+'.join(sorted(input_json['classes']))
        assert key in mocks
        return load_json(mocks[key])

    return []


def get_surge_calculator_response(request, surge_value, load_json):
    input_json = json.loads(request.get_data())
    mocks = {
        'econom': 'get_surge_econom.json',
        'child_tariff': 'get_surge_child.json',
    }
    key = '+'.join(sorted(input_json['classes']))
    assert key in mocks
    surge_json = load_json(mocks[key])
    surge_json['classes'][0]['surge']['value'] = surge_value
    surge_json['classes'][0]['value_raw'] = surge_value
    surge_json['classes'][0]['calculation_meta']['smooth']['point_a'][
        'value'
    ] = surge_value
    return surge_json


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'child_tariff'],
    },
    ROUTER_MAPS_ENABLED=True,
    INTEGRATION_API_ESTIMATE_USE_DRIVER_ETA=True,
)
@pytest.mark.parametrize(
    'phone,personal_phone_id,user_id,yandex_uid,'
    'taxi_class,sourceid,payment,details_tariff,'
    'cost_breakdown,price,price_with_currency,time,offer_prices,'
    'price_modifiers,config_values,pdp_data',
    [
        (
            '+79061112288',
            'p00000000000000000000008',
            'e4707fc6e79e4562b4f0af20a8e877a8',
            None,
            'econom',
            'corp_cabinet',
            {'type': 'corp', 'payment_method_id': 'corp-1234'},
            DETAILS_NO_MODIFIERS,
            ONLY_BASE_DISCOUNT_COST_BREAKDOWN,
            814,
            '814 rub',
            '49 min',
            [
                {
                    'driver_price': 915.0,
                    'price': 814.0,
                    'cat_type': 'application',
                    'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                    'sp': 1.0,
                    'cls': 'econom',
                    'is_fixed_price': True,
                    'using_new_pricing': False,
                },
            ],
            None,
            {},
            {'user_price': 814, 'driver_price': 915, 'min_price': 99},
        ),
        (
            '+79061112255',
            'p00000000000000000000005',
            'a5607fc6e79e4562b4f0af20a8e877a4',
            '480301451',
            'econom',
            'alice',
            {'type': 'corp', 'payment_method_id': 'corp-1234'},
            DETAILS_NO_MODIFIERS,
            ONLY_BASE_DISCOUNT_COST_BREAKDOWN,
            814,
            '814 rub',
            '49 min',
            [
                {
                    'driver_price': 915.0,
                    'price': 814.0,
                    'cat_type': 'application',
                    'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                    'sp': 1.0,
                    'cls': 'econom',
                    'is_fixed_price': True,
                    'using_new_pricing': False,
                },
            ],
            None,
            {},
            {'user_price': 814, 'driver_price': 915, 'min_price': 99},
        ),
        # With 'users/integration/create' as USER_API
        (
            '+79061112255',
            'p00000000000000000000005',
            'a5607fc6e79e4562b4f0af20a8e877a4',
            '480301451',
            'econom',
            'alice',
            {'type': 'cash'},
            DETAILS_YAPLUS_SOURCE,
            PLUS_COST_BREAKDOWN,
            733,
            '733 rub',
            '49 min',
            [
                {
                    'driver_price': 915.0,
                    'price': 733.0,
                    'cat_type': 'application',
                    'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                    'sp': 1.0,
                    'cls': 'econom',
                    'is_fixed_price': True,
                    'using_new_pricing': False,
                },
            ],
            YAPLUS_PRICE_MODIFIERS,
            {
                'ALICE_APPLY_PLUS_PRICE_MODIFIER': True,
                'USER_API_USERS_ENDPOINTS': {'users/integration/create': True},
            },
            {'user_price': 733, 'driver_price': 915, 'min_price': 89},
        ),
        # With 'users/integration/create' from MONGO
        (
            '+79061112255',
            'p00000000000000000000005',
            'a5607fc6e79e4562b4f0af20a8e877a4',
            '480301451',
            'econom',
            'alice',
            {'type': 'cash'},
            DETAILS_YAPLUS_SOURCE,
            PLUS_COST_BREAKDOWN,
            733,
            '733 rub',
            '49 min',
            [
                {
                    'driver_price': 915.0,
                    'price': 733.0,
                    'cat_type': 'application',
                    'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                    'sp': 1.0,
                    'cls': 'econom',
                    'is_fixed_price': True,
                    'using_new_pricing': False,
                },
            ],
            YAPLUS_PRICE_MODIFIERS,
            {'ALICE_APPLY_PLUS_PRICE_MODIFIER': True},
            {'user_price': 733, 'driver_price': 915, 'min_price': 89},
        ),
        (
            '+79061112255',
            'p00000000000000000000005',
            'a5607fc6e79e4562b4f0af20a8e877a4',
            '480301451',
            'econom',
            'alice',
            {'type': 'cash'},
            DETAILS_NO_MODIFIERS,
            ONLY_BASE_DISCOUNT_COST_BREAKDOWN,
            814,
            '814 rub',
            '49 min',
            [
                {
                    'driver_price': 915.0,
                    'price': 814.0,
                    'cat_type': 'application',
                    'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                    'sp': 1.0,
                    'cls': 'econom',
                    'is_fixed_price': True,
                    'using_new_pricing': False,
                },
            ],
            None,
            {},
            {'user_price': 814, 'driver_price': 915, 'min_price': 99},
        ),
        (
            '+79061112255',
            'p00000000000000000000005',
            'a5607fc6e79e4562b4f0af20a8e877aa',
            '480301451',
            'econom',
            'turboapp',
            {'type': 'cash'},
            DETAILS_YAPLUS_SOURCE,
            PLUS_COST_BREAKDOWN,
            733,
            '733 rub',
            '49 min',
            [
                {
                    'driver_price': 915.0,
                    'price': 733.0,
                    'cat_type': 'application',
                    'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                    'sp': 1.0,
                    'cls': 'econom',
                    'is_fixed_price': True,
                    'using_new_pricing': False,
                },
            ],
            YAPLUS_PRICE_MODIFIERS,
            {
                'ALICE_APPLY_PLUS_PRICE_MODIFIER': True,
                'INTEGRATION_API_ENABLED_YA_PLUS_FOR_SOURCE': ['turboapp'],
            },
            {'user_price': 733, 'driver_price': 915, 'min_price': 89},
        ),
        (
            '+79061112255',
            'p00000000000000000000005',
            'a5607fc6e79e4562b4f0af20a8e877aa',
            '480301451',
            'econom',
            'turboapp',
            {'type': 'cash'},
            DETAILS_NO_MODIFIERS,
            ONLY_BASE_DISCOUNT_COST_BREAKDOWN,
            814,
            '814 rub',
            '49 min',
            [
                {
                    'driver_price': 915.0,
                    'price': 814.0,
                    'cat_type': 'application',
                    'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                    'sp': 1.0,
                    'cls': 'econom',
                    'is_fixed_price': True,
                    'using_new_pricing': False,
                },
            ],
            None,
            {
                'ALICE_APPLY_PLUS_PRICE_MODIFIER': True,
                'INTEGRATION_API_ENABLED_YA_PLUS_FOR_SOURCE': [],
            },
            {'user_price': 814, 'driver_price': 915, 'min_price': 99},
        ),
    ],
    ids=[
        'corp cabinet, corp pay',
        'alice, corp pay',
        'ya_plus, alice, cash, user_api',
        'ya_plus, alice, cash, mongo',
        'ya_plus, cash, disabled ya_plus config',
        'ya_plus, turboapp',
        'disabled ya_plus for source, turboapp',
    ],
)
@pytest.mark.now('2018-04-24T08:15:00+0000')
@pytest.mark.user_experiments('fixed_price', 'use_discounts_service')
def test_with_sourceid(
        taxi_integration,
        mockserver,
        config,
        db,
        discounts,
        test_fixture_surge,
        test_fixtures,
        phone,
        personal_phone_id,
        user_id,
        yandex_uid,
        taxi_class,
        sourceid,
        payment,
        details_tariff,
        cost_breakdown,
        price,
        price_with_currency,
        time,
        offer_prices,
        price_modifiers,
        config_values,
        pricing_data_preparer,
        pdp_data,
):
    pricing_data_preparer.set_strikeout(915)
    pricing_data_preparer.set_cost(
        pdp_data['user_price'], pdp_data['driver_price'],
    )
    pricing_data_preparer.set_user_category_prices_id(
        'c/b7c4d5f6aa3b40a3807bb74b3bc042af',
    )
    pricing_data_preparer.set_categories([taxi_class])
    pricing_data_preparer.set_user_surge(
        1.0, alpha=None, beta=None, surcharge=None,
    )
    pricing_data_preparer.set_trip_information(time=49 * 60, distance=1000)
    pricing_data_preparer.set_meta('min_price', pdp_data['min_price'])

    offer_prices = copy.deepcopy(offer_prices)
    offer_prices[0]['using_new_pricing'] = True
    offer_prices[0]['pricing_data'] = pricing_data_preparer.get_pricing_data()
    cost_breakdown = filter_pdp_cost_breakdown(cost_breakdown)
    details_tariff = filter_pdp_details_tariff(details_tariff)

    config.set_values(config_values)
    discounts.set_discount_response(COMMON_DISCOUNTS_RESPONSE)

    request_body = {
        'user': {
            'phone': phone,
            'personal_phone_id': personal_phone_id,
            'user_id': user_id,
        },
        'requirements': {'nosmoking': True},
        'route': [
            [37.1946401739712, 55.478983901730004],
            [37.565210, 55.734434],
        ],
        'selected_class': taxi_class,
        'sourceid': sourceid,
        'chainid': 'chainid_1',
    }
    if yandex_uid is not None:
        request_body['user']['yandex_uid'] = yandex_uid

    if payment is not None:
        request_body['payment'] = payment

    response = taxi_integration.post('v1/orders/estimate', json=request_body)

    assert response.status_code == 200, response.text

    es_utils.check_response(
        response.json(),
        db,
        user_id,
        offer_prices,
        price_modifiers,
        taxi_class,
        cost_breakdown,
        details_tariff,
        price,
        price_with_currency,
        time,
    )


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'child_tariff'],
    },
    ROUTER_MAPS_ENABLED=True,
    INTEGRATION_API_ESTIMATE_USE_DRIVER_ETA=True,
)
@pytest.mark.parametrize(
    'phone,personal_phone_id,user_id,taxi_class,payment,details_tariff,'
    'cost_breakdown,price,price_with_currency,time,offer_prices,'
    'config_values,pdp_data',
    [
        (
            '+79061112255',
            'p00000000000000000000005',
            'e4707fc6e79e4562b4f0af20a8e877a3',
            'econom',
            {'type': 'corp', 'payment_method_id': 'corp-1234'},
            DETAILS_CALLCENTER_CATEGORY_CALLCENTER_SOURCE,
            CALLCENTER_COST_839_BREAKDOWN,
            839,
            '839 rub',
            '49 min',
            [
                {
                    'driver_price': 943.0,
                    'price': 839.0,
                    'cat_type': 'call_center',
                    'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042a3',
                    'sp': 1.0,
                    'cls': 'econom',
                    'is_fixed_price': True,
                    'using_new_pricing': False,
                },
            ],
            {'INTEGRATION_TARIFFS_ENABLED': True},
            {
                'strikeout_price': 1109,
                'user_price': 839,
                'driver_price': 943,
                'sp': 1.0,
                'category_prices_id': 'c/b7c4d5f6aa3b40a3807bb74b3bc042a3',
                'min_price': 111,
            },
        ),
        (
            '+79061112255',
            'p00000000000000000000005',
            'e4707fc6e79e4562b4f0af20a8e877a3',
            'child_tariff',
            {'type': 'cash'},
            RESPONSE_DETAILS_TARIFF_CHILD_EN_SURGE,
            [
                {
                    'display_amount': 'Ride 1,212 rub, ~49 min',
                    'display_name': 'cost',
                },
                {
                    'display_amount': '1,426 rub',
                    'display_name': 'cost_without_discount',
                },
                {'display_amount': '15%', 'display_name': 'discount'},
                {'display_amount': '15%', 'display_name': 'total_discount'},
                {
                    'display_amount': '15%',
                    'display_name': 'call_center_discount',
                },
            ],
            1212,
            '1,212 rub',
            '49 min',
            [
                {
                    'driver_price': 1212.0,
                    'price': 1212.0,
                    'cat_type': 'application',
                    'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                    'sp': 1.3,
                    'cls': 'child_tariff',
                    'is_fixed_price': True,
                    'using_new_pricing': False,
                },
            ],
            {'INTEGRATION_TARIFFS_ENABLED': False},
            {
                'strikeout_price': 1426,
                'user_price': 1212,
                'driver_price': 1212,
                'sp': 1.3,
                'category_prices_id': 'c/b7c4d5f6aa3b40a3807bb74b3bc042af',
                'min_price': 131,
            },
        ),
        (
            '+79061112266',
            'p00000000000000000000006',
            'e4707fc6e79e4562b4f0af20a8e877a4',
            'econom',
            None,
            DETAILS_CALLCENTER_CATEGORY_CALLCENTER_SOURCE,
            CALLCENTER_COST_839_BREAKDOWN,
            839,
            '839 rub',
            '49 min',
            [
                {
                    'driver_price': 943.0,
                    'price': 839.0,
                    'cat_type': 'call_center',
                    'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042a3',
                    'sp': 1.0,
                    'cls': 'econom',
                    'is_fixed_price': True,
                    'using_new_pricing': False,
                },
            ],
            {'INTEGRATION_TARIFFS_ENABLED': True},
            {
                'strikeout_price': 1109,
                'user_price': 839,
                'driver_price': 943,
                'sp': 1.0,
                'category_prices_id': 'c/b7c4d5f6aa3b40a3807bb74b3bc042a3',
                'min_price': 111,
            },
        ),
    ],
    ids=[
        'corp pay',
        'cash, no call_center category, child_tariff',
        'user has active order, none pay',
    ],
)
@pytest.mark.now('2018-04-24T08:15:00+0000')
@pytest.mark.user_experiments('fixed_price', 'use_discounts_service')
def test_call_center(
        taxi_integration,
        mockserver,
        config,
        db,
        discounts,
        test_fixture_surge,
        test_fixtures,
        phone,
        personal_phone_id,
        user_id,
        taxi_class,
        payment,
        details_tariff,
        cost_breakdown,
        price,
        price_with_currency,
        time,
        offer_prices,
        config_values,
        pricing_data_preparer,
        pdp_data,
):
    pricing_data_preparer.set_strikeout(pdp_data['strikeout_price'])
    pricing_data_preparer.set_cost(
        pdp_data['user_price'], pdp_data['driver_price'],
    )
    pricing_data_preparer.set_user_category_prices_id(
        pdp_data['category_prices_id'],
    )
    pricing_data_preparer.set_categories([taxi_class])
    pricing_data_preparer.set_user_surge(
        pdp_data['sp'], alpha=None, beta=None, surcharge=None,
    )
    pricing_data_preparer.set_trip_information(time=49 * 60, distance=1000)
    pricing_data_preparer.set_meta('min_price', pdp_data['min_price'])
    config.set_values(config_values)
    discounts.set_discount_response(COMMON_DISCOUNTS_RESPONSE)
    offer_prices[0]['using_new_pricing'] = True
    offer_prices[0]['pricing_data'] = pricing_data_preparer.get_pricing_data()
    cost_breakdown = filter_pdp_cost_breakdown(cost_breakdown)
    details_tariff = filter_pdp_details_tariff(details_tariff)

    request_body = {
        'user': {
            'phone': phone,
            'personal_phone_id': personal_phone_id,
            'user_id': user_id,
        },
        'requirements': {'nosmoking': True},
        'route': [
            [37.1946401739712, 55.478983901730004],
            [37.565210, 55.734434],
        ],
        'selected_class': taxi_class,
        'chainid': 'chainid_1',
    }
    if payment is not None:
        request_body['payment'] = payment

    response = taxi_integration.post(
        'v1/orders/estimate', json=request_body, headers=CC_HEADERS,
    )
    assert response.status_code == 200, response.text

    es_utils.check_response(
        response.json(),
        db,
        user_id,
        offer_prices,
        CALLCENTER_PRICE_MODIFIERS,
        taxi_class,
        cost_breakdown,
        details_tariff,
        price,
        price_with_currency,
        time,
    )


TEST_REQUEST_BODY = {
    'user': {
        'phone': '+79061112255',
        'personal_phone_id': 'p00000000000000000000005',
        'user_id': 'a5607fc6e79e4562b4f0af20a8e877a4',
        'yandex_uid': '480301451',
    },
    'payment': {'type': 'cash'},
    'requirements': {'nosmoking': True},
    'route': [[37.1946401739712, 55.478983901730004], [37.565210, 55.734434]],
    'selected_class': 'econom',
    'sourceid': 'alice',
}


@pytest.mark.parametrize(
    'sourceid,expected_status',
    [('wizard', 200), ('maps_app', 200), ('maps_web', 200), ('bream', 400)],
)
def test_source_is_available(
        taxi_integration,
        test_fixture_surge,
        test_fixtures,
        sourceid,
        expected_status,
        config,
        db,
        pricing_data_preparer,
):
    pricing_data_preparer.set_strikeout(100)
    request_body = copy.deepcopy(TEST_REQUEST_BODY)
    del request_body['user']['user_id']
    request_body['sourceid'] = sourceid

    before_users_count = db.users.count()

    response = taxi_integration.post('v1/orders/estimate', json=request_body)
    assert response.status_code == expected_status

    if response.status_code == 200:
        assert db.users.count() == before_users_count + 1


def test_alice_class_not_allowed(taxi_integration, config, db):
    request_body = copy.deepcopy(TEST_REQUEST_BODY)
    request_body['selected_class'] = 'express'

    expected_error = {'error': {'text': 'class is not enabled for alice'}}
    response = taxi_integration.post('v1/orders/estimate', json=request_body)
    assert response.status_code == 400, response.text
    assert response.json() == expected_error, response.text


CALLCENTER_REQUEST = {
    'user': {
        'phone': '+79061112255',
        'personal_phone_id': 'p00000000000000000000005',
        'user_id': 'e4707fc6e79e4562b4f0af20a8e877a3',
        'yandex_uid': '480301451',
    },
    'payment': {'type': 'cash'},
    'requirements': {'nosmoking': True},
    'route': [[37.1946401739712, 55.478983901730004], [37.565210, 55.734434]],
    'selected_class': 'econom',
}


CALLCENTER_WITH_CORP_REQUEST = {
    'user': {
        'phone': '+79061112255',
        'personal_phone_id': 'p00000000000000000000005',
        'user_id': 'e4707fc6e79e4562b4f0af20a8e877a3',
        'yandex_uid': '480301451',
    },
    'payment': {'type': 'corp', 'payment_method_id': 'corp-1234'},
    'requirements': {'nosmoking': True},
    'route': [[37.1946401739712, 55.478983901730004], [37.565210, 55.734434]],
    'selected_class': 'econom',
}


@pytest.mark.config(ALL_CATEGORIES=['econom'])
@pytest.mark.parametrize('tariffs_enabled', [False, True])
@pytest.mark.now('2018-04-24T15:15:00+0000')
@pytest.mark.user_experiments('fixed_price', 'use_discounts_service')
def test_new_tariff_categories(
        taxi_integration,
        test_fixture_surge,
        test_fixtures,
        config,
        discounts,
        tariffs_enabled,
        pricing_data_preparer,
):
    pricing_data_preparer.set_strikeout(1097)
    pricing_data_preparer.set_cost(830, 830)
    pricing_data_preparer.set_trip_information(time=49 * 60, distance=1000)
    pricing_data_preparer.set_meta('min_price', 101)
    config.set_values(dict(INTEGRATION_TARIFFS_ENABLED=tariffs_enabled))

    discounts.set_discount_response(
        {
            'discounts': [
                {
                    'class': 'econom',
                    'discount': {
                        'value': 0.11,
                        'price': 100,
                        'id': 'a122c228ba2b4d3189971a430ca6d2d3',
                        'reason': 'for_all',
                        'method': 'full-driver-less',
                    },
                },
            ],
            'discount_offer_id': '123456',
        },
    )

    response = taxi_integration.post(
        'v1/orders/estimate', json=CALLCENTER_REQUEST, headers=CC_HEADERS,
    )
    assert response.status_code == 200, response.text

    response_body = response.json()
    service_levels = response_body['service_levels']
    response_cost_breakdown = service_levels[0]['cost_message_details'][
        'cost_breakdown'
    ]
    cost_breakdown = CALLCENTER_COST_830_BREAKDOWN
    details_tariff = DETAILS_APPLICATION_CATEGORY_CALLCENTER_SOURCE
    cost_breakdown = filter_pdp_cost_breakdown(cost_breakdown)
    details_tariff = filter_pdp_details_tariff(details_tariff)
    ordered_object.assert_eq(response_cost_breakdown, cost_breakdown, [''])
    assert service_levels[0]['details_tariff'] == details_tariff


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'business', 'comfortplus', 'vip'],
)
@pytest.mark.now('2018-04-24T15:15:00+0000')
@pytest.mark.user_experiments('fixed_price', 'use_discounts_service')
def test_my_test(
        taxi_integration,
        test_fixture_surge,
        test_fixtures,
        pricing_data_preparer,
):
    pricing_data_preparer.set_fixed_price(False)
    pricing_data_preparer.set_meta('yaplus_delta_raw', 17.1)
    pricing_data_preparer.set_strikeout(300)
    pricing_data_preparer.set_cost(300, 300)
    pricing_data_preparer.set_meta('min_price', 100)
    pricing_data_preparer.set_categories(['econom'])

    response = taxi_integration.post(
        'v1/orders/estimate',
        json={
            'user': {
                'personal_phone_id': 'p00000000000000000000008',
                'phone': '+79061112288',
                'user_id': 'e4707fc6e79e4562b4f0af20a8e877a8',
            },
            'payment': {'type': 'corp', 'payment_method_id': 'corp-1234'},
            'route': [[37.1946401739712, 55.478983901730004]],
            'selected_class': 'econom',
            'sourceid': 'corp_cabinet',
        },
    )
    assert response.status_code == 200, response.text

    response_body = response.json()
    service_levels = response_body['service_levels']
    response_cost_breakdown_names = [
        item['display_name']
        for item in service_levels[0]['cost_message_details']['cost_breakdown']
    ]
    assert len(response_cost_breakdown_names) <= 1
    assert 'cost_without_discount' not in response_cost_breakdown_names
    assert 'discount' not in response_cost_breakdown_names
    assert 'total_discount' not in response_cost_breakdown_names
    assert 'ya_plus_discount' not in response_cost_breakdown_names


@pytest.mark.config(
    ALL_CATEGORIES=['child_tariff'],
    APPLICATION_BRAND_CATEGORIES_SETS={'__default__': ['child_tariff']},
    ROUTER_MAPS_ENABLED=True,
)
@pytest.mark.parametrize(
    'locale,drivers,service_level,currency_text',
    [
        (
            'ru',
            None,
            [
                {
                    'details_tariff': RESPONSE_DETAILS_TARIFF_CHILD_RU_SURGE,
                    'estimated_waiting': {'message': 'Мало свободных машин'},
                    'class': 'child_tariff',
                    'cost_message_details': {
                        'cost_breakdown': [
                            {
                                'display_amount': 'Поездка 1212 руб., ~49 мин',
                                'display_name': 'cost',
                            },
                            {
                                'display_amount': '1426 руб.',
                                'display_name': 'cost_without_discount',
                            },
                            {
                                'display_amount': '15%',
                                'display_name': 'discount',
                            },
                            {
                                'display_amount': '15%',
                                'display_name': 'total_discount',
                            },
                            {
                                'display_amount': '15%',
                                'display_name': 'call_center_discount',
                            },
                        ],
                    },
                    'price': '1212 руб.',
                    'price_raw': 1212,
                    'time': '49 мин',
                    'time_raw': 49,
                    'fare_disclaimer': 'Высокий спрос',
                    'is_fixed_price': True,
                },
            ],
            'руб.',
        ),
        (
            'en',
            None,
            [
                {
                    'details_tariff': RESPONSE_DETAILS_TARIFF_CHILD_EN_SURGE,
                    'estimated_waiting': {
                        'message': 'Not enough cars available',
                    },
                    'class': 'child_tariff',
                    'cost_message_details': {
                        'cost_breakdown': [
                            {
                                'display_amount': 'Ride 1,212 rub, ~49 min',
                                'display_name': 'cost',
                            },
                            {
                                'display_amount': '1,426 rub',
                                'display_name': 'cost_without_discount',
                            },
                            {
                                'display_amount': '15%',
                                'display_name': 'discount',
                            },
                            {
                                'display_amount': '15%',
                                'display_name': 'total_discount',
                            },
                            {
                                'display_amount': '15%',
                                'display_name': 'call_center_discount',
                            },
                        ],
                    },
                    'price': '1,212 rub',
                    'price_raw': 1212,
                    'time': '49 min',
                    'time_raw': 49,
                    'fare_disclaimer': 'High demand',
                    'is_fixed_price': True,
                },
            ],
            'rub',
        ),
        (
            'en',
            'nearest_drivers_near.json',
            [
                {
                    'details_tariff': RESPONSE_DETAILS_TARIFF_CHILD_EN_SURGE,
                    'estimated_waiting': {'seconds': 33, 'message': '1 min'},
                    'class': 'child_tariff',
                    'cost_message_details': {
                        'cost_breakdown': [
                            {
                                'display_amount': 'Ride 1,212 rub, ~49 min',
                                'display_name': 'cost',
                            },
                            {
                                'display_amount': '1,426 rub',
                                'display_name': 'cost_without_discount',
                            },
                            {
                                'display_amount': '15%',
                                'display_name': 'discount',
                            },
                            {
                                'display_amount': '15%',
                                'display_name': 'total_discount',
                            },
                            {
                                'display_amount': '15%',
                                'display_name': 'call_center_discount',
                            },
                        ],
                    },
                    'price': '1,212 rub',
                    'price_raw': 1212,
                    'time': '49 min',
                    'time_raw': 49,
                    'fare_disclaimer': 'High demand',
                    'is_fixed_price': True,
                },
            ],
            'rub',
        ),
    ],
    ids=['no drivers ru', 'no drivers en', 'estimated time less than 1 min'],
)
@pytest.mark.user_experiments('fixed_price')
@ORDER_OFFERS_SAVE_SWITCH
def test_no_drivers(
        taxi_integration,
        locale,
        drivers,
        service_level,
        currency_text,
        db,
        test_fixture_surge,
        test_fixtures,
        mockserver,
        load_json,
        pricing_data_preparer,
        mock_order_offers,
        order_offers_save_enabled,
):
    pricing_data_preparer.set_strikeout(1426)
    pricing_data_preparer.set_locale(locale[:2])
    pricing_data_preparer.set_cost(1212, 1212)
    pricing_data_preparer.set_meta('min_price', 131)
    pricing_data_preparer.set_trip_information(time=49 * 60, distance=1000)
    pricing_data_preparer.set_user_surge(3)

    service_level = copy.deepcopy(service_level)
    service_level[0]['cost_message_details']['cost_breakdown'] = (
        filter_pdp_cost_breakdown(
            service_level[0]['cost_message_details']['cost_breakdown'],
        )
    )
    service_level[0]['details_tariff'] = filter_pdp_details_tariff(
        service_level[0]['details_tariff'],
    )

    @mockserver.json_handler('/driver-eta/eta')
    def mock_eta_drivers(request):
        if drivers is None:
            return load_json('eta_response_no_drivers.json')
        response = load_json('eta_response.json')
        for v in response['classes'].values():
            v['estimated_time'] = 33
        return response

    request_body = copy.deepcopy(CALLCENTER_REQUEST)
    request_body['selected_class'] = 'child_tariff'

    response = taxi_integration.post(
        'v1/orders/estimate',
        json=request_body,
        headers={'Accept-Language': locale, 'User-Agent': 'call_center'},
    )
    assert response.status_code == 200, response.text

    response_body = response.json()
    assert response_body['user_id'] == 'e4707fc6e79e4562b4f0af20a8e877a3'

    assert 'offer' in response_body
    offer = rs_utils.get_user_offer(
        response_body['offer'],
        response_body['user_id'],
        db,
        mock_order_offers,
        order_offers_save_enabled,
    )
    assert offer is not None

    assert response_body['is_fixed_price'] is True

    response_service_levels = response_body['service_levels']
    ordered_object.assert_eq(
        response_service_levels,
        service_level,
        ['cost_message_details.cost_breakdown'],
    )
    currency_rules = response_body['currency_rules']
    assert currency_rules['code'] == 'RUB'
    assert currency_rules['sign'] == ''
    assert currency_rules['template'] == '$VALUE$ $SIGN$$CURRENCY$'
    assert currency_rules['text'] == currency_text


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'child_tariff'],
    },
)
@pytest.mark.now('2018-04-24T08:15:00+0000')
@pytest.mark.user_experiments('fixed_price')
@ORDER_OFFERS_SAVE_SWITCH
@PROTOCOL_SWITCH_TO_REPLICA_DBUSERS
def test_no_destination(
        taxi_integration,
        db,
        test_fixture_surge,
        test_fixtures,
        testpoint,
        pricing_data_preparer,
        mock_order_offers,
        order_offers_save_enabled,
        read_from_replica_dbusers,
):
    pricing_data_preparer.set_strikeout(132)
    pricing_data_preparer.set_no_trip_information()
    pricing_data_preparer.set_fixed_price(False)
    pricing_data_preparer.set_meta('min_price', 111)
    pricing_data_preparer.set_cost(112, 112)
    pricing_data_preparer.set_user_surge(
        sp=1.0, alpha=None, beta=None, surcharge=None,
    )
    pricing_data_preparer.set_user_category_prices_id(
        'c/b7c4d5f6aa3b40a3807bb74b3bc042a3',
    )
    pricing_data_preparer.set_categories(['econom'])
    pricing_data_preparer.set_tariff_info(
        included_minutes=5,
        included_kilometers=2,
        price_per_minute=9,
        price_per_kilometer=9,
    )

    @testpoint('orderkit::GetUserById')
    def replica_dbusers_test_point(data):
        assert read_from_replica_dbusers == data['replica']

    user_id = 'e4707fc6e79e4562b4f0af20a8e877a3'
    payment = {'type': 'corp', 'payment_method_id': 'corp-1234'}
    request_body = {
        'user': {
            'phone': '+79061112255',
            'personal_phone_id': 'p00000000000000000000005',
            'user_id': user_id,
        },
        'requirements': {'nosmoking': True},
        'route': [[37.1946401739712, 55.478983901730004]],
        'selected_class': 'econom',
        'chainid': 'chainid_1',
        'payment': payment,
    }

    response = taxi_integration.post(
        'v1/orders/estimate', json=request_body, headers=CC_HEADERS,
    )
    assert response.status_code == 200
    assert replica_dbusers_test_point.times_called == 1

    content = response.json()
    offer_id = content.pop('offer')
    assert type(offer_id) is str
    assert len(offer_id) > 0
    assert content == {
        'currency_rules': {
            'code': 'RUB',
            'sign': '',
            'template': '$VALUE$ $SIGN$$CURRENCY$',
            'text': 'rub',
        },
        'is_fixed_price': False,
        'service_levels': [
            {
                'class': 'econom',
                'cost_message_details': {
                    'cost_breakdown': [
                        {
                            'display_amount': '132 rub',
                            'display_name': 'cost_without_discount',
                        },
                        {'display_amount': '15%', 'display_name': 'discount'},
                        {
                            'display_amount': '15%',
                            'display_name': 'total_discount',
                        },
                    ],
                },
                'details_tariff': [{'type': 'price', 'value': 'from 111 rub'}],
                'estimated_waiting': {'message': '14 min', 'seconds': 839},
                'price': '111 rub for the first 5 min and 2 km',
                'min_price': 111.0,
                'is_fixed_price': False,
            },
        ],
        'user_id': user_id,
    }

    offer = rs_utils.get_user_offer(
        offer_id, user_id, db, mock_order_offers, order_offers_save_enabled,
    )
    if order_offers_save_enabled:
        assert mock_order_offers.mock_save_offer.times_called == 1
    assert offer is not None

    offer.pop('routestats_link')
    offer.pop('routestats_type')
    offer.pop('_shard_id')
    assert offer == {
        '_id': offer_id,
        'authorized': True,
        'created': datetime.datetime(2018, 4, 24, 8, 15),
        'destination_is_airport': False,
        'distance': 0.0,
        'due': datetime.datetime(2018, 4, 24, 8, 25),
        'is_fixed_price': False,
        'payment_type': payment['type'],
        'price_modifiers': {
            'items': [
                {
                    'pay_subventions': False,
                    'reason': 'call_center',
                    'tariff_categories': ['econom', 'child_tariff'],
                    'type': 'multiplier',
                    'value': '1.020000',
                },
            ],
        },
        'prices': [
            {
                'cat_type': 'call_center',
                'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042a3',
                'cls': 'econom',
                'driver_price': 112.0,
                'price': 112.0,
                'sp': 1.0,
                'is_fixed_price': False,
                'using_new_pricing': True,
                'pricing_data': pricing_data_preparer.get_pricing_data(),
            },
        ],
        'classes_requirements': {
            'econom': {'nosmoking': True},
            'child_tariff': {'nosmoking': True},
        },
        'route': [[37.1946401739712, 55.478983901730004]],
        'time': 0.0,
        'user_id': user_id,
        'user_phone_id': bson.ObjectId('5a7b678babae14bb0db4453f'),
    }


@pytest.mark.config(
    ALL_CATEGORIES=['econom'],
    INTEGRATION_TARIFFS_ENABLED=False,
    ROUTER_MAPS_ENABLED=True,
)
@pytest.mark.user_experiments('fixed_price')
@ORDER_OFFERS_SAVE_SWITCH
def test_cant_construct_route(
        taxi_integration,
        db,
        test_fixture_surge,
        test_fixtures,
        mockserver,
        load_binary,
        pricing_data_preparer,
        mock_order_offers,
        order_offers_save_enabled,
):
    pricing_data_preparer.set_strikeout(118)
    pricing_data_preparer.set_meta('min_price', 101)
    pricing_data_preparer.set_fixed_price(False)
    pricing_data_preparer.set_no_trip_information()
    pricing_data_preparer.set_tariff_info(
        included_minutes=5,
        included_kilometers=2,
        price_per_minute=9,
        price_per_kilometer=9,
    )

    @mockserver.json_handler('/maps-router/route_jams/')
    def mock_yamaps_router(request):
        def response_generator():
            yield mockserver.make_response(
                load_binary('yamaps_response_2.protobuf'),
                content_type='application/x-protobuf',
            )
            while True:
                yield mockserver.make_response('', 404)

        if not hasattr(mock_yamaps_router, 'generator'):
            mock_yamaps_router.generator = response_generator()
        return next(mock_yamaps_router.generator)

    response = taxi_integration.post(
        'v1/orders/estimate', json=CALLCENTER_REQUEST, headers=CC_HEADERS,
    )

    assert response.status_code == 200
    content = response.json()
    offer_id = content.pop('offer')
    assert type(offer_id) is str
    assert len(offer_id) > 0
    assert content == {
        'alert': {
            'description': (
                'Impossible to build route. '
                'You can change destination point or '
                'ride without destination point by tariff '
                '101 rub for the first 5 min and 2 km'
            ),
            'code': 'CANT_CONSTRUCT_ROUTE',
        },
        'currency_rules': {
            'code': 'RUB',
            'sign': '',
            'template': '$VALUE$ $SIGN$$CURRENCY$',
            'text': 'rub',
        },
        'is_fixed_price': False,
        'service_levels': [
            {
                'class': 'econom',
                'cost_message_details': {
                    'cost_breakdown': [
                        {
                            'display_amount': '118 rub',
                            'display_name': 'cost_without_discount',
                        },
                        {'display_amount': '15%', 'display_name': 'discount'},
                        {
                            'display_amount': '15%',
                            'display_name': 'total_discount',
                        },
                    ],
                },
                'details_tariff': [{'type': 'price', 'value': 'from 101 rub'}],
                'estimated_waiting': {'message': '14 min', 'seconds': 839},
                'price': '101 rub for the first 5 min and 2 km',
                'min_price': 101.0,
                'is_fixed_price': False,
            },
        ],
        'user_id': 'e4707fc6e79e4562b4f0af20a8e877a3',
    }

    # offer created
    offer = rs_utils.get_offer(
        offer_id, db, mock_order_offers, order_offers_save_enabled,
    )
    assert CALLCENTER_REQUEST['route'] == offer['route']


@pytest.mark.config(ALL_CATEGORIES=['econom'])
@pytest.mark.parametrize(
    'phone,personal_phone_id,expected_user_id,route,'
    'category_prices_id,expected_code',
    [
        (
            '+79061112233',
            'p00000000000000000000003',
            None,
            [[37.411956, 55.981682], [37.907173584260395, 55.90891808601154]],
            'c/00000000000000000000000000000002/moscow/svo',
            200,
        ),
        (
            '+79061112244',
            'p00000000000000000000004',
            None,
            [[37.411956, 55.981682], [37.907173584260395, 55.90891808601154]],
            'c/00000000000000000000000000000002/moscow/svo',
            200,
        ),
        (
            '+79061112277',
            'p00000000000000000000007',
            None,
            [[37.411956, 55.981682], [37.907173584260395, 55.90891808601154]],
            'c/00000000000000000000000000000002/moscow/svo',
            200,
        ),
        (
            '+79061112255',
            'p00000000000000000000005',
            'e4707fc6e79e4562b4f0af20a8e877a6',
            [[37.411956, 55.981682], [37.907173584260395, 55.90891808601154]],
            'c/00000000000000000000000000000002/moscow/svo',
            200,
        ),
        (
            '+79061112255',
            'p00000000000000000000005',
            None,
            [[37.411956, 55.981682]],
            'c/00000000000000000000000000000003',
            400,
        ),
        (
            '+79061112255',
            'p00000000000000000000005',
            None,
            [[37.411956, 55.981682], [37.70, 55.80]],
            'c/00000000000000000000000000000003',
            400,
        ),
        (
            '+79061112255',
            'p00000000000000000000005',
            None,
            [[37.1946401739712, 55.478983901730004], [37.565210, 55.734434]],
            'c/00000000000000000000000000000002/moscow/svo',
            400,
        ),
    ],
    ids=[
        'no phone, no user',
        'have phone, no user',
        'unauthorized',
        'correct route',
        'without destination',
        'not transfer',
        'point A is not airport',
    ],
)
@pytest.mark.user_experiments('fixed_price')
@pytest.mark.now('2018-04-24T10:15:00+0000')
def test_svo_estimate(
        taxi_integration,
        mockserver,
        load_json,
        db,
        phone,
        personal_phone_id,
        expected_user_id,
        test_fixture_surge,
        test_fixtures,
        route,
        category_prices_id,
        expected_code,
        pricing_data_preparer,
):
    pricing_data_preparer.set_strikeout(1358)
    pricing_data_preparer.set_fixed_price(False)
    pricing_data_preparer.set_cost(1358, 1358)
    pricing_data_preparer.set_trip_information(time=49 * 60, distance=10000)
    pricing_data_preparer.set_user_category_prices_id(category_prices_id)
    pricing_data_preparer.set_driver_category_prices_id(category_prices_id)

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_getsurge(request):
        input_json = json.loads(request.get_data())
        mocks = {'econom': 'get_surge_econom_svo.json'}
        key = '+'.join(sorted(input_json['classes']))
        assert key in mocks
        return load_json(mocks[key])

    request_body = {
        'user': {'phone': phone, 'personal_phone_id': personal_phone_id},
        'requirements': {},
        'route': route,
        'selected_class': 'econom',
        'sourceid': 'svo_order',
        'chainid': 'chainid_1',
    }
    response = taxi_integration.post('v1/orders/estimate', json=request_body)
    assert response.status_code == expected_code

    if response.status_code == 200:
        response_body = response.json()
        if expected_user_id:
            assert expected_user_id == response_body['user_id']

        assert (
            db.users.count(
                {'_id': response_body['user_id'], 'sourceid': 'svo_order'},
            )
            == 1
        )

        assert 'offer' in response_body
        assert response_body['valid_until'] == '2018-04-24T10:30:00+0000'

        offer = rs_utils.get_user_offer(
            response_body['offer'], response_body['user_id'], db,
        )
        assert offer is not None

        assert response_body['is_fixed_price'] is False

        currency_rules = response_body['currency_rules']
        assert currency_rules['code'] == 'RUB'
        assert currency_rules['sign'] == ''
        assert currency_rules['template'] == '$VALUE$ $SIGN$$CURRENCY$'
        assert currency_rules['text'] == 'rub'

        service_levels = response_body['service_levels']
        assert service_levels[0]['class'] == 'econom'
        assert service_levels[0]['price'] == '1,358 rub'
        assert service_levels[0]['time'] == '49 min'
        assert service_levels[0]['estimated_waiting']['message'] == '0 min'
        assert service_levels[0]['estimated_waiting']['seconds'] == 0
        assert service_levels[0]['cost_message_details']['cost_breakdown'] == (
            [
                {
                    'display_amount': 'Ride 1,358 rub, ~49 min',
                    'display_name': 'cost',
                },
            ]
        )


AIRPORT_NOT_TRANSFER_ROUTE = [[37.411956, 55.981682], [37.70, 55.80]]
NOT_AIRPORT_NOT_TRANSFER = [
    [37.1946401739712, 55.478983901730004],
    [37.565210, 55.734434],
]
NOT_AIRPORT_TRANSFER = [
    [37.907173584260395, 55.90891808601154],
    [37.411956, 55.981682],
]
TRANSFER_CATEGORY_PRICES_ID = 'c/00000000000000000000000000000002/moscow/svo'
NOT_TRANSFER_CATEGORY_PRICES_ID = 'c/00000000000000000000000000000003'


@pytest.mark.parametrize(
    'check_source_is_airport,check_route_is_transfer,route,'
    'category_prices_id,expected_code,expected_error',
    [
        (
            False,
            False,
            AIRPORT_NOT_TRANSFER_ROUTE,
            NOT_TRANSFER_CATEGORY_PRICES_ID,
            200,
            None,
        ),
        (
            True,
            False,
            AIRPORT_NOT_TRANSFER_ROUTE,
            NOT_TRANSFER_CATEGORY_PRICES_ID,
            200,
            None,
        ),
        (
            True,
            True,
            AIRPORT_NOT_TRANSFER_ROUTE,
            NOT_TRANSFER_CATEGORY_PRICES_ID,
            400,
            'it is not transfer',
        ),
        (
            False,
            False,
            NOT_AIRPORT_NOT_TRANSFER,
            NOT_TRANSFER_CATEGORY_PRICES_ID,
            200,
            None,
        ),
        (
            False,
            True,
            NOT_AIRPORT_NOT_TRANSFER,
            NOT_TRANSFER_CATEGORY_PRICES_ID,
            400,
            'it is not transfer',
        ),
        (
            True,
            False,
            NOT_AIRPORT_NOT_TRANSFER,
            NOT_TRANSFER_CATEGORY_PRICES_ID,
            400,
            'source is not airport',
        ),
        (
            False,
            False,
            NOT_AIRPORT_TRANSFER,
            TRANSFER_CATEGORY_PRICES_ID,
            200,
            None,
        ),
        (
            False,
            True,
            NOT_AIRPORT_TRANSFER,
            TRANSFER_CATEGORY_PRICES_ID,
            200,
            None,
        ),
        (
            True,
            False,
            NOT_AIRPORT_TRANSFER,
            TRANSFER_CATEGORY_PRICES_ID,
            400,
            'source is not airport',
        ),
    ],
)
@pytest.mark.user_experiments('fixed_price')
@pytest.mark.now('2018-04-24T10:15:00+0000')
def test_svo_route_checks(
        taxi_integration,
        config,
        now,
        test_fixture_surge,
        test_fixtures,
        check_source_is_airport,
        check_route_is_transfer,
        route,
        category_prices_id,
        expected_code,
        expected_error,
        pricing_data_preparer,
):
    pricing_data_preparer.set_strikeout(100)
    pricing_data_preparer.set_user_category_prices_id(category_prices_id)
    pricing_data_preparer.set_driver_category_prices_id(category_prices_id)
    config.set_values(
        dict(
            SVO_ROUTE_CHECKS={
                '__default__': {
                    'check_route_is_transfer': check_route_is_transfer,
                    'check_source_is_airport': check_source_is_airport,
                },
            },
            ALL_CATEGORIES=['econom'],
        ),
    )
    taxi_integration.tests_control(now=now, invalidate_caches=True)

    request_body = {
        'user': {
            'phone': '+79061112255',
            'personal_phone_id': 'p00000000000000000000005',
        },
        'requirements': {},
        'route': route,
        'selected_class': 'econom',
        'sourceid': 'svo_order',
        'chainid': 'chainid_1',
    }
    response = taxi_integration.post('v1/orders/estimate', json=request_body)
    assert response.status_code == expected_code
    if expected_error:
        assert response.json()['error']['text'] == expected_error


@pytest.mark.config(ALL_CATEGORIES=['econom', 'child_tariff'])
@pytest.mark.parametrize(
    'phone,personal_phone_id,user_id,sourceid,headers',
    [
        (
            '+79061112233',
            'p00000000000000000000003',
            'e4707fc6e79e4562b4f0af20a8e877a3',
            None,
            CC_HEADERS,
        ),
        (
            '+79061112233',
            'p00000000000000000000003',
            'a5607fc6e79e4562b4f0af20a8e877a4',
            'alice',
            {},
        ),
    ],
    ids=['call center', 'alice'],
)
@pytest.mark.now('2018-04-24T08:15:00+0000')
def test_user_mismatch(
        taxi_integration,
        db,
        test_fixture_surge,
        test_fixtures,
        phone,
        personal_phone_id,
        user_id,
        sourceid,
        headers,
        pricing_data_preparer,
):
    pricing_data_preparer.set_strikeout(100)
    """
    For 'call_center' && 'alice' user should be created in v1/profile.
    In this case phone data in request should match
    founded phone data from db.users,
    (if config INTEGRATION_USER_CONSISTENCY_CHECK is active).

    Test checks return 400, when phone data doesn't match

    We find user by user_id from request if it's present.
    """
    request_body = {
        'user': {
            'phone': phone,
            'personal_phone_id': personal_phone_id,
            'user_id': user_id,
        },
        'requirements': {'nosmoking': True},
        'route': [[37.194640, 55.478983], [37.565210, 55.734434]],
        'selected_class': 'econom',
        'chainid': 'chainid_1',
    }
    if sourceid:
        request_body['sourceid'] = sourceid

    if sourceid == 'alice':
        request_body['user'].update({'yandex_uid': '480301451'})

    response = taxi_integration.post(
        'v1/orders/estimate', json=request_body, headers=headers,
    )
    assert response.status_code == 400, response
    data = response.json()
    assert data == {
        'error': {
            'text': (
                'user personal_phone_id doesn\'t match request '
                'personal_phone_id'
            ),
        },
    }


@pytest.mark.config(
    INTEGRATION_SUPPORTED_APPLICATIONS=['valid_app'],
    APPLICATION_DETECTION_RULES_NEW={
        'rules': [
            {'match': 'valid_app', '@app_name': 'valid_app', '@app_ver1': '2'},
            {'@app_name': 'foolish', '@app_ver1': '2'},
        ],
    },
)
@pytest.mark.config(ALL_CATEGORIES=['econom', 'child_tariff'])
@pytest.mark.parametrize(
    'sourceid,application,code,category_prices_id',
    [
        ('corp_cabinet', 'corpweb', 200, NOT_TRANSFER_CATEGORY_PRICES_ID),
        ('svo_order', 'call_center', 200, TRANSFER_CATEGORY_PRICES_ID),
        (None, 'valid_app', 200, NOT_TRANSFER_CATEGORY_PRICES_ID),
        (None, 'bad_app', 400, NOT_TRANSFER_CATEGORY_PRICES_ID),
        ('uber', 'uber', 400, NOT_TRANSFER_CATEGORY_PRICES_ID),
        ('wrong', 'wrong', 400, NOT_TRANSFER_CATEGORY_PRICES_ID),
    ],
)
@pytest.mark.now('2018-07-20T10:15:00+0000')
def test_create_user(
        taxi_integration,
        db,
        test_fixture_surge,
        test_fixtures,
        sourceid,
        application,
        code,
        category_prices_id,
        pricing_data_preparer,
):
    pricing_data_preparer.set_strikeout(100)
    pricing_data_preparer.set_user_category_prices_id(category_prices_id)
    pricing_data_preparer.set_driver_category_prices_id(category_prices_id)
    db.users.remove()
    db.user_phones.remove()
    request_body = {
        'user': {
            'phone': '+79061112200',
            'personal_phone_id': 'p00000000000000000000000',
        },
        'requirements': {'nosmoking': True},
        'route': [
            [37.411956, 55.981682],
            [37.907173584260395, 55.90891808601154],
        ],
        'selected_class': 'econom',
        'sourceid': sourceid,
        'chainid': 'chainid_1',
    }
    if sourceid == 'alice':
        request_body['user']['yandex_uid'] = '480301451'

    headers = {}
    if not sourceid:
        headers = {'User-Agent': application}
    response = taxi_integration.post(
        'v1/orders/estimate', json=request_body, headers=headers,
    )
    assert response.status_code == code, response
    data = response.json()

    if code == 200:
        assert data is not None
        response_user_id = data['user_id']
        user_doc = db.users.find_one({'_id': response_user_id})
        assert user_doc['sourceid'] == sourceid or application
        assert user_doc['application'] == application
    elif code == 400:
        text = 'source_id invalid'
        if not sourceid:
            text = 'Invalid application'
        assert data == {'error': {'text': text}}
    else:
        assert False


@pytest.mark.config(
    INTEGRATION_SUPPORTED_APPLICATIONS=['valid_app'],
    APPLICATION_DETECTION_RULES_NEW={
        'rules': [
            {'match': 'valid_app', '@app_name': 'valid_app', '@app_ver1': '2'},
            {'@app_name': 'corpapi', 'header': 'X-Taxi', 'match': 'corpapi'},
            {'@app_name': 'corpweb', 'header': 'X-Taxi', 'match': 'corpweb'},
            {'@app_name': 'foolish', '@app_ver1': '2'},
        ],
    },
)
@pytest.mark.config(ALL_CATEGORIES=['econom', 'child_tariff'])
@pytest.mark.parametrize('x_taxi', ['corpweb', 'corpapi'])
@pytest.mark.parametrize(
    'phone,clean_phone,phone_format_ok',
    [
        ('+7 (906) 111 22 00', '+79061112200', True),
        ('8 906 1112200', '+79061112200', True),
        ('+11111', '+11111', True),
        ('+111111111111111111111111111111111111', None, False),
    ],
)
@pytest.mark.now('2018-07-20T10:15:00+0000')
def test_create_corp_user(
        taxi_integration,
        db,
        test_fixture_surge,
        test_fixtures,
        x_taxi,
        phone,
        clean_phone,
        phone_format_ok,
        pricing_data_preparer,
):
    pricing_data_preparer.set_strikeout(100)
    db.users.remove()
    db.user_phones.remove()
    request_body = {
        'user': {'phone': phone},
        'requirements': {'nosmoking': True},
        'route': [
            [37.411956, 55.981682],
            [37.907173584260395, 55.90891808601154],
        ],
        'selected_class': 'econom',
        'sourceid': 'corp_cabinet',
        'chainid': 'chainid_1',
    }

    response = taxi_integration.post(
        'v1/orders/estimate', json=request_body, headers={'X-Taxi': x_taxi},
    )
    if phone_format_ok:
        assert response.status_code == 200, response
        data = response.json()

        assert data is not None
        response_user_id = data['user_id']
        user_doc = db.users.find_one({'_id': response_user_id})
        assert user_doc
        assert es_utils.PERSONAL_PHONES_DB[-1]['value'] == clean_phone
    else:
        assert response.status_code == 400, response
        data = response.json()
        assert data['error']['text'] == 'invalid phone number format'


@pytest.mark.config(ALL_CATEGORIES=['econom'])
@pytest.mark.parametrize(
    'zone_name,expected_cat',
    [
        (None, '45e0830b3929406497348b24b482d4ae'),  # from boryasvo tariff
        (
            'boryarst',
            '45e0830b3929406497348b24b482d444',  # from boryarst tariff
        ),
    ],
)
@pytest.mark.now('2018-07-20T10:15:00+0000')
def test_svo_zones(
        taxi_integration,
        db,
        test_fixture_surge,
        test_fixtures,
        zone_name,
        expected_cat,
        pricing_data_preparer,
):
    pricing_data_preparer.set_strikeout(100)
    pricing_data_preparer.set_user_category_prices_id(
        f'c/{expected_cat}/moscow/svo',
    )
    request_body = {
        'user': {
            'phone': '+79061112200',
            'personal_phone_id': 'p00000000000000000000000',
        },
        'requirements': {'nosmoking': True},
        'route': [
            [37.411956, 55.981682],
            [37.907173584260395, 55.90891808601154],
        ],
        'selected_class': 'econom',
        'sourceid': 'svo_order',
        'chainid': 'chainid_1',
        'zone_name': zone_name,
    }
    if zone_name:
        db.tariff_settings.update(
            {'hz': 'boryasvo'}, {'$set': {'hz': zone_name}},
        )

    response = taxi_integration.post('v1/orders/estimate', json=request_body)
    assert response.status_code == 200, response

    data = response.json()
    offer_id = data['offer']

    offer = rs_utils.get_offer(offer_id, db)
    assert offer['prices'][0]['category_id'] == expected_cat


def check_default_response(response_body, new_pricing_response=False):
    assert 'offer' not in response_body
    assert response_body['is_fixed_price'] is False

    currency_rules = response_body['currency_rules']
    assert currency_rules['code'] == 'RUB'
    assert currency_rules['sign'] == ''
    assert currency_rules['template'] == '$VALUE$ $SIGN$$CURRENCY$'
    assert currency_rules['text'] == 'rub'

    service_level = response_body['service_levels'][0]
    assert service_level['class'] == 'econom'
    response_cost_breakdown = service_level['cost_message_details'][
        'cost_breakdown'
    ]
    expected_cost_breakdown = [
        {'display_amount': 'Ride 915 rub, ~49 min', 'display_name': 'cost'},
    ]
    ordered_object.assert_eq(
        expected_cost_breakdown, response_cost_breakdown, [''],
    )
    assert service_level['price'] == '915 rub'
    assert service_level['time'] == '49 min'
    assert service_level['estimated_waiting']['message'] == '14 min'
    assert service_level['estimated_waiting']['seconds'] == 839
    if new_pricing_response:
        assert (
            service_level['details_tariff'] == DETAILS_NO_MODIFIERS_NEW_PRICING
        )
    else:
        assert service_level['details_tariff'] == DETAILS_NO_MODIFIERS


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff'],
    ROUTER_MAPS_ENABLED=True,
    INTEGRATION_API_PHONELESS_APPS=['corp_cabinet', 'wizard', 'no_phone_app'],
    INTEGRATION_SUPPORTED_APPLICATIONS=['no_phone_app', 'need_user_app'],
    APPLICATION_DETECTION_RULES_NEW={
        'rules': [
            {'match': 'no_phone_app', '@app_name': 'no_phone_app'},
            {'@app_name': 'need_user_app'},
        ],
    },
)
@pytest.mark.parametrize(
    'sourceid,headers,expected_status',
    [
        ('corp_cabinet', {}, 200),
        ('wizard', {}, 200),
        (None, {'User-Agent': 'no_phone_app'}, 200),
        (None, CC_HEADERS, 400),
    ],
    ids=[
        'no_user_allowed',
        'Wizard is allowed without the phone',
        'no_user_allowed_by_application',
        'no_user_not_allowed',
    ],
)
@pytest.mark.now('2018-04-24T08:15:00+0000')
def test_no_user(
        taxi_integration,
        test_fixture_surge,
        test_fixtures,
        sourceid,
        headers,
        expected_status,
        pricing_data_preparer,
):
    pricing_data_preparer.set_strikeout(100)
    pricing_data_preparer.set_cost(915, 915)
    pricing_data_preparer.set_trip_information(time=49 * 60, distance=1000)
    pricing_data_preparer.set_meta('min_price', 99)

    request_body = {
        'payment': {'type': 'corp'},
        'requirements': {'nosmoking': True},
        'route': [
            [37.1946401739712, 55.478983901730004],
            [37.565210, 55.734434],
        ],
        'selected_class': 'econom',
        'chainid': 'chainid_1',
    }
    if sourceid:
        request_body['sourceid'] = sourceid

    response = taxi_integration.post(
        'v1/orders/estimate', json=request_body, headers=headers,
    )
    assert response.status_code == expected_status

    response_body = response.json()
    if response.status_code == 200:
        check_default_response(response_body, True)
    elif response.status_code == 400:
        assert response_body == {'error': {'text': 'user not provided'}}


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff'],
    ROUTER_MAPS_ENABLED=True,
    INTEGRATION_API_PHONELESS_APPS=['corp_cabinet', 'wizard', 'no_user_app'],
    INTEGRATION_API_FIXPRICE_WO_USER_APPS=['no_user_app'],
    INTEGRATION_SUPPORTED_APPLICATIONS=['no_user_app'],
    APPLICATION_DETECTION_RULES_NEW={'rules': [{'@app_name': 'no_user_app'}]},
)
@pytest.mark.user_experiments('fixed_price')
@pytest.mark.now('2018-04-24T08:15:00+0000')
def test_fixprice_no_user(
        taxi_integration,
        test_fixture_surge,
        test_fixtures,
        pricing_data_preparer,
):
    pricing_data_preparer.set_strikeout(100)
    pricing_data_preparer.set_cost(915, 915)
    pricing_data_preparer.set_fixed_price(True)
    pricing_data_preparer.set_trip_information(time=49 * 60, distance=1000)
    pricing_data_preparer.set_meta('min_price', 99)

    request_body = {
        'payment': {'type': 'corp'},
        'requirements': {'nosmoking': True},
        'route': [
            [37.1946401739712, 55.478983901730004],
            [37.565210, 55.734434],
        ],
        'selected_class': 'econom',
        'chainid': 'chainid_1',
    }

    response = taxi_integration.post(
        'v1/orders/estimate',
        json=request_body,
        headers={'User-Agent': 'no_user_app'},
    )
    assert response.status_code == 200

    response_body = response.json()
    assert response_body['is_fixed_price'] is True
    assert 'offer' in response_body


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff'],
    ROUTER_MAPS_ENABLED=True,
    INTEGRATION_API_ALLOW_ZUSER_APPS=['light_business'],
)
@pytest.mark.parametrize(
    'sourceid,headers,expected_status',
    [('light_business', {}, 200), (None, CC_HEADERS, 400)],
    ids=['zuser_allowed', 'zuser_not_allowed'],
)
@pytest.mark.now('2018-04-24T08:15:00+0000')
def test_zuser(
        taxi_integration,
        test_fixture_surge,
        test_fixtures,
        sourceid,
        headers,
        expected_status,
        pricing_data_preparer,
):
    pricing_data_preparer.set_strikeout(100)
    pricing_data_preparer.set_cost(915, 915)
    pricing_data_preparer.set_trip_information(time=49 * 60, distance=1000)
    pricing_data_preparer.set_meta('min_price', 99)

    taxi_class = 'econom'
    request_body = {
        'payment': {'type': 'corp'},
        'requirements': {'nosmoking': True},
        'route': [
            [37.1946401739712, 55.478983901730004],
            [37.565210, 55.734434],
        ],
        'user': {'user_id': 'zuser'},
        'selected_class': taxi_class,
        'chainid': 'chainid_1',
    }
    if sourceid:
        request_body['sourceid'] = sourceid

    response = taxi_integration.post(
        'v1/orders/estimate', json=request_body, headers=headers,
    )
    assert response.status_code == expected_status

    response_body = response.json()
    if response.status_code == 200:
        check_default_response(response_body, True)
    elif response.status_code == 400:
        assert response_body == {'error': {'text': 'zuser not allowed'}}


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff'],
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=True,
    AFS_IS_SPAMER_ENABLED={
        '__default__': {'use_afs': False, 'timeout': 100, 'retries': 1},
        'orders_estimate': {'use_afs': True, 'timeout': 200, 'retries': 2},
    },
)
@pytest.mark.now('2018-11-20T11:00:00+0300')
@pytest.mark.parametrize(
    'time_offset,response_code',
    [(0, 403), (-1, 403), (60 * 60 * 4, 403), (None, 200)],
)
@pytest.mark.user_experiments('fixed_price')
def test_afs_is_spammer_checking(
        taxi_integration,
        test_fixture_surge,
        test_fixtures,
        mockserver,
        time_offset,
        now,
        response_code,
        pricing_data_preparer,
):
    pricing_data_preparer.set_strikeout(100)

    @mockserver.json_handler(
        '/antifraud/client/user/is_spammer/orders_estimate',
    )
    def mock_afs_is_spammer(request):
        data = json.loads(request.get_data())
        assert data == {
            'is_multiorder': False,
            'user_id': 'e4707fc6e79e4562b4f0af20a8e877a3',
            'user_phone_id': '5a7b678babae14bb0db4453f',
            'user_source_id': 'call_center',
        }
        return make_afs_is_spammer_response_builder(time_offset)(now)

    response = taxi_integration.post(
        'v1/orders/estimate',
        json=CALLCENTER_WITH_CORP_REQUEST,
        headers=CC_HEADERS,
    )

    assert response.status_code == response_code, response.text

    if response_code != 200:
        data = response.json()
        assert 'blocked' in data
        assert 'type' in data


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff'],
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=False,
    AFS_IS_SPAMER_ENABLED={
        '__default__': {'use_afs': False, 'timeout': 100, 'retries': 1},
        'orders_estimate': {'use_afs': True, 'timeout': 200, 'retries': 2},
    },
)
@pytest.mark.now('2018-11-20T11:00:00+0300')
@pytest.mark.parametrize('time_offset', [0, -1, 60 * 60 * 4, None])
@pytest.mark.user_experiments('fixed_price')
def test_afs_is_spammer_disabled_in_client(
        taxi_integration,
        test_fixture_surge,
        test_fixtures,
        mockserver,
        time_offset,
        now,
        pricing_data_preparer,
):
    pricing_data_preparer.set_strikeout(100)

    @mockserver.json_handler(
        '/antifraud/client/user/is_spammer/orders_estimate',
    )
    def mock_afs_is_spammer(request):
        data = json.loads(request.get_data())
        assert data == {
            'is_multiorder': False,
            'user_id': 'e4707fc6e79e4562b4f0af20a8e877a3',
            'user_phone_id': '5a7b678babae14bb0db4453f',
            'user_source_id': 'call_center',
        }
        return make_afs_is_spammer_response_builder(time_offset)(now)

    response = taxi_integration.post(
        'v1/orders/estimate',
        json=CALLCENTER_WITH_CORP_REQUEST,
        headers=CC_HEADERS,
    )

    assert response.status_code == 200, response.text


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff'],
    AFS_IS_SPAMMER_IN_CLIENT_ENABLED=True,
    AFS_IS_SPAMER_ENABLED={
        '__default__': {'use_afs': False, 'timeout': 100, 'retries': 1},
        'orders_estimate': {'use_afs': True, 'timeout': 200, 'retries': 2},
    },
)
@pytest.mark.parametrize('response_code', [500, 400, 403])
@pytest.mark.user_experiments('fixed_price')
def test_antifraud_affected(
        taxi_integration,
        test_fixture_surge,
        test_fixtures,
        mockserver,
        response_code,
        pricing_data_preparer,
):
    pricing_data_preparer.set_strikeout(100)

    @mockserver.handler('/antifraud/client/user/is_spammer/orders_estimate')
    def mock_detect_invalid(request):
        return mockserver.make_response(
            '{"code":' + str(response_code) + '}', response_code,
        )

    response = taxi_integration.post(
        'v1/orders/estimate',
        json=CALLCENTER_WITH_CORP_REQUEST,
        headers=CC_HEADERS,
    )

    assert response.status_code == 200


@pytest.mark.config(
    ALL_CATEGORIES=['econom'],
    ROUTER_MAPS_ENABLED=True,
    USER_API_USERS_ENDPOINTS={'users/integration/create': True},
)
@pytest.mark.now('2018-04-24T08:15:00+0000')
@pytest.mark.user_experiments('fixed_price', 'use_discounts_service')
@ORDER_OFFERS_SAVE_SWITCH
def test_user_api_get(
        taxi_integration,
        db,
        test_fixture_surge,
        test_fixtures,
        mockserver,
        discounts,
        pricing_data_preparer,
        mock_order_offers,
        order_offers_save_enabled,
):
    pricing_data_preparer.set_strikeout(915.0)
    pricing_data_preparer.set_cost(814, 915)
    pricing_data_preparer.set_discount()
    pricing_data_preparer.set_discount_meta(943, 0.11)
    pricing_data_preparer.set_trip_information(49 * 60, 10)
    pricing_data_preparer.set_meta('min_price', 99)
    pricing_data_preparer.set_user_category_prices_id(
        'c/b7c4d5f6aa3b40a3807bb74b3bc042af',
        'b7c4d5f6aa3b40a3807bb74b3bc042af',
    )
    discounts.set_discount_response(
        {
            'discounts': [
                {
                    'class': 'econom',
                    'discount': {
                        'value': 0.11,
                        'price': 943.0,
                        'original_value': 0.12,
                        'reason': 'for_all',
                        'method': 'full-driver-less',
                    },
                },
            ],
            'discount_offer_id': '123456',
        },
    )

    @mockserver.json_handler('/user-api/users/integration/create')
    def _mock_user_api_create_user(request):
        assert request.json == {
            'phone_id': '5a7b678babae14bb0db4453f',
            'sourceid': 'corp_cabinet',
            'application': 'corpweb',
        }
        return {
            'id': 'e4707fc6e79e4562b4f0af20a8e877a8',
            'application': 'corpweb',
            'sourceid': 'corp_cabinet',
            'phone_id': '5a7b678babae14bb0db4453f',
            'authorized': True,
        }

    request_body = copy.deepcopy(TEST_REQUEST_BODY)
    request_body['sourceid'] = 'corp_cabinet'
    del request_body['user']['user_id']
    request_body['payment'] = {
        'type': 'corp',
        'payment_method_id': 'corp-1234',
    }

    response = taxi_integration.post('v1/orders/estimate', json=request_body)
    assert response.status_code == 200

    response_body = response.json()
    offer_id = response_body.pop('offer')
    response_cost_breakdown = (
        response_body['service_levels'][0]['cost_message_details']
    ).pop('cost_breakdown')

    assert response_body == {
        'user_id': 'e4707fc6e79e4562b4f0af20a8e877a8',
        'is_fixed_price': True,
        'currency_rules': {
            'code': 'RUB',
            'sign': '',
            'template': '$VALUE$ $SIGN$$CURRENCY$',
            'text': 'rub',
        },
        'service_levels': [
            {
                'class': 'econom',
                'price': '814 rub',
                'price_raw': 814,
                'time': '49 min',
                'time_raw': 49,
                'estimated_waiting': {'message': '14 min', 'seconds': 839},
                'details_tariff': DETAILS_NO_MODIFIERS_NEW_PRICING,
                'cost_message_details': {},
                'is_fixed_price': True,
            },
        ],
    }
    ordered_object.assert_eq(
        ONLY_BASE_DISCOUNT_COST_BREAKDOWN, response_cost_breakdown, [''],
    )

    assert _mock_user_api_create_user.wait_call()

    offer = rs_utils.get_user_offer(
        offer_id,
        'e4707fc6e79e4562b4f0af20a8e877a8',
        db,
        mock_order_offers,
        order_offers_save_enabled,
    )
    assert offer is not None

    assert 'price_modifiers' not in offer
    assert offer['prices'] == [
        {
            'driver_price': 915.0,
            'price': 814.0,
            'cat_type': 'application',
            'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
            'sp': 1.0,
            'cls': 'econom',
            'is_fixed_price': True,
            'using_new_pricing': True,
            'pricing_data': pricing_data_preparer.get_pricing_data(
                category='econom',
            ),
        },
    ]


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff'],
    USER_API_USERS_ENDPOINTS={'users/integration/create': True},
)
@pytest.mark.now('2018-07-20T10:15:00+0000')
def test_user_api_create(
        taxi_integration,
        db,
        test_fixture_surge,
        test_fixtures,
        mockserver,
        pricing_data_preparer,
):
    pricing_data_preparer.set_strikeout(100)

    @mockserver.json_handler('/user-api/users/integration/create')
    def _mock_user_api_create_user(request):
        phone_id = request.json['phone_id']
        assert phone_id is not None
        assert request.json == {
            'phone_id': phone_id,
            'sourceid': 'corp_cabinet',
            'application': 'corpweb',
        }
        db.users.insert(
            {
                '_id': '1234567890',
                'phone_id': bson.ObjectId(phone_id),
                'sourceid': 'corp_cabinet',
                'application': 'corpweb',
                'authorized': True,
            },
        )
        return {
            'id': '1234567890',
            'application': 'corpweb',
            'sourceid': 'corp_cabinet',
            'phone_id': phone_id,
            'authorized': True,
        }

    db.users.remove()
    db.user_phones.remove()
    request_body = {
        'user': {
            'phone': '+79061112200',
            'personal_phone_id': 'p00000000000000000000000',
        },
        'requirements': {'nosmoking': True},
        'route': [
            [37.411956, 55.981682],
            [37.907173584260395, 55.90891808601154],
        ],
        'selected_class': 'econom',
        'sourceid': 'corp_cabinet',
        'chainid': 'chainid_1',
    }

    response = taxi_integration.post('v1/orders/estimate', json=request_body)
    assert response.status_code == 200

    assert _mock_user_api_create_user.wait_call()

    user_doc = db.users.find_one({'_id': response.json()['user_id']})
    assert user_doc['sourceid'] == 'corp_cabinet'
    assert user_doc['application'] == 'corpweb'


OFFER_EXTRA_DATA_SUCCESS = {
    'decoupling': {
        'success': True,
        'user': {
            'tariff': (
                '585a6f47201dd1b2017a0eab-'
                '507000939f17427e951df9791573ac7e-'
                '7fc5b2d1115d4341b7be206875c40e11'
            ),
            'prices': [
                {
                    'cls': 'econom',
                    'cat_type': 'application',
                    'category_id': '5f40b7f324414f51a1f9549c65211ea5',
                    'price': 1829.0,
                    'sp': 1.0,
                    'is_fixed_price': True,
                    'using_new_pricing': False,
                },
            ],
        },
        'driver': {
            'tariff': '585a6f47201dd1b2017a0eab',
            'prices': [
                {
                    'cls': 'econom',
                    'cat_type': 'application',
                    'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                    'price': 4571.0,
                    'sp': 5.0,
                    'is_fixed_price': True,
                    'using_new_pricing': False,
                },
            ],
        },
    },
}

OFFER_PRICES_SUCCESS = [
    {
        'cls': 'econom',
        'cat_type': 'application',
        'category_id': '5f40b7f324414f51a1f9549c65211ea5',
        'price': 1829.0,
        'driver_price': 1829.0,
        'sp': 1.0,
        'is_fixed_price': True,
        'using_new_pricing': False,
    },
]


OFFER_EXTRA_DATA_UNSUCCESS = {
    'decoupling': {
        'success': False,
        'error': {
            'reason': 'get_corp_tarif_fail',
            'stage': 'calculating_offer',
        },
    },
}

PDP_DECOUPLING_CATEGORY_PRICES_ID = (
    'd/585a6f47201dd1b2017a0eab-'
    '507000939f17427e951df9791573ac7e-'
    '7fc5b2d1115d4341b7be206875c40e11/'
    '5f40b7f324414f51a1f9549c65211ea5/moscow/svo'
)

PDP_FAILED_DECOUPLING_CATEGORY_PRICES_ID = (
    'd/585a6f47201dd1b2017a0eab-'
    '507000939f17427e951df9791573ac7e-'
    '7fc5b2d1115d4341b7be206875c40e11/'
    'b7c4d5f6aa3b40a3807bb74b3bc042af/moscow/svo'
)


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.parametrize(
    'offer_extra_data, offer_prices, discount_response,'
    'price_with_currency, details_tariff, '
    'cost_breakdown, surge, fallback, '
    'user_id, sourceid, pdp_data, all_classes',
    [
        (
            OFFER_EXTRA_DATA_SUCCESS,
            OFFER_PRICES_SUCCESS,
            {'discounts': [], 'discount_offer_id': '123456'},
            '1,829 rub',
            DETAILS_DECOUPLING,
            [
                {
                    'display_amount': 'Ride 1,829 rub, ~49 min',
                    'display_name': 'cost',
                },
            ],
            5.0,
            False,
            'e4707fc6e79e4562b4f0af20a8e877a8',
            'corp_cabinet',
            {
                'user_price': 1829,
                'driver_price': 4571,
                'user_surge': 1,
                'driver_surge': 5,
                'discount': None,
                'user_category_prices_id': PDP_DECOUPLING_CATEGORY_PRICES_ID,
                'driver_category_prices_id': (
                    'c/b7c4d5f6aa3b40a3807bb74b3bc042af'
                ),
                'decoupling': {
                    'econom': True,
                    'comfortplus': False,
                    'child_tariff': False,
                },
                'replace_offer_from_new_pricing': True,
                'min_price': 198,
                'strikeout_price': 1829,
            },
            False,
        ),
        (
            OFFER_EXTRA_DATA_SUCCESS,
            OFFER_PRICES_SUCCESS,
            {'discounts': [], 'discount_offer_id': '123456'},
            '1,829 rub',
            DETAILS_DECOUPLING,
            [
                {
                    'display_amount': 'Ride 1,829 rub, ~49 min',
                    'display_name': 'cost',
                },
            ],
            5.0,
            False,
            'e4707fc6e79e4562b4f0af20a8e877a8',
            'corp_cabinet',
            {
                'user_price': 1829,
                'driver_price': 4571,
                'user_surge': 1,
                'driver_surge': 5,
                'discount': None,
                'user_category_prices_id': PDP_DECOUPLING_CATEGORY_PRICES_ID,
                'driver_category_prices_id': (
                    'c/b7c4d5f6aa3b40a3807bb74b3bc042af'
                ),
                'decoupling': {
                    'econom': True,
                    'comfortplus': False,
                    'child_tariff': False,
                },
                'replace_offer_from_new_pricing': True,
                'min_price': 198,
                'strikeout_price': 1829,
            },
            True,
        ),
        (
            OFFER_EXTRA_DATA_UNSUCCESS,
            [
                {
                    'cls': 'econom',
                    'cat_type': 'application',
                    'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                    'price': 814.0,
                    'driver_price': 915.0,  # unceiled 914.01113294751121
                    'sp': 1.0,
                    'is_fixed_price': True,
                },
            ],
            {
                'discounts': [
                    {
                        'class': 'econom',
                        'discount': {
                            'value': 0.11,
                            'original_value': 0.11,
                            'price': 800.0,
                            'reason': 'for_all',
                            'method': 'full-driver-less',
                        },
                    },
                ],
                'discount_offer_id': '123456',
            },
            '814 rub',
            DETAILS_NO_MODIFIERS,
            ONLY_BASE_DISCOUNT_COST_BREAKDOWN,
            1.0,
            True,
            'e4707fc6e79e4562b4f0af20a8e877a8',
            'corp_cabinet',
            {
                'user_price': 814,
                'driver_price': 915,
                'user_surge': 1,
                'driver_surge': 5,
                'discount': {'value': 0.11, 'price': 800},
                'user_category_prices_id': (
                    PDP_FAILED_DECOUPLING_CATEGORY_PRICES_ID
                ),
                'driver_category_prices_id': (
                    'c/b7c4d5f6aa3b40a3807bb74b3bc042af'
                ),
                'min_price': 99,
                'decoupling': {
                    'econom': False,
                    'comfortplus': False,
                    'child_tariff': False,
                },
                'replace_offer_from_new_pricing': True,
                'strikeout_price': 915,
            },
            False,
        ),
        (
            OFFER_EXTRA_DATA_SUCCESS,
            OFFER_PRICES_SUCCESS,
            {'discounts': [], 'discount_offer_id': '123456'},
            '1,829 rub',
            DETAILS_DECOUPLING,
            [
                {
                    'display_amount': 'Ride 1,829 rub, ~49 min',
                    'display_name': 'cost',
                },
                {
                    'display_amount': '2,152 rub',
                    'display_name': 'cost_without_discount',
                },
                {
                    'display_amount': '15%',
                    'display_name': 'call_center_discount',
                },
                {'display_amount': '15%', 'display_name': 'discount'},
                {'display_amount': '15%', 'display_name': 'total_discount'},
            ],
            5.0,
            False,
            'e4707fc6e79e4562b4f0af20a8e877a9',
            'call_center',
            {
                'user_price': 1829,
                'driver_price': 4571,
                'user_surge': 1,
                'driver_surge': 5,
                'discount': None,
                'user_category_prices_id': PDP_DECOUPLING_CATEGORY_PRICES_ID,
                'driver_category_prices_id': (
                    'c/b7c4d5f6aa3b40a3807bb74b3bc042af'
                ),
                'decoupling': {
                    'econom': True,
                    'comfortplus': False,
                    'child_tariff': False,
                },
                'replace_offer_from_new_pricing': True,
                'min_price': 198,
                'strikeout_price': 2152,
            },
            False,
        ),
        (
            OFFER_EXTRA_DATA_UNSUCCESS,
            [
                {
                    'cls': 'econom',
                    'cat_type': 'application',
                    'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                    'price': 830.0,
                    'driver_price': 933.0,
                    'sp': 1.0,
                    'is_fixed_price': True,
                },
            ],
            {
                'discounts': [
                    {
                        'class': 'econom',
                        'discount': {
                            'value': 0.11,
                            'original_value': 0.11,
                            'price': 800.0,
                            'reason': 'for_all',
                            'method': 'full-driver-less',
                        },
                    },
                ],
                'discount_offer_id': '123456',
            },
            '830 rub',
            DETAILS_APPLICATION_CATEGORY_CALLCENTER_SOURCE,
            [
                {
                    'display_amount': 'Ride 830 rub, ~49 min',
                    'display_name': 'cost',
                },
                {
                    'display_amount': '1,097 rub',
                    'display_name': 'cost_without_discount',
                },
                {
                    'display_amount': '15%',
                    'display_name': 'call_center_discount',
                },
                {'display_amount': '11%', 'display_name': 'base_discount'},
                {'display_amount': '24%', 'display_name': 'discount'},
                {'display_amount': '24%', 'display_name': 'total_discount'},
            ],
            1.0,
            True,
            'e4707fc6e79e4562b4f0af20a8e877a9',
            'call_center',
            {
                'user_price': 830,
                'driver_price': 933,
                'user_surge': 1,
                'driver_surge': 5,
                'discount': {'value': 0.11, 'price': 800},
                'user_category_prices_id': (
                    PDP_FAILED_DECOUPLING_CATEGORY_PRICES_ID
                ),
                'driver_category_prices_id': (
                    'c/b7c4d5f6aa3b40a3807bb74b3bc042af'
                ),
                'min_price': 101,
                'decoupling': {
                    'econom': False,
                    'comfortplus': False,
                    'child_tariff': False,
                },
                'replace_offer_from_new_pricing': True,
                'strikeout_price': 1097,
            },
            False,
        ),
    ],
    ids=[
        'decoupled_corp_cabinet',
        'decoupled_corp_cabinet_all_classes',
        'decoupling_failed_corp_cabinet',
        'decoupled_call_center',
        'decoupling_failed_call_center',
    ],
)
@pytest.mark.config(
    INTEGRATION_TARIFFS_ENABLED=False,
    ROUTER_MAPS_ENABLED=True,
    TVM_ENABLED=True,
    TVM_DISABLE_CHECK=['integration-api'],
    TVM_RULES=[{'src': 'integration-api', 'dst': 'corp-integration-api'}],
    ALL_CATEGORIES=['econom', 'child_tariff', 'comfortplus', 'minivan'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'comfortplus', 'child_tariff', 'minivan'],
    },
)
@pytest.mark.user_experiments('fixed_price', 'use_discounts_service')
@pytest.mark.experiments3(filename='experiments3_offer_coupon.json')
def test_decoupling(
        taxi_integration,
        db,
        discounts,
        load_json,
        test_fixtures,
        mockserver,
        tvm2_client,
        now,
        offer_extra_data,
        discount_response,
        details_tariff,
        offer_prices,
        price_with_currency,
        cost_breakdown,
        surge,
        fallback,
        user_id,
        sourceid,
        pricing_data_preparer,
        pdp_data,
        all_classes,
):

    discounts.set_discount_response(discount_response)
    if details_tariff:
        details_tariff = [
            detail for detail in details_tariff if detail['type'] != 'comment'
        ]
    pricing_data_preparer.set_categories(['econom'])
    pricing_data_preparer.set_user_category_prices_id(
        pdp_data['user_category_prices_id'],
    )
    pricing_data_preparer.set_driver_category_prices_id(
        pdp_data['driver_category_prices_id'],
    )
    pricing_data_preparer.set_meta('min_price', pdp_data['min_price'])
    pricing_data_preparer.set_cost(
        pdp_data['user_price'], pdp_data['driver_price'],
    )
    pricing_data_preparer.set_user_surge(pdp_data['user_surge'])
    pricing_data_preparer.set_driver_surge(pdp_data['driver_surge'])
    pricing_data_preparer.set_trip_information(time=49 * 60, distance=1000)
    if pdp_data['discount']:
        pricing_data_preparer.set_discount()
        pricing_data_preparer.set_discount_meta(
            pdp_data['discount']['price'], pdp_data['discount']['value'],
        )
    try:
        offer_extra_data = copy.deepcopy(offer_extra_data)
        for price in offer_extra_data['decoupling']['driver']['prices']:
            price['using_new_pricing'] = True
        for price in offer_extra_data['decoupling']['user']['prices']:
            price['using_new_pricing'] = True
    except KeyError:
        pass
    if cost_breakdown:
        cost_breakdown = filter_pdp_cost_breakdown(cost_breakdown)

    if 'error' in offer_extra_data.get('decoupling', {}):
        offer_extra_data['decoupling']['error'][
            'reason'
        ] = 'plugin_internal_error'

    for cat_name, enabled in pdp_data['decoupling'].items():
        pricing_data_preparer.set_decoupling(enabled, category=cat_name)

    pricing_data_preparer.set_corp_decoupling(True)

    pricing_data_preparer.set_meta('min_price', pdp_data['min_price'])
    pricing_data_preparer.set_strikeout(pdp_data['strikeout_price'])
    offer_prices = copy.deepcopy(offer_prices)
    for offer_price in offer_prices:
        offer_price['using_new_pricing'] = True
        offer_price['pricing_data'] = pricing_data_preparer.get_pricing_data(
            category=offer_price['cls'],
        )

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        input_json = json.loads(request.get_data())
        if len(input_json['classes']) > 1:
            return load_json('get_surge_all_classes_decoupling.json')
        return get_surge_calculator_response(request, surge, load_json)

    ticket = 'ticket'
    tvm2_client.set_ticket(json.dumps({'24': {'ticket': ticket}}))

    @mockserver.json_handler('/statistics/v1/metrics/store')
    def mock_stat(request):
        pass

    request_body = load_json('decoupling/request.json')
    request_body['user']['user_id'] = user_id
    request_body['all_classes'] = all_classes
    if sourceid == 'call_center':
        headers = CC_HEADERS
        del request_body['sourceid']
    else:
        headers = {}
        request_body['sourceid'] = sourceid

    response = taxi_integration.post(
        'v1/orders/estimate', json=request_body, headers=headers,
    )

    assert response.status_code == 200, response.text
    response_body = response.json()
    assert response_body['user_id'] == user_id

    assert 'offer' in response_body
    assert response_body['is_fixed_price'] is True

    currency_rules = response_body['currency_rules']
    assert currency_rules['code'] == 'RUB'
    assert currency_rules['sign'] == ''
    assert currency_rules['template'] == '$VALUE$ $SIGN$$CURRENCY$'
    assert currency_rules['text'] == 'rub'

    service_levels = response_body['service_levels']
    assert service_levels[0]['class'] == 'econom'
    response_cost_breakdown = service_levels[0]['cost_message_details'][
        'cost_breakdown'
    ]
    assert sorted(cost_breakdown, key=lambda v: v['display_name']) == sorted(
        response_cost_breakdown, key=lambda v: v['display_name'],
    )

    assert service_levels[0]['price'] == price_with_currency
    assert service_levels[0]['time'] == '49 min'
    assert service_levels[0]['estimated_waiting']['message'] == '14 min'
    assert service_levels[0]['estimated_waiting']['seconds'] == 839
    assert service_levels[0]['details_tariff'] == details_tariff

    offer = rs_utils.get_user_offer(
        response_body['offer'], response_body['user_id'], db,
    )
    assert offer is not None

    assert offer['_id'] == response_body['offer']
    assert offer['authorized']
    assert offer['created'] == now.replace(microsecond=0)
    assert not offer['destination_is_airport']
    assert offer['prices'] == offer_prices
    assert offer['classes_requirements'] == {
        'econom': {'nosmoking': True},
        'child_tariff': {'nosmoking': True},
        'comfortplus': {'nosmoking': True},
    }
    assert offer['route'] == [
        [37.1946401739712, 55.478983901730004],
        [37.565210, 55.734434],
    ]
    assert offer['user_id'] == user_id
    assert offer['extra_data'] == offer_extra_data

    assert pricing_data_preparer.calls == 1


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments('fixed_price')
def test_decoupling_no_user(
        taxi_integration,
        db,
        load_json,
        test_fixtures,
        mockserver,
        pricing_data_preparer,
):
    pricing_data_preparer.set_strikeout(100)
    pricing_data_preparer.set_cost(1829, 1829)
    pricing_data_preparer.set_trip_information(time=49 * 60, distance=1000)
    pricing_data_preparer.set_decoupling(True)
    pricing_data_preparer.set_user_category_prices_id(
        PDP_TARIFF_CATEGORY_INFO['user_category_prices_id'],
        PDP_TARIFF_CATEGORY_INFO['user_category_id'],
        PDP_TARIFF_CATEGORY_INFO['user_tariff_id'],
    )
    pricing_data_preparer.set_driver_category_prices_id(
        PDP_TARIFF_CATEGORY_INFO['driver_category_prices_id'],
        PDP_TARIFF_CATEGORY_INFO['driver_category_id'],
        PDP_TARIFF_CATEGORY_INFO['driver_tariff_id'],
    )
    pricing_data_preparer.set_meta('min_price', 198)

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return get_surge_calculator_response(request, 5.0, load_json)

    @mockserver.json_handler('/corp_integration_api/tariffs')
    def mock_tariffs(request):
        return load_json('decoupling/tariffs_response.json')

    request_body = load_json('decoupling/request.json')
    request_body.pop('user')
    response = taxi_integration.post('v1/orders/estimate', json=request_body)

    assert response.status_code == 200
    response_body = response.json()

    assert 'user_id' not in response_body
    assert 'offer' not in response_body

    assert response_body['is_fixed_price'] is False

    currency_rules = response_body['currency_rules']
    assert currency_rules['code'] == 'RUB'
    assert currency_rules['sign'] == ''
    assert currency_rules['template'] == '$VALUE$ $SIGN$$CURRENCY$'
    assert currency_rules['text'] == 'rub'

    service_levels = response_body['service_levels']
    assert service_levels[0]['class'] == 'econom'
    response_cost_breakdown = service_levels[0]['cost_message_details'][
        'cost_breakdown'
    ]
    cost_breakdown = [
        {'display_amount': 'Ride 1,829 rub, ~49 min', 'display_name': 'cost'},
    ]
    ordered_object.assert_eq(cost_breakdown, response_cost_breakdown, [''])

    assert service_levels[0]['price'] == '1,829 rub'
    assert service_levels[0]['time'] == '49 min'
    assert service_levels[0]['estimated_waiting']['message'] == '14 min'
    assert service_levels[0]['estimated_waiting']['seconds'] == 839
    assert (
        service_levels[0]['details_tariff']
        == DETAILS_DECOUPLING_FROM_NEW_PRICING_RESPONSE
    )


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.parametrize('disable_fixed_price', [True, False])
@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    TVM_ENABLED=True,
    TVM_DISABLE_CHECK=['integration-api'],
    TVM_RULES=[{'src': 'integration-api', 'dst': 'corp-integration-api'}],
)
@pytest.mark.user_experiments('fixed_price')
@ORDER_OFFERS_SAVE_SWITCH
def test_decoupling_disable_fixed_price(
        taxi_integration,
        db,
        load_json,
        test_fixtures,
        tvm2_client,
        mockserver,
        disable_fixed_price,
        pricing_data_preparer,
        mock_order_offers,
        order_offers_save_enabled,
):
    pricing_data_preparer.set_strikeout(100)
    pricing_data_preparer.set_fixed_price(not disable_fixed_price)
    pricing_data_preparer.set_decoupling(True)
    pricing_data_preparer.set_user_category_prices_id(
        PDP_TARIFF_CATEGORY_INFO['user_category_prices_id'],
        PDP_TARIFF_CATEGORY_INFO['user_category_id'],
        PDP_TARIFF_CATEGORY_INFO['user_tariff_id'],
    )
    pricing_data_preparer.set_driver_category_prices_id(
        PDP_TARIFF_CATEGORY_INFO['driver_category_prices_id'],
        PDP_TARIFF_CATEGORY_INFO['driver_category_id'],
        PDP_TARIFF_CATEGORY_INFO['driver_tariff_id'],
    )

    ticket = 'ticket'
    tvm2_client.set_ticket(json.dumps({'24': {'ticket': ticket}}))

    @mockserver.json_handler('/corp_integration_api/tariffs')
    def mock_tariffs(request):
        response = load_json('decoupling/tariffs_response.json')
        if disable_fixed_price:
            response['disable_fixed_price'] = True
        return response

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_getsurge(request):
        input_json = json.loads(request.get_data())
        mocks = {
            'econom': 'get_surge_econom.json',
            'child_tariff': 'get_surge_child.json',
        }
        key = '+'.join(sorted(input_json['classes']))
        assert key in mocks
        return load_json(mocks[key])

    request_body = load_json('decoupling/request.json')
    response = taxi_integration.post('v1/orders/estimate', json=request_body)

    assert response.status_code == 200
    response_body = response.json()
    assert not disable_fixed_price == response_body['is_fixed_price']

    offer = rs_utils.get_user_offer(
        response_body['offer'],
        response_body['user_id'],
        db,
        mock_order_offers,
        order_offers_save_enabled,
    )
    price_types = (
        offer['prices'],
        offer['extra_data']['decoupling']['user']['prices'],
        offer['extra_data']['decoupling']['driver']['prices'],
    )
    for price_type in price_types:
        for price in price_type:
            assert not disable_fixed_price == price['is_fixed_price']


def prices_almost_the_same(p1, p2, epsilon):
    """
    In price calculations there is some rounding issue,
    so we are just checking that prices match with some error margin.
    """
    return abs(p1 - p2) < epsilon


@pytest.mark.parametrize(
    ['requirements', 'expected_multipliers', 'pdp_user_driver_prices'],
    (
        ({'cargo_loaders': 2}, ('22.000000',), (646.37 * 2 * 22, 646.37 * 22)),
        (
            {'cargo_loaders': [2]},
            ('22.000000',),
            (646.37 * 2 * 22, 646.37 * 22),
        ),
        ({'cargo_loaders': 1}, ('11.000000',), (646.37 * 2 * 11, 646.37 * 11)),
        (
            {'cargo_type': 'lcv_m'},
            ('55.000000',),
            (646.37 * 2 * 55, 646.37 * 55),
        ),
        (
            {'cargo_loaders': [1, 1]},
            ('121.000000',),
            (646.37 * 2 * 121, 646.37 * 121),
        ),
        (
            {'cargo_type': ['lcv_l'], 'cargo_loaders': [1, 1]},
            ('121.000000', '66.000000'),
            (646.37 * 2 * 7986, 646.37 * 7986),
        ),
    ),
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.filldb(
    requirements='with_multiplier', tariffs='with_multiplier_req',
)
@pytest.mark.config(ROUTER_MAPS_ENABLED=True)
@pytest.mark.user_experiments('fixed_price')
def test_decoupling_requirements_multiplier(
        taxi_integration,
        db,
        load_json,
        test_fixtures,
        mockserver,
        now,
        requirements,
        expected_multipliers,
        pricing_data_preparer,
        pdp_user_driver_prices,
):
    pricing_data_preparer.set_strikeout(100)
    pricing_data_preparer.set_decoupling(True)
    pricing_data_preparer.set_cost(
        pdp_user_driver_prices[0], pdp_user_driver_prices[1],
    )
    pricing_data_preparer.set_user_category_prices_id(
        PDP_TARIFF_CATEGORY_INFO['user_category_prices_id'],
        PDP_TARIFF_CATEGORY_INFO['user_category_id'],
        PDP_TARIFF_CATEGORY_INFO['user_tariff_id'],
    )
    pricing_data_preparer.set_driver_category_prices_id(
        PDP_TARIFF_CATEGORY_INFO['driver_category_prices_id'],
        PDP_TARIFF_CATEGORY_INFO['driver_category_id'],
        PDP_TARIFF_CATEGORY_INFO['driver_tariff_id'],
    )

    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock_phones_store(request):
        return {}

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return get_surge_calculator_response(request, 1.0, load_json)

    @mockserver.json_handler('/corp_integration_api/tariffs')
    def mock_tariffs(request):
        return load_json('decoupling/tariffs_response.json')

    request_body = load_json('decoupling/request.json')
    request_body['requirements'] = {}
    for req_name, req_value in requirements.items():
        request_body['requirements'][req_name] = req_value

    response = taxi_integration.post('v1/orders/estimate', json=request_body)

    assert response.status_code == 200
    data = response.json()
    offer_id = data['offer']
    offer = rs_utils.get_offer(offer_id, db)
    assert 'price_modifiers' in offer
    price_modifiers = offer['price_modifiers']
    assert len(price_modifiers['items']) == len(requirements)
    for price_modifier_item, expected_multiplier in zip(
            price_modifiers['items'], expected_multipliers,
    ):
        assert price_modifier_item['reason'] == 'requirements'
        assert price_modifier_item['pay_subventions'] is False
        assert price_modifier_item['tariff_categories'] == ['econom']
        assert price_modifier_item['type'] == 'multiplier'
        assert price_modifier_item['value'] == expected_multiplier

    total_multiplier = 1
    for m in expected_multipliers:
        total_multiplier *= int(m.replace('.000000', ''))

    decoupling = offer['extra_data']['decoupling']
    # base 646.37 * (multiplier) by cargo_loaders requirement
    assert prices_almost_the_same(
        decoupling['driver']['prices'][0]['price'],
        646.37 * total_multiplier,
        total_multiplier,
    )
    # base 646.37 * 2 by corp tariff * (multiplier) by cargo_loaders
    assert prices_almost_the_same(
        offer['prices'][0]['price'],
        646.37 * 2 * total_multiplier,
        total_multiplier,
    )
    assert prices_almost_the_same(
        decoupling['user']['prices'][0]['price'],
        646.37 * 2 * total_multiplier,
        total_multiplier,
    )


TEST_USER_ID = 'e4707fc6e79e4562b4f0af20a8e877a3'
TEST_PHONE = '+79061112255'
TEST_PERSONAL_PHONE_ID = 'p00000000000000000000005'

NEW_PHONE = '+79061112299'
NEW_PERSONAL_PHONE_ID = 'p00000000000000000000009'


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'child_tariff'],
    },
    ROUTER_MAPS_ENABLED=True,
    CATEGORIES_SETS_BY_APPLICATION_BRAND_ENABLED=True,
)
@pytest.mark.parametrize(
    'user_data, expected_code, personal_times_called, error_text',
    [
        pytest.param(
            {'user_id': TEST_USER_ID, 'phone': TEST_PHONE},
            200,
            1,
            None,
            id='only_phone',
        ),
        pytest.param(
            {
                'user_id': TEST_USER_ID,
                'personal_phone_id': TEST_PERSONAL_PHONE_ID,
            },
            200,
            0,
            None,
            id='only_personal_phone_id',
        ),
        pytest.param(
            {
                'user_id': TEST_USER_ID,
                'phone': TEST_PHONE,
                'personal_phone_id': TEST_PERSONAL_PHONE_ID,
            },
            200,
            0,
            None,
            id='both',
        ),
        pytest.param(
            {'user_id': TEST_USER_ID},
            400,
            0,
            'either personal_phone_id or phone should be passed',
            id='none',
        ),
        pytest.param(
            {'user_id': TEST_USER_ID, 'phone': NEW_PHONE},
            400,
            1,
            'user personal_phone_id doesn\'t match request personal_phone_id',
            id='new_phone_does_not_match_user_phone',
        ),
        pytest.param(
            {'user_id': TEST_USER_ID, 'phone': '+7903'},
            400,
            1,
            'invalid phone number format',
            id='phone_bad_format',
        ),
        pytest.param(
            {
                'user_id': TEST_USER_ID,
                'personal_phone_id': 'p99999999999999999999999',
            },
            400,
            0,
            'user personal_phone_id doesn\'t match request personal_phone_id',
            id='phone_doc_does_not_exist',
        ),
    ],
)
def test_personal(
        taxi_integration,
        mockserver,
        db,
        discounts,
        test_fixture_surge,
        test_fixtures,
        user_data,
        expected_code,
        personal_times_called,
        error_text,
        pricing_data_preparer,
):
    """
    Test checks whether personal client should be called based on user_identity
    passed with request. If personal_phone_id is missing it should be retrieved
    via personal service.
    """
    pricing_data_preparer.set_strikeout(100)

    @mockserver.json_handler('/personal/v1/phones/store')
    def mock_personal(request):
        request_json = json.loads(request.get_data())
        assert 'value' in request_json
        if request_json['value'] == TEST_PHONE:
            return {'id': TEST_PERSONAL_PHONE_ID, 'value': TEST_PHONE}
        elif request_json['value'] == NEW_PHONE:
            db.user_phones.insert(
                {'_id': NEW_PERSONAL_PHONE_ID, 'value': NEW_PHONE},
            )

            return {'id': NEW_PERSONAL_PHONE_ID, 'value': NEW_PHONE}
        else:
            return mockserver.make_response({}, 400)

    discounts.set_discount_response(
        {'discounts': [], 'discount_offer_id': '123456'},
    )

    request_body = {
        'user': user_data,
        'requirements': {'nosmoking': True},
        'route': [
            [37.1946401739712, 55.478983901730004],
            [37.565210, 55.734434],
        ],
        'selected_class': 'econom',
        'chainid': 'chainid_1',
    }

    response = taxi_integration.post(
        'v1/orders/estimate', json=request_body, headers=CC_HEADERS,
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        assert mock_personal.times_called == personal_times_called

        user_data.pop('user_id')
        phone_doc = db.user_phones.find_one(user_data)
        assert phone_doc is not None
    else:
        assert response.json()['error']['text'] == error_text


@pytest.mark.config(
    USER_API_USER_PHONES_RETRIEVAL_ENDPOINTS={'__default__': True},
)
@pytest.mark.parametrize(
    'user_api_enabled, user_api_times_called',
    [
        pytest.param(True, 1, id='user_api_enabled'),
        pytest.param(False, 0, id='user_api_disabled'),
    ],
)
def test_user_api_create_by_personal(
        taxi_integration,
        mockserver,
        config,
        load_json,
        discounts,
        test_fixture_surge,
        test_fixtures,
        user_api_enabled,
        user_api_times_called,
        pricing_data_preparer,
):
    """
    Test checks whether user-api client is used during phone doc creation or
    data is fetched from mongo database directly.
    """
    pricing_data_preparer.set_strikeout(100)
    config.set(USER_API_USE_USER_PHONES_CREATION=user_api_enabled)

    @mockserver.json_handler('/user-api/user_phones')
    def _mock_user_api_user_phones(request):
        assert request.json == {
            'personal_phone_id': TEST_PERSONAL_PHONE_ID,
            'type': 'yandex',
            'validate_phone': False,
        }
        return load_json('user_api_response.json')

    request_body = {
        'user': {
            'phone': TEST_PHONE,
            'personal_phone_id': TEST_PERSONAL_PHONE_ID,
        },
        'requirements': {'nosmoking': True},
        'route': [
            [37.1946401739712, 55.478983901730004],
            [37.565210, 55.734434],
        ],
        'selected_class': 'econom',
        'sourceid': 'corp_cabinet',
        'chainid': 'chainid_1',
    }

    response = taxi_integration.post('v1/orders/estimate', json=request_body)

    assert response.status_code == 200
    assert _mock_user_api_user_phones.times_called == user_api_times_called


@pytest.mark.parametrize(
    'headers',
    [{'User-Agent': 'call_center'}, {'User-Agent': 'vezet_call_center'}],
)
@pytest.mark.now('2018-04-24T08:15:00+0000')
@pytest.mark.user_experiments('fixed_price')
def test_callcenter_discounts(
        taxi_integration,
        test_fixtures,
        test_fixture_surge,
        headers,
        pricing_data_preparer,
):
    pricing_data_preparer.set_strikeout(118)
    pricing_data_preparer.set_meta('min_price', 111)
    request_body = {
        'user': {
            'phone': '+79061112266',
            'personal_phone_id': 'p00000000000000000000006',
            'user_id': 'e4707fc6e79e4562b4f0af20a8e877a4',
        },
        'route': [
            [37.1946401739712, 55.478983901730004],
            [37.565210, 55.734434],
        ],
        'selected_class': 'econom',
    }

    response = taxi_integration.post(
        'v1/orders/estimate', json=request_body, headers=headers,
    )

    assert response.status_code == 200, response.text
    response_body = response.json()
    service_levels = response_body['service_levels']
    assert (
        service_levels[0]['details_tariff']
        == DETAILS_CALLCENTER_CATEGORY_CALLCENTER_SOURCE_NEW_PRICING
    )
    assert all(
        [
            discount
            in service_levels[0]['cost_message_details']['cost_breakdown']
            for discount in (
                {'display_amount': '15%', 'display_name': 'discount'},
                {'display_amount': '15%', 'display_name': 'total_discount'},
            )
        ],
    )

    assert response_body['user_id'] == 'e4707fc6e79e4562b4f0af20a8e877a4'


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(filename='preorder_experiment.json')
@pytest.mark.parametrize(
    ('is_preorder', 'expected_cost'),
    [
        pytest.param(
            False, 'Ride 1,658 rub, ~88 min', id='default_cost_format',
        ),
        pytest.param(
            True, 'Ride from 1,658 rub, ~88 min', id='preorder_cost_format',
        ),
    ],
)
def test_preorder_cost_format(
        taxi_integration,
        test_fixture_surge,
        test_fixtures,
        is_preorder,
        expected_cost,
        pricing_data_preparer,
):
    pricing_data_preparer.set_strikeout(100)
    pricing_data_preparer.set_cost(user_cost=1658, driver_cost=1658)
    pricing_data_preparer.set_trip_information(time=88 * 60, distance=100)
    request_body = copy.deepcopy(TEST_REQUEST_BODY)
    if is_preorder:
        request_body['preorder_request_id'] = 'test_id'

    response = taxi_integration.post('v1/orders/estimate', json=request_body)

    assert response.status_code == 200
    response_body = response.json()

    assert 'service_levels' in response_body
    service_levels = response_body['service_levels']

    for service_level in service_levels:
        if service_level['class'] != 'econom':
            continue

        assert 'cost_message_details' in service_level
        cost_message_details = service_level['cost_message_details']

        for cost_breakdown in cost_message_details['cost_breakdown']:
            if cost_breakdown['display_name'] == 'cost':
                assert cost_breakdown['display_amount'] == expected_cost


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.parametrize('is_preorder', [True, False])
@pytest.mark.parametrize(
    'fp_exp',
    [
        pytest.param(True, marks=pytest.mark.user_experiments('fixed_price')),
        pytest.param(False),
    ],
)
@pytest.mark.parametrize(
    'router_maps',
    [
        pytest.param(True, marks=pytest.mark.config(ROUTER_MAPS_ENABLED=True)),
        pytest.param(False),
    ],
)
@pytest.mark.parametrize(
    'preorder_exp',
    [
        pytest.param(
            True,
            marks=pytest.mark.experiments3(
                filename='preorder_experiment.json',
            ),
        ),
        pytest.param(False),
    ],
)
@ORDER_OFFERS_SAVE_SWITCH
def test_fix_price(
        taxi_integration,
        test_fixtures,
        test_fixture_surge,
        db,
        is_preorder,
        fp_exp,
        router_maps,
        preorder_exp,
        pricing_data_preparer,
        mock_order_offers,
        order_offers_save_enabled,
):
    pricing_data_preparer.set_strikeout(100)
    pricing_data_preparer.set_categories(['econom'])
    is_fixed_price = (
        router_maps and fp_exp and not (preorder_exp and is_preorder)
    )
    pricing_data_preparer.set_fixed_price(is_fixed_price)

    request = copy.deepcopy(TEST_REQUEST_BODY)
    if is_preorder:
        request['preorder_request_id'] = 'some_preorder_request_id'

    response = taxi_integration.post('v1/orders/estimate', json=request)

    assert response.status_code == 200

    offer_id = response.json()['offer']
    offer = rs_utils.get_offer(
        offer_id, db, mock_order_offers, order_offers_save_enabled,
    )

    assert [price['cls'] for price in offer['prices']] == ['econom']

    assert offer['is_fixed_price'] == is_fixed_price
    for price in offer['prices']:
        assert price['is_fixed_price'] == is_fixed_price


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments('fixed_price')
@pytest.mark.config(ROUTER_MAPS_ENABLED=True)
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='estimate_save_offer_via_service',
    consumers=['integration/ordersestimate'],
    clauses=[
        {
            'enabled': True,
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
)
def test_order_offers_no_fallback(
        taxi_integration,
        test_fixtures,
        test_fixture_surge,
        pricing_data_preparer,
        mockserver,
):
    pricing_data_preparer.set_strikeout(100)
    pricing_data_preparer.set_categories(['econom'])
    pricing_data_preparer.set_fixed_price(True)

    @mockserver.handler('/order-offers/v1/save-offer')
    def _mock_save_offer(request):
        return mockserver.make_response('', 500)

    response = taxi_integration.post(
        'v1/orders/estimate', json=TEST_REQUEST_BODY,
    )
    assert response.status_code == 500


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments('fixed_price')
@pytest.mark.config(ROUTER_MAPS_ENABLED=True)
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='estimate_save_offer_via_service',
    consumers=['integration/ordersestimate'],
    clauses=[
        {
            'enabled': True,
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
)
@pytest.mark.config(PROTOCOL_GENERATE_OFFER_ID_BY_SERVICE='enabled')
def test_order_offers_generate_id(
        taxi_integration,
        test_fixtures,
        test_fixture_surge,
        pricing_data_preparer,
        mockserver,
        mock_order_offers,
):
    pricing_data_preparer.set_strikeout(100)
    pricing_data_preparer.set_categories(['econom'])
    pricing_data_preparer.set_fixed_price(True)

    generated_id = 'offer-id-from-service'

    @mockserver.json_handler('/order-offers/v1/generate-offer-id')
    def mock_generate_offer_id(request):
        return {'offer_id': generated_id}

    response = taxi_integration.post(
        'v1/orders/estimate', json=TEST_REQUEST_BODY,
    )

    assert response.status_code == 200
    assert response.json().get('offer') == generated_id

    assert mock_generate_offer_id.times_called == 1

    assert mock_order_offers.get_offer(generated_id) is not None


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments('fixed_price')
@pytest.mark.config(ROUTER_MAPS_ENABLED=True)
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='estimate_save_offer_via_service',
    consumers=['integration/ordersestimate'],
    clauses=[
        {
            'enabled': True,
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
)
@pytest.mark.config(PROTOCOL_GENERATE_OFFER_ID_BY_SERVICE='enabled')
def test_order_offers_generate_id_error(
        taxi_integration,
        test_fixtures,
        test_fixture_surge,
        pricing_data_preparer,
        mockserver,
        mock_order_offers,
):
    pricing_data_preparer.set_strikeout(100)
    pricing_data_preparer.set_categories(['econom'])
    pricing_data_preparer.set_fixed_price(True)

    @mockserver.json_handler('/order-offers/v1/generate-offer-id')
    def mock_generate_offer_id(request):
        return mockserver.make_response('', 500)

    response = taxi_integration.post(
        'v1/orders/estimate', json=TEST_REQUEST_BODY,
    )

    assert response.status_code == 500

    assert mock_generate_offer_id.times_called == 1


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments('fixed_price')
@pytest.mark.config(ROUTER_MAPS_ENABLED=True)
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='estimate_save_offer_via_service',
    consumers=['integration/ordersestimate'],
    clauses=[
        {
            'enabled': True,
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
)
@pytest.mark.config(
    PROTOCOL_GENERATE_OFFER_ID_BY_SERVICE='enabled_with_fallback',
)
@pytest.mark.parametrize('generate_with_error', [False, True])
def test_order_offers_generate_id_fallback(
        taxi_integration,
        test_fixtures,
        test_fixture_surge,
        pricing_data_preparer,
        mockserver,
        mock_order_offers,
        generate_with_error,
):
    pricing_data_preparer.set_strikeout(100)
    pricing_data_preparer.set_categories(['econom'])
    pricing_data_preparer.set_fixed_price(True)

    generated_id = 'offer-id-from-service'

    @mockserver.json_handler('/order-offers/v1/generate-offer-id')
    def mock_generate_offer_id(request):
        if generate_with_error:
            return mockserver.make_response('', 500)
        return {'offer_id': generated_id}

    response = taxi_integration.post(
        'v1/orders/estimate', json=TEST_REQUEST_BODY,
    )

    assert response.status_code == 200

    response_offer_id = response.json().get('offer')
    assert response_offer_id is not None
    if generate_with_error:
        assert response_offer_id != generated_id
    else:
        assert response_offer_id == generated_id

    assert mock_generate_offer_id.times_called == 1

    if generate_with_error:
        assert mock_order_offers.get_offer(generated_id) is None
        assert mock_order_offers.get_offer(response_offer_id) is not None
    else:
        assert mock_order_offers.get_offer(generated_id) is not None


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'child_tariff'],
    },
    ROUTER_MAPS_ENABLED=True,
    INTEGRATION_API_ESTIMATE_USE_DRIVER_ETA=True,
)
@pytest.mark.now('2018-04-24T08:15:00+0000')
@pytest.mark.user_experiments('fixed_price', 'use_discounts_service')
@pytest.mark.parametrize(
    'config_value, exp_code',
    ((['turboapp'], 200), ([], 400)),
    ids=('user_found', 'user_not_fetch'),
)
def test_user_without_source_id(
        taxi_integration,
        db,
        discounts,
        test_fixture_surge,
        taxi_config,
        test_fixtures,
        config_value,
        exp_code,
        pricing_data_preparer,
):
    pricing_data_preparer.set_strikeout(100)
    taxi_config.set_values(
        {'INTEGRATION_API_USE_APP_INSTEAD_OF_SOURCE_ID': config_value},
    )
    request_body = {
        'user': {
            'phone': '+79061112255',
            'personal_phone_id': 'p00000000000000000000005',
            'user_id': 'without_source_id',
        },
        'requirements': {'nosmoking': True},
        'route': [
            [37.1946401739712, 55.478983901730004],
            [37.565210, 55.734434],
        ],
        'selected_class': 'econom',
        'sourceid': 'turboapp',
        'chainid': 'chainid_1',
        'payment': {'type': 'cash'},
    }

    response = taxi_integration.post(
        'v1/orders/estimate',
        json=request_body,
        headers={'User-Agent': 'app1-turboapp'},
    )
    assert response.status_code == exp_code
    if exp_code == 400:
        assert response.json() == {
            'error': {
                'text': 'user sourceid doesn\'t match request source_id',
            },
        }


@pytest.mark.experiments3(filename='experiments3_offer_coupon.json')
def test_check_coupon_simple(
        taxi_integration,
        test_fixtures,
        test_fixture_surge,
        db,
        tvm2_client,
        pricing_data_preparer,
):
    pricing_data_preparer.set_strikeout(100)
    pricing_data_preparer.set_coupon(
        value=100,
        percent=10,
        limit=50,
        price_before_coupon=1658,
        valid_classes=['econom'],
    )
    pricing_data_preparer.set_cost(1608, 1658)

    taxi_integration.invalidate_caches()

    offer_coupon = {
        'code': 'discount10',
        'value': 100,
        'percent': 10,
        'limit': 50,
        'valid': True,
        'classes': ['econom'],
    }

    request = copy.deepcopy(TEST_REQUEST_BODY)
    request['requirements']['coupon'] = offer_coupon['code']

    response = taxi_integration.post('v1/orders/estimate', json=request)

    assert response.status_code == 200
    content = response.json()

    offer = rs_utils.get_user_offer(content['offer'], content['user_id'], db)

    coupon_info = offer.get('extra_data', {}).get('coupon')
    assert coupon_info == offer_coupon

    price = 1658
    discount = offer_coupon['limit']
    assert price - discount == offer['prices'][0]['price']

    assert price == content['service_levels'][0]['price_ride_raw']
    assert price - discount == content['service_levels'][0]['price_raw']


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff', 'comfortplus', 'minivan'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'comfortplus', 'child_tariff', 'minivan'],
    },
    ROUTER_MAPS_ENABLED=True,
    INTEGRATION_API_ESTIMATE_USE_DRIVER_ETA=True,
)
@pytest.mark.now('2018-04-24T08:15:00+0000')
@pytest.mark.user_experiments('fixed_price', 'use_discounts_service')
def test_multiple_service_levels(
        taxi_integration,
        mockserver,
        db,
        discounts,
        test_fixtures,
        load_json,
        pricing_data_preparer,
):
    pricing_data_preparer.set_strikeout(100)

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return load_json('get_four.json')

    request_body = {
        'user': {
            'phone': '+79061112255',
            'personal_phone_id': 'p00000000000000000000005',
            'user_id': 'e4707fc6e79e4562b4f0af20a8e877a3',
        },
        'requirements': {'nosmoking': True},
        'route': [
            [37.1946401739712, 55.478983901730004],
            [37.565210, 55.734434],
        ],
        'selected_class': 'comfortplus',
        'all_classes': True,
        'chainid': 'chainid_1',
        'payment': {'type': 'cash'},
    }

    response = taxi_integration.post(
        'v1/orders/estimate', json=request_body, headers=CC_HEADERS,
    )
    assert response.status_code == 200, response.text
    response_body = response.json()

    service_levels = response_body['service_levels']

    classes = ['econom', 'child_tariff', 'comfortplus', 'minivan']
    assert len(service_levels) == len(classes)

    for level in service_levels:
        assert level['class'] in classes

    offer = rs_utils.get_saved_offer(db)
    for price in offer['prices']:
        assert price['cls'] in classes


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff', 'comfortplus'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'comfortplus', 'child_tariff'],
    },
    ROUTER_MAPS_ENABLED=True,
    INTEGRATION_API_ESTIMATE_USE_DRIVER_ETA=True,
)
@pytest.mark.now('2018-04-24T08:15:00+0000')
@pytest.mark.user_experiments('fixed_price', 'use_discounts_service')
def test_concistency(
        taxi_integration,
        mockserver,
        db,
        discounts,
        test_fixtures,
        pricing_data_preparer,
):
    pricing_data_preparer.set_strikeout(100)

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return rs_utils.get_surge_calculator_response(request, 2)

    # 'all_classes' == False
    request_body = {
        'user': {
            'phone': '+79061112255',
            'personal_phone_id': 'p00000000000000000000005',
            'user_id': 'e4707fc6e79e4562b4f0af20a8e877a3',
        },
        'requirements': {'nosmoking': True},
        'route': [
            [37.1946401739712, 55.478983901730004],
            [37.565210, 55.734434],
        ],
        'selected_class': 'comfortplus',
        'all_classes': False,
        'chainid': 'chainid_1',
        'payment': {'type': 'cash'},
    }

    responses_levels = []
    classes = ['econom', 'child_tariff', 'comfortplus']
    for cls in classes:
        request_body['selected_class'] = cls
        response = taxi_integration.post(
            'v1/orders/estimate', json=request_body, headers=CC_HEADERS,
        )
        assert response.status_code == 200, response.text
        response_body = response.json()
        service_levels = response_body['service_levels']
        assert len(service_levels) == 1
        responses_levels.append(service_levels[0])

    request_body['all_classes'] = True
    response = taxi_integration.post(
        'v1/orders/estimate', json=request_body, headers=CC_HEADERS,
    )
    assert response.status_code == 200, response.text

    response_body = response.json()
    service_levels = response_body['service_levels']
    assert len(service_levels) == len(classes)

    def get_class(x):
        return x['class']

    assert responses_levels.sort(key=get_class) == service_levels.sort(
        key=get_class,
    )


CALL_CENTER_USER = {
    'phone': '+79061112255',
    'personal_phone_id': 'p00000000000000000000005',
    'user_id': 'e4707fc6e79e4562b4f0af20a8e877a3',
}

CORP_CABINET_USER = {
    'phone': '+79061112288',
    'personal_phone_id': 'p00000000000000000000008',
    'user_id': 'e4707fc6e79e4562b4f0af20a8e877a8',
}


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff', 'comfortplus', 'minivan'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'comfortplus', 'child_tariff', 'minivan'],
    },
    ROUTER_MAPS_ENABLED=True,
    INTEGRATION_API_ESTIMATE_USE_DRIVER_ETA=True,
)
@pytest.mark.now('2018-04-24T08:15:00+0000')
@pytest.mark.user_experiments('fixed_price', 'no_cars_order_available')
@pytest.mark.parametrize(
    'source_id, headers, user_info, expected_response_file',
    [
        (
            None,
            CC_HEADERS,
            CALL_CENTER_USER,
            'offer_prices_call_center_user.json',
        ),
        (
            'corp_cabinet',
            {},
            CORP_CABINET_USER,
            'offer_prices_corp_cabinet_user.json',
        ),
    ],
)
def test_call_pricing_data_preparer(
        taxi_integration,
        mockserver,
        db,
        discounts,
        test_fixtures,
        load_json,
        source_id,
        headers,
        user_info,
        expected_response_file,
        pricing_data_preparer,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return load_json('get_four.json')

    pricing_data_preparer.set_strikeout(100)
    pricing_data_preparer.set_cost(933, 933)
    pricing_data_preparer.set_user_category_prices_id(
        'c/b7c4d5f6aa3b40a3807bb74b3bc042af',
    )
    pricing_data_preparer.set_cost(943, 943, category='econom')
    pricing_data_preparer.set_user_category_prices_id(
        'c/b7c4d5f6aa3b40a3807bb74b3bc042a3', category='econom',
    )

    request_body = {
        'user': user_info,
        'requirements': {'nosmoking': True},
        'route': [
            [37.1946401739712, 55.478983901730004],
            [37.565210, 55.734434],
        ],
        'selected_class': 'comfortplus',
        'all_classes': True,
        'chainid': 'chainid_1',
        'payment': {'type': 'cash'},
    }
    if source_id:
        request_body['sourceid'] = source_id

    response = taxi_integration.post(
        'v1/orders/estimate', json=request_body, headers=headers,
    )
    assert response.status_code == 200, response.text

    offer = rs_utils.get_saved_offer(db)
    expected = load_json(expected_response_file)
    for price in expected:
        price['pricing_data'] = pricing_data_preparer.get_pricing_data(
            category=price['cls'],
        )
    prices = sorted(offer['prices'], key=lambda x: x['cls'])
    assert prices == expected


PDP_SURGE = {'sp': 1.1, 'sp_alpha': 0.2, 'sp_beta': 0.8, 'sp_surcharge': 1.4}


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff', 'comfortplus', 'minivan'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'comfortplus', 'child_tariff', 'minivan'],
    },
    ROUTER_MAPS_ENABLED=True,
    INTEGRATION_API_ESTIMATE_USE_DRIVER_ETA=True,
)
@pytest.mark.user_experiments('fixed_price', 'no_cars_order_available')
@pytest.mark.parametrize(
    'user, pdp_fixed_price',
    [(None, False), (None, True), (CORP_CABINET_USER, True)],
    ids=['no_user_no_fix', 'no_user_with_fix', 'with_user'],
)
@pytest.mark.parametrize(
    'pdp_data, expected_offer_data,'
    'cost_breakdown, expected_details_tariff, offer_discount',
    [
        (
            {
                'price': 321,
                'driver_price': 654,
                'surge': PDP_SURGE,
                'strikeout': 321,
            },
            dict(price=321, driver_price=654, **PDP_SURGE),
            [
                {
                    'display_amount': 'Ride 321 rub, ~49 min',
                    'display_name': 'cost',
                },
            ],
            [
                {'type': 'price', 'value': 'from 99 rub'},
                {
                    'type': 'comment',
                    'value': '5 min included thereafter 9 rub/min',
                },
                {
                    'type': 'comment',
                    'value': '2 km included thereafter 9 rub/km',
                },
            ],
            None,
        ),
        (
            {
                'price': 321,
                'driver_price': 654,
                'surge': PDP_SURGE,
                'discount': {
                    'price': 140,
                    'value': 0.5,
                    'discount_offer_id': '123456',
                },
                'strikeout': 642,
            },
            dict(price=321, driver_price=654, **PDP_SURGE),
            [
                {'display_amount': '50%', 'display_name': 'base_discount'},
                {
                    'display_amount': 'Ride 321 rub, ~49 min',
                    'display_name': 'cost',
                },
                {
                    'display_amount': '642 rub',
                    'display_name': 'cost_without_discount',
                },
                {'display_amount': '50%', 'display_name': 'discount'},
                {'display_amount': '50%', 'display_name': 'total_discount'},
            ],
            [
                {'type': 'price', 'value': 'from 99 rub'},
                {
                    'type': 'comment',
                    'value': '5 min included thereafter 9 rub/min',
                },
                {
                    'type': 'comment',
                    'value': '2 km included thereafter 9 rub/km',
                },
            ],
            'pdp_offer_discount.json',
        ),
    ],
    ids=['setup_new_prices', 'setup_prices_and_discounts'],
)
def test_use_new_pricing_simple(
        taxi_integration,
        mockserver,
        db,
        discounts,
        test_fixtures,
        load_json,
        experiments3,
        pdp_data,
        expected_offer_data,
        pricing_data_preparer,
        user,
        cost_breakdown,
        expected_details_tariff,
        now,
        offer_discount,
        pdp_fixed_price,
):
    pricing_data_preparer.set_strikeout(pdp_data['strikeout'])
    pricing_data_preparer.set_cost(pdp_data['price'], pdp_data['driver_price'])
    pricing_data_preparer.set_fixed_price(pdp_fixed_price)
    pricing_data_preparer.set_tariff_info(
        included_minutes=5,
        included_kilometers=2,
        price_per_minute=9,
        price_per_kilometer=9,
    )
    pricing_data_preparer.set_meta('min_price', 99)
    pricing_data_preparer.set_trip_information(time=49 * 60, distance=1)
    pricing_data_preparer.set_user_category_prices_id(
        'c/b7c4d5f6aa3b40a3807bb74b3bc042af',
    )

    cost_breakdown = [
        item
        for item in cost_breakdown
        if item['display_name'] != 'base_discount'
    ]
    expected_details_tariff = [
        detail
        for detail in expected_details_tariff
        if detail['type'] == 'price'
    ]

    if 'discount' in pdp_data:
        pdp_disc = pdp_data['discount']
        pricing_data_preparer.set_discount()
        pricing_data_preparer.set_discount_meta(
            pdp_disc['price'], pdp_disc['value'],
        )

    if user:
        expected_prices = load_json('simple_offer.json')
        for price in expected_prices:
            if 'surge' in pdp_data:
                pricing_data_preparer.set_user_surge(
                    pdp_data['surge']['sp'],
                    alpha=pdp_data['surge']['sp_alpha'],
                    beta=pdp_data['surge']['sp_beta'],
                    surcharge=pdp_data['surge']['sp_surcharge'],
                )
            price.update(expected_offer_data)
            price['using_new_pricing'] = True
            price['pricing_data'] = pricing_data_preparer.get_pricing_data()

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return load_json('get_four.json')

    request_body = {
        'requirements': {'nosmoking': True},
        'route': [
            [37.1946401739712, 55.478983901730004],
            [37.565210, 55.734434],
        ],
        'selected_class': 'comfortplus',
        'sourceid': 'corp_cabinet',
        'chainid': 'chainid_1',
        'payment': {'type': 'cash'},
    }
    if user:
        request_body['user'] = user

    response = taxi_integration.post('v1/orders/estimate', json=request_body)
    assert response.status_code == 200
    response_value = response.json()

    if user:
        offer = rs_utils.get_offer(response_value['offer'], db)
        assert (
            sorted(offer['prices'], key=lambda x: x['cls']) == expected_prices
        )

        assert offer['_id'] == response_value['offer']
        assert offer['authorized']
        assert offer['created'] == now.replace(microsecond=0)
        assert not offer['destination_is_airport']
        assert offer['classes_requirements'] == {
            'comfortplus': {'nosmoking': True},
            'econom': {'nosmoking': True},
            'child_tariff': {'nosmoking': True},
            'minivan': {'nosmoking': True},
        }
        assert offer['route'] == [
            [37.1946401739712, 55.478983901730004],
            [37.565210, 55.734434],
        ]
        assert offer['user_id'] == user['user_id']

        if offer_discount:
            expected_offer_discount = load_json(offer_discount)
            offer_discount = offer['discount']
            offer_discount['by_classes'] = sorted(
                offer_discount['by_classes'], key=lambda d: d['class'],
            )
            offer_discount['cashbacks'] = sorted(
                offer_discount['cashbacks'], key=lambda d: d['class'],
            )
            assert offer_discount == expected_offer_discount
    else:
        assert 'offer' not in response_value

    service_levels = response_value['service_levels']
    response_cost_breakdown = service_levels[0]['cost_message_details'][
        'cost_breakdown'
    ]
    assert {v['display_name']: v for v in response_cost_breakdown} == {
        v['display_name']: v for v in cost_breakdown
    }
    if not user:
        assert not response_value['is_fixed_price']

    details_tariff = service_levels[0]['details_tariff']
    assert details_tariff == expected_details_tariff


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff', 'comfortplus', 'minivan'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'comfortplus', 'child_tariff', 'minivan'],
    },
    ROUTER_MAPS_ENABLED=True,
    INTEGRATION_API_ESTIMATE_USE_DRIVER_ETA=True,
)
@pytest.mark.user_experiments('fixed_price', 'no_cars_order_available')
@pytest.mark.parametrize(
    'trip_info, fixed_price, expected_price, config_enabled',
    [
        ({'time': 49 * 60, 'distance': 1}, True, '123 rub', True),
        ({'time': 49 * 60, 'distance': 1}, False, '~120 rub', True),
        (None, False, '99 rub for the first 5 min and 2 km', True),
        ({'time': 49 * 60, 'distance': 1}, True, '123 rub', False),
        ({'time': 49 * 60, 'distance': 1}, False, '123 rub', False),
        (None, False, '99 rub for the first 5 min and 2 km', False),
    ],
)
def test_approximate_price(
        taxi_integration,
        mockserver,
        config,
        db,
        discounts,
        test_fixtures,
        load_json,
        pricing_data_preparer,
        trip_info,
        fixed_price,
        expected_price,
        config_enabled,
):
    config.set(INTEGRATION_API_SHOW_APPROXIMATE_PRICE=config_enabled)
    pricing_data_preparer.set_strikeout(123)
    pricing_data_preparer.set_cost(123, 321)
    pricing_data_preparer.set_fixed_price(fixed_price)
    pricing_data_preparer.set_tariff_info(
        included_minutes=5,
        included_kilometers=2,
        price_per_minute=9,
        price_per_kilometer=9,
    )
    pricing_data_preparer.set_meta('min_price', 99)
    if trip_info:
        pricing_data_preparer.set_trip_information(**trip_info)
    else:
        pricing_data_preparer.set_no_trip_information()
    pricing_data_preparer.set_user_category_prices_id(
        'c/b7c4d5f6aa3b40a3807bb74b3bc042af',
    )

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return load_json('get_four.json')

    request_body = {
        'requirements': {'nosmoking': True},
        'route': [
            [37.1946401739712, 55.478983901730004],
            [37.565210, 55.734434],
        ],
        'selected_class': 'comfortplus',
        'sourceid': 'corp_cabinet',
        'chainid': 'chainid_1',
        'payment': {'type': 'cash'},
        'user': CORP_CABINET_USER,
    }

    response = taxi_integration.post('v1/orders/estimate', json=request_body)
    assert response.status_code == 200
    response_value = response.json()
    service_levels = response_value['service_levels'][0]
    assert service_levels['price'] == expected_price


PDP_COST_BREAKDOWN = [
    {'display_amount': 'Ride 200 rub, ~49 min', 'display_name': 'cost'},
    {'display_amount': '500 rub', 'display_name': 'cost_without_discount'},
    {'display_amount': '60%', 'display_name': 'discount'},
    {'display_amount': '60%', 'display_name': 'total_discount'},
]

PDP_ROUND_BREAKDOWN = [
    {'display_amount': 'Ride 300 rub, ~49 min', 'display_name': 'cost'},
    {'display_amount': '520 rub', 'display_name': 'cost_without_discount'},
    {'display_amount': '42%', 'display_name': 'discount'},
    {'display_amount': '42%', 'display_name': 'total_discount'},
]

PDP_NO_DISCOUNT_COST_BREAKDOWN = [
    {'display_amount': 'Ride 200 rub, ~49 min', 'display_name': 'cost'},
]

PDP_NO_REPLACE_COST_BREAKDOWN = [
    {'display_amount': 'Ride 200 rub, ~49 min', 'display_name': 'cost'},
    {'display_amount': '235 rub', 'display_name': 'cost_without_discount'},
    {'display_amount': '15%', 'display_name': 'call_center_discount'},
    {'display_amount': '15%', 'display_name': 'discount'},
    {'display_amount': '15%', 'display_name': 'total_discount'},
]

PDP_FALLBACK_PRICE_COST_BREAKDOWN = [
    {'display_amount': 'Ride 200 rub, ~49 min', 'display_name': 'cost'},
]

PDP_DEFAULT_TARIFF_DETAILS = [{'type': 'price', 'value': 'from 123 rub'}]

PDP_DISABLED_TARIFF_DETAILS = [
    {'type': 'price', 'value': 'from 101 rub'},
    {'type': 'comment', 'value': '5 min included thereafter 9 rub/min'},
    {'type': 'comment', 'value': '2 km included thereafter 9 rub/km'},
]

PDP_FALLBACK_TARIFF_DETAILS = [{'type': 'price', 'value': 'from 123 rub'}]


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff', 'comfortplus', 'minivan'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'comfortplus', 'child_tariff', 'minivan'],
    },
    ROUTER_MAPS_ENABLED=True,
    INTEGRATION_USER_CONSISTENCY_CHECK=True,
    INTEGRATION_API_ESTIMATE_USE_DRIVER_ETA=True,
    INTEGRATION_TARIFFS_ENABLED=True,
)
@pytest.mark.user_experiments('fixed_price', 'no_cars_order_available')
@pytest.mark.parametrize(
    'fixed_price, user_price,'
    ' strikeout_price, expected_cost_breakdown, expected_tariff_details',
    [
        (True, 200, 500, PDP_COST_BREAKDOWN, PDP_DEFAULT_TARIFF_DETAILS),
        (
            True,
            200,
            0,
            PDP_NO_DISCOUNT_COST_BREAKDOWN,
            PDP_DEFAULT_TARIFF_DETAILS,
        ),
        (
            True,
            200,
            199,
            PDP_NO_DISCOUNT_COST_BREAKDOWN,
            PDP_DEFAULT_TARIFF_DETAILS,
        ),
        (
            True,
            200,
            201,
            PDP_NO_DISCOUNT_COST_BREAKDOWN,
            PDP_DEFAULT_TARIFF_DETAILS,
        ),
        (True, 300, 520, PDP_ROUND_BREAKDOWN, PDP_DEFAULT_TARIFF_DETAILS),
        (
            False,
            200,
            0,
            PDP_FALLBACK_PRICE_COST_BREAKDOWN,
            PDP_FALLBACK_TARIFF_DETAILS,
        ),
    ],
    ids=[
        'simple_discounts',
        'zero_strikeout',
        'strikeout_less_then_price',
        'almost_zero_discount',
        'rounding_discount',
        'fixed_price_fallback',
    ],
)
def test_use_new_pricing_tariff_details(
        taxi_integration,
        mockserver,
        config,
        db,
        discounts,
        test_fixtures,
        load_json,
        pricing_data_preparer,
        user_price,
        strikeout_price,
        expected_cost_breakdown,
        fixed_price,
        expected_tariff_details,
):
    discounts.set_discount_response(
        {
            'discounts': [
                {
                    'class': 'econom',
                    'discount': {
                        'value': 0.11,
                        'original_value': 0.11,
                        'price': 800.0,
                        'reason': 'for_all',
                        'method': 'full-driver-less',
                    },
                },
            ],
            'discount_offer_id': '123456',
        },
    )

    pricing_data_preparer.set_meta('min_price', 123)
    pricing_data_preparer.set_strikeout(strikeout_price)
    pricing_data_preparer.set_cost(user_price, 100)
    pricing_data_preparer.set_fixed_price(fixed_price)
    pricing_data_preparer.set_trip_information(time=49 * 60, distance=1000)

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return load_json('get_four.json')

    request_body = {
        'requirements': {'nosmoking': True},
        'route': [
            [37.1946401739712, 55.478983901730004],
            [37.565210, 55.734434],
        ],
        'selected_class': 'comfortplus',
        'chainid': 'chainid_1',
        'payment': {'type': 'cash'},
        'user': CALL_CENTER_USER,
    }

    response = taxi_integration.post(
        'v1/orders/estimate', json=request_body, headers=CC_HEADERS,
    )
    assert response.status_code == 200
    response_value = response.json()

    service_levels = response_value['service_levels'][0]
    cost_breakdown = service_levels['cost_message_details']['cost_breakdown']
    assert cost_breakdown == expected_cost_breakdown
    assert service_levels['details_tariff'] == expected_tariff_details


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff', 'comfortplus', 'minivan'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'comfortplus', 'child_tariff', 'minivan'],
    },
    ROUTER_MAPS_ENABLED=True,
    INTEGRATION_API_ESTIMATE_USE_DRIVER_ETA=True,
    PROTOCOL_CREATE_PIN_IN_PIN_STORAGE=True,
)
@pytest.mark.user_experiments('fixed_price', 'no_cars_order_available')
def test_use_new_pricing_with_preorder(
        taxi_integration, mockserver, db, load_json, pricing_data_preparer,
):
    pricing_data_preparer.set_cost(42, 24)
    pricing_data_preparer.set_fixed_price(False)
    pricing_data_preparer.set_strikeout(49)

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return load_json('get_four.json')

    @mockserver.json_handler('/maps-router/route_jams/')
    def mock_route(request):
        return {}

    pins = []

    @mockserver.json_handler('/pin_storage/v1/create_pin')
    def mock_pin_storage_create_pin(request):
        pins.append(request.json)
        return {}

    @mockserver.handler('/driver-eta/eta')
    def _mock_dricer_eta(request):
        return mockserver.make_response('', 200)

    request_body = {
        'requirements': {'nosmoking': True},
        'route': [
            [37.1946401739712, 55.478983901730004],
            [37.565210, 55.734434],
        ],
        'selected_class': 'comfortplus',
        'chainid': 'chainid_1',
        'payment': {'type': 'cash'},
        'due': '2020-06-03T21:00:00.000Z',
        'preorder_request_id': 'f98f3ebbac344fcca6c7886a487b69a5',
        'user': CALL_CENTER_USER,
    }

    response = taxi_integration.post(
        'v1/orders/estimate', json=request_body, headers=CC_HEADERS,
    )
    assert response.status_code == 200, response.text
    response_value = response.json()

    offer = rs_utils.get_offer(response_value['offer'], db)
    for offer_price in offer['prices']:
        assert offer_price['price'] == 42.0
        assert offer_price['driver_price'] == 24.0
    assert offer['_id'] == response_value['offer']
    service_levels = response_value['service_levels']
    response_cost_breakdown = {
        v['display_name']: v['display_amount']
        for v in service_levels[0]['cost_message_details']['cost_breakdown']
    }
    assert response_cost_breakdown['cost_without_discount'] == '49 rub'
    assert not response_value['is_fixed_price']
    mock_pin_storage_create_pin.wait_call()
    assert pins[0]['pin']['client']['name'] == 'call_center'


def _make_pdp_user_info(
        user_id='',
        payment_type='cash',
        payment_method='',
        user_agent=service_client.DEFAULT_USER_AGENT,
):
    return {
        'application': {
            'name': 'android',
            'platform_version': '6.0.0',
            'version': '3.18.0',
            'user_agent': user_agent,
        },
        'payment_info': {
            'cashback_enabled': True,
            'method_id': payment_method,
            'type': payment_type,
        },
        'user_id': user_id,
    }


PDP_DEFAULT_REQUEST = {
    'calc_additional_prices': {
        'antisurge': False,
        'plus_promo': False,
        'combo_order': False,
        'combo_inner': False,
        'combo_outer': False,
        'alt_offer_discount': False,
        'full_auction': False,
        'strikeout': True,
    },
    'categories': ['econom', 'comfortplus', 'minivan'],
    'classes_requirements': {},
    'modifications_scope': 'taxi',
    'tolls': 'DENY',
    'user_info': _make_pdp_user_info('zd71eea389d7cf65277e5f0024170f1f'),
    'waypoints': [
        [37.1946401739712, 55.478983901730004],
        [37.56521, 55.734434],
    ],
    'zone': 'moscow',
}


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff', 'comfortplus', 'minivan'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'comfortplus', 'child_tariff', 'minivan'],
    },
    ROUTER_MAPS_ENABLED=True,
    INTEGRATION_API_ESTIMATE_USE_DRIVER_ETA=True,
    INTEGRATION_API_ALLOW_ZUSER_APPS=['light_business'],
    TARIFF_CATEGORIES_VISIBILITY={
        '__default__': {'child_tariff': {'visible_by_default': False}},
    },
)
@pytest.mark.user_experiments('fixed_price', 'no_cars_order_available')
@pytest.mark.parametrize(
    'request_patch, pdp_request_patch, random_zuser',
    [
        ({}, {}, True),
        (
            {'selected_class': 'child_tariff'},
            {
                'categories': [
                    'econom',
                    'comfortplus',
                    'minivan',
                    'child_tariff',
                ],
            },
            True,
        ),
        (
            {'due': '2020-06-02T12:40:00.000Z'},
            {'due': '2020-06-02T15:40:00+0300'},
            True,
        ),
        (
            {
                'user': {'user_id': 'zaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'},
                'sourceid': 'light_business',
            },
            {
                'user_info': _make_pdp_user_info(
                    'zaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
                ),
            },
            False,
        ),
        (
            {
                'payment': {'type': 'corp', 'payment_method_id': 'corp-1234'},
                'sourceid': 'corp_cabinet',
            },
            {
                'categories': ['econom', 'comfortplus'],
                'user_info': _make_pdp_user_info(
                    payment_type='corp', payment_method='corp-1234',
                ),
            },
            True,
        ),
    ],
    ids=[
        'anonymous_user',
        'unavailable_class_request',
        'preorder_request',
        'zuser_request',
        'corp_payment_anon_user',
    ],
)
@pytest.mark.parametrize('locale', [None, 'en-US', 'ru-RU'])
def test_use_new_pricing_request(
        taxi_integration,
        mockserver,
        config,
        db,
        discounts,
        test_fixtures,
        load_json,
        pricing_data_preparer,
        request_patch,
        pdp_request_patch,
        random_zuser,
        locale,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return load_json('get_four.json')

    pricing_data_preparer.set_strikeout(100)
    request_body = {
        'route': [
            [37.1946401739712, 55.478983901730004],
            [37.565210, 55.734434],
        ],
        'selected_class': 'comfortplus',
        'sourceid': 'corp_cabinet',
        'chainid': 'chainid_1',
        'payment': {'type': 'cash'},
    }
    request_body.update(request_patch)

    headers = {}
    if locale:
        headers['Accept-Language'] = locale
        pricing_data_preparer.set_locale(locale[:2])

    response = taxi_integration.post(
        'v1/orders/estimate', json=request_body, headers=headers,
    )
    assert response.status_code == 200
    pdp_request = pricing_data_preparer.last_request
    pdp_expected_request = copy.deepcopy(PDP_DEFAULT_REQUEST)
    pdp_expected_request.update(pdp_request_patch)

    if random_zuser:
        assert 'user_info' in pdp_request
        assert pdp_request['user_info'].pop('user_id').startswith('z')
        if 'user_id' in pdp_expected_request['user_info']:
            del pdp_expected_request['user_info']['user_id']

    assert pricing_data_preparer.last_request == pdp_expected_request


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff', 'comfortplus', 'minivan'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'comfortplus', 'child_tariff', 'minivan'],
    },
    ROUTER_MAPS_ENABLED=True,
    INTEGRATION_API_ESTIMATE_USE_DRIVER_ETA=True,
    SMART_PRICING_FALLBACK_SETTINGS={'enabled': True, 'forced_enabled': True},
)
@pytest.mark.user_experiments('fixed_price', 'no_cars_order_available')
def test_pricing_data_preparer_fallback(
        taxi_integration,
        mockserver,
        config,
        db,
        discounts,
        test_fixtures,
        load_json,
        pricing_data_preparer,
        pricing_data_preparer_fallback,
        now,
):
    pricing_data_preparer.set_error()
    pricing_data_preparer_fallback.set_strikeout(100)
    pricing_data_preparer_fallback.set_user_category_prices_id(
        'c/b7c4d5f6aa3b40a3807bb74b3bc042af',
    )
    pricing_data_preparer_fallback.set_cost(915, 915)

    expected_prices = load_json(
        'test_use_new_pricing_simple/simple_offer.json',
    )
    for price in expected_prices:
        price['is_fixed_price'] = False
        price['using_new_pricing'] = True
        price[
            'pricing_data'
        ] = pricing_data_preparer_fallback.get_pricing_data()

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return load_json('get_four.json')

    user = CORP_CABINET_USER
    request_body = {
        'requirements': {'nosmoking': True},
        'route': [
            [37.1946401739712, 55.478983901730004],
            [37.565210, 55.734434],
        ],
        'selected_class': 'comfortplus',
        'sourceid': 'corp_cabinet',
        'chainid': 'chainid_1',
        'payment': {'type': 'cash'},
        'user': user,
    }

    response = taxi_integration.post('v1/orders/estimate', json=request_body)
    assert response.status_code == 200
    response_value = response.json()

    offer = rs_utils.get_offer(response_value['offer'], db)
    assert sorted(offer['prices'], key=lambda x: x['cls']) == expected_prices
    assert offer['_id'] == response_value['offer']
    assert offer['authorized']
    assert offer['created'] == now.replace(microsecond=0)
    assert not offer['destination_is_airport']
    assert offer['classes_requirements'] == {
        'comfortplus': {'nosmoking': True},
        'econom': {'nosmoking': True},
        'child_tariff': {'nosmoking': True},
        'minivan': {'nosmoking': True},
    }
    assert offer['route'] == [
        [37.1946401739712, 55.478983901730004],
        [37.565210, 55.734434],
    ]
    assert offer['user_id'] == user['user_id']

    service_levels = response_value['service_levels']
    response_cost_breakdown = service_levels[0]['cost_message_details'][
        'cost_breakdown'
    ]
    cost_breakdown = [
        {'display_amount': 'Ride 915 rub, ~1 min', 'display_name': 'cost'},
    ]
    assert (
        sorted(response_cost_breakdown, key=lambda v: v['display_name'])
        == cost_breakdown
    )


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff', 'comfortplus', 'minivan'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'comfortplus', 'child_tariff', 'minivan'],
    },
    ROUTER_MAPS_ENABLED=True,
    INTEGRATION_API_ESTIMATE_USE_DRIVER_ETA=True,
    SMART_PRICING_FALLBACK_SETTINGS={
        'enabled': False,
        'forced_enabled': False,
    },
)
@pytest.mark.user_experiments('fixed_price', 'no_cars_order_available')
def test_pricing_fallback_disabled(
        taxi_integration,
        mockserver,
        db,
        discounts,
        test_fixtures,
        load_json,
        pricing_data_preparer,
        pricing_data_preparer_fallback,
):
    pricing_data_preparer.set_error()
    pricing_data_preparer_fallback.set_strikeout(100)

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return load_json('get_four.json')

    request_body = {
        'requirements': {'nosmoking': True},
        'route': [
            [37.1946401739712, 55.478983901730004],
            [37.565210, 55.734434],
        ],
        'selected_class': 'comfortplus',
        'sourceid': 'corp_cabinet',
        'chainid': 'chainid_1',
        'payment': {'type': 'cash'},
        'user': CORP_CABINET_USER,
    }

    response = taxi_integration.post('v1/orders/estimate', json=request_body)
    assert response.status_code == 500


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff', 'comfortplus', 'minivan'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'comfortplus', 'child_tariff', 'minivan'],
    },
    INTEGRATION_API_ESTIMATE_USE_DRIVER_ETA=True,
)
@pytest.mark.parametrize(
    ('pdp_response_code', 'estimate_response_code'),
    [
        pytest.param(200, 200, id='pdp_code_200'),
        pytest.param(400, 500, id='pdp_code_400'),
        pytest.param(429, 500, id='pdp_code_429'),
        pytest.param(500, 500, id='pdp_code_500'),  # without pricing-fallback
    ],
)
def test_pdp_response_code(
        taxi_integration,
        mockserver,
        db,
        test_fixtures,
        load_json,
        pdp_response_code,
        estimate_response_code,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return load_json('get_four.json')

    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def _mock_v2_prepare(request):
        if pdp_response_code == 400:
            response_json = {
                'message': 'error UNABLE_TO_MATCH_TARIFF',
                'code': 'UNABLE_TO_MATCH_TARIFF',
            }
            return mockserver.make_response(json.dumps(response_json), 400)
        elif pdp_response_code != 200:
            return mockserver.make_response({}, pdp_response_code)
        return load_json('pdp-response.json')

    request_body = {
        'requirements': {'nosmoking': True},
        'route': [
            [37.1946401739712, 55.478983901730004],
            [37.565210, 55.734434],
        ],
        'selected_class': 'comfortplus',
        'sourceid': 'corp_cabinet',
        'chainid': 'chainid_1',
        'payment': {'type': 'cash'},
        'user': CORP_CABINET_USER,
    }

    response = taxi_integration.post('v1/orders/estimate', json=request_body)
    assert response.status_code == estimate_response_code


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff', 'comfortplus', 'minivan'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'comfortplus', 'child_tariff', 'minivan'],
    },
    ROUTER_MAPS_ENABLED=True,
    INTEGRATION_API_ESTIMATE_USE_DRIVER_ETA=True,
)
@pytest.mark.experiments3(filename='experiments3_offer_coupon.json')
@pytest.mark.user_experiments('fixed_price', 'no_cars_order_available')
@pytest.mark.parametrize(
    'pdp_data, pdp_coupon, response_price,'
    'offer_price, request_coupon, offer_coupon',
    [
        (
            {'price': 454, 'driver_price': 907},
            {'price_before_coupon': 1000, 'value': 150, 'percent': 25},
            {'price_raw': 454, 'price_ride_raw': 1000},
            {'price': 454, 'driver_price': 907},
            {'coupon': 'ABBA'},
            {
                'code': 'ABBA',
                'limit': 1000.0,
                'percent': 25,
                'valid': True,
                'value': 150.0,
            },
        ),
    ],
    ids=['coupon_in_new_pricing_only'],
)
def test_use_new_pricing_coupons(
        taxi_integration,
        mockserver,
        db,
        discounts,
        test_fixtures,
        load_json,
        pdp_data,
        pdp_coupon,
        offer_price,
        request_coupon,
        response_price,
        pricing_data_preparer,
        offer_coupon,
):
    if pdp_data:
        pricing_data_preparer.set_cost(
            pdp_data['price'], pdp_data['driver_price'],
        )

    pricing_data_preparer.set_user_surge(1)
    pricing_data_preparer.set_driver_surge(1)
    pricing_data_preparer.set_strikeout(100)
    pricing_data_preparer.set_user_category_prices_id(
        'c/b7c4d5f6aa3b40a3807bb74b3bc042af',
    )

    if pdp_coupon:
        pricing_data_preparer.set_coupon(
            pdp_coupon['value'],
            pdp_coupon['percent'],
            pdp_coupon['price_before_coupon'],
        )

    expected_offer = load_json('simple_offer.json')
    for price in expected_offer:
        price['pricing_data'] = pricing_data_preparer.get_pricing_data()
        price['driver_price'] = offer_price['driver_price']
        price['price'] = offer_price['price']
        price['using_new_pricing'] = True

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return load_json('get_four.json')

    request_body = {
        'user': CORP_CABINET_USER,
        'requirements': {'nosmoking': True},
        'route': [
            [37.1946401739712, 55.478983901730004],
            [37.565210, 55.734434],
        ],
        'selected_class': 'comfortplus',
        'sourceid': 'corp_cabinet',
        'all_classes': False,
        'chainid': 'chainid_1',
        'payment': {'type': 'cash'},
    }
    if request_coupon:
        request_body['requirements'].update(request_coupon)

    response = taxi_integration.post('v1/orders/estimate', json=request_body)
    assert response.status_code == 200
    response_value = response.json()

    assert 'offer' in response_value
    offer = rs_utils.get_offer(response_value['offer'], db)
    prices = sorted(offer['prices'], key=lambda x: x['cls'])
    assert prices == expected_offer

    service_levels = response_value['service_levels'][0]
    assert service_levels['price_raw'] == response_price['price_raw']
    if 'price_ride_raw' in response_price:
        assert (
            service_levels['price_ride_raw']
            == response_price['price_ride_raw']
        )
    if offer_coupon:
        assert offer['extra_data']['coupon'] == offer_coupon


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.parametrize(
    'request_body, headers, offer_extra_data, offer_prices,'
    'details_tariff, cost_breakdown, surge, pdp_data,'
    ' pdp_tariff_cat_info, fixed_price, pdp_trip_info, '
    'expected_response_price, expected_response_time, price_raw',
    [
        (
            CALLCENTER_WITH_DECOUPLING_REQUEST,
            CC_HEADERS,
            OFFER_EXTRA_DATA_SUCCESS_PDP_PRICES_CALL_CENTER,
            [
                {
                    'cls': 'econom',
                    'cat_type': 'call_center',
                    'category_id': 'user_decoupling_category_id',
                    'price': 123.0,
                    'driver_price': 123.0,
                    'sp': 2.0,
                    'is_fixed_price': True,
                    'using_new_pricing': True,
                },
            ],
            DETAILS_DECOUPLING_FROM_NEW_PRICING_RESPONSE,
            [
                {
                    'display_amount': 'Ride 123 rub, ~98 min',
                    'display_name': 'cost',
                },
            ],
            5.0,
            {
                'user_price': 123,
                'driver_price': 321,
                'user_surge': 2,
                'driver_surge': 4,
                'discount': None,
            },
            PDP_TARIFF_CATEGORY_INFO,
            True,
            {'time': 49 * 60, 'distance': 10},
            '123 rub',
            '98 min',
            123,
        ),
        (
            CORP_CABINET_WITH_DECOUPLING_REQUEST,
            {},
            OFFER_EXTRA_DATA_SUCCESS_PDP_PRICES_CORP_CABINET,
            [
                {
                    'cls': 'econom',
                    'cat_type': 'application',
                    'category_id': 'user_decoupling_category_id',
                    'price': 123.0,
                    'driver_price': 123.0,
                    'sp': 2.0,
                    'is_fixed_price': True,
                    'using_new_pricing': True,
                },
            ],
            DETAILS_DECOUPLING_FROM_NEW_PRICING_RESPONSE,
            [
                {
                    'display_amount': 'Ride 123 rub, ~98 min',
                    'display_name': 'cost',
                },
            ],
            5.0,
            {
                'user_price': 123,
                'driver_price': 321,
                'user_surge': 2,
                'driver_surge': 4,
                'discount': None,
            },
            PDP_TARIFF_CATEGORY_INFO,
            True,
            {'time': 49 * 60, 'distance': 10},
            '123 rub',
            '98 min',
            123,
        ),
        (
            CORP_CABINET_WITH_DECOUPLING_REQUEST,
            {},
            OFFER_EXTRA_DATA_PDP_NO_FIX_PRICES,
            [
                {
                    'cls': 'econom',
                    'cat_type': 'application',
                    'category_id': 'user_decoupling_category_id',
                    'price': 123.0,
                    'driver_price': 123.0,
                    'sp': 2.0,
                    'is_fixed_price': False,
                    'using_new_pricing': True,
                },
            ],
            DETAILS_DECOUPLING_FROM_NEW_PRICING_RESPONSE,
            [
                {
                    'display_amount': 'Ride 123 rub, ~98 min',
                    'display_name': 'cost',
                },
            ],
            5.0,
            {
                'user_price': 123,
                'driver_price': 321,
                'user_surge': 2,
                'driver_surge': 4,
                'discount': None,
            },
            PDP_TARIFF_CATEGORY_INFO,
            False,
            {'time': 49 * 60, 'distance': 10},
            '123 rub',
            '98 min',
            123,
        ),
        (
            CORP_CABINET_WITH_DECOUPLING_REQUEST,
            {},
            OFFER_EXTRA_DATA_PDP_NO_FIX_PRICES,
            [
                {
                    'cls': 'econom',
                    'cat_type': 'application',
                    'category_id': 'user_decoupling_category_id',
                    'price': 123.0,
                    'driver_price': 123.0,
                    'sp': 2.0,
                    'is_fixed_price': False,
                    'using_new_pricing': True,
                },
            ],
            DETAILS_DECOUPLING_FROM_NEW_PRICING_RESPONSE,
            [],
            5.0,
            {
                'user_price': 123,
                'driver_price': 321,
                'user_surge': 2,
                'driver_surge': 4,
                'discount': None,
            },
            PDP_TARIFF_CATEGORY_INFO,
            False,
            None,
            '198 rub for the first 1 min and 2 km',
            None,
            None,
        ),
        (
            CORP_CABINET_WITH_DECOUPLING_REQUEST,
            {},
            OFFER_EXTRA_DATA_SUCCESS_PDP_PRICES_CORP_CABINET,
            [
                {
                    'cls': 'econom',
                    'cat_type': 'application',
                    'category_id': 'user_decoupling_category_id',
                    'price': 123.0,
                    'driver_price': 123.0,
                    'sp': 2.0,
                    'is_fixed_price': True,
                    'using_new_pricing': True,
                },
            ],
            DETAILS_DECOUPLING_FROM_NEW_PRICING_RESPONSE,
            [
                {
                    'display_amount': 'Ride 123 rub, ~0 min',
                    'display_name': 'cost',
                },
            ],
            5.0,
            {
                'user_price': 123,
                'driver_price': 321,
                'user_surge': 2,
                'driver_surge': 4,
                'discount': None,
            },
            PDP_TARIFF_CATEGORY_INFO,
            True,
            {'time': 0, 'distance': 0},
            '123 rub',
            '0 min',
            123,
        ),
    ],
    ids=[
        'simple_callcenter_decoupling',
        'simple_corp_cabinet_decoupling',
        'disabled_fixed_price_from_new_pricing_approximate_price',
        'disabled_fixed_price_from_new_pricing_min_price',
        'fixed_price_with_empty_route',
    ],
)
@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    TVM_ENABLED=True,
    TVM_DISABLE_CHECK=['integration-api'],
    TVM_RULES=[{'src': 'integration-api', 'dst': 'corp-integration-api'}],
    ALL_CATEGORIES=['econom', 'child_tariff', 'comfortplus', 'minivan'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'comfortplus', 'child_tariff', 'minivan'],
    },
    INT_API_FALLBACK_PRICES_ON_PDP_ERROR=True,
    PASSENGER_TIME_RESERVE_COEFFICIENT={'__default__': 2},
)
@pytest.mark.user_experiments('fixed_price', 'use_discounts_service')
@pytest.mark.experiments3(filename='experiments3_offer_coupon.json')
def test_decoupling_with_new_pricing(
        taxi_integration,
        db,
        load_json,
        test_fixtures,
        mockserver,
        now,
        request_body,
        headers,
        offer_extra_data,
        details_tariff,
        offer_prices,
        cost_breakdown,
        surge,
        pricing_data_preparer,
        pdp_data,
        pdp_tariff_cat_info,
        fixed_price,
        pdp_trip_info,
        expected_response_price,
        expected_response_time,
        price_raw,
):

    user_id = request_body['user']['user_id']

    pricing_data_preparer.set_decoupling(True, category='econom')
    pricing_data_preparer.set_cost(
        pdp_data['user_price'], pdp_data['driver_price'],
    )
    pricing_data_preparer.set_user_surge(pdp_data['user_surge'])
    pricing_data_preparer.set_driver_surge(pdp_data['driver_surge'])
    pricing_data_preparer.set_strikeout(pdp_data['user_price'])
    pricing_data_preparer.set_meta('min_price', 198)
    pricing_data_preparer.set_fixed_price(fixed_price)
    pricing_data_preparer.set_user_category_prices_id(
        pdp_tariff_cat_info['user_category_prices_id'],
        pdp_tariff_cat_info['user_category_id'],
        pdp_tariff_cat_info['user_tariff_id'],
    )
    pricing_data_preparer.set_driver_category_prices_id(
        pdp_tariff_cat_info['driver_category_prices_id'],
        pdp_tariff_cat_info['driver_category_id'],
        pdp_tariff_cat_info['driver_tariff_id'],
    )
    if pdp_trip_info:
        pricing_data_preparer.set_trip_information(
            time=pdp_trip_info['time'], distance=pdp_trip_info['distance'],
        )
    else:
        pricing_data_preparer.set_no_trip_information()

    pricing_data_preparer.set_tariff_info(
        included_minutes=1,
        included_kilometers=2,
        price_per_minute=3,
        price_per_kilometer=4,
    )
    offer_prices = copy.deepcopy(offer_prices)
    for offer_price in offer_prices:
        offer_price['pricing_data'] = pricing_data_preparer.get_pricing_data(
            category=offer_price['cls'],
        )

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return get_surge_calculator_response(request, surge, load_json)

    response = taxi_integration.post(
        'v1/orders/estimate', json=request_body, headers=headers,
    )

    assert response.status_code == 200
    response_body = response.json()
    assert response_body['user_id'] == user_id

    assert 'offer' in response_body
    assert response_body['is_fixed_price'] == fixed_price

    currency_rules = response_body['currency_rules']
    assert currency_rules['code'] == 'RUB'
    assert currency_rules['sign'] == ''
    assert currency_rules['template'] == '$VALUE$ $SIGN$$CURRENCY$'
    assert currency_rules['text'] == 'rub'

    service_levels = response_body['service_levels']
    assert service_levels[0]['class'] == 'econom'
    response_cost_breakdown = service_levels[0]['cost_message_details'][
        'cost_breakdown'
    ]
    ordered_object.assert_eq(cost_breakdown, response_cost_breakdown, [''])

    assert service_levels[0]['price'] == expected_response_price
    if price_raw:
        assert service_levels[0]['price_raw'] == price_raw
    if expected_response_time:
        assert service_levels[0]['time'] == expected_response_time
    else:
        assert 'time' not in service_levels[0]
    assert service_levels[0]['estimated_waiting']['message'] == '14 min'
    assert service_levels[0]['estimated_waiting']['seconds'] == 839
    assert service_levels[0]['details_tariff'] == details_tariff

    offer = rs_utils.get_user_offer(
        response_body['offer'], response_body['user_id'], db,
    )
    assert offer is not None

    assert offer['prices'] == offer_prices

    assert offer['_id'] == response_body['offer']
    assert offer['authorized']
    assert offer['created'] == now.replace(microsecond=0)
    assert not offer['destination_is_airport']
    assert offer['classes_requirements'] == {
        'econom': {'nosmoking': True},
        'child_tariff': {'nosmoking': True},
        'comfortplus': {'nosmoking': True},
    }
    assert offer['route'] == [
        [37.1946401739712, 55.478983901730004],
        [37.565210, 55.734434],
    ]
    assert offer['user_id'] == user_id
    assert offer['extra_data'] == offer_extra_data
    if pdp_trip_info:
        assert offer['time'] == pdp_trip_info['time']
        assert offer['distance'] == pdp_trip_info['distance']
    assert pricing_data_preparer.calls == 1


@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    TVM_ENABLED=True,
    TVM_DISABLE_CHECK=['integration-api'],
    TVM_RULES=[{'src': 'integration-api', 'dst': 'corp-integration-api'}],
    ALL_CATEGORIES=['econom'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'comfortplus', 'child_tariff', 'minivan'],
    },
    INT_API_FALLBACK_PRICES_ON_PDP_ERROR=True,
)
@pytest.mark.user_experiments('fixed_price', 'use_discounts_service')
@pytest.mark.experiments3(filename='experiments3_offer_coupon.json')
def test_new_pricing_decoupling_failed_on_requested_categories_only(
        taxi_integration,
        db,
        load_json,
        test_fixtures,
        mockserver,
        now,
        pricing_data_preparer,
):

    user_id = CORP_CABINET_WITH_DECOUPLING_REQUEST['user']['user_id']
    surge = 1

    pricing_data_preparer.set_strikeout(100)
    pricing_data_preparer.set_decoupling(True)
    pricing_data_preparer.set_decoupling(False, category='econom')
    pricing_data_preparer.set_fixed_price(True)
    pricing_data_preparer.set_meta('min_price', 198)
    pricing_data_preparer.set_user_surge(sp=1.0)
    pricing_data_preparer.set_user_category_prices_id(
        PDP_TARIFF_CATEGORY_INFO['user_category_prices_id'],
        PDP_TARIFF_CATEGORY_INFO['user_category_id'],
        PDP_TARIFF_CATEGORY_INFO['user_tariff_id'],
    )
    pricing_data_preparer.set_driver_category_prices_id(
        PDP_TARIFF_CATEGORY_INFO['driver_category_prices_id'],
        PDP_TARIFF_CATEGORY_INFO['driver_category_id'],
        PDP_TARIFF_CATEGORY_INFO['driver_tariff_id'],
    )
    pricing_data_preparer.set_trip_information(time=60 * 30, distance=1000)

    offer_prices = [
        {
            'cls': 'econom',
            'cat_type': 'application',
            'category_id': 'user_decoupling_category_id',
            'price': 100.0,
            'driver_price': 100.0,
            'sp': 1.0,
            'is_fixed_price': True,
            'using_new_pricing': True,
        },
    ]
    for offer_price in offer_prices:
        offer_price['pricing_data'] = pricing_data_preparer.get_pricing_data(
            category=offer_price['cls'],
        )

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return get_surge_calculator_response(request, surge, load_json)

    response = taxi_integration.post(
        'v1/orders/estimate', json=CORP_CABINET_WITH_DECOUPLING_REQUEST,
    )

    assert response.status_code == 200
    response_body = response.json()
    assert response_body['user_id'] == user_id

    assert 'offer' in response_body
    assert response_body['is_fixed_price']

    currency_rules = response_body['currency_rules']
    assert currency_rules['code'] == 'RUB'
    assert currency_rules['sign'] == ''
    assert currency_rules['template'] == '$VALUE$ $SIGN$$CURRENCY$'
    assert currency_rules['text'] == 'rub'

    service_levels = response_body['service_levels']
    assert service_levels[0]['class'] == 'econom'
    response_cost_breakdown = service_levels[0]['cost_message_details'][
        'cost_breakdown'
    ]
    response_cost_breakdown == [
        {'display_amount': 'Ride 100 rub, ~30 min', 'display_name': 'cost'},
    ]

    assert service_levels[0]['price'] == '100 rub'
    assert service_levels[0]['time'] == '30 min'
    assert service_levels[0]['estimated_waiting']['message'] == '14 min'
    assert service_levels[0]['estimated_waiting']['seconds'] == 839
    assert (
        service_levels[0]['details_tariff']
        == DETAILS_DECOUPLING_FROM_NEW_PRICING_RESPONSE
    )

    offer = rs_utils.get_user_offer(
        response_body['offer'], response_body['user_id'], db,
    )
    assert offer is not None

    assert offer['prices'] == offer_prices

    assert offer['_id'] == response_body['offer']
    assert offer['authorized']
    assert offer['created'] == now.replace(microsecond=0)
    assert not offer['destination_is_airport']
    assert offer['prices'] == offer_prices
    assert offer['classes_requirements'] == {'econom': {'nosmoking': True}}
    assert offer['route'] == [
        [37.1946401739712, 55.478983901730004],
        [37.565210, 55.734434],
    ]
    assert offer['user_id'] == user_id
    assert offer['extra_data'] == OFFER_EXTRA_DATA_SUCCESS_PDP_FALLBACK
    assert pricing_data_preparer.calls == 1


PDP_FALLBACK_OFFER_PRICES = [
    {
        'cls': 'econom',
        'cat_type': 'application',
        'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
        'price': 4571.0,
        'driver_price': 4571.0,
        'sp': 5.0,
        'is_fixed_price': True,
        'using_new_pricing': False,
    },
]

OFFER_EXTRA_DATA_SUCCESS_PDP_FALLBACK = {
    'decoupling': {
        'success': False,
        'error': {
            'reason': 'plugin_internal_error',
            'stage': 'calculating_offer',
        },
    },
}


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.parametrize(
    'offer_extra_data, offer_prices, discount_response,'
    'price_with_currency, details_tariff, '
    'cost_breakdown, surge, '
    'user_id, sourceid, pdp_data',
    [
        (
            OFFER_EXTRA_DATA_SUCCESS_PDP_FALLBACK,
            PDP_FALLBACK_OFFER_PRICES,
            {'discounts': [], 'discount_offer_id': '123456'},
            '99 rub',
            [{'type': 'price', 'value': 'from 100 rub'}],
            [
                {
                    'display_amount': 'Ride 99 rub, ~1 min',
                    'display_name': 'cost',
                },
            ],
            5.0,
            'e4707fc6e79e4562b4f0af20a8e877a8',
            'corp_cabinet',
            {
                'user_price': 123,
                'driver_price': 321,
                'user_surge': 2,
                'driver_surge': 4,
                'discount': None,
            },
        ),
    ],
    ids=['decoupled_corp_cabinet'],
)
@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    TVM_ENABLED=True,
    TVM_DISABLE_CHECK=['integration-api'],
    TVM_RULES=[{'src': 'integration-api', 'dst': 'corp-integration-api'}],
    ALL_CATEGORIES=['econom', 'child_tariff', 'comfortplus', 'minivan'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'comfortplus', 'child_tariff', 'minivan'],
    },
    SMART_PRICING_FALLBACK_SETTINGS={'enabled': True, 'forced_enabled': True},
)
@pytest.mark.user_experiments('fixed_price', 'use_discounts_service')
@pytest.mark.experiments3(filename='experiments3_offer_coupon.json')
def test_decoupling_fallback_with_new_pricing(
        taxi_integration,
        db,
        discounts,
        load_json,
        test_fixtures,
        mockserver,
        tvm2_client,
        offer_extra_data,
        discount_response,
        details_tariff,
        offer_prices,
        price_with_currency,
        cost_breakdown,
        surge,
        user_id,
        sourceid,
        pricing_data_preparer,
        pricing_data_preparer_fallback,
        pdp_data,
):

    discounts.set_discount_response(discount_response)
    pricing_data_preparer.set_error(500)

    pricing_data_preparer_fallback.set_cost(99, 99)
    pricing_data_preparer_fallback.set_strikeout(99)
    pricing_data_preparer_fallback.set_decoupling(True)
    pricing_data_preparer_fallback.set_user_category_prices_id(
        PDP_TARIFF_CATEGORY_INFO['user_category_prices_id'],
        PDP_TARIFF_CATEGORY_INFO['user_category_id'],
        PDP_TARIFF_CATEGORY_INFO['user_tariff_id'],
    )
    pricing_data_preparer_fallback.set_driver_category_prices_id(
        PDP_TARIFF_CATEGORY_INFO['driver_category_prices_id'],
        PDP_TARIFF_CATEGORY_INFO['driver_category_id'],
        PDP_TARIFF_CATEGORY_INFO['driver_tariff_id'],
    )

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return get_surge_calculator_response(request, surge, load_json)

    ticket = 'ticket'
    tvm2_client.set_ticket(json.dumps({'24': {'ticket': ticket}}))

    @mockserver.json_handler('/corp_integration_api/tariffs')
    def mock_tariffs(request):
        assert request.headers['X-Ya-Service-Ticket'] == ticket
        return load_json('decoupling/tariffs_response.json')

    request_body = load_json('decoupling/request.json')
    request_body['sourceid'] = sourceid
    request_body['user']['user_id'] = user_id
    response = taxi_integration.post('v1/orders/estimate', json=request_body)

    assert response.status_code == 200
    response_body = response.json()
    assert response_body['user_id'] == user_id

    assert 'offer' in response_body
    assert not response_body['is_fixed_price']

    currency_rules = response_body['currency_rules']
    assert currency_rules['code'] == 'RUB'
    assert currency_rules['sign'] == ''
    assert currency_rules['template'] == '$VALUE$ $SIGN$$CURRENCY$'
    assert currency_rules['text'] == 'rub'

    service_levels = response_body['service_levels']
    assert service_levels[0]['class'] == 'econom'
    response_cost_breakdown = service_levels[0]['cost_message_details'][
        'cost_breakdown'
    ]
    ordered_object.assert_eq(cost_breakdown, response_cost_breakdown, [''])

    assert service_levels[0]['price'] == price_with_currency
    assert service_levels[0]['estimated_waiting']['message'] == '14 min'
    assert service_levels[0]['estimated_waiting']['seconds'] == 839
    assert service_levels[0]['details_tariff'] == details_tariff
    assert pricing_data_preparer.calls == 1


@pytest.mark.parametrize(
    'driver_eta_new_flow_enabled',
    [
        pytest.param(
            False,
            marks=pytest.mark.experiments3(
                filename='experiments3_driver_eta_v1.json',
            ),
            id='v1',
        ),
        pytest.param(
            True,
            marks=pytest.mark.experiments3(
                filename='experiments3_driver_eta_v2.json',
            ),
            id='v2',
        ),
    ],
)
@pytest.mark.config(
    APPLICATION_DETECTION_RULES_NEW={
        'rules': [
            {'@app_name': 'agent_007', 'match': 'agent_gepard'},
            {'@app_name': 'foolish', '@app_ver1': '2'},
        ],
    },
)
def test_driver_eta_request_with_auth_context(
        taxi_integration,
        load_json,
        test_fixtures,
        test_fixture_surge,
        mockserver,
        tvm2_client,
        pricing_data_preparer,
        driver_eta_new_flow_enabled,
):
    pricing_data_preparer.set_strikeout(100)

    def _parse_app_vars(application_header):
        result = {}
        for key_value in application_header.split(','):
            key, value = key_value.split('=')
            result[key] = value
        return result

    def _check_headers(headers):
        assert headers.get('X-YaTaxi-PhoneId') == '5a7b678babae14bb0db4453f'
        assert 'X-Request-Application' in headers
        app_vars = _parse_app_vars(headers.get('X-Request-Application'))
        assert 'app_name' in app_vars
        assert app_vars.get('app_name') == 'agent_007'

    @mockserver.json_handler('/driver-eta/eta')
    def mock_eta_drivers(request):
        _check_headers(request.headers)
        return load_json('eta_response.json')

    @mockserver.json_handler('/driver-eta/driver-eta/v2/eta')
    def mock_eta_drivers_v2(request):
        _check_headers(request.headers)
        return load_json('driver_eta_v2.json')

    response = taxi_integration.post(
        'v1/orders/estimate',
        json=TEST_REQUEST_BODY,
        headers={'User-Agent': 'agent_gepard'},
    )
    assert response.status_code == 200
    if driver_eta_new_flow_enabled:
        assert mock_eta_drivers_v2.times_called > 0
    else:
        assert mock_eta_drivers.times_called > 0


@pytest.mark.parametrize(
    'agent_user_type,is_valid',
    [
        (None, True),
        ('individual', True),
        ('corporate', True),
        ('unsupported', False),
    ],
)
def test_agent_user_type_check(
        taxi_integration,
        db,
        load_json,
        mockserver,
        pricing_data_preparer,
        test_fixture_surge,
        agent_user_type,
        is_valid,
):
    pricing_data_preparer.set_strikeout(100)

    @mockserver.json_handler('/driver-eta/eta')
    def mock_eta_drivers(request):
        excpected_headers = {'X-YaTaxi-PhoneId': '5a7b678babae14bb0db4453f'}
        for key, value in excpected_headers.items():
            assert request.headers.get(key) == value

        return load_json('eta_response.json')

    request = copy.deepcopy(TEST_REQUEST_BODY)
    if agent_user_type is not None:
        request['agent'] = {
            'agent_user_type': agent_user_type,
            'agent_id': '007',
        }
    response = taxi_integration.post('v1/orders/estimate', json=request)

    pdp_request = pricing_data_preparer.last_request
    if is_valid:
        assert response.status_code == 200
        disable_discounts = False
        if 'extra' in pdp_request and 'providers' in pdp_request['extra']:
            discounts = pdp_request['extra']['providers'].get('discounts')
            if discounts:
                assert 'is_enabled' in discounts
                disable_discounts = not (discounts['is_enabled'])
        assert disable_discounts == bool(agent_user_type)
        r_json = response.json()

        offer = rs_utils.get_user_offer(r_json['offer'], r_json['user_id'], db)
        assert offer is not None

        if agent_user_type is None:
            assert offer.get('agent_user_type') is None
        else:
            assert offer['agent']['agent_user_type'] == agent_user_type
    else:
        assert response.status_code == 400
        assert pdp_request is None


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff', 'comfortplus', 'minivan'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'comfortplus', 'child_tariff', 'minivan'],
    },
    ROUTER_MAPS_ENABLED=True,
    INTEGRATION_API_ESTIMATE_USE_DRIVER_ETA=True,
)
@pytest.mark.experiments3(filename='experiments3_offer_coupon.json')
@pytest.mark.user_experiments('fixed_price', 'no_cars_order_available')
def test_new_pricing_ya_plus(
        taxi_integration,
        mockserver,
        db,
        discounts,
        test_fixtures,
        load_json,
        pricing_data_preparer,
):
    pricing_data_preparer.set_cost(97, 97)
    pricing_data_preparer.set_strikeout(114)
    pricing_data_preparer.set_meta('yaplus_delta_raw', 17.1)

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return load_json('get_four.json')

    request_body = {
        'user': CORP_CABINET_USER,
        'requirements': {'nosmoking': True},
        'route': [
            [37.1946401739712, 55.478983901730004],
            [37.565210, 55.734434],
        ],
        'selected_class': 'comfortplus',
        'sourceid': 'corp_cabinet',
        'all_classes': False,
        'chainid': 'chainid_1',
        'payment': {'type': 'cash'},
    }

    response = taxi_integration.post('v1/orders/estimate', json=request_body)
    assert response.status_code == 200
    response_value = response.json()

    service_levels = response_value['service_levels'][0]
    cost_breakdown = {
        v['display_name']: v['display_amount']
        for v in service_levels['cost_message_details']['cost_breakdown']
    }
    assert cost_breakdown['ya_plus_discount'] == '15%'
    assert cost_breakdown['total_discount'] == '15%'
    assert cost_breakdown['cost_without_discount'] == '114 rub'


@pytest.mark.config(
    ALL_CATEGORIES=['econom'],
    APPLICATION_BRAND_CATEGORIES_SETS={'__default__': ['econom']},
    ROUTER_MAPS_ENABLED=True,
    INTEGRATION_API_ESTIMATE_USE_DRIVER_ETA=True,
    INTEGRATION_API_ESTIMATE_SERVICE_LEVEL_TITLES_ENABLED=True,
)
@pytest.mark.now('2018-04-24T08:15:00+0000')
@pytest.mark.user_experiments('fixed_price', 'use_discounts_service')
@pytest.mark.parametrize(
    'button_title',
    [{}, {'button_title': 'routestats.tariff.econom.button_title'}],
)
@pytest.mark.parametrize(
    'button_title_glued',
    [
        {},
        {'button_title_glued': 'routestats.tariff.econom.button_title_glued'},
    ],
)
@pytest.mark.parametrize(
    'tariff_requirements, request_requirements, glued_title_expected',
    [
        pytest.param(None, None, False, id='no_glued_requirements'),
        pytest.param(
            {'s.0.glued_requirements': ['check']},
            {'check': True},
            False,
            id='glued_requirement_selected',
        ),
        pytest.param(
            {
                's.0.glued_requirements': ['check'],
                's.0.glued_optional_requirements': ['check'],
            },
            None,
            False,
            id='optional_glued_requirement',
        ),
        pytest.param(
            {'s.0.glued_requirements': ['check']},
            None,
            True,
            id='obligatory_glued_requirement',
        ),
    ],
)
def test_service_level_title(
        taxi_integration,
        mockserver,
        config,
        db,
        discounts,
        test_fixtures,
        load_json,
        pricing_data_preparer,
        button_title,
        button_title_glued,
        tariff_requirements,
        request_requirements,
        glued_title_expected,
):
    pricing_data_preparer.set_strikeout(100)

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return load_json('get_four.json')

    # prepare config ZONES_TARIFFS_SETTINGS
    config.set_values(
        {
            'ZONES_TARIFFS_SETTINGS': {
                '__default__': {
                    'econom': {'keys': {**button_title, **button_title_glued}},
                },
            },
        },
    )

    # prepare tariff_settings
    if tariff_requirements:
        db.tariff_settings.update_one(
            {'hz': 'moscow'}, {'$set': tariff_requirements},
        )

    # prepare request
    request = load_json('request.json')
    if request_requirements:
        request['requirements'] = request_requirements

    response = taxi_integration.post(
        'v1/orders/estimate', json=request, headers=CC_HEADERS,
    )
    assert response.status_code == 200, response.text
    response_body = response.json()

    service_levels = response_body['service_levels']
    assert len(service_levels) == 1

    response_button_title = service_levels[0].get('title')

    if button_title_glued and glued_title_expected:
        assert response_button_title == 'Button glued title'
    elif button_title:
        assert response_button_title == 'Button custom title'
    else:
        assert response_button_title is None


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff', 'comfortplus', 'minivan'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'comfortplus', 'child_tariff', 'minivan'],
    },
    ROUTER_MAPS_ENABLED=True,
    INTEGRATION_API_ESTIMATE_USE_DRIVER_ETA=True,
)
@pytest.mark.now('2018-04-24T08:15:00+0000')
@pytest.mark.user_experiments('fixed_price', 'use_discounts_service')
@pytest.mark.config(
    INTEGRATION_API_WHITELABELS_DROP_DESTINATIONS_IN_ESTIMATE={
        '__default__': False,
        '/whitelabel/whitelabel_0': True,
    },
)
@pytest.mark.parametrize(
    'order_origin, explicit_requirements, expected_code, destination_dropped, with_forced_fixprice',
    [
        pytest.param(
            'unknown/whitelabel_0',
            True,
            400,
            None,
            False,
            id='unknown_order_explicit_requirements',
        ),
        pytest.param(
            'superweb/whitelabel_0',
            True,
            200,
            True,
            False,
            id='superweb_order_explicit_requirements_destination_dropped',
        ),
        pytest.param(
            'superweb/whitelabel_0',
            True,
            200,
            False,
            True,
            id='superweb_order_explicit_requirements_with_forced_fixprice',
        ),
        pytest.param(
            'superweb/whitelabel_1',
            False,
            200,
            False,
            False,
            id='superweb_order_no_explicit_requirements',
        ),
        pytest.param(
            'turboapp/whitelabel_0',
            False,
            200,
            True,
            False,
            id='turboapp_order_no_explicit_requirements_destination_dropped',
        ),
        pytest.param(
            'turboapp/whitelabel_1',
            False,
            200,
            False,
            False,
            id='turboapp_order_no_explicit_requirements',
        ),
    ],
)
def test_whitelabel(
        taxi_integration,
        whitelabel_fixtures,
        mockserver,
        discounts,
        test_fixtures,
        test_fixture_surge,
        pricing_data_preparer,
        order_origin,
        explicit_requirements,
        expected_code,
        destination_dropped,
        with_forced_fixprice,
):
    forced_fixprice = 10

    if destination_dropped:
        pricing_data_preparer.set_no_trip_information()

    pricing_data_preparer.set_tariff_info(
        included_minutes=5,
        included_kilometers=2,
        price_per_minute=9,
        price_per_kilometer=9,
    )
    user_agent = f'Mozilla/5.0 Chrome/89.0 whitelabel/{order_origin}'
    request = {
        'payment': {'type': 'cash'},
        'route': [
            [37.1946401739712, 55.478983901730004],
            [37.56521, 55.734434],
        ],
        'selected_class': 'econom',
        'sourceid': 'turboapp',
        'user': {
            'personal_phone_id': 'p00000000000000000000005',
            'user_id': f'{order_origin}_user_id',
        },
    }
    if explicit_requirements:
        request['white_label_requirements'] = {
            'source_park_id': 'park_id',
            'dispatch_requirement': 'only_source_park',
        }
        if with_forced_fixprice:
            request['white_label_requirements'][
                'forced_fixprice'
            ] = forced_fixprice

    response = taxi_integration.post(
        'v1/orders/estimate', json=request, headers={'User-Agent': user_agent},
    )
    assert response.status_code == expected_code

    if response.status_code != 200:
        return

    response_body = response.json()

    pdp_request = pricing_data_preparer.last_request
    assert len(pdp_request['waypoints']) == (1 if destination_dropped else 2)

    assert response_body['is_fixed_price'] == (not destination_dropped)

    econom_data = next(
        level
        for level in response_body['service_levels']
        if level['class'] == 'econom'
    )
    assert econom_data['is_fixed_price'] == (not destination_dropped)

    if with_forced_fixprice:
        assert pdp_request['extra']['forced_fixprice'] == 10.0

    if destination_dropped:
        assert econom_data['price'] == '100 rub for the first 5 min and 2 km'
        assert econom_data['min_price'] == 100.00

        assert 'offer' not in response_body
    else:
        assert econom_data['price'] == f'100 rub'
        assert econom_data['price_raw'] == 100.00

        assert 'offer' in response_body

    assert test_fixtures.mock_driver_eta.times_called == 1
    driver_eta_request = test_fixtures.driver_eta_requests[0]

    assert 'white_label_requirements' in driver_eta_request
    assert driver_eta_request['white_label_requirements'] == {
        'source_park_id': 'park_id',
        'dispatch_requirement': 'only_source_park',
    }


@pytest.mark.config(
    INTEGRATION_SUPPORTED_APPLICATIONS=['some_app', 'agent_gepard'],
    INTEGRATION_API_USE_APP_INSTEAD_OF_SOURCE_ID=['some_app', 'agent_gepard'],
    APPLICATION_DETECTION_RULES_NEW={
        'rules': [
            {'match': 'some_app', '@app_name': 'some_app', '@app_ver1': '2'},
            {
                'match': 'agent_gepard',
                '@app_name': 'agent_gepard',
                '@app_ver1': '2',
            },
            {'@app_name': 'foolish', '@app_ver1': '2'},
        ],
    },
)
@pytest.mark.config(ALL_CATEGORIES=['econom', 'child_tariff'])
@pytest.mark.now('2018-04-24T10:15:00+0000')
@pytest.mark.parametrize(
    'sourceid, application, category_price_id, expected_valid_until',
    [
        (
            'svo_order',
            'call_center',
            TRANSFER_CATEGORY_PRICES_ID,
            '2018-04-24T10:30:00+0000',  # valid_until = now + SVO_DUE_OFFSET
        ),
        (None, 'some_app', NOT_TRANSFER_CATEGORY_PRICES_ID, None),
        (
            None,
            'agent_gepard',
            NOT_TRANSFER_CATEGORY_PRICES_ID,
            '2018-04-24T10:25:00+0000',  # valid_until = now + DEFAULT_URGENCY
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_include_valid_until_field.json')
def test_including_valid_until(
        taxi_integration,
        db,
        test_fixture_surge,
        test_fixtures,
        sourceid,
        application,
        category_price_id,
        expected_valid_until,
        pricing_data_preparer,
):
    pricing_data_preparer.set_strikeout(100)
    pricing_data_preparer.set_user_category_prices_id(category_price_id)
    pricing_data_preparer.set_driver_category_prices_id(category_price_id)
    db.users.remove()
    db.user_phones.remove()

    request_body = {
        'user': {
            'phone': '+79061112200',
            'personal_phone_id': 'p00000000000000000000000',
        },
        'requirements': {'nosmoking': True},
        'route': [
            [37.411956, 55.981682],
            [37.907173584260395, 55.90891808601154],
        ],
        'selected_class': 'econom',
        'sourceid': sourceid,
        'chainid': 'chainid_1',
    }
    headers = {}
    if not sourceid:
        headers = {'User-Agent': application}
    response = taxi_integration.post(
        'v1/orders/estimate', json=request_body, headers=headers,
    )
    assert response.status_code == 200
    if expected_valid_until is not None:
        assert response.json().get('valid_until') == expected_valid_until
    else:
        assert 'valid_until' not in response.json()


@pytest.mark.config(
    INTEGRATION_SUPPORTED_APPLICATIONS=['call_center', 'agent_gepard'],
    INTEGRATION_API_USE_APP_INSTEAD_OF_SOURCE_ID=[
        'call_center',
        'agent_gepard',
    ],
    APPLICATION_DETECTION_RULES_NEW={
        'rules': [
            {
                'match': 'call_center',
                '@app_name': 'call_center',
                '@app_ver1': '2',
            },
            {
                'match': 'agent_gepard',
                '@app_name': 'agent_gepard',
                '@app_ver1': '2',
            },
            {'@app_name': 'foolish', '@app_ver1': '2'},
        ],
    },
)
@pytest.mark.parametrize('application', ['call_center', 'agent_gepard'])
@pytest.mark.experiments3(filename='exp3_forward_expected_prices.json')
def test_expected_prices(
        taxi_integration,
        db,
        load_json,
        mockserver,
        pricing_data_preparer,
        test_fixture_surge,
        application,
):
    @mockserver.json_handler('/driver-eta/eta')
    def mock_eta_drivers(_):
        return load_json('eta_response.json')

    @mockserver.json_handler('/pin_storage/v1/create_pin')
    def mock_pin_storage_create_pin(_):
        return {}

    request = copy.deepcopy(TEST_REQUEST_BODY)
    request['expected_prices'] = [
        {'class': 'econom', 'price': 100},
        {'class': 'child_tariff', 'price': 200},
    ]
    headers = {'User-Agent': application}
    response = taxi_integration.post(
        'v1/orders/estimate', json=request, headers=headers,
    )

    pdp_request = pricing_data_preparer.last_request
    assert response.status_code == 200
    if application == 'agent_gepard':
        assert 'extra' in pdp_request
        assert 'expected_prices' in pdp_request['extra']
        assert pdp_request['extra']['expected_prices'] == {
            'econom': 100,
            'child_tariff': 200,
        }
    else:
        assert 'expected_prices' not in pdp_request.get('extra', {})


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'child_tariff'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'child_tariff'],
    },
    ROUTER_MAPS_ENABLED=True,
    INTEGRATION_API_ESTIMATE_USE_DRIVER_ETA=True,
    PAID_SUPPLY_LONG_TRIP_CRITERIA={
        'moscow': {
            '__default__': {'apply': 'either', 'distance': 1, 'duration': 1},
        },
    },
)
@pytest.mark.experiments3(filename='experiments3_driver_eta_v2.json')
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
@pytest.mark.experiments3(filename='exp3_paid_supply_paid_cancel.json')
@pytest.mark.parametrize(
    'int_api_request_key,int_api_request_value,response_paid_supply,'
    'offer_paid_supply_price,offer_paid_supply_info',
    [
        (
            'payment',
            {'type': 'corp', 'payment_method_id': 'corp-1234'},
            {'paid_supply_price': '146 rub', 'paid_supply_price_raw': 146.0},
            146.0,
            {'distance': 9067, 'time': 939},
        ),
        (
            'route',
            [[37.1946401739712, 55.478983901730004]],
            {
                'enable_conditions': [
                    'change_payment_type_to_cashless',
                    'define_point_b',
                ],
            },
            None,
            None,
        ),
    ],
)
def test_int_api_paid_supply(
        taxi_integration,
        load_json,
        test_fixtures,
        test_fixture_surge,
        mockserver,
        db,
        tvm2_client,
        pricing_data_preparer,
        int_api_request_key,
        int_api_request_value,
        response_paid_supply,
        offer_paid_supply_price,
        offer_paid_supply_info,
):
    pricing_data_preparer.set_cost(
        category='econom', user_cost=517, driver_cost=517,
    )
    pricing_data_preparer.set_cost(
        category='child_tariff', user_cost=489, driver_cost=489,
    )
    pricing_data_preparer.set_paid_supply(
        category='econom', price={'price': 146},
    )
    pricing_data_preparer.set_meta('min_price', 101)
    expected_category_ids = {
        'econom': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
        'child_tariff': '471995706dc948489584c4179f7a6827',
    }
    for cls, id in expected_category_ids.items():
        pricing_data_preparer.set_fixed_price(category=cls, enable=True)
        pricing_data_preparer.set_user_category_prices_id(
            category=cls, category_prices_id='c/' + id, category_id=id,
        )

    pricing_data_preparer.set_trip_information(
        time=1421.5866954922676, distance=7514.629286628636,
    )

    pricing_data_preparer.set_strikeout(100)

    @mockserver.json_handler('/driver-eta/driver-eta/v2/eta')
    def mock_eta_drivers_v2(_):
        return load_json('driver_eta_v2.json')

    request_json = copy.deepcopy(TEST_REQUEST_BODY)
    request_json[int_api_request_key] = int_api_request_value

    response = taxi_integration.post('v1/orders/estimate', json=request_json)
    assert mock_eta_drivers_v2.times_called > 0
    assert response.status_code == 200

    response_json = response.json()
    service_levels = response_json.get('service_levels', [])
    assert service_levels
    is_econom_exists = False
    for service_level in service_levels:
        if service_level['class'] == 'econom':
            is_econom_exists = True
            assert 'paid_supply' in service_level
            if 'enable_conditions' in response_paid_supply:
                assert 'enable_conditions' in service_level['paid_supply']
                assert sorted(
                    service_level['paid_supply']['enable_conditions'],
                ) == sorted(response_paid_supply['enable_conditions'])
            else:
                assert service_level['paid_supply'] == response_paid_supply
    assert is_econom_exists
    offer = rs_utils.get_saved_offer(db)
    for item in offer['prices']:
        assert 'cls' in item
        if item['cls'] == 'econom':
            assert item['price'] == 517.0
            assert item['driver_price'] == 517.0
            if offer_paid_supply_price is not None:
                assert 'paid_supply_price' in item
                assert item['paid_supply_price'] == offer_paid_supply_price
            if offer_paid_supply_info is not None:
                assert 'paid_supply_info' in item
                assert item['paid_supply_info'] == offer_paid_supply_info
        elif item['cls'] == 'child_tariff':
            assert item['price'] == 489.0
            assert item['driver_price'] == 489.0
            assert 'paid_supply_price' not in item
            assert 'paid_supply_info' not in item
        else:
            assert False


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.user_experiments('fixed_price')
@pytest.mark.config(
    ROUTER_MAPS_ENABLED=True,
    INTEGRATION_SUPPORTED_APPLICATIONS=['agent_gepard'],
    INTEGRATION_API_USE_APP_INSTEAD_OF_SOURCE_ID=['agent_gepard'],
    APPLICATION_DETECTION_RULES_NEW={
        'rules': [
            {
                'match': 'agent_gepard',
                '@app_name': 'agent_gepard',
                '@app_ver1': '2',
            },
            {'@app_name': 'foolish', '@app_ver1': '2'},
        ],
    },
)
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='estimate_save_offer_via_service',
    consumers=['integration/ordersestimate'],
    clauses=[
        {
            'enabled': True,
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
)
@pytest.mark.config(PROTOCOL_GENERATE_OFFER_ID_BY_SERVICE='enabled')
def test_estimate_agent_application(
        taxi_integration,
        test_fixtures,
        test_fixture_surge,
        pricing_data_preparer,
        mockserver,
        mock_order_offers,
):
    pricing_data_preparer.set_strikeout(100)
    pricing_data_preparer.set_categories(['econom'])
    pricing_data_preparer.set_fixed_price(True)

    generated_id = 'offer-id-from-service'

    agent = {
        'agent_id': 'gepard',
        'agent_user_type': 'individual',
        'agent_application': 'callcenter',
    }

    @mockserver.json_handler('/order-offers/v1/generate-offer-id')
    def mock_generate_offer_id(_):
        return {'offer_id': generated_id}

    response = taxi_integration.post(
        'v1/orders/estimate',
        json={
            'selected_class': 'econom',
            'user': {'phone': '+79170127222'},
            'payment': {'type': 'agent', 'payment_method_id': 'agent_gepard'},
            'requirements': {},
            'route': [[37.643018, 55.734985], [37.63703, 55.732399]],
            'agent': agent,
            'use_toll_roads': False,
            'expected_prices': [{'class': 'econom', 'price': 1330.0}],
        },
        headers={'User-Agent': 'agent_gepard'},
    )

    assert response.status_code == 200
    assert response.json().get('offer') == generated_id
    assert mock_generate_offer_id.times_called == 1
    offer = mock_order_offers.get_offer(generated_id)
    assert offer is not None
    assert 'agent' in offer
    assert offer['agent'] == agent
