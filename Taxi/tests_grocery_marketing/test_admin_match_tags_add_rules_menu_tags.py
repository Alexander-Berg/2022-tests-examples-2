import pytest

from tests_grocery_marketing import common

NOW = '2019-11-12T13:00:50.283761+00:00'


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'rules, tag, expected_status_code, expected_response',
    (
        pytest.param(
            [common.VALID_ACTIVE_PERIOD, common.RULE_ID_CONDITION],
            common.small_menu_tag(),
            200,
            None,
            id='valid_menu_tag',
        ),
        pytest.param(
            [common.VALID_ACTIVE_PERIOD, common.RULE_ID_CONDITION],
            {
                'description': 'smth',
                'values_with_schedules': [
                    {
                        'value': {
                            'tag': 'some_tag_2',
                            'kind': 'marketing',
                            'min_cart_cost': '100.5',
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
            },
            200,
            None,
            id='valid_menu_tag_with_min_cart_cost',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                common.RULE_ID_CONDITION,
                {'condition_name': 'country', 'values': ['some_country']},
            ],
            common.small_menu_tag(),
            200,
            None,
            id='country_menu_tag',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                common.RULE_ID_CONDITION,
                {'condition_name': 'country', 'values': 'Other'},
            ],
            common.small_menu_tag(),
            200,
            None,
            id='country_other_menu_tag',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                common.RULE_ID_CONDITION,
                {'condition_name': 'city', 'values': ['213']},
            ],
            common.small_menu_tag(),
            200,
            None,
            id='city_menu_tag',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                common.RULE_ID_CONDITION,
                {'condition_name': 'depot', 'values': ['some_depot']},
            ],
            common.small_menu_tag(),
            200,
            None,
            id='depot_menu_tag',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                common.RULE_ID_CONDITION,
                {'condition_name': 'group', 'values': ['some_group']},
            ],
            common.small_menu_tag(),
            200,
            None,
            id='group_menu_tag',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                common.RULE_ID_CONDITION,
                {
                    'condition_name': 'group',
                    'values': 'Any',
                    'exclusions': ['some_group'],
                },
            ],
            common.small_menu_tag(),
            200,
            None,
            id='group_any_menu_tag',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                common.RULE_ID_CONDITION,
                {'condition_name': 'product', 'values': ['some_product']},
            ],
            common.small_menu_tag(),
            200,
            None,
            id='product_menu_tag',
        ),
        pytest.param(
            [common.VALID_ACTIVE_PERIOD],
            common.small_menu_tag(),
            400,
            {
                'code': 'Validation error',
                'message': 'No rule_id in rules conditions, it\'s required',
            },
            id='no_rule_id',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                common.RULE_ID_CONDITION,
                common.RULE_ID_CONDITION,
            ],
            common.small_menu_tag(),
            400,
            {
                'code': 'Validation error',
                'message': 'Found duplicate condition \'rule_id\'',
            },
            id='not_one_rule_id',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                common.RULE_ID_CONDITION,
                {
                    'condition_name': 'product',
                    'values': 'Other',
                    'exclusions': ['some_product'],
                },
            ],
            common.small_menu_tag(),
            200,
            None,
            id='product_other_menu_tag',
        ),
        pytest.param(
            [
                common.RULE_ID_CONDITION,
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
            common.small_menu_tag(),
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
                common.RULE_ID_CONDITION,
                {'condition_name': 'class', 'values': []},
            ],
            common.small_menu_tag(),
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
                common.RULE_ID_CONDITION,
                {'condition_name': 'experiment', 'values': []},
            ],
            common.small_menu_tag(),
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
                common.RULE_ID_CONDITION,
                {'condition_name': 'country', 'values': []},
            ],
            common.small_menu_tag(),
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
                common.RULE_ID_CONDITION,
                {'condition_name': 'city', 'values': []},
            ],
            common.small_menu_tag(),
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
                common.RULE_ID_CONDITION,
                {'condition_name': 'depot', 'values': []},
            ],
            common.small_menu_tag(),
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
                common.RULE_ID_CONDITION,
                {'condition_name': 'group', 'values': []},
            ],
            common.small_menu_tag(),
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
                common.RULE_ID_CONDITION,
                {'condition_name': 'product', 'values': []},
            ],
            common.small_menu_tag(),
            400,
            {
                'code': 'Validation error',
                'message': 'Vector for \'product\' is empty',
            },
            id='product_empty',
        ),
        pytest.param(
            [
                {'condition_name': 'active_period', 'values': []},
                common.RULE_ID_CONDITION,
            ],
            common.small_menu_tag(),
            400,
            {
                'code': 'Validation error',
                'message': 'Vector for \'active_period\' is empty',
            },
            id='active_period_empty',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                common.VALID_ACTIVE_PERIOD,
                common.RULE_ID_CONDITION,
            ],
            common.small_menu_tag(),
            400,
            {
                'code': 'Validation error',
                'message': 'Found duplicate condition \'active_period\'',
            },
            id='duplicate_rule',
        ),
        pytest.param(
            [common.VALID_ACTIVE_PERIOD, common.RULE_ID_CONDITION],
            {
                'description': '1',
                'values_with_schedules': [
                    {'schedule': common.DEFAULT_SCHEDULE},
                ],
            },
            400,
            {
                'code': 'Validation error',
                'message': 'All schedules are empty on tag values',
            },
            id='menu_tags_no_values',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                common.RULE_ID_CONDITION,
                {
                    'condition_name': 'country',
                    'values': ['some_country'],
                    'exclusions': ['some_country'],
                },
            ],
            common.small_menu_tag(),
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
                common.RULE_ID_CONDITION,
                {
                    'condition_name': 'city',
                    'values': ['213'],
                    'exclusions': ['some_city'],
                },
            ],
            common.small_menu_tag(),
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
                common.RULE_ID_CONDITION,
                {
                    'condition_name': 'depot',
                    'values': ['some_depot'],
                    'exclusions': ['some_depot'],
                },
            ],
            common.small_menu_tag(),
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
                common.RULE_ID_CONDITION,
                {
                    'condition_name': 'product',
                    'values': ['some_product'],
                    'exclusions': ['some_product'],
                },
            ],
            common.small_menu_tag(),
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
            [
                {'condition_name': 'active_period', 'values': 'Other'},
                common.RULE_ID_CONDITION,
            ],
            common.small_menu_tag(),
            400,
            {
                'code': 'Validation error',
                'message': 'active_period is not time_range vector',
            },
            id='active_period_does_not_support_other',
        ),
        pytest.param(
            [
                {'condition_name': 'active_period', 'values': 'Any'},
                common.RULE_ID_CONDITION,
            ],
            common.small_menu_tag(),
            400,
            {
                'code': 'Validation error',
                'message': 'active_period is not time_range vector',
            },
            id='active_period_does_not_support_any',
        ),
        pytest.param(
            [
                common.RULE_ID_CONDITION,
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
            common.small_menu_tag(),
            400,
            {
                'code': 'Validation error',
                'message': 'active_period is not time_range vector',
            },
            id='active_period_does_not_support_other_exclusions',
        ),
        pytest.param(
            [
                common.RULE_ID_CONDITION,
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
            common.small_menu_tag(),
            400,
            {
                'code': 'Validation error',
                'message': 'active_period is not time_range vector',
            },
            id='active_period_does_not_support_any_exclusions',
        ),
        pytest.param(
            [
                common.RULE_ID_CONDITION,
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
            common.small_menu_tag(),
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
@pytest.mark.parametrize(
    'handler, additional_request_fields',
    (
        pytest.param(
            common.ADD_RULES_URL,
            {'update_existing_tags': True, 'revisions': []},
            id='add_rules',
        ),
        pytest.param(
            common.ADD_RULES_CHECK_URL,
            {'update_existing_tags': True},
            id='add_rules_check_update_existing_tags',
        ),
        pytest.param(
            common.ADD_RULES_CHECK_URL,
            {'update_existing_tags': False},
            id='add_rules_check_not_update_existing_tags',
        ),
    ),
)
@pytest.mark.pgsql('grocery_marketing', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_add_rules_menu_tags_validation(
        taxi_grocery_marketing,
        pgsql,
        handler,
        additional_request_fields,
        rules,
        tag,
        expected_status_code,
        expected_response,
):
    await common.check_add_rules_validation(
        taxi_grocery_marketing,
        pgsql,
        handler,
        additional_request_fields,
        'menu_tags',
        rules,
        tag,
        expected_status_code,
        expected_response,
    )
