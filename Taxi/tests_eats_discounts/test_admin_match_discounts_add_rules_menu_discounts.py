import copy

import discounts_match  # pylint: disable=E0401
import pytest

from tests_eats_discounts import common

TIME_IN_THE_PAST_ERROR = (
    'Time in the past for {}. The start time of the discount '
    'must be no earlier than the start time of the draft + delta. '
    'Delta: {} seconds.\nStart time of the draft + delta: {}. '
    'Discount start time: {}'
)


@pytest.mark.parametrize(
    'rules, discount, expected_status_code, expected_response',
    (
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
                            'is_start_utc': True,
                            'is_end_utc': True,
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
                    TIME_IN_THE_PAST_ERROR.format(
                        'utc',
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
                            'is_start_utc': True,
                            'is_end_utc': True,
                            'end': '2021-01-01T00:00:00+00:00',
                        },
                        {
                            'start': '2021-01-01T00:00:01+00:00',
                            'is_start_utc': True,
                            'is_end_utc': True,
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
                {'condition_name': 'brand', 'values': []},
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'Vector for \'brand\' is empty',
            },
            id='brand_empty',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'place', 'values': []},
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'Vector for \'place\' is empty',
            },
            id='place_empty',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'region', 'values': []},
            ],
            common.small_menu_discount(),
            400,
            {
                'code': 'Validation error',
                'message': 'Vector for \'region\' is empty',
            },
            id='region_empty',
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
                'name': '1',
                'values_with_schedules': [
                    {'schedule': common.DEFAULT_SCHEDULE},
                ],
                'discount_meta': common.get_discount_meta(),
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
                'name': '1',
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
                'discount_meta': common.get_discount_meta(),
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
                'name': '1',
                'values_with_schedules': [
                    {
                        'product_value': {
                            'discount_value': '201',
                            'bundle': 2,
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
                'discount_meta': common.get_discount_meta(),
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
                            'is_start_utc': True,
                            'is_end_utc': True,
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
    ),
)
@discounts_match.parametrize_is_check
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_add_rules_menu_discounts_validation(
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
        'menu_discounts',
        rules,
        discount,
        expected_status_code,
        expected_response,
    )
