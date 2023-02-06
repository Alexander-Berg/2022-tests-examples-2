import copy

import discounts_match  # pylint: disable=E0401
import pytest

from tests_eats_discounts import common


@pytest.mark.parametrize(
    'rules, discount, expected_status_code, expected_response',
    (
        pytest.param(
            [common.VALID_ACTIVE_PERIOD],
            common.small_cart_discount(),
            200,
            None,
            id='minimal_valid_cart_discount_with_utc',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'product_set', 'values': [[]]},
            ],
            {
                'name': '1',
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
                'discount_meta': common.get_discount_meta(),
            },
            200,
            None,
            id='product_set_empty_cart_discount',
        ),
        pytest.param(
            [
                common.VALID_ACTIVE_PERIOD,
                {'condition_name': 'product_set', 'values': [[]]},
            ],
            {
                'name': '1',
                'values_with_schedules': [
                    {
                        'money_value': {
                            'set_value': {
                                'value_type': 'promocode',
                                'value': 'promocode',
                            },
                        },
                        'schedule': common.DEFAULT_SCHEDULE,
                    },
                ],
                'discount_meta': common.get_discount_meta(),
            },
            200,
            None,
            id='promocode_cart_discount',
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
            id='cart_discounts_no_values',
        ),
        pytest.param(
            [common.VALID_ACTIVE_PERIOD],
            {
                'name': '1',
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
                'discount_meta': common.get_discount_meta(),
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
                'name': '1',
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
            id='cart_discounts_product_discount_failed_bundle',
        ),
    ),
)
@discounts_match.parametrize_is_check
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_add_rules_carts_discounts_validation(
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
        'cart_discounts',
        rules,
        discount,
        expected_status_code,
        expected_response,
    )
