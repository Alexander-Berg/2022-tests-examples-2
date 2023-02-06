# pylint: disable=too-many-lines
import copy
from typing import List
from typing import Optional

import discounts_match  # pylint: disable=E0401
import pytest

from tests_grocery_discounts import common


def _discount_with_orders_restrictionis(orders_restrictions: List[dict]):
    discount = common.small_menu_discount()
    discount['orders_restrictions'] = orders_restrictions
    return discount


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
            id='minimal_valid_menu_discount',
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
            id='class_menu_discount',
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
            id='class_default_menu_discount',
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
            id='experiment_menu_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'experiment', 'values': 'Other'},
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
            id='experiment_other_menu_discount',
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
            id='country_menu_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'country', 'values': 'Other'},
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
                                        'from_cost': '1.1',
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
            },
            200,
            None,
            id='country_other_menu_discount',
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
                                'value_type': 'table',
                                'value': [
                                    {
                                        'from_cost': '1.1',
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
            id='city_menu_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'city',
                    'values': 'Any',
                    'exclusions': ['213'],
                },
            ],
            common.small_menu_discount(),
            200,
            None,
            id='city_any_menu_discount',
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
                                'value_type': 'table',
                                'value': [
                                    {
                                        'from_cost': '1.1',
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
            id='depot_menu_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'depot',
                    'values': 'Any',
                    'exclusions': ['some_depot'],
                },
            ],
            common.small_menu_discount(),
            200,
            None,
            id='depot_any_menu_discount',
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
                        'product_value': {'discount_value': '1', 'bundle': 2},
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
            id='group_menu_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'group',
                    'values': 'Any',
                    'exclusions': ['some_group'],
                },
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'product_value': {'discount_value': '1', 'bundle': 2},
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
            id='group_any_menu_discount',
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
            id='product_menu_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'product',
                    'values': 'Other',
                    'exclusions': ['some_product'],
                },
            ],
            {
                'description': '1',
                'values_with_schedules': [
                    {
                        'product_value': {'discount_value': '1', 'bundle': 2},
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
            id='product_other_menu_discount',
        ),
        pytest.param(
            [],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'Rules must contain active_period field',
            },
            id='active_period_missing',
        ),
        pytest.param(
            [
                {
                    'condition_name': 'active_period',
                    'values': [
                        {
                            'start': '2020-01-01T00:00:00+00:00',
                            'end': '2021-01-01T00:00:00+00:00',
                        },
                    ],
                },
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': (
                    common.TIME_IN_THE_PAST_ERROR.format(
                        'Any/Other',
                        7200,
                        '2020-01-01T02:00:00+0000',
                        '2020-01-01T00:00:00+0000',
                    )
                ),
            },
            id='active_period_start_in_past',
        ),
        pytest.param(
            [
                {
                    'condition_name': 'active_period',
                    'values': [
                        {
                            'start': '2020-01-01T09:00:01+00:00',
                            'end': '2021-01-01T00:00:00+00:00',
                        },
                        {
                            'start': '2021-01-01T00:00:01+00:00',
                            'end': '2022-01-01T09:00:02+00:00',
                        },
                    ],
                },
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': (
                    '\'active_period\' condition must contain exactly 1 '
                    'element, not 2'
                ),
            },
            id='too_many_active_period',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'class', 'values': []},
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'Vector for \'class\' is empty',
            },
            id='class_empty',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'experiment', 'values': []},
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'Vector for \'experiment\' is empty',
            },
            id='experiment_empty',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'country', 'values': []},
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'Vector for \'country\' is empty',
            },
            id='country_empty',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'city', 'values': []},
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'Vector for \'city\' is empty',
            },
            id='city_empty',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'depot', 'values': []},
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'Vector for \'depot\' is empty',
            },
            id='depot_empty',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'group', 'values': []},
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'Vector for \'group\' is empty',
            },
            id='group_empty',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'product', 'values': []},
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'Vector for \'product\' is empty',
            },
            id='product_empty',
        ),
        pytest.param(
            [{'condition_name': 'active_period', 'values': []}],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'Vector for \'active_period\' is empty',
            },
            id='active_period_empty',
        ),
        pytest.param(
            [common.VALID_ACTIVE_PERIOD, common.VALID_ACTIVE_PERIOD],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'Found duplicate condition \'active_period\'',
            },
            id='duplicate_rule',
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
            id='menu_discounts_no_values',
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
            id='menu_discounts_overlapping_schedules',
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
            id='menu_discounts_product_discount_failed_bundle',
        ),
        pytest.param(
            [
                {
                    'condition_name': 'active_period',
                    'values': [
                        {
                            'start': '2021-01-01T00:00:00+00:00',
                            'end': '2020-01-01T09:00:01+00:00',
                        },
                    ],
                },
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': (
                    'Exception in AnyOtherConditionsVectorFromGenerated for '
                    '\'active_period\' : begin more than end in TimeRange'
                ),
            },
            id='menu_discounts_match_rules_range_check_fails',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'class', 'values': 'Other'},
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'condition (class) does not support Other',
            },
            id='class_does_not_support_other',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'class', 'values': 'Any'},
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'condition (class) does not support Any',
            },
            id='class_does_not_support_any',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'class',
                    'values': 'Other',
                    'exclusions': ['some_class'],
                },
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': (
                    'condition (class) with type Other does not support '
                    'exclusions'
                ),
            },
            id='class_does_not_support_other_exclusions',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'class',
                    'values': 'Any',
                    'exclusions': ['some_class'],
                },
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': (
                    'condition (class) with type Any does not support '
                    'exclusions'
                ),
            },
            id='class_does_not_support_any_exclusions',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'class',
                    'values': ['some_class'],
                    'exclusions': ['some_class'],
                },
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': (
                    'condition (class) with type Type does not support '
                    'exclusions'
                ),
            },
            id='class_does_not_support_type_exclusions',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'experiment',
                    'values': ['some_experiment'],
                    'exclusions': ['some_experiment'],
                },
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': (
                    'condition (experiment) with type Type does not support '
                    'exclusions'
                ),
            },
            id='experiment_does_not_support_type_exclusions',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'country',
                    'values': ['some_country'],
                    'exclusions': ['some_country'],
                },
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': (
                    'condition (country) with type Type does not support '
                    'exclusions'
                ),
            },
            id='country_does_not_support_type_exclusions',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'city',
                    'values': ['213'],
                    'exclusions': ['some_city'],
                },
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': (
                    'condition (city) with type Type does not support '
                    'exclusions'
                ),
            },
            id='city_does_not_support_type_exclusions',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'depot',
                    'values': ['some_depot'],
                    'exclusions': ['some_depot'],
                },
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': (
                    'condition (depot) with type Type does not support '
                    'exclusions'
                ),
            },
            id='depot_does_not_support_type_exclusions',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'product',
                    'values': ['some_product'],
                    'exclusions': ['some_product'],
                },
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': (
                    'condition (product) with type Type does not support '
                    'exclusions'
                ),
            },
            id='product_does_not_support_type_exclusions',
        ),
        pytest.param(
            [{'condition_name': 'active_period', 'values': 'Other'}],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'active_period is not time_range vector',
            },
            id='active_period_does_not_support_other',
        ),
        pytest.param(
            [{'condition_name': 'active_period', 'values': 'Any'}],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'active_period is not time_range vector',
            },
            id='active_period_does_not_support_any',
        ),
        pytest.param(
            [
                {
                    'condition_name': 'active_period',
                    'values': 'Other',
                    'exclusions': [
                        {
                            'start': '2020-01-01T09:00:01+00:00',
                            'end': '2021-01-01T00:00:00+00:00',
                        },
                    ],
                },
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'active_period is not time_range vector',
            },
            id='active_period_does_not_support_other_exclusions',
        ),
        pytest.param(
            [
                {
                    'condition_name': 'active_period',
                    'values': 'Any',
                    'exclusions': [
                        {
                            'start': '2020-01-01T09:00:01+00:00',
                            'end': '2021-01-01T00:00:00+00:00',
                        },
                    ],
                },
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'active_period is not time_range vector',
            },
            id='active_period_does_not_support_any_exclusions',
        ),
        pytest.param(
            [
                {
                    'condition_name': 'active_period',
                    'values': [
                        {
                            'start': '2020-01-01T09:00:01+00:00',
                            'end': '2021-01-01T00:00:00+00:00',
                        },
                    ],
                    'exclusions': [
                        {
                            'start': '2020-01-01T09:00:01+00:00',
                            'end': '2021-01-01T00:00:00+00:00',
                        },
                    ],
                },
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': (
                    'condition (active_period) with type Type does not '
                    'support exclusions'
                ),
            },
            id='active_period_does_not_support_type_exclusions',
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
                ],
            ),
            200,
            None,
            id='valid_orders_restrictions_menu_discount',
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
            id='orders_restrictions_no_application_name_menu_discount',
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
            id='orders_restrictions_no_payment_method_menu_discount',
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
            id='orders_restrictions_invalid_range_menu_discount',
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
            id='orders_restrictions_invalid_application_name_menu_discount',
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
            id='orders_restrictions_orders_restrictions_menu_discount',
        ),
    ),
)
@discounts_match.parametrize_is_check
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(**common.DEFAULT_CONFIGS)
async def test_add_rules_menu_discounts_validation(
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
        'menu_discounts',
        rules,
        discount,
        expected_status_code,
        expected_response,
    )
