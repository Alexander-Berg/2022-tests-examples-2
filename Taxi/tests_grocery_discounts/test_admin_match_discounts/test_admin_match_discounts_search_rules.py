import copy
from typing import Dict
from typing import List
from typing import Optional

import discounts_match  # pylint: disable=E0401
import pytest

from tests_grocery_discounts import common

WITHIN_VALID_ACTIVE_PERIOD = {
    'condition_name': 'active_period',
    'values': [
        {
            'start': '2020-01-01T09:00:02+00:00',
            'is_start_utc': False,
            'is_end_utc': False,
            'end': '2020-12-31T00:00:00+00:00',
        },
    ],
}

AFTER_VALID_ACTIVE_PERIOD = {
    'condition_name': 'active_period',
    'values': [
        {
            'start': '2021-01-01T00:00:01+00:00',
            'is_start_utc': False,
            'is_end_utc': False,
            'end': '2021-01-01T00:00:02+00:00',
        },
    ],
}

BEFORE_VALID_ACTIVE_PERIOD = {
    'condition_name': 'active_period',
    'values': [
        {
            'start': '2020-01-01T08:00:00+00:00',
            'is_start_utc': False,
            'is_end_utc': False,
            'end': '2020-01-01T09:00:00+00:00',
        },
    ],
}


def _common_expected_data(
        hierarchy_name: Optional[str] = None,
        active_period: Optional[dict] = None,
) -> dict:
    result: dict = {
        'payment_method_discounts': [
            {
                'discount': (
                    common.get_added_discount(
                        common.get_add_rules_data(),
                        'payment_method_discounts',
                    )
                ),
                'match_path': (
                    common.payment_method_match_path(active_period)[
                        'match_path'
                    ]
                ),
                'meta_info': {
                    'create_draft_id': 'draft_id_check_add_rules_validation',
                    'create_author': 'user',
                },
            },
        ],
        'menu_discounts': [
            {
                'discount': (
                    common.get_added_discount(
                        common.get_add_rules_data(), 'menu_discounts',
                    )
                ),
                'match_path': (
                    common.menu_match_path(active_period)['match_path']
                ),
                'meta_info': {
                    'create_draft_id': 'draft_id_check_add_rules_validation',
                    'create_author': 'user',
                },
            },
        ],
        'cart_discounts': [
            {
                'discount': (
                    common.get_added_discount(
                        common.get_add_rules_data(), 'cart_discounts',
                    )
                ),
                'match_path': (
                    common.cart_match_path(active_period)['match_path']
                ),
                'meta_info': {
                    'create_draft_id': 'draft_id_check_add_rules_validation',
                    'create_author': 'user',
                },
            },
        ],
        'dynamic_discounts': [
            {
                'discount': (
                    common.get_added_discount(
                        common.get_add_rules_data(), 'dynamic_discounts',
                    )
                ),
                'match_path': (
                    common.dynamic_match_path(active_period)['match_path']
                ),
                'meta_info': {
                    'create_draft_id': 'draft_id_check_add_rules_validation',
                    'create_author': 'user',
                },
            },
        ],
    }

    if hierarchy_name is not None:
        for name in result:
            if name != hierarchy_name:
                result[name] = []
    return result


CART_DISCOUNT_EXCLUSIONS = {
    'products': ['some_product'],
    'groups': ['some_group'],
}


def _get_cart_discount_with_exclusions() -> dict:
    discount = copy.deepcopy(common.small_cart_discount())
    discount['exclusions'] = CART_DISCOUNT_EXCLUSIONS
    return discount


def _get_cart_discount_with_exclusions_expected_data(
        expected_data: dict,
) -> dict:
    result = copy.deepcopy(expected_data)
    result['cart_discounts'][0]['discount'][
        'exclusions'
    ] = CART_DISCOUNT_EXCLUSIONS
    return result


