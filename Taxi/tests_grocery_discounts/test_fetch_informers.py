from typing import Dict
from typing import List
from typing import Optional

import pytest

from tests_grocery_discounts import common


FUTURE_ACTIVE_PERIOD = {
    'condition_name': 'active_period',
    'values': [
        {
            'start': '2020-01-10T10:01:00+00:00',
            'is_utc': False,
            'end': '2021-01-01T00:00:00+00:00',
        },
    ],
}


@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.pgsql(
    'grocery_discounts', files=['init.sql', 'fill_menu_discounts.sql'],
)
async def test_fetch_informers_common(
        taxi_grocery_discounts, load_json, pgsql, mocked_time,
) -> None:
    request = {
        'request_time': '2020-01-10T10:00:00+0000',
        'request_timezone': 'UTC',
        'hierarchy_names': [
            'menu_discounts',
            'cart_discounts',
            'payment_method_discounts',
            'dynamic_discounts',
        ],
        'depot': '233211',
        'city': '213',
        'country': 'RUS',
        'tag': [],
        'experiment': ['second'],
    }

    response = await taxi_grocery_discounts.post(
        'v3/fetch-informers/', request, headers=common.get_headers(),
    )

    assert response.status_code == 200

    response_json = response.json()
    expected_json = load_json('response.json')

    assert response_json == expected_json


def _get_informer_value(
        add_rules_data: Dict[str, List[dict]], hierarchy_name: str,
):
    discount = add_rules_data[hierarchy_name][0]['discount']
    values = discount['values_with_schedules'][0]
    field_name = 'payment_method'
    for field in ('menu', 'cart'):
        if field in hierarchy_name:
            field_name = field
            break
    informer_values: Dict[str, dict] = {}
    for type_value in ('money_value', 'cashback_value'):
        if type_value in values:
            informer_values[type_value] = {}
            informer_values[type_value][field_name] = values[type_value]
    return informer_values


def _common_expected_data(
        add_rules_data: Dict[str, List[dict]],
        hierarchy_names: List[str] = None,
) -> dict:
    result: dict = {'informers': []}

    for hierarchy_name in hierarchy_names or []:
        result['informers'].append(
            {
                'hierarchy_name': hierarchy_name,
                'informer': {
                    'color': hierarchy_name + '_color',
                    'picture': hierarchy_name + '_picture',
                    'text': hierarchy_name + '_text',
                    'discount_value': _get_informer_value(
                        add_rules_data, hierarchy_name,
                    ),
                },
            },
        )

    result['informers'].sort(key=lambda result: result['hierarchy_name'])

    return result


async def _check_fetch_discounted_products(
        taxi_grocery_discounts,
        hierarchy_names: List[str],
        request_time: str,
        depot_time_zone: str,
        depot: str,
        city: Optional[str],
        country: Optional[str],
        experiments: Optional[List[str]],
        add_rules_data: dict,
        expected_status_code: int,
):
    expected_data = _common_expected_data(add_rules_data, hierarchy_names)

    request = {
        'request_time': request_time,
        'request_timezone': depot_time_zone,
        'depot': depot,
        'hierarchy_names': hierarchy_names,
    }

    if country is not None:
        request['country'] = country
    if city is not None:
        request['city'] = city
    if experiments is not None:
        request['experiments'] = experiments

    response = await taxi_grocery_discounts.post(
        'v3/fetch-informers/', request, headers=common.get_headers(),
    )

    assert response.status_code == expected_status_code
    if expected_status_code != 200:
        return

    response_json = response.json()
    response_json['informers'].sort(
        key=lambda result: result['hierarchy_name'],
    )
    assert response_json == expected_data


@pytest.mark.parametrize(
    'add_rules_data, depot_time_zone, ' 'depot, city, country, experiments',
    (
        pytest.param(
            common.get_add_rules_data(),
            'UTC',
            'some_depot',
            '213',
            'some_country',
            ['some_exp'],
            id='add_all_hierarchies_discounts',
        ),
    ),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(**common.DEFAULT_CONFIGS)
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
    ),
)
async def test_fetch_discountes_informers(
        taxi_grocery_discounts,
        pgsql,
        mocked_time,
        add_rules_data: Dict[str, List[dict]],
        depot_time_zone: str,
        depot: str,
        city: Optional[str],
        country: Optional[str],
        experiments: Optional[List[str]],
        add_rules,
        hierarchy_names: List[str],
) -> None:
    await common.init_bin_sets(taxi_grocery_discounts)
    await common.init_classes(taxi_grocery_discounts)
    await common.init_groups(taxi_grocery_discounts, mocked_time)

    await add_rules(add_rules_data)

    await taxi_grocery_discounts.invalidate_caches()

    await _check_fetch_discounted_products(
        taxi_grocery_discounts,
        hierarchy_names,
        '2020-01-10T10:00:00+0000',  # Friday
        depot_time_zone,
        depot,
        city,
        country,
        experiments,
        add_rules_data,
        200,
    )
