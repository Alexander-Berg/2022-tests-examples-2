import pytest

from order_notify.repositories.order_info import OrderData
from order_notify.repositories.payment import basic_cost as basic_cost_info


CHOSEN_CANDIDATE = {'tariff_class': 'plus'}


@pytest.mark.parametrize(
    'order, expected_is_include',
    [
        pytest.param({}, False, id='no_current_prices'),
        pytest.param({'current_prices': {}}, False, id='no_final_cost_meta'),
        pytest.param(
            {'current_prices': {'final_cost_meta': {}}},
            False,
            id='no_user_meta',
        ),
        pytest.param(
            {'current_prices': {'final_cost_meta': {'user': {}}}},
            False,
            id='no_use_cost_includes_coupon',
        ),
        pytest.param(
            {
                'current_prices': {
                    'final_cost_meta': {
                        'user': {'use_cost_includes_coupon': 0.5},
                    },
                },
            },
            False,
            id='use_cost_includes_coupon_not_equal_1.0',
        ),
        pytest.param(
            {
                'current_prices': {
                    'final_cost_meta': {
                        'user': {'use_cost_includes_coupon': 1.0},
                    },
                },
            },
            True,
            id='no_coupon_no_new_pricing_coupon',
        ),
        pytest.param(
            {
                'coupon': {},
                'current_prices': {
                    'final_cost_meta': {
                        'user': {'use_cost_includes_coupon': 1.0},
                    },
                },
            },
            True,
            id='no_coupon_was_used_no_new_pricing_coupon',
        ),
        pytest.param(
            {
                'coupon': {'was_used': False},
                'current_prices': {
                    'final_cost_meta': {
                        'user': {'use_cost_includes_coupon': 1.0},
                    },
                },
            },
            True,
            id='false_coupon_was_used_no_new_pricing_coupon',
        ),
        pytest.param(
            {
                'coupon': {'was_used': True},
                'current_prices': {
                    'final_cost_meta': {
                        'user': {'use_cost_includes_coupon': 1.0},
                    },
                },
            },
            False,
            id='coupon_was_used_no_new_pricing_coupon',
        ),
        pytest.param(
            {
                'coupon': {'was_used': False},
                'current_prices': {
                    'final_cost_meta': {
                        'user': {
                            'use_cost_includes_coupon': 1.0,
                            'coupon_value': 10,
                        },
                    },
                },
            },
            False,
            id='false_coupon_was_used_new_pricing_coupon_exists',
        ),
        pytest.param(
            {
                'coupon': {'was_used': True},
                'current_prices': {
                    'final_cost_meta': {
                        'user': {
                            'use_cost_includes_coupon': 1.0,
                            'coupon_value': 10,
                        },
                    },
                },
            },
            True,
            id='coupon_was_used_new_pricing_coupon_exists',
        ),
    ],
)
def test_does_order_cost_consider_coupon(order, expected_is_include):
    is_include = basic_cost_info.does_order_cost_consider_coupon(
        order_data=OrderData(
            brand='', country='', order={}, order_proc={'order': order},
        ),
    )
    assert is_include == expected_is_include


@pytest.mark.parametrize(
    'coupon_data, cost, expected_coupon_value',
    [
        pytest.param(None, 100, 0, id='None_coupon_data'),
        pytest.param({}, 100, 0, id='empty_coupon_data'),
        pytest.param(
            {'valid': True, 'was_used': True, 'value': 25},
            None,
            0,
            id='None_cost',
        ),
        pytest.param(
            {'valid': True, 'was_used': True, 'value': 25},
            0,
            0,
            id='zero_cost',
        ),
        pytest.param({'valid': False}, 100, 0, id='not_valid'),
        pytest.param(
            {'valid': True, 'was_used': False}, 100, 0, id='not_used',
        ),
        pytest.param(
            {'valid': True, 'was_used': True, 'value': 25},
            100,
            25,
            id='no_percent',
        ),
        pytest.param(
            {'valid': True, 'was_used': True, 'percent': 20},
            100,
            20,
            id='percent_exist_no_limit',
        ),
        pytest.param(
            {'valid': True, 'was_used': True, 'percent': 20, 'limit': 21},
            100,
            20,
            id='limit_bigger',
        ),
        pytest.param(
            {'valid': True, 'was_used': True, 'percent': 20, 'limit': 15},
            100,
            15,
            id='limit_less',
        ),
    ],
)
def test_get_coupon_value(coupon_data, cost, expected_coupon_value):
    coupon_value = basic_cost_info.get_coupon_value(
        OrderData(
            brand='',
            country='',
            order={},
            order_proc={'order': {'coupon': coupon_data, 'cost': cost}},
        ),
    )
    assert coupon_value == expected_coupon_value
