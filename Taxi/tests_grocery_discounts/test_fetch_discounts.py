import copy
import random
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
) -> dict:
    result: dict = {
        'all_discounts_count': 4,
        'match_results': [
            {
                'discounts': [
                    {
                        'discount': (
                            common.get_matched_discount(
                                common.get_add_rules_data(),
                                'bundle_discounts',
                            )
                        ),
                        'match_path': (
                            common.get_match_path(
                                'bundle_discounts', active_period,
                            )['match_path']
                        ),
                    },
                ],
                'status': 'ok',
                'hierarchy_name': 'bundle_discounts',
            },
            {
                'discounts': [
                    {
                        'discount': (
                            common.get_matched_discount(
                                common.get_add_rules_data(), 'cart_discounts',
                            )
                        ),
                        'match_path': (
                            common.cart_match_path(active_period)['match_path']
                        ),
                    },
                ],
                'status': 'ok',
                'hierarchy_name': 'cart_discounts',
            },
            {
                'discounts': [
                    {
                        'discount': (
                            common.get_matched_discount(
                                common.get_add_rules_data(),
                                'dynamic_discounts',
                            )
                        ),
                        'match_path': (
                            common.dynamic_match_path(active_period)[
                                'match_path'
                            ]
                        ),
                    },
                ],
                'status': 'ok',
                'hierarchy_name': 'dynamic_discounts',
            },
            {
                'discounts': [
                    {
                        'discount': (
                            common.get_matched_discount(
                                common.get_add_rules_data(), 'menu_discounts',
                            )
                        ),
                        'match_path': (
                            common.menu_match_path(active_period)['match_path']
                        ),
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
                                common.get_add_rules_data(),
                                'payment_method_discounts',
                            )
                        ),
                        'match_path': (
                            common.payment_method_match_path(active_period)[
                                'match_path'
                            ]
                        ),
                    },
                ],
                'status': 'ok',
                'hierarchy_name': 'payment_method_discounts',
            },
        ],
    }

    if hierarchy_name is not None:
        for res in result['match_results']:
            if res['hierarchy_name'] != hierarchy_name:
                result['all_discounts_count'] -= 1
                res['discounts'] = []
    return result


def _get_count_discounts(match_results: dict):
    discounts = match_results['match_results']
    result = 0
    for hierarchy in discounts:
        result += len(hierarchy['discounts'])
    return result


async def _check_fetch_discounts(
        taxi_grocery_discounts,
        hierarchy_names: List[str],
        request_time: str,
        depot_time_zone: str,
        depot: str,
        city: Optional[str],
        country: Optional[str],
        experiments: Optional[List[str]],
        show_match_parameters: bool,
        expected_data: dict,
        expected_status_code: int,
):
    expected_data = copy.deepcopy(expected_data)

    request = {
        'show_path': show_match_parameters,
        'request_time': request_time,
        'request_timezone': depot_time_zone,
        'hierarchy_names': hierarchy_names,
        'depot': depot,
    }

    if country is not None:
        request['country'] = country
    if city is not None:
        request['city'] = city
    if experiments is not None:
        request['experiments'] = experiments

    response = await taxi_grocery_discounts.post(
        'v3/fetch-discounts/', request, headers=common.get_headers(),
    )

    assert response.status_code == expected_status_code
    if expected_status_code != 200:
        return

    response_json = response.json()

    common.make_response_matched_results(response_json['match_results'])
    unique_hierarchy_names = set(hierarchy_names)
    expected_data['match_results'] = common.make_expected_matched_results(
        expected_data['match_results'],
        unique_hierarchy_names,
        show_match_parameters,
    )

    expected_data['all_discounts_count'] = _get_count_discounts(expected_data)

    assert response_json == expected_data