@pytest.mark.parametrize(
    'hierarchy_name',
    (
        pytest.param('menu_discounts', id='menu_discounts_hierarchy'),
        pytest.param('cart_discounts', id='cart_discounts_hierarchy'),
        pytest.param(
            'payment_method_discounts',
            id='payment_method_discounts_hierarchy',
        ),
        pytest.param('dynamic_discounts', id='dynamic_discounts_hierarchy'),
    ),
)
@pytest.mark.parametrize(
    'add_rules_data, conditions, limit, offset, expected_data,'
    'expected_status_code',
    (
        pytest.param(
            common.get_add_rules_data(),
            [
                {'condition_name': 'city', 'values': ['213']},
                {'condition_name': 'country', 'values': ['some_country']},
                {'condition_name': 'depot', 'values': ['some_depot']},
                {
                    'condition_name': 'application_name',
                    'values': ['some_application_name'],
                },
            ],
            1,
            0,
            _common_expected_data(),
            200,
            id='add_all_hierarchies_discounts',
        ),
        pytest.param(
            common.get_add_rules_data(),
            [],
            1,
            100500,
            _common_expected_data(),
            200,
            id='valid_offset',
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
            [],
            1,
            0,
            _common_expected_data('menu_discounts'),
            200,
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
            [],
            1,
            0,
            _common_expected_data('cart_discounts'),
            200,
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
            [],
            1,
            0,
            _common_expected_data('payment_method_discounts'),
            200,
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
            [],
            1,
            0,
            _common_expected_data('dynamic_discounts'),
            200,
            id='add_dynamic_hierarchy_discount',
        ),
        pytest.param(
            common.get_add_rules_data(AFTER_VALID_ACTIVE_PERIOD),
            [common.VALID_ACTIVE_PERIOD],
            1,
            0,
            _common_expected_data(''),
            200,
            id='add_future_discounts',
        ),
        pytest.param(
            common.get_add_rules_data(BEFORE_VALID_ACTIVE_PERIOD),
            [common.VALID_ACTIVE_PERIOD],
            1,
            0,
            _common_expected_data(''),
            200,
            id='add_past_discounts',
        ),
        pytest.param(
            common.get_add_rules_data(WITHIN_VALID_ACTIVE_PERIOD),
            [common.VALID_ACTIVE_PERIOD],
            1,
            0,
            _common_expected_data(None, WITHIN_VALID_ACTIVE_PERIOD),
            200,
            id='add_within_discounts',
        ),
        pytest.param(
            common.get_add_rules_data(AFTER_VALID_ACTIVE_PERIOD),
            [],
            1,
            0,
            _common_expected_data(None, AFTER_VALID_ACTIVE_PERIOD),
            200,
            id='add_future_discounts_no_active_period',
        ),
        pytest.param(
            common.get_full_add_rules_data(),
            [],
            1,
            0,
            {
                'cart_discounts': [
                    {
                        'discount': (
                            common.get_added_discount(
                                common.get_full_add_rules_data(),
                                'cart_discounts',
                            )
                        ),
                        'match_path': (common.cart_match_path()['match_path']),
                        'meta_info': {
                            'create_draft_id': (
                                'draft_id_check_add_rules_validation'
                            ),
                            'create_author': 'user',
                        },
                    },
                ],
                'menu_discounts': [
                    {
                        'discount': (
                            common.get_added_discount(
                                common.get_full_add_rules_data(),
                                'menu_discounts',
                            )
                        ),
                        'match_path': (common.menu_match_path()['match_path']),
                        'meta_info': {
                            'create_draft_id': (
                                'draft_id_check_add_rules_validation'
                            ),
                            'create_author': 'user',
                        },
                    },
                ],
                'payment_method_discounts': [
                    {
                        'discount': (
                            common.get_added_discount(
                                common.get_full_add_rules_data(),
                                'payment_method_discounts',
                            )
                        ),
                        'match_path': (
                            common.payment_method_match_path()['match_path']
                        ),
                        'meta_info': {
                            'create_draft_id': (
                                'draft_id_check_add_rules_validation'
                            ),
                            'create_author': 'user',
                        },
                    },
                ],
                'dynamic_discounts': [
                    {
                        'discount': (
                            common.get_added_discount(
                                common.get_full_add_rules_data(),
                                'menu_discounts',
                            )
                        ),
                        'match_path': (
                            common.dynamic_match_path()['match_path']
                        ),
                        'meta_info': {
                            'create_draft_id': (
                                'draft_id_check_add_rules_validation'
                            ),
                            'create_author': 'user',
                        },
                    },
                ],
            },
            200,
            id='add_full_all_hierarchies_discounts',
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
                        'discount': _get_cart_discount_with_exclusions(),
                    },
                ],
            },
            [],
            1,
            0,
            _get_cart_discount_with_exclusions_expected_data(
                _common_expected_data('cart_discounts'),
            ),
            200,
            id='add_cart_hierarchy_discount_with_exclusions',
        ),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(
    **common.DEFAULT_CONFIGS, GROCERY_DISCOUNTS_USE_NAMED_GROUPS=True,
)
async def test_search_rules_common(
        taxi_grocery_discounts,
        pgsql,
        mocked_time,
        hierarchy_name: str,
        add_rules_data: Dict[str, List[dict]],
        conditions: List[dict],
        expected_data: Optional[dict],
        limit: int,
        expected_status_code,
        offset: Optional[int],
        add_rules,
) -> None:
    await common.init_bin_sets(taxi_grocery_discounts)
    await common.init_classes(taxi_grocery_discounts)
    await common.init_groups(taxi_grocery_discounts, mocked_time)

    await add_rules(add_rules_data)

    await common.check_search_rules(
        taxi_grocery_discounts,
        hierarchy_name,
        conditions,
        limit,
        offset,
        expected_data,
        expected_status_code,
    )


