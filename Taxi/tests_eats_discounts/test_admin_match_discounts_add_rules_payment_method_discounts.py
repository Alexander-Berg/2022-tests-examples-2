import copy

import discounts_match  # pylint: disable=E0401
import pytest

from tests_eats_discounts import common


@pytest.mark.parametrize(
    'rules, discount, expected_status_code, expected_response',
    (
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
                            'is_start_utc': True,
                            'is_end_utc': True,
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
            id='payment_method_discounts_no_values',
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
            id='payment_method_discounts_overlapping_schedules',
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
            id='payment_method_discounts_product_discount_failed_bundle',
        ),
    ),
)
@discounts_match.parametrize_is_check
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_add_rules_payment_method_discounts_validation(
        taxi_eats_discounts,
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
    await common.init_bin_sets(taxi_eats_discounts)
    await check_add_rules_validation(
        is_check,
        additional_request_fields,
        'payment_method_discounts',
        rules,
        discount,
        expected_status_code,
        expected_response,
    )
