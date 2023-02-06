import copy

import discounts_match  # pylint: disable=E0401
import pytest

from tests_grocery_discounts import common


@pytest.mark.parametrize(
    'rules, discount, expected_status_code, expected_response',
    (
        pytest.param(
            [common.VALID_ACTIVE_PERIOD],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'money_value': {
                            'menu_value': {
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
            id='minimal_valid_payment_method_discount',
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
                            'menu_value': {
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
            id='class_payment_method_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'class', 'values': ['default']},
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'money_value': {
                            'menu_value': {
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
            id='class_default_payment_method_discount',
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
                            'menu_value': {
                                'value_type': 'table',
                                'value': [
                                    {
                                        'from_cost': '1.0',
                                        'discount': {
                                            'value_type': 'absolute',
                                            'value': '1.0',
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
            id='experiment_payment_method_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'experiment',
                    'values': 'Other',
                    'exclusions': ['some_experiment'],
                },
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'money_value': {
                            'menu_value': {
                                'value_type': 'table',
                                'value': [
                                    {
                                        'from_cost': '1.0',
                                        'discount': {
                                            'value_type': 'fraction',
                                            'value': '1.0',
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
            id='experiment_other_payment_method_discount',
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
                        'money_value': {
                            'menu_value': {
                                'value_type': 'absolute',
                                'value': '10.0',
                            },
                            'cart_value': {
                                'discount_values': {
                                    'value_type': 'table',
                                    'value': [
                                        {
                                            'from_cost': '1.0',
                                            'discount': {
                                                'value_type': 'absolute',
                                                'value': '1.0',
                                            },
                                        },
                                    ],
                                },
                            },
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
            id='application_name_payment_method_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'application_name', 'values': 'Any'},
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'money_value': {
                            'menu_value': {
                                'value_type': 'absolute',
                                'value': '10.0',
                            },
                            'cart_value': {
                                'discount_values': {
                                    'value_type': 'table',
                                    'value': [
                                        {
                                            'from_cost': '1.0',
                                            'discount': {
                                                'value_type': 'fraction',
                                                'value': '1.0',
                                            },
                                        },
                                    ],
                                },
                                'maximum_discount': '10.0',
                            },
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
            id='application_name_any_payment_method_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'country', 'values': ['some_country']},
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'cashback_value': {
                            'menu_value': {
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
            id='country_payment_method_discount',
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
                            'menu_value': {
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
            id='country_any_payment_method_discount',
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
                            'menu_value': {
                                'value_type': 'fraction',
                                'value': '10.0',
                                'maximum_discount': '10.0',
                            },
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
            id='city_payment_method_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'city',
                    'values': 'Other',
                    'exclusions': ['213'],
                },
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'cashback_value': {
                            'menu_value': {
                                'value_type': 'table',
                                'value': [
                                    {
                                        'from_cost': '1.0',
                                        'discount': {
                                            'value_type': 'absolute',
                                            'value': '1.0',
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
            id='city_other_payment_method_discount',
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
                            'menu_value': {
                                'value_type': 'fraction',
                                'value': '10.0',
                                'maximum_discount': '10.0',
                            },
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
            id='depot_payment_method_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'depot',
                    'values': 'Other',
                    'exclusions': ['some_depot'],
                },
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'cashback_value': {
                            'menu_value': {
                                'value_type': 'table',
                                'value': [
                                    {
                                        'from_cost': '1.0',
                                        'discount': {
                                            'value_type': 'absolute',
                                            'value': '1.0',
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
            id='depot_other_payment_method_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'payment_method',
                    'values': ['some_payment_method'],
                },
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'cashback_value': {
                            'menu_value': {
                                'value_type': 'table',
                                'value': [
                                    {
                                        'from_cost': '1.0',
                                        'discount': {
                                            'value_type': 'fraction',
                                            'value': '1.0',
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
            id='payment_method_payment_method_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'payment_method',
                    'values': 'Any',
                    'exclusions': ['some_payment_method'],
                },
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'cashback_value': {
                            'menu_value': {
                                'value_type': 'absolute',
                                'value': '10.0',
                            },
                            'cart_value': {
                                'discount_values': {
                                    'value_type': 'table',
                                    'value': [
                                        {
                                            'from_cost': '1.0',
                                            'discount': {
                                                'value_type': 'absolute',
                                                'value': '1.0',
                                            },
                                        },
                                    ],
                                },
                            },
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
            id='payment_method_any_payment_method_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'payment_method',
                    'values': 'Other',
                    'exclusions': ['some_payment_method'],
                },
            ],
            common.small_payment_method_discount(),
            200,
            None,
            id='payment_method_other_payment_method_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'bins', 'values': ['some_bins']},
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'cashback_value': {
                            'menu_value': {
                                'value_type': 'absolute',
                                'value': '10.0',
                            },
                            'cart_value': {
                                'discount_values': {
                                    'value_type': 'table',
                                    'value': [
                                        {
                                            'from_cost': '1.0',
                                            'discount': {
                                                'value_type': 'fraction',
                                                'value': '1.0',
                                            },
                                        },
                                    ],
                                },
                                'maximum_discount': '10.0',
                            },
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
            id='bins_payment_method_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'bins',
                    'values': 'Other',
                    'exclusions': ['some_bins'],
                },
            ],
            common.small_payment_method_discount(),
            200,
            None,
            id='bins_other_payment_method_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'bins',
                    'values': 'Any',
                    'exclusions': ['some_bins'],
                },
            ],
            common.small_payment_method_discount(),
            200,
            None,
            id='bins_any_payment_method_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'group', 'values': ['some_group']},
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'product_value': {
                            'discount_value': '1.6',
                            'bundle': 2,
                        },
                        'money_value': {
                            'menu_value': {
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
            id='group_payment_method_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'group',
                    'values': 'Other',
                    'exclusions': ['some_group'],
                },
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'product_value': {
                            'discount_value': '1.6',
                            'bundle': 2,
                        },
                        'cashback_value': {
                            'menu_value': {
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
            id='group_other_payment_method_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'product', 'values': ['some_product']},
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'money_value': {
                            'menu_value': {
                                'value_type': 'absolute',
                                'value': '10.0',
                            },
                        },
                        'cashback_value': {
                            'menu_value': {
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
            id='product_payment_method_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'product',
                    'values': 'Any',
                    'exclusions': ['some_product'],
                },
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'product_value': {
                            'discount_value': '1.6',
                            'bundle': 2,
                        },
                        'money_value': {
                            'menu_value': {
                                'value_type': 'absolute',
                                'value': '10.0',
                            },
                        },
                        'cashback_value': {
                            'menu_value': {
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
            id='product_any_payment_method_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'application_name',
                    'values': 'Other',
                    'exclusions': ['some_application_name'],
                },
            ],
            common.small_payment_method_discount(),
            200,
            None,
            id='application_name_other_exclusions_payment_method_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'application_name', 'values': []},
            ],
            common.small_payment_method_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'Vector for \'application_name\' is empty',
            },
            id='application_name_empty',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'payment_method', 'values': []},
            ],
            common.small_payment_method_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'Vector for \'payment_method\' is empty',
            },
            id='payment_method_empty',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'bins', 'values': []},
            ],
            common.small_payment_method_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'Vector for \'bins\' is empty',
            },
            id='bins_empty',
        ),
        pytest.param(
            [
                {
                    'condition_name': 'active_period',
                    'values': [
                        {
                            'start': '2020-01-01T09:00:01+00:00',
                            'end': '2022-01-01T00:00:00+00:00',
                        },
                    ],
                },
                {'condition_name': 'bins', 'values': ['some_bins']},
            ],
            common.small_payment_method_discount(),
            400,
            {
                'code': 'Validation error',
                'message': (
                    'Bin set some_bins could be inactive in discount time. '
                    'Change bin-set end-time or create a new one'
                ),
            },
            id='bin_set_inactive',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'bins', 'values': ['missing_bins']},
            ],
            common.small_payment_method_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'Couldn\'t find bin set missing_bins',
            },
            id='missing_bin_set',
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
            id='payment_method_discounts_no_values',
        ),
        pytest.param(
            [common.VALID_ACTIVE_PERIOD],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'product_value': {
                            'discount_value': '1.6',
                            'bundle': 2,
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                    {
                        'product_value': {
                            'discount_value': '1.6',
                            'bundle': 2,
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
            id='payment_method_discounts_overlapping_schedules',
        ),
        pytest.param(
            [common.VALID_ACTIVE_PERIOD],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'product_value': {
                            'discount_value': '201',
                            'bundle': 2,
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
            id='payment_method_discounts_product_discount_failed_bundle',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'application_name',
                    'values': ['some_application_name'],
                    'exclusions': ['some_application_name'],
                },
            ],
            common.small_payment_method_discount(),
            400,
            {
                'code': 'Validation error',
                'message': (
                    'condition (application_name) with type Type does not '
                    'support exclusions'
                ),
            },
            id='application_name_does_not_support_type_exclusions',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'payment_method',
                    'values': ['some_payment_method'],
                    'exclusions': ['some_payment_method'],
                },
            ],
            common.small_payment_method_discount(),
            400,
            {
                'code': 'Validation error',
                'message': (
                    'condition (payment_method) with type Type does not '
                    'support exclusions'
                ),
            },
            id='payment_method_does_not_support_type_exclusions',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'bins',
                    'values': ['some_bins'],
                    'exclusions': ['some_bins'],
                },
            ],
            common.small_payment_method_discount(),
            400,
            {
                'code': 'Validation error',
                'message': (
                    'condition (bins) with type Type does not support '
                    'exclusions'
                ),
            },
            id='bins_does_not_support_type_exclusions',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'group',
                    'values': ['some_group'],
                    'exclusions': ['some_group'],
                },
            ],
            common.small_payment_method_discount(),
            400,
            {
                'code': 'Validation error',
                'message': (
                    'condition (group) with type Type does not support '
                    'exclusions'
                ),
            },
            id='group_does_not_support_type_exclusions',
        ),
    ),
)
@discounts_match.parametrize_is_check
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(**common.DEFAULT_CONFIGS)
async def test_add_rules_payment_method_discounts_validation(
        taxi_grocery_discounts,
        is_check,
        additional_request_fields,
        rules,
        discount,
        expected_status_code,
        expected_response,
        check_add_rules_validation,
):
    additional_request_fields = copy.deepcopy(additional_request_fields)
    additional_request_fields.update({'series_id': common.SERIES_ID})
    await common.init_bin_sets(taxi_grocery_discounts)
    await check_add_rules_validation(
        is_check,
        additional_request_fields,
        'payment_method_discounts',
        rules,
        discount,
        expected_status_code,
        expected_response,
    )
