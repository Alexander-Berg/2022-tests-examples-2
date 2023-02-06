# pylint: disable=too-many-lines
import random
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import discounts_match  # pylint: disable=E0401
import pytest

from tests_grocery_discounts import common


FUTURE_ACTIVE_PERIOD = {
    'condition_name': 'active_period',
    'values': [
        {
            'start': '2020-01-10T10:01:00+00:00',
            'is_start_utc': False,
            'is_end_utc': False,
            'end': '2021-01-01T00:00:00+00:00',
        },
    ],
}


def _common_expected_data(
        hierarchy_name: Optional[str] = None,
        active_period: Optional[dict] = None,
        subquery_id: Optional[str] = None,
        excluded_hierarchy_names: Optional[List[str]] = None,
) -> dict:
    if subquery_id is None:
        subquery_id = '1'
    result: dict = {
        'match_results': [
            {
                'subquery_id': subquery_id,
                'results': [
                    {
                        'discounts': [
                            {
                                'discount': common.get_matched_discount(
                                    common.get_add_rules_data(),
                                    'cart_discounts',
                                ),
                                'create_draft_id': (
                                    'draft_id_check_add_rules_validation'
                                ),
                            },
                        ],
                        'status': 'ok',
                        'hierarchy_name': 'cart_discounts',
                    },
                    {
                        'discounts': [
                            {
                                'discount': common.get_matched_discount(
                                    common.get_add_rules_data(),
                                    'dynamic_discounts',
                                ),
                                'create_draft_id': (
                                    'draft_id_check_add_rules_validation'
                                ),
                            },
                        ],
                        'status': 'ok',
                        'hierarchy_name': 'dynamic_discounts',
                    },
                    {
                        'discounts': [
                            {
                                'discount': common.get_matched_discount(
                                    common.get_add_rules_data(),
                                    'menu_discounts',
                                ),
                                'create_draft_id': (
                                    'draft_id_check_add_rules_validation'
                                ),
                            },
                        ],
                        'status': 'ok',
                        'hierarchy_name': 'menu_discounts',
                    },
                    {
                        'discounts': [
                            {
                                'discount': common.get_matched_discount(
                                    common.get_add_rules_data(),
                                    'payment_method_discounts',
                                ),
                                'create_draft_id': (
                                    'draft_id_check_add_rules_validation'
                                ),
                            },
                        ],
                        'status': 'ok',
                        'hierarchy_name': 'payment_method_discounts',
                    },
                ],
            },
        ],
    }
    if excluded_hierarchy_names:
        for res in result['match_results'][0]['results']:
            if res['hierarchy_name'] in excluded_hierarchy_names:
                res['discounts'] = []
    if hierarchy_name is not None:
        for res in result['match_results'][0]['results']:
            if res['hierarchy_name'] != hierarchy_name:
                res['discounts'] = []
    return result