@pytest.mark.parametrize(
    'hierarchy_names',
    (
        pytest.param(
            [
                'menu_discounts',
                'cart_discounts',
                'bundle_discounts',
                'payment_method_discounts',
                'dynamic_discounts',
            ],
            id='all_hierarchies',
        ),
        pytest.param(['menu_discounts'], id='menu_discounts_hierarchy'),
        pytest.param(['cart_discounts'], id='cart_discounts_hierarchy'),
        pytest.param(['bundle_discounts'], id='bundle_discounts_hierarchy'),
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
    'add_rules_data, expected_data, depot_time_zone, '
    'depot, city, country, experiments',
    (
        pytest.param(
            common.get_add_rules_data(),
            _common_expected_data(),
            'UTC',
            'some_depot',
            '213',
            'some_country',
            ['some_exp'],
            id='add_all_hierarchies_discounts',
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
            _common_expected_data('menu_discounts'),
            'UTC',
            'some_depot',
            '213',
            'some_country',
            ['some_exp'],
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
            _common_expected_data('cart_discounts'),
            'UTC',
            'some_depot',
            '213',
            'some_country',
            ['some_exp'],
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
            _common_expected_data('payment_method_discounts'),
            'UTC',
            'some_depot',
            '213',
            'some_country',
            ['some_exp'],
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
            _common_expected_data('dynamic_discounts'),
            'UTC',
            'some_depot',
            '213',
            'some_country',
            ['some_exp'],
            id='add_dynamic_hierarchy_discount',
        ),
        pytest.param(
            common.get_add_rules_data(FUTURE_ACTIVE_PERIOD),
            _common_expected_data(''),
            'UTC',
            'some_depot',
            '213',
            'some_country',
            ['some_exp'],
            id='add_future_discounts',
        ),
        pytest.param(
            common.get_add_rules_data(FUTURE_ACTIVE_PERIOD),
            _common_expected_data(None, FUTURE_ACTIVE_PERIOD),
            'Europe/Moscow',
            'some_depot',
            '213',
            'some_country',
            ['some_exp'],
            id='add_future_discounts_time_zone',
        ),
        pytest.param(
            {
                'menu_discounts': [
                    {
                        'rules': [
                            common.VALID_ACTIVE_PERIOD,
                            {
                                'condition_name': 'orders_restriction',
                                'values': [
                                    {
                                        'allowed_orders_count': {
                                            'start': 0,
                                            'end': 1,
                                        },
                                    },
                                ],
                            },
                            {
                                'condition_name': 'country',
                                'values': ['some_country'],
                            },
                        ],
                        'discount': common.small_menu_discount(),
                    },
                ],
            },
            _common_expected_data(
                'all_hierarchies_is_empty', common.VALID_ACTIVE_PERIOD,
            ),
            'Europe/Moscow',
            'some_depot',
            '213',
            'some_country',
            ['some_exp'],
            id='discounts_with_orders_restrictions',
        ),
        pytest.param(
            common.get_full_add_rules_data(),
            {
                'match_results': [
                    {
                        'discounts': [
                            {
                                'discount': (
                                    common.get_matched_discount(
                                        common.get_full_add_rules_data(),
                                        'bundle_discounts',
                                    )
                                ),
                                **common.get_match_path('bundle_discounts'),
                            },
                        ],
                        'status': 'ok',
                        'hierarchy_name': 'bundle_discounts',
                    },
                    {
                        'discounts': [
                            {
                                'discount': (
                                    common.get_matched_discount(
                                        common.get_full_add_rules_data(),
                                        'cart_discounts',
                                    )
                                ),
                                'match_path': (
                                    common.cart_match_path()['match_path']
                                ),
                            },
                        ],
                        'status': 'ok',
                        'hierarchy_name': 'cart_discounts',
                    },
                    {
                        'discounts': [
                            {
                                'discount': (
                                    common.get_matched_discount(
                                        common.get_full_add_rules_data(),
                                        'dynamic_discounts',
                                    )
                                ),
                                'match_path': (
                                    common.dynamic_match_path()['match_path']
                                ),
                            },
                        ],
                        'status': 'ok',
                        'hierarchy_name': 'dynamic_discounts',
                    },
                    {
                        'discounts': [
                            {
                                'discount': (
                                    common.get_matched_discount(
                                        common.get_full_add_rules_data(),
                                        'menu_discounts',
                                    )
                                ),
                                'match_path': (
                                    common.menu_match_path()['match_path']
                                ),
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
                                        common.get_full_add_rules_data(),
                                        'payment_method_discounts',
                                    )
                                ),
                                'match_path': (
                                    common.payment_method_match_path()[
                                        'match_path'
                                    ]
                                ),
                            },
                        ],
                        'status': 'ok',
                        'hierarchy_name': 'payment_method_discounts',
                    },
                ],
            },
            'UTC',
            'some_depot',
            '213',
            'some_country',
            ['some_exp'],
            id='add_full_all_hierarchies_discounts',
        ),
    ),
)
@pytest.mark.parametrize(
    'show_match_parameters',
    (
        pytest.param(True, id='show_match_parameters'),
        pytest.param(False, id='not_show_match_parameters'),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(**common.DEFAULT_CONFIGS)
async def test_fetch_discounts_common(
        taxi_grocery_discounts,
        pgsql,
        mocked_time,
        hierarchy_names: List[str],
        add_rules_data: Dict[str, List[dict]],
        expected_data: dict,
        depot_time_zone: str,
        depot: str,
        city: Optional[str],
        country: Optional[str],
        experiments: Optional[List[str]],
        show_match_parameters: bool,
        add_rules,
) -> None:
    await common.init_bin_sets(taxi_grocery_discounts)
    await common.init_classes(taxi_grocery_discounts)
    await common.init_groups(taxi_grocery_discounts, mocked_time)

    await add_rules(add_rules_data)

    await taxi_grocery_discounts.invalidate_caches()

    random.shuffle(hierarchy_names)  # order insufficient

    await _check_fetch_discounts(
        taxi_grocery_discounts,
        hierarchy_names,
        '2020-01-10T10:00:00+0000',  # Friday
        depot_time_zone,
        depot,
        city,
        country,
        experiments,
        show_match_parameters,
        expected_data,
        200,
    )


@pytest.mark.parametrize(
    'hierarchy_names',
    (
        pytest.param(
            ['menu_discounts', 'cart_discounts', 'payment_method_discounts'],
            id='many_hierarchies',
        ),
        pytest.param(['menu_discounts'], id='menu_discounts_hierarchy'),
        pytest.param(['cart_discounts'], id='cart_discounts_hierarchy'),
        pytest.param(
            ['payment_method_discounts'],
            id='payment_method_discounts_hierarchy',
        ),
        pytest.param(
            ['cart_discounts', 'cart_discounts', 'menu_discounts'],
            id='duplicate_hierarchy',
        ),
    ),
)
@pytest.mark.parametrize(
    'add_rules_data, expected_data, depot_time_zone, '
    'depot, city, country, experiments',
    (
        pytest.param(
            common.get_add_rules_data(),
            _common_expected_data(''),
            'UTC',
            'some_depot',
            '214',
            'some_country',
            ['some_exp'],
            id='another_city',
        ),
        pytest.param(
            common.get_add_rules_data(),
            _common_expected_data(''),
            'UTC',
            'some_depot',
            '213',
            'another_country',
            ['some_exp'],
            id='another_country',
        ),
        pytest.param(
            common.get_add_rules_data(),
            _common_expected_data(''),
            'UTC',
            'another_depot',
            '213',
            'some_country',
            ['some_exp'],
            id='another_depot',
        ),
    ),
)
@pytest.mark.parametrize(
    'show_match_parameters',
    (
        pytest.param(True, id='show_match_parameters'),
        pytest.param(False, id='not_show_match_parameters'),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(**common.DEFAULT_CONFIGS)
async def test_fetch_cart_menu_payment_method_discounts(
        taxi_grocery_discounts,
        pgsql,
        mocked_time,
        hierarchy_names: List[str],
        add_rules_data: Dict[str, List[dict]],
        expected_data: dict,
        depot_time_zone: str,
        depot: str,
        city: Optional[str],
        country: Optional[str],
        experiments: Optional[List[str]],
        show_match_parameters: bool,
        add_rules,
) -> None:
    await common.init_bin_sets(taxi_grocery_discounts)
    await common.init_classes(taxi_grocery_discounts)
    await common.init_groups(taxi_grocery_discounts, mocked_time)

    await add_rules(add_rules_data)

    await taxi_grocery_discounts.invalidate_caches()

    random.shuffle(hierarchy_names)  # order insufficient

    await _check_fetch_discounts(
        taxi_grocery_discounts,
        hierarchy_names,
        '2020-01-10T10:00:00+0000',  # Friday
        depot_time_zone,
        depot,
        city,
        country,
        experiments,
        show_match_parameters,
        expected_data,
        200,
    )


@pytest.mark.parametrize(
    'hierarchy_names',
    (pytest.param(['dynamic_discounts'], id='dynamic_discounts_hierarchy'),),
)
@pytest.mark.parametrize(
    'add_rules_data, expected_data, depot_time_zone, '
    'depot, city, country, experiments',
    (
        pytest.param(
            common.get_add_rules_data(),
            _common_expected_data(),
            'UTC',
            'some_depot',
            '214',
            'some_country',
            ['some_exp'],
            id='another_city',
        ),
        pytest.param(
            common.get_add_rules_data(),
            _common_expected_data(),
            'UTC',
            'some_depot',
            '213',
            'another_country',
            ['some_exp'],
            id='another_country',
        ),
        pytest.param(
            common.get_add_rules_data(),
            _common_expected_data(),
            'UTC',
            'another_depot',
            '213',
            'some_country',
            ['some_exp'],
            id='another_depot',
        ),
    ),
)
@pytest.mark.parametrize(
    'show_match_parameters',
    (
        pytest.param(True, id='show_match_parameters'),
        pytest.param(False, id='not_show_match_parameters'),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(**common.DEFAULT_CONFIGS)
async def test_fetch_dynamic_discounts(
        taxi_grocery_discounts,
        pgsql,
        mocked_time,
        hierarchy_names: List[str],
        add_rules_data: Dict[str, List[dict]],
        expected_data: dict,
        depot_time_zone: str,
        depot: str,
        city: Optional[str],
        country: Optional[str],
        experiments: Optional[List[str]],
        show_match_parameters: bool,
        add_rules,
) -> None:
    await common.init_bin_sets(taxi_grocery_discounts)
    await common.init_classes(taxi_grocery_discounts)
    await common.init_groups(taxi_grocery_discounts, mocked_time)

    await add_rules(add_rules_data)

    await taxi_grocery_discounts.invalidate_caches()

    random.shuffle(hierarchy_names)  # order insufficient

    await _check_fetch_discounts(
        taxi_grocery_discounts,
        hierarchy_names,
        '2020-01-10T10:00:00+0000',  # Friday
        depot_time_zone,
        depot,
        city,
        country,
        experiments,
        show_match_parameters,
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
@pytest.mark.parametrize(
    'show_match_parameters',
    (
        pytest.param(True, id='show_match_parameters'),
        pytest.param(False, id='not_show_match_parameters'),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_fetch_discounts_missing_hierarchy(
        taxi_grocery_discounts,
        missing_hierarchy_name,
        show_match_parameters: bool,
) -> None:
    await taxi_grocery_discounts.invalidate_caches()

    expected_data: dict = {
        'all_discounts_count': 0,
        'match_results': [
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
    }
    for result in expected_data['match_results']:
        if result['hierarchy_name'] == missing_hierarchy_name:
            result['status'] = 'hierarchy_not_found'
            break

    await _check_fetch_discounts(
        taxi_grocery_discounts,
        [
            'menu_discounts',
            'cart_discounts',
            'payment_method_discounts',
            'dynamic_discounts',
        ],
        '2020-01-10T10:00:00+0000',
        'UTC',
        'some_depot',
        'some_city',
        'some_country',
        ['some_exp'],
        show_match_parameters,
        expected_data,
        200,
    )
