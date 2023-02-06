import copy
from typing import List
from typing import Optional

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
            id='minimal_valid_suppliers_discount',
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
            id='country_suppliers_discount',
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
                        'money_value': {
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
            id='country_other_suppliers_discount',
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
                        'money_value': {
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
            id='city_suppliers_discount',
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
            400,
            None,
            id='cashback_not_allowed_discount',
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
            common.small_suppliers_discount(),
            200,
            None,
            id='city_any_suppliers_discount',
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
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
            id='product_suppliers_discount',
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
            id='product_other_suppliers_discount',
        ),
        pytest.param(
            [],
            common.small_suppliers_discount(),
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
            common.small_suppliers_discount(),
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
            common.small_suppliers_discount(),
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
                {'condition_name': 'country', 'values': []},
            ],
            common.small_suppliers_discount(),
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
            common.small_suppliers_discount(),
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
                {'condition_name': 'product', 'values': []},
            ],
            common.small_suppliers_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'Vector for \'product\' is empty',
            },
            id='product_empty',
        ),
        pytest.param(
            [{'condition_name': 'active_period', 'values': []}],
            common.small_suppliers_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'Vector for \'active_period\' is empty',
            },
            id='active_period_empty',
        ),
        pytest.param(
            [common.VALID_ACTIVE_PERIOD, common.VALID_ACTIVE_PERIOD],
            common.small_suppliers_discount(),
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
            id='suppliers_discounts_no_values',
        ),
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
                    {
                        'money_value': {
                            'menu_value': {
                                'value_type': 'absolute',
                                'value': '15.0',
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
            id='suppliers_discounts_overlapping_schedules',
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
            common.small_suppliers_discount(),
            400,
            {
                'code': 'Validation error',
                'message': (
                    'Exception in AnyOtherConditionsVectorFromGenerated for '
                    '\'active_period\' : begin more than end in TimeRange'
                ),
            },
            id='suppliers_discounts_match_rules_range_check_fails',
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
            common.small_suppliers_discount(),
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
            common.small_suppliers_discount(),
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
                    'condition_name': 'product',
                    'values': ['some_product'],
                    'exclusions': ['some_product'],
                },
            ],
            common.small_suppliers_discount(),
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
            common.small_suppliers_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'active_period is not time_range vector',
            },
            id='active_period_does_not_support_other',
        ),
        pytest.param(
            [{'condition_name': 'active_period', 'values': 'Any'}],
            common.small_suppliers_discount(),
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
            common.small_suppliers_discount(),
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
            common.small_suppliers_discount(),
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
            common.small_suppliers_discount(),
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
    ),
)
@discounts_match.parametrize_is_check
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(**common.DEFAULT_CONFIGS)
async def test_add_rules_suppliers_discounts_validation(
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
        'suppliers_discounts',
        rules,
        discount,
        expected_status_code,
        expected_response,
    )