@pytest.mark.parametrize(
    'hierarchy_names',
    (
        pytest.param(
            [
                'menu_discounts',
                'cart_discounts',
                'payment_method_discounts',
                'dynamic_discounts',
            ],
            id='all_hierarchies',
        ),
        pytest.param(['menu_discounts'], id='menu_discounts_hierarchy'),
        pytest.param(['cart_discounts'], id='cart_discounts_hierarchy'),
        pytest.param(
            ['payment_method_discounts'],
            id='payment_method_discounts_hierarchy',
        ),
        pytest.param(['dynamic_discounts'], id='dynamic_discounts_hierarchy'),
        pytest.param(
            ['cart_discounts', 'cart_discounts', 'menu_discounts'],
            id='duplicate_hierarchy',
        ),
    ),
)
@pytest.mark.parametrize(
    'add_rules_data, common_conditions, subqueries, expected_data,'
    'place_time_zone',
    (
        pytest.param(
            common.get_add_rules_data(),
            {
                'cities': ['213'],
                'countries': ['some_country'],
                'depots': ['some_depot'],
                'application_names': ['some_application_name'],
            },
            [
                {
                    'subquery_id': '1',
                    'conditions': {
                        'labels': ['some_label'],
                        'product': 'some_product',
                    },
                },
            ],
            _common_expected_data(),
            'UTC',
            id='add_all_hierarchies_discounts',
        ),
        pytest.param(
            common.get_add_rules_data(),
            {
                'countries': ['some_country'],
                'depots': ['some_depot'],
                'application_names': ['some_application_name'],
            },
            [],
            _common_expected_data(''),
            'UTC',
            id='no_city',
        ),
        pytest.param(
            common.get_add_rules_data(),
            {
                'countries': ['some_country'],
                'application_names': ['some_application_name'],
            },
            [],
            _common_expected_data(''),
            'UTC',
            id='no_city_depot',
        ),
        pytest.param(
            common.get_add_rules_data(),
            {
                'cities': ['213'],
                'countries': ['some_country'],
                'application_names': ['some_application_name'],
            },
            [],
            _common_expected_data(''),
            'UTC',
            id='no_depot',
        ),
        pytest.param(
            common.get_add_rules_data(),
            {
                'cities': ['213'],
                'application_names': ['some_application_name'],
            },
            [],
            _common_expected_data(''),
            'UTC',
            id='no_country_depot',
        ),
        pytest.param(
            common.get_add_rules_data(),
            {
                'cities': ['213'],
                'depots': ['some_depot'],
                'application_names': ['some_application_name'],
            },
            [],
            _common_expected_data(''),
            'UTC',
            id='no_country',
        ),
        pytest.param(
            common.get_add_rules_data(),
            {
                'depots': ['some_depot'],
                'application_names': ['some_application_name'],
            },
            [],
            _common_expected_data(''),
            'UTC',
            id='no_city_country',
        ),
        pytest.param(
            common.get_add_rules_data(),
            {
                'cities': ['213'],
                'countries': ['another_country'],
                'depots': ['some_depot'],
                'application_names': ['some_application_name'],
            },
            [],
            _common_expected_data(''),
            'UTC',
            id='another_country',
        ),
        pytest.param(
            common.get_add_rules_data(),
            {
                'cities': ['214'],
                'countries': ['some_country'],
                'depots': ['some_depot'],
                'application_names': ['some_application_name'],
            },
            [],
            _common_expected_data(''),
            'UTC',
            id='another_city',
        ),
        pytest.param(
            common.get_add_rules_data(),
            {
                'cities': ['213'],
                'countries': ['some_country'],
                'depots': ['another_depot'],
                'application_names': ['some_application_name'],
            },
            [],
            _common_expected_data(''),
            'UTC',
            id='another_depot',
        ),
        pytest.param(
            {
                'menu_discounts': [
                    {
                        'rules': [
                            common.VALID_ACTIVE_PERIOD,
                            {'condition_name': 'city', 'values': ['213']},
                            {
                                'condition_name': 'country',
                                'values': ['some_country'],
                            },
                            {
                                'condition_name': 'depot',
                                'values': ['some_depot'],
                            },
                        ],
                        'discount': common.small_menu_discount(),
                    },
                ],
            },
            {
                'cities': ['213'],
                'countries': ['some_country'],
                'depots': ['some_depot'],
                'application_names': ['some_application_name'],
            },
            [],
            _common_expected_data('menu_discounts'),
            'UTC',
            id='add_menu_hierarchy_discount',
        ),
        pytest.param(
            {
                'cart_discounts': [
                    {
                        'rules': [
                            common.VALID_ACTIVE_PERIOD,
                            {
                                'condition_name': 'application_name',
                                'values': ['some_application_name'],
                            },
                            {'condition_name': 'city', 'values': ['213']},
                            {
                                'condition_name': 'country',
                                'values': ['some_country'],
                            },
                            {
                                'condition_name': 'depot',
                                'values': ['some_depot'],
                            },
                        ],
                        'discount': common.small_cart_discount(),
                    },
                ],
            },
            {
                'cities': ['213'],
                'countries': ['some_country'],
                'depots': ['some_depot'],
                'application_names': ['some_application_name'],
            },
            [],
            _common_expected_data('cart_discounts'),
            'UTC',
            id='add_cart_hierarchy_discount',
        ),
        pytest.param(
            {
                'payment_method_discounts': [
                    {
                        'rules': [
                            common.VALID_ACTIVE_PERIOD,
                            {
                                'condition_name': 'application_name',
                                'values': ['some_application_name'],
                            },
                            {'condition_name': 'city', 'values': ['213']},
                            {
                                'condition_name': 'country',
                                'values': ['some_country'],
                            },
                            {
                                'condition_name': 'depot',
                                'values': ['some_depot'],
                            },
                        ],
                        'discount': common.small_payment_method_discount(),
                    },
                ],
            },
            {
                'cities': ['213'],
                'countries': ['some_country'],
                'depots': ['some_depot'],
                'application_names': ['some_application_name'],
            },
            [],
            _common_expected_data('payment_method_discounts'),
            'UTC',
            id='add_payment_method_hierarchy_discount',
        ),
        pytest.param(
            {
                'dynamic_discounts': [
                    {
                        'rules': [
                            common.VALID_ACTIVE_PERIOD,
                            {
                                'condition_name': 'label',
                                'values': ['some_label'],
                            },
                        ],
                        'discount': common.small_menu_discount(),
                    },
                ],
            },
            {'application_names': ['some_application_name']},
            [
                {
                    'subquery_id': '1',
                    'conditions': {
                        'labels': ['some_label'],
                        'product': 'some_product',
                    },
                },
            ],
            _common_expected_data('dynamic_discounts'),
            'UTC',
            id='add_dynamic_hierarchy_discount',
        ),
        pytest.param(
            common.get_add_rules_data(FUTURE_ACTIVE_PERIOD),
            {
                'cities': ['213'],
                'countries': ['some_country'],
                'depots': ['some_depot'],
                'application_names': ['some_application_name'],
            },
            [],
            _common_expected_data(''),
            'UTC',
            id='add_future_discounts',
        ),
        pytest.param(
            common.get_add_rules_data(FUTURE_ACTIVE_PERIOD),
            {
                'cities': ['213'],
                'countries': ['some_country'],
                'depots': ['some_depot'],
                'application_names': ['some_application_name'],
            },
            [
                {
                    'subquery_id': '1',
                    'conditions': {
                        'labels': ['some_label'],
                        'product': 'some_product',
                    },
                },
            ],
            _common_expected_data(None, FUTURE_ACTIVE_PERIOD),
            'Europe/Moscow',
            id='add_future_discounts_time_zone',
        ),
        pytest.param(
            common.get_add_rules_data(),
            {
                'cities': ['213'],
                'countries': ['some_country'],
                'depots': ['some_depot'],
                'application_names': ['some_application_name'],
            },
            [
                {
                    'subquery_id': '1',
                    'conditions': {
                        'labels': ['some_label'],
                        'product': 'some_product',
                    },
                },
            ],
            _common_expected_data(),
            'UTC',
            id='no_common_conditions',
        ),
        pytest.param(
            common.get_add_rules_data(),
            {
                'cities': ['213'],
                'countries': ['some_country'],
                'depots': ['some_depot'],
                'application_names': ['some_application_name'],
            },
            [
                {
                    'subquery_id': '1',
                    'conditions': {
                        'labels': ['some_label'],
                        'product': 'some_product',
                    },
                },
            ],
            _common_expected_data(),
            'UTC',
            id='label_subquery',
        ),
        pytest.param(
            common.get_add_rules_data(),
            {
                'cities': ['213'],
                'countries': ['some_country'],
                'depots': ['some_depot'],
                'application_names': ['some_application_name'],
            },
            [],
            _common_expected_data(
                None, None, 'no_subquery_id', ['dynamic_discounts'],
            ),
            'UTC',
            id='empty_subquery',
        ),
        pytest.param(
            common.get_add_rules_data(),
            {
                'cities': ['213'],
                'countries': ['some_country'],
                'depots': ['some_depot'],
            },
            [
                {
                    'subquery_id': '1',
                    'conditions': {
                        'labels': ['some_label'],
                        'product': 'some_product',
                    },
                },
                {
                    'subquery_id': '2',
                    'conditions': {'product': 'some_product'},
                },
            ],
            {
                'match_results': [
                    _common_expected_data(
                        excluded_hierarchy_names=[
                            'payment_method_discounts',
                            'cart_discounts',
                        ],
                    )['match_results'][0],
                    {
                        'subquery_id': '2',
                        'results': [
                            {
                                'discounts': [],
                                'status': 'ok',
                                'hierarchy_name': 'cart_discounts',
                            },
                            {
                                'discounts': [],
                                'status': 'ok',
                                'hierarchy_name': 'dynamic_discounts',
                            },
                            {
                                'discounts': [
                                    {
                                        'discount': (
                                            common.get_matched_discount(
                                                common.get_add_rules_data(),
                                                'menu_discounts',
                                            )
                                        ),
                                        'create_draft_id': 'draft_id_check_add_rules_validation',  # noqa: E501
                                    },
                                ],
                                'status': 'ok',
                                'hierarchy_name': 'menu_discounts',
                            },
                            {
                                'discounts': [],
                                'status': 'ok',
                                'hierarchy_name': 'payment_method_discounts',
                            },
                        ],
                    },
                ],
            },
            'UTC',
            id='several_subqueries',
        ),
        pytest.param(
            common.get_add_rules_data(),
            {
                'cities': ['213'],
                'countries': ['some_country'],
                'depots': ['some_depot'],
            },
            [
                {
                    'subquery_id': '1',
                    'conditions': {
                        'labels': ['some_label'],
                        'product': 'some_product',
                    },
                },
                {
                    'subquery_id': '1',
                    'conditions': {'product': 'some_product'},
                },
            ],
            {
                'match_results': [
                    _common_expected_data(
                        excluded_hierarchy_names=[
                            'payment_method_discounts',
                            'cart_discounts',
                        ],
                    )['match_results'][0],
                    {
                        'subquery_id': '1',
                        'results': [
                            {
                                'discounts': [],
                                'status': 'ok',
                                'hierarchy_name': 'cart_discounts',
                            },
                            {
                                'discounts': [],
                                'status': 'ok',
                                'hierarchy_name': 'dynamic_discounts',
                            },
                            {
                                'discounts': [
                                    {
                                        'discount': (
                                            common.get_matched_discount(
                                                common.get_add_rules_data(),
                                                'menu_discounts',
                                            )
                                        ),
                                        'create_draft_id': 'draft_id_check_add_rules_validation',  # noqa: E501
                                    },
                                ],
                                'status': 'ok',
                                'hierarchy_name': 'menu_discounts',
                            },
                            {
                                'discounts': [],
                                'status': 'ok',
                                'hierarchy_name': 'payment_method_discounts',
                            },
                        ],
                    },
                ],
            },
            'UTC',
            id='duplicate_subqueries',
        ),
        pytest.param(
            common.get_full_add_rules_data(),
            {
                'cities': ['213'],
                'countries': ['some_country'],
                'depots': ['some_depot'],
                'application_names': ['some_application_name'],
            },
            [],
            {
                'match_results': [
                    {
                        'subquery_id': 'no_subquery_id',
                        'results': [
                            {
                                'discounts': [
                                    {
                                        'discount': (
                                            common.get_matched_discount(
                                                common.get_full_add_rules_data(),  # noqa: E501
                                                'cart_discounts',
                                            )
                                        ),
                                        'create_draft_id': 'draft_id_check_add_rules_validation',  # noqa: E501
                                    },
                                ],
                                'status': 'ok',
                                'hierarchy_name': 'cart_discounts',
                            },
                            {
                                'discounts': [],
                                'status': 'ok',
                                'hierarchy_name': 'dynamic_discounts',
                            },
                            {
                                'discounts': [
                                    {
                                        'discount': (
                                            common.get_matched_discount(
                                                common.get_full_add_rules_data(),  # noqa: E501
                                                'menu_discounts',
                                            )
                                        ),
                                        'create_draft_id': 'draft_id_check_add_rules_validation',  # noqa: E501
                                    },
                                ],
                                'status': 'ok',
                                'hierarchy_name': 'menu_discounts',
                            },
                            {
                                'discounts': [
                                    {
                                        'discount': (
                                            common.get_matched_discount(
                                                common.get_full_add_rules_data(),  # noqa: E501
                                                'payment_method_discounts',
                                            )
                                        ),
                                        'create_draft_id': 'draft_id_check_add_rules_validation',  # noqa: E501
                                    },
                                ],
                                'status': 'ok',
                                'hierarchy_name': 'payment_method_discounts',
                            },
                        ],
                    },
                ],
            },
            'UTC',
            id='add_full_all_hierarchies_discounts',
        ),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(**common.DEFAULT_CONFIGS)
async def test_match_discounts(
        client,
        mocked_time,
        hierarchy_names: List[str],
        add_rules_data: Dict[str, List[dict]],
        subqueries: List[Dict[str, Any]],
        common_conditions: Optional[Dict[str, Any]],
        expected_data: dict,
        place_time_zone: str,
        add_rules,
) -> None:
    await common.init_bin_sets(client)
    await common.init_classes(client)
    await common.init_groups(client, mocked_time)

    await add_rules(add_rules_data)

    await client.invalidate_caches()

    random.shuffle(hierarchy_names)  # order insufficient

    await common.check_match_discounts(
        client,
        hierarchy_names,
        subqueries,
        common_conditions,
        '2020-01-10T10:00:00+0000',  # Friday
        place_time_zone,
        False,
        expected_data,
        200,
    )


@pytest.mark.parametrize(
    'missing_hierarchy_name',
    (
        pytest.param(
            'cart_discounts',
            marks=discounts_match.remove_hierarchies('cart_discounts'),
            id='missing_cart_discounts',
        ),
        pytest.param(
            'menu_discounts',
            marks=discounts_match.remove_hierarchies('menu_discounts'),
            id='missing_menu_discounts',
        ),
        pytest.param(
            'payment_method_discounts',
            marks=discounts_match.remove_hierarchies(
                'payment_method_discounts',
            ),
            id='missing_payment_method_discounts',
        ),
        pytest.param(
            'dynamic_discounts',
            marks=discounts_match.remove_hierarchies('dynamic_discounts'),
            id='missing_dynamic_discounts',
        ),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_match_discounts_missing_hierarchy(
        client, missing_hierarchy_name,
) -> None:
    await client.invalidate_caches()

    expected_data: dict = {
        'match_results': [
            {
                'subquery_id': '1',
                'results': [
                    {
                        'discounts': [],
                        'status': 'ok',
                        'hierarchy_name': 'cart_discounts',
                    },
                    {
                        'discounts': [],
                        'status': 'ok',
                        'hierarchy_name': 'dynamic_discounts',
                    },
                    {
                        'discounts': [],
                        'status': 'ok',
                        'hierarchy_name': 'menu_discounts',
                    },
                    {
                        'discounts': [],
                        'status': 'ok',
                        'hierarchy_name': 'payment_method_discounts',
                    },
                ],
            },
        ],
    }
    for result in expected_data['match_results'][0]['results']:
        if result['hierarchy_name'] == missing_hierarchy_name:
            result['status'] = 'hierarchy_not_found'
            break
    await common.check_match_discounts(
        client,
        [
            'menu_discounts',
            'cart_discounts',
            'payment_method_discounts',
            'dynamic_discounts',
        ],
        [],
        {
            'cities': ['213'],
            'country': ['some_country'],
            'depots': ['some_depot'],
            'application_names': ['some_application_name'],
        },
        '2020-01-10T10:00:00+0000',
        'UTC',
        False,
        expected_data,
        200,
    )


@pytest.mark.parametrize(
    'orders_restrictions, orders_counts, expected_data',
    (
        pytest.param(
            None,
            [
                {
                    'orders_count': 10,
                    'application_name': 'some_application_name',
                    'payment_method': 'some_payment_method',
                },
            ],
            _common_expected_data(),
            id='no_orders_restrictions',
        ),
        pytest.param(
            [
                {
                    'allowed_orders_count': {'start': 1, 'end': 1},
                    'application_name': 'some_application_name',
                    'payment_method': 'some_payment_method',
                },
            ],
            None,
            _common_expected_data(''),
            id='no_orders_count',
        ),
        pytest.param(
            [
                {
                    'allowed_orders_count': {'start': 1, 'end': 1},
                    'application_name': 'some_application_name',
                    'payment_method': 'some_payment_method',
                },
            ],
            [
                {
                    'orders_count': 0,
                    'application_name': 'some_application_name',
                    'payment_method': 'some_payment_method',
                },
            ],
            _common_expected_data(''),
            id='too_small_orders_count',
        ),
        pytest.param(
            [
                {
                    'allowed_orders_count': {'start': 1, 'end': 1},
                    'application_name': 'some_application_name',
                    'payment_method': 'some_payment_method',
                },
            ],
            [
                {
                    'orders_count': 2,
                    'application_name': 'some_application_name',
                    'payment_method': 'some_payment_method',
                },
            ],
            _common_expected_data(''),
            id='too_big_orders_count',
        ),
        pytest.param(
            [
                {
                    'allowed_orders_count': {'start': 1, 'end': 1},
                    'application_name': 'some_application_name',
                    'payment_method': 'some_payment_method',
                },
            ],
            [
                {
                    'orders_count': 1,
                    'application_name': 'another_application_name',
                    'payment_method': 'some_payment_method',
                },
            ],
            _common_expected_data(''),
            id='another_application_name',
        ),
        pytest.param(
            [
                {
                    'allowed_orders_count': {'start': 1, 'end': 1},
                    'application_name': 'some_application_name',
                    'payment_method': 'some_payment_method',
                },
            ],
            [
                {
                    'orders_count': 1,
                    'application_name': 'some_application_name',
                    'payment_method': 'another_payment_method',
                },
            ],
            _common_expected_data(''),
            id='another_payment_method',
        ),
        pytest.param(
            [
                {
                    'allowed_orders_count': {'start': 1, 'end': 1},
                    'application_name': 'some_application_name',
                    'payment_method': 'some_payment_method',
                },
            ],
            [
                {
                    'orders_count': 1,
                    'application_name': 'some_application_name',
                    'payment_method': 'some_payment_method',
                },
            ],
            _common_expected_data(),
            id='single_count',
        ),
        pytest.param(
            [
                {
                    'allowed_orders_count': {'start': 0, 'end': 0},
                    'application_name': 'some_application_name',
                    'payment_method': 'some_payment_method',
                },
            ],
            [
                {
                    'orders_count': 0,
                    'application_name': 'some_application_name',
                    'payment_method': 'some_payment_method',
                },
            ],
            _common_expected_data(),
            id='zero_orders_count',
        ),
        pytest.param(
            [
                {
                    'allowed_orders_count': {'start': 0, 'end': 0},
                    'application_name': 'some_application_name',
                    'payment_method': 'some_payment_method',
                },
            ],
            None,
            _common_expected_data(''),
            id='no_orders_does_NOT_count_as_zero',
        ),
        pytest.param(
            [
                {
                    'allowed_orders_count': {'start': 0, 'end': 0},
                    'application_name': 'some_application_name',
                    'payment_method': 'some_payment_method',
                },
            ],
            [
                {
                    'orders_count': 10,
                    'application_name': 'another_application_name',
                    'payment_method': 'another_payment_method',
                },
            ],
            _common_expected_data(),
            id='missing_orders_count_as_zero',
        ),
        pytest.param(
            [
                {
                    'allowed_orders_count': {'start': 9, 'end': 11},
                    'application_name': 'some_application_name',
                    'payment_method': 'some_payment_method',
                },
            ],
            [
                {
                    'orders_count': 9,
                    'application_name': 'some_application_name',
                    'payment_method': 'some_payment_method',
                },
                {
                    'orders_count': 9,
                    'application_name': 'another_application_name',
                    'payment_method': 'another_payment_method',
                },
            ],
            _common_expected_data(),
            id='several_orders_count',
        ),
        pytest.param(
            [
                {
                    'allowed_orders_count': {'start': 9, 'end': 11},
                    'application_name': 'some_application_name',
                    'payment_method': 'some_payment_method',
                },
                {
                    'allowed_orders_count': {'start': 9, 'end': 11},
                    'application_name': 'some_application_name',
                    'payment_method': 'another_payment_method',
                },
            ],
            [
                {
                    'orders_count': 9,
                    'application_name': 'some_application_name',
                    'payment_method': 'some_payment_method',
                },
                {
                    'orders_count': 9,
                    'application_name': 'some_application_name',
                    'payment_method': 'another_payment_method',
                },
            ],
            _common_expected_data(),
            id='several_orders_count_one_application_name',
        ),
        pytest.param(
            [
                {
                    'allowed_orders_count': {'start': 18, 'end': 18},
                    'application_name': 'some_application_name',
                },
            ],
            [
                {
                    'orders_count': 9,
                    'application_name': 'some_application_name',
                    'payment_method': 'some_payment_method',
                },
                {
                    'orders_count': 9,
                    'application_name': 'some_application_name',
                    'payment_method': 'another_payment_method',
                },
            ],
            _common_expected_data(),
            id='several_orders_count_missing_payment_method',
        ),
        pytest.param(
            [
                {
                    'allowed_orders_count': {'start': 18, 'end': 18},
                    'payment_method': 'some_payment_method',
                },
            ],
            [
                {
                    'orders_count': 9,
                    'application_name': 'some_application_name',
                    'payment_method': 'some_payment_method',
                },
                {
                    'orders_count': 9,
                    'application_name': 'another_application_name',
                    'payment_method': 'some_payment_method',
                },
            ],
            _common_expected_data(),
            id='several_orders_count_missing_application_name',
        ),
        pytest.param(
            [
                {
                    'allowed_orders_count': {'start': 18, 'end': 18},
                    'application_name': 'some_application_name',
                    'payment_method': 'some_payment_method',
                },
            ],
            [
                {
                    'orders_count': 9,
                    'application_name': 'some_application_name',
                    'payment_method': 'some_payment_method',
                },
                {
                    'orders_count': 9,
                    'application_name': 'some_application_name',
                    'payment_method': 'some_payment_method',
                },
            ],
            _common_expected_data(),
            id='duplicate_orders_count',
        ),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(**common.DEFAULT_CONFIGS)
async def test_match_discounts_orders_counts(
        client,
        mocked_time,
        orders_restrictions: Optional[List[dict]],
        orders_counts: Optional[List[dict]],
        expected_data: dict,
        add_rules,
) -> None:
    hierarchy_names = ['menu_discounts', 'cart_discounts']
    add_rules_data = common.get_add_rules_data()
    if orders_restrictions is not None:
        for discounts in add_rules_data.values():
            for discount in discounts:
                discount['discount'][
                    'orders_restrictions'
                ] = orders_restrictions

    common_conditions: Dict[str, Any] = {
        'cities': ['213'],
        'countries': ['some_country'],
        'depots': ['some_depot'],
        'application_names': ['some_application_name'],
    }

    place_time_zone = 'UTC'

    if orders_counts is not None:
        common_conditions['orders_counts'] = orders_counts

    await common.init_bin_sets(client)
    await common.init_classes(client)
    await common.init_groups(client, mocked_time)

    await add_rules(add_rules_data)

    await client.invalidate_caches()

    random.shuffle(hierarchy_names)  # order insufficient

    await common.check_match_discounts(
        client,
        hierarchy_names,
        [],
        common_conditions,
        '2020-01-10T10:00:00+0000',  # Friday
        place_time_zone,
        False,
        expected_data,
        200,
    )
