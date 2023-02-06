import copy
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

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

DEFAULT_FETCH_REQUEST = {
    'request_time': '2020-01-10T10:00:00+0000',  # Friday
    'request_timezone': 'UTC',
    'depot': 'some_depot',
    'city': '213',
    'country': 'some_country',
    'experiments': ['some_exp'],
    'limit': 50,
    'offset': 0,
}


@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.pgsql(
    'grocery_discounts', files=['init.sql', 'fill_menu_discounts.sql'],
)
async def test_fetch_discounted_products_common(
        taxi_grocery_discounts, load_json, pgsql, mocked_time,
) -> None:
    request = {
        'request_time': '2020-01-10T10:00:00+0000',
        'request_timezone': 'UTC',
        'depot': '233211',
        'limit': 10,
        'city': '213',
        'country': 'RUS',
        'offset': 0,
        'tag': [],
        'experiment': ['second'],
        'filters': ['money_discount', 'cashback_discount'],
    }

    response = await taxi_grocery_discounts.post(
        'v3/fetch-discounted-products/', request, headers=common.get_headers(),
    )

    assert response.status_code == 200

    response_json = response.json()
    expected_json = load_json('response.json')

    assert response_json == expected_json


def _common_expected_data(
        hierarchies: Union[List[str], Tuple[str, ...]] = (
            'menu_discounts',
            'menu_cashback',
        ),
        all_discounts_count: Optional[int] = None,
) -> dict:
    if all_discounts_count is None:
        all_discounts_count = len(hierarchies)
    result: dict = {'all_discounts_count': all_discounts_count, 'items': []}
    discount_products = [
        {
            'groups': {'condition_name': 'group', 'value_type': 'Other'},
            'products': {'condition_name': 'product', 'value_type': 'Other'},
        },
    ]
    if 'menu_discounts' in hierarchies:
        result['items'].append(
            {
                'discount_products': copy.deepcopy(discount_products),
                'discount_type': 'money_discount',
            },
        )
    if 'menu_cashback' in hierarchies:
        result['items'].append(
            {
                'discount_products': copy.deepcopy(discount_products),
                'discount_type': 'cashback_discount',
            },
        )
    return result


async def _check_fetch_discounted_products(
        taxi_grocery_discounts,
        special_fetch_request_parameters: dict,
        expected_data: dict,
        expected_status_code: int,
):
    request = copy.deepcopy(DEFAULT_FETCH_REQUEST)
    request.update(special_fetch_request_parameters)
    expected_data = copy.deepcopy(expected_data)
    response = await taxi_grocery_discounts.post(
        'v3/fetch-discounted-products/', request, headers=common.get_headers(),
    )

    assert response.status_code == expected_status_code
    if expected_status_code != 200:
        return

    response_json = response.json()
    assert response_json == expected_data


@pytest.mark.parametrize(
    'add_rules_data, expected_data, special_fetch_request_parameters',
    (
        pytest.param(
            common.get_add_rules_data(),
            _common_expected_data(),
            {},
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
            _common_expected_data(['menu_discounts']),
            {},
            id='add_menu_hierarchy_discount',
        ),
        pytest.param(
            common.get_add_rules_data(FUTURE_ACTIVE_PERIOD),
            _common_expected_data(),
            {'request_timezone': 'Europe/Moscow'},
            id='add_future_discounts_time_zone',
        ),
        pytest.param(
            common.get_add_rules_data(),
            _common_expected_data(['menu_discounts'], 2),
            {'limit': 1, 'offset': 1},
            id='add_all_hierarchies_discounts',
        ),
        pytest.param(
            common.get_add_rules_data(),
            _common_expected_data(['menu_cashback'], 2),
            {'limit': 1, 'offset': 0},
            id='add_all_hierarchies_discounts',
        ),
        pytest.param(
            common.get_add_rules_data(),
            _common_expected_data([], 2),
            {'limit': 1, 'offset': 2},
            id='add_all_hierarchies_discounts',
        ),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(**common.DEFAULT_CONFIGS)
async def test_fetch_discounted_products(
        taxi_grocery_discounts,
        pgsql,
        mocked_time,
        add_rules_data: Dict[str, List[dict]],
        expected_data: dict,
        special_fetch_request_parameters: dict,
        add_rules,
) -> None:
    await common.init_bin_sets(taxi_grocery_discounts)
    await common.init_classes(taxi_grocery_discounts)
    await common.init_groups(taxi_grocery_discounts, mocked_time)

    await add_rules(add_rules_data)

    await taxi_grocery_discounts.invalidate_caches()

    await _check_fetch_discounted_products(
        taxi_grocery_discounts,
        special_fetch_request_parameters,
        expected_data,
        200,
    )
