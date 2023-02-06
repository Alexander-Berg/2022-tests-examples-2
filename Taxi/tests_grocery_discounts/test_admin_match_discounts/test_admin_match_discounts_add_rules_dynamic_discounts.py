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
            id='minimal_valid_dynamic_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'label', 'values': ['some_label']},
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
            id='label_dynamic_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'label', 'values': ['default']},
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
            id='label_default_dynamic_discount',
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
                {'condition_name': 'label', 'values': []},
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'Vector for \'label\' is empty',
            },
            id='label_empty',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'label', 'values': 'Other'},
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'condition (label) does not support Other',
            },
            id='label_does_not_support_other',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'label', 'values': 'Any'},
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'condition (label) does not support Any',
            },
            id='label_does_not_support_any',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'label',
                    'values': 'Other',
                    'exclusions': ['some_label'],
                },
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': (
                    'condition (label) with type Other does not support '
                    'exclusions'
                ),
            },
            id='label_does_not_support_other_exclusions',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'label',
                    'values': 'Any',
                    'exclusions': ['some_label'],
                },
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': (
                    'condition (label) with type Any does not support '
                    'exclusions'
                ),
            },
            id='label_does_not_support_any_exclusions',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {
                    'condition_name': 'label',
                    'values': ['some_label'],
                    'exclusions': ['some_label'],
                },
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': (
                    'condition (label) with type Type does not support '
                    'exclusions'
                ),
            },
            id='label_does_not_support_type_exclusions',
        ),
    ),
)
@discounts_match.parametrize_is_check
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_add_rules_dynamic_discounts_validation(
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
    await check_add_rules_validation(
        is_check,
        additional_request_fields,
        'dynamic_discounts',
        rules,
        discount,
        expected_status_code,
        expected_response,
    )
