import copy
from typing import List
from typing import Optional

import discounts_match  # pylint: disable=E0401
import pytest

from tests_grocery_discounts import common


def _discount_with_orders_restrictionis(orders_restrictions: List[dict]):
    discount = common.small_cart_discount()
    discount['orders_restrictions'] = orders_restrictions
    return discount


@pytest.mark.parametrize(
    'rules, discount, expected_status_code, expected_response',
    (
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'orders_restriction',
                    'values': [
                        {
                            'application_name': 'some_application_name',
                            'allowed_orders_count': {'start': 1, 'end': 10},
                        },
                    ],
                },
            ],
            common.small_cart_discount(),
            200,
            None,
            id='valid_cart_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'tag', 'values': ['some_tag']},
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'money_value': {
                            'set_value': {
                                'value_type': 'absolute',
                                'value': '10.0',
                            },
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
                'discount_meta': {'any': 'meta'},
            },
            200,
            None,
            id='tag_cart_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'class', 'values': ['some_class']},
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'money_value': {
                            'set_value': {
                                'value_type': 'absolute',
                                'value': '10.0',
                            },
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
                'discount_meta': {'any': 'meta'},
            },
            200,
            None,
            id='class_cart_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'class', 'values': ['No class']},
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'money_value': {
                            'cart_value': {
                                'value': [
                                    {
                                        'from_cost': '1.0',
                                        'discount': {
                                            'value_type': 'absolute',
                                            'value': '10.0',
                                        },
                                    },
                                ],
                            },
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
                'discount_meta': {'any': 'meta'},
                'active_with_surge': True,
            },
            200,
            None,
            id='class_no_class_cart_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'experiment',
                    'values': ['some_experiment'],
                },
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'money_value': {
                            'cart_value': {
                                'value': [
                                    {
                                        'from_cost': '1.0',
                                        'discount': {
                                            'value_type': 'fraction',
                                            'value': '10.0',
                                        },
                                    },
                                ],
                                'maximum_discount': '1.3',
                            },
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
                'discount_meta': {'other': 'meta'},
                'active_with_surge': False,
                'max_set_apply_count': 2,
            },
            200,
            None,
            id='experiment_cart_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'experiment',
                    'values': 'Any',
                    'exclusions': ['some_experiment'],
                },
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'money_value': {
                            'cart_value': {
                                'value': [
                                    {
                                        'from_cost': '1.0',
                                        'discount': {
                                            'value_type': 'fraction',
                                            'value': '10.0',
                                        },
                                    },
                                ],
                            },
                            'set_value': {
                                'value_type': 'absolute',
                                'value': '10.0',
                            },
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
            id='experiment_any_cart_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'application_name',
                    'values': ['some_application_name'],
                },
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'cashback_value': {
                            'set_value': {
                                'value_type': 'absolute',
                                'value': '10.0',
                            },
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
            id='application_name_cart_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'application_name', 'values': 'Other'},
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'cashback_value': {
                            'set_value': {
                                'value_type': 'fraction',
                                'value': '10.0',
                            },
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
            id='application_name_other_cart_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'country', 'values': ['russia']},
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'cashback_value': {
                            'cart_value': {
                                'value': [
                                    {
                                        'from_cost': '10.0',
                                        'discount': {
                                            'value_type': 'fraction',
                                            'value': '10.0',
                                        },
                                    },
                                ],
                            },
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
            id='country_cart_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'country',
                    'values': 'Any',
                    'exclusions': ['some_country'],
                },
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'cashback_value': {
                            'cart_value': {
                                'value': [
                                    {
                                        'from_cost': '10.0',
                                        'discount': {
                                            'value_type': 'absolute',
                                            'value': '10.0',
                                        },
                                    },
                                ],
                                'maximum_discount': '1.3',
                            },
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
            id='country_any_cart_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'city', 'values': ['213']},
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'cashback_value': {
                            'cart_value': {
                                'value': [
                                    {
                                        'from_cost': '10.0',
                                        'discount': {
                                            'value_type': 'absolute',
                                            'value': '10.0',
                                        },
                                    },
                                ],
                            },
                            'set_value': {
                                'value_type': 'fraction',
                                'value': '10.0',
                            },
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
            id='city_cart_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'city', 'values': 'Any'},
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'product_value': {
                            'value': [
                                {
                                    'step': {
                                        'from_cost': '1.0',
                                        'discount': '1.0',
                                    },
                                    'products': [{'id': 'some_product'}],
                                    'bundle': 1,
                                },
                            ],
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
            id='city_any_cart_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'depot', 'values': ['some_depot']},
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'cashback_value': {
                            'cart_value': {
                                'value': [
                                    {
                                        'from_cost': '10.0',
                                        'discount': {
                                            'value_type': 'absolute',
                                            'value': '10.0',
                                        },
                                    },
                                ],
                            },
                            'set_value': {
                                'value_type': 'fraction',
                                'value': '10.0',
                            },
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
            id='depot_cart_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'depot', 'values': 'Any'},
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'product_value': {
                            'value': [
                                {
                                    'step': {
                                        'from_cost': '1.0',
                                        'discount': '1.0',
                                    },
                                    'products': [{'id': 'some_product'}],
                                    'bundle': 1,
                                },
                            ],
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
            id='depot_any_cart_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'product_set',
                    'values': [['some_product']],
                },
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'money_value': {
                            'set_value': {
                                'value_type': 'absolute',
                                'value': '10.0',
                            },
                        },
                        'cashback_value': {
                            'set_value': {
                                'value_type': 'absolute',
                                'value': '10.0',
                            },
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
            id='product_set_cart_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'product_set', 'values': [[]]},
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'money_value': {
                            'set_value': {
                                'value_type': 'absolute',
                                'value': '10.0',
                            },
                        },
                        'product_value': {
                            'value': [
                                {
                                    'step': {
                                        'from_cost': '1.0',
                                        'discount': '1.0',
                                    },
                                    'products': [{'id': 'some_product'}],
                                    'bundle': 1,
                                },
                            ],
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
            id='product_set_empty_cart_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'application_name',
                    'values': 'Any',
                    'exclusions': ['some_application_name'],
                },
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'money_value': {
                            'set_value': {
                                'value_type': 'absolute',
                                'value': '10.0',
                            },
                        },
                        'cashback_value': {
                            'set_value': {
                                'value_type': 'fraction',
                                'value': '10.0',
                            },
                        },
                        'product_value': {
                            'value': [
                                {
                                    'step': {
                                        'from_cost': '1.0',
                                        'discount': '1.0',
                                    },
                                    'products': [{'id': 'some_product'}],
                                    'bundle': 1,
                                },
                            ],
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
            id='application_name_any_exclusions_cart_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'product_set', 'values': 'Other'},
            ],
            common.small_cart_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'condition (product_set) does not support Other',
            },
            id='product_set_does_not_support_other',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'product_set', 'values': 'Any'},
            ],
            common.small_cart_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'condition (product_set) does not support Any',
            },
            id='product_set_does_not_support_any',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'product_set',
                    'values': 'Other',
                    'exclusions': [['some_product']],
                },
            ],
            common.small_cart_discount(),
            400,
            {
                'code': 'Validation error',
                'message': (
                    'condition (product_set) with type Other does not support '
                    'exclusions'
                ),
            },
            id='product_set_does_not_support_other_exclusions',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'product_set',
                    'values': 'Any',
                    'exclusions': [['some_product']],
                },
            ],
            common.small_cart_discount(),
            400,
            {
                'code': 'Validation error',
                'message': (
                    'condition (product_set) with type Any does not support '
                    'exclusions'
                ),
            },
            id='product_set_does_not_support_any_exclusions',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'product_set', 'values': []},
            ],
            common.small_cart_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'Vector for \'product_set\' is empty',
            },
            id='product_set_empty',
        ),
        pytest.param(
            [common.VALID_ACTIVE_PERIOD],
            {
                'description': '1',
                'values_with_schedules': [
                    {'schedule': common.DEFAULT_SCHEDULE},
                ],
            },
            400,
            {
                'code': 'Validation error',
                'message': 'All schedules are empty on discount values',
            },
            id='cart_discounts_no_values',
        ),
        pytest.param(
            [common.VALID_ACTIVE_PERIOD],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'money_value': {
                            'set_value': {
                                'value_type': 'fraction',
                                'value': '10.0',
                            },
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                    {
                        'money_value': {
                            'set_value': {
                                'value_type': 'fraction',
                                'value': '10.0',
                                'maximum_discount': '51',
                            },
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
            },
            400,
            {
                'code': 'Validation error',
                'message': 'Validating overlapping schedules failed',
            },
            id='cart_discounts_overlapping_schedules',
        ),
        pytest.param(
            [common.VALID_ACTIVE_PERIOD],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'product_value': {
                            'value': [
                                {
                                    'step': {
                                        'from_cost': '1.0',
                                        'discount': '201',
                                    },
                                    'products': [{'id': 'some_product'}],
                                    'bundle': 2,
                                },
                            ],
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
            },
            400,
            {
                'code': 'Validation error',
                'message': (
                    'Product discount (201.0) value has to be between 0 '
                    'and bundle*100 (200.0)'
                ),
            },
            id='cart_discounts_product_discount_failed_bundle',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'application_name',
                    'values': ['missing_application_name'],
                },
            ],
            common.small_cart_discount(),
            400,
            {
                'code': 'Validation error',
                'message': (
                    'Invalid application_name: missing_application_name'
                ),
            },
            id='missing_application_name',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'city', 'values': ['moscow']},
            ],
            common.small_cart_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'Cant cast city to region_id: moscow, error: ',
            },
            id='city_name_instead_of_region_id',
        ),
        # pytest.param(
        #     [
        #         common.VALID_ACTIVE_PERIOD,
        #         {'condition_name': 'city', 'values': ['10050000']},
        #     ],
        #     common.small_cart_discount(),
        #     400,
        #
        #     {
        #         'code': 'Validation error',
        #         'message': (
        #             'Geobase error: failed to resolve
        #             timezone by region_id: '
        #             '10050000: Impl::RegIdxById(10050000) - unknown id '
        #             '(out-of-range)'
        #         ),
        #     },
        #     id='city_invalid_region_id',
        # ),
        pytest.param(
            [common.VALID_ACTIVE_PERIOD],
            _discount_with_orders_restrictionis(
                [
                    {
                        'allowed_orders_count': {'start': 0, 'end': 1},
                        'application_name': 'some_application_name',
                        'payment_method': 'some_payment_method',
                    },
                ],
            ),
            200,
            None,
            id='valid_orders_restrictions_cart_discount',
        ),
        pytest.param(
            [common.VALID_ACTIVE_PERIOD],
            _discount_with_orders_restrictionis(
                [
                    {
                        'allowed_orders_count': {'start': 0, 'end': 1},
                        'payment_method': 'some_payment_method',
                    },
                ],
            ),
            200,
            None,
            id='orders_restrictions_no_application_name_cart_discount',
        ),
        pytest.param(
            [common.VALID_ACTIVE_PERIOD],
            _discount_with_orders_restrictionis(
                [
                    {
                        'allowed_orders_count': {'start': 0, 'end': 0},
                        'application_name': 'some_application_name',
                    },
                ],
            ),
            200,
            None,
            id='orders_restrictions_no_payment_method_cart_discount',
        ),
        pytest.param(
            [common.VALID_ACTIVE_PERIOD],
            _discount_with_orders_restrictionis(
                [
                    {
                        'allowed_orders_count': {'start': 1, 'end': 0},
                        'application_name': 'some_application_name',
                        'payment_method': 'some_payment_method',
                    },
                ],
            ),
            400,
            {
                'code': 'Validation error',
                'message': (
                    'Orders restriction for '
                    'some_application_name-some_payment_method is invalid: '
                    'start (1) greater than end (0)'
                ),
            },
            id='orders_restrictions_invalid_range_cart_discount',
        ),
        pytest.param(
            [common.VALID_ACTIVE_PERIOD],
            _discount_with_orders_restrictionis(
                [
                    {
                        'allowed_orders_count': {'start': 0, 'end': 1},
                        'application_name': 'another_application_name',
                        'payment_method': 'some_payment_method',
                    },
                ],
            ),
            400,
            {
                'code': 'Validation error',
                'message': (
                    'Invalid application_name: another_application_name'
                ),
            },
            id='orders_restrictions_invalid_application_name_cart_discount',
        ),
        pytest.param(
            [common.VALID_ACTIVE_PERIOD],
            _discount_with_orders_restrictionis(
                [
                    {
                        'allowed_orders_count': {'start': 0, 'end': 1},
                        'application_name': 'some_application_name',
                        'payment_method': 'some_payment_method',
                    },
                    {
                        'allowed_orders_count': {'start': 2, 'end': 3},
                        'application_name': 'some_application_name',
                        'payment_method': 'some_payment_method',
                    },
                ],
            ),
            400,
            {
                'code': 'Validation error',
                'message': (
                    'Found duplicate counter for key some_payment_method'
                ),
            },
            id='orders_restrictions_orders_restrictions_cart_discount',
        ),
    ),
)
@discounts_match.parametrize_is_check
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(**common.DEFAULT_CONFIGS)
async def test_add_rules_carts_discounts_validation(
        is_check,
        additional_request_fields,
        rules: List[dict],
        discount: dict,
        expected_status_code: int,
        expected_response: Optional[dict],
        check_add_rules_validation,
):
    additional_request_fields = copy.deepcopy(additional_request_fields)
    additional_request_fields.update({'series_id': common.SERIES_ID})
    await check_add_rules_validation(
        is_check,
        additional_request_fields,
        'cart_discounts',
        rules,
        discount,
        expected_status_code,
        expected_response,
    )