@pytest.mark.parametrize(
    'hierarchy_name',
    (
        pytest.param('menu_discounts', id='menu_discounts_hierarchy'),
        pytest.param('cart_discounts', id='cart_discounts_hierarchy'),
        pytest.param(
            'payment_method_discounts',
            id='payment_method_discounts_hierarchy',
        ),
    ),
)
@pytest.mark.parametrize(
    'add_rules_data, conditions, limit, offset, expected_data,'
    'expected_status_code',
    (
        pytest.param(
            common.get_add_rules_data(),
            [{'condition_name': 'country', 'values': ['another_country']}],
            1,
            0,
            _common_expected_data(''),
            200,
            id='another_country',
        ),
        pytest.param(
            common.get_add_rules_data(),
            [{'condition_name': 'city', 'values': ['214']}],
            1,
            0,
            _common_expected_data(''),
            200,
            id='another_city',
        ),
        pytest.param(
            common.get_add_rules_data(),
            [{'condition_name': 'depot', 'values': ['another_depot']}],
            1,
            0,
            _common_expected_data(''),
            200,
            id='another_depot',
        ),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(
    **common.DEFAULT_CONFIGS, GROCERY_DISCOUNTS_USE_NAMED_GROUPS=True,
)
async def test_search_rules_menu_cart_payment_method_specific(
        taxi_grocery_discounts,
        pgsql,
        mocked_time,
        hierarchy_name: str,
        add_rules_data: Dict[str, List[dict]],
        conditions: List[dict],
        expected_data: Optional[dict],
        limit: int,
        expected_status_code,
        offset: Optional[int],
        add_rules,
) -> None:
    await common.init_bin_sets(taxi_grocery_discounts)
    await common.init_classes(taxi_grocery_discounts)
    await common.init_groups(taxi_grocery_discounts, mocked_time)

    await add_rules(add_rules_data)

    await common.check_search_rules(
        taxi_grocery_discounts,
        hierarchy_name,
        conditions,
        limit,
        offset,
        expected_data,
        expected_status_code,
    )


@pytest.mark.parametrize(
    'hierarchy_name',
    (pytest.param('dynamic_discounts', id='dynamic_discounts_hierarchy'),),
)
@pytest.mark.parametrize(
    'add_rules_data, conditions, limit, offset, expected_data,'
    'expected_status_code',
    (
        pytest.param(
            common.get_add_rules_data(),
            [{'condition_name': 'label', 'values': ['another_label']}],
            1,
            0,
            _common_expected_data(''),
            200,
            id='another_label',
        ),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(
    **common.DEFAULT_CONFIGS, GROCERY_DISCOUNTS_USE_NAMED_GROUPS=True,
)
async def test_search_rules_dynamic_specific(
        taxi_grocery_discounts,
        mocked_time,
        hierarchy_name: str,
        add_rules_data: Dict[str, List[dict]],
        conditions: List[dict],
        expected_data: Optional[dict],
        limit: int,
        expected_status_code,
        offset: Optional[int],
        add_rules,
) -> None:
    await common.init_bin_sets(taxi_grocery_discounts)
    await common.init_classes(taxi_grocery_discounts)
    await common.init_groups(taxi_grocery_discounts, mocked_time)

    await add_rules(add_rules_data)

    await common.check_search_rules(
        taxi_grocery_discounts,
        hierarchy_name,
        conditions,
        limit,
        offset,
        expected_data,
        expected_status_code,
    )


@pytest.mark.parametrize(
    'hierarchy_name',
    (
        pytest.param('cart_discounts', id='cart_discounts'),
        pytest.param('menu_discounts', id='menu_discounts'),
        pytest.param(
            'payment_method_discounts', id='payment_method_discounts',
        ),
        pytest.param('dynamic_discounts', id='dynamic_discounts'),
    ),
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
async def test_search_rules_missing_hierarchy(
        taxi_grocery_discounts, missing_hierarchy_name, hierarchy_name,
) -> None:

    if hierarchy_name == missing_hierarchy_name:
        expected_data: dict = {
            'code': '404',
            'message': f'Hierarchy {missing_hierarchy_name} not found',
        }
        expected_status_code = 400
    else:
        expected_data = _common_expected_data('')
        expected_status_code = 200

    await common.check_search_rules(
        taxi_grocery_discounts,
        hierarchy_name,
        [],
        1,
        None,
        expected_data,
        expected_status_code,
    )


@pytest.mark.parametrize(
    'authors, discounts_found',
    (
        pytest.param(['user'], True, id='author_match'),
        pytest.param(['some_author'], False, id='author_not_match'),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(
    **common.DEFAULT_CONFIGS, GROCERY_DISCOUNTS_USE_NAMED_GROUPS=True,
)
async def test_search_rules_author(
        client,
        pgsql,
        mocked_time,
        add_rules,
        authors: List[str],
        discounts_found: bool,
):
    hierarchy_name = 'menu_discounts'
    await common.init_classes(client)
    await common.init_groups(client, mocked_time)
    await add_rules(
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
                        {'condition_name': 'depot', 'values': ['some_depot']},
                    ],
                    'discount': common.small_menu_discount(),
                },
            ],
        },
    )

    await common.check_search_rules(
        client,
        hierarchy_name,
        [{'condition_name': 'city', 'values': ['213']}],
        1,
        0,
        _common_expected_data('menu_discounts' if discounts_found else ''),
        200,
        None,
        None,
        authors,
    )
