import copy
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import pytest

from tests_grocery_discounts import common


async def _set_config(
        taxi_grocery_discounts,
        taxi_config,
        enabling_validation: Optional[bool],
        config_categories: List[str],
):
    """
    Setting the desired values in the config
    """
    config: Dict[str, Any] = {
        'tanker_keys_by_hierarchy': {'__default__': config_categories},
    }
    if enabling_validation is not None:
        config['enabling_validation'] = enabling_validation
    taxi_config.set(GROCERY_DISCOUNTS_DISCOUNT_CATEGORIES_BY_HIERARCHY=config)
    await taxi_grocery_discounts.invalidate_caches()


def _get_add_rule_body() -> dict:
    return {
        'rules': [
            {'condition_name': 'country', 'values': 'Any'},
            {'condition_name': 'city', 'values': 'Any'},
            {'condition_name': 'depot', 'values': 'Any'},
            {'condition_name': 'experiment', 'values': 'Any'},
            {
                'condition_name': 'product_set',
                'values': [
                    ['product_id_1', 'product_id_2'],
                    ['product_id_1', 'product_id_3'],
                ],
            },
            {
                'condition_name': 'active_period',
                'values': [
                    {
                        'start': '2020-01-01T10:00:00+0000',
                        'end': '2020-02-10T18:00:00+0000',
                    },
                ],
            },
        ],
        'update_existing_discounts': True,
        'revisions': [],
        'data': {
            'hierarchy_name': 'cart_discounts',
            'discount': {
                'description': '1',
                'active_with_surge': False,
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
                ],
            },
        },
    }


def _preparing_parameters(
        add_rules_data: dict,
        hierarchy_name: str,
        discount_category: Optional[str],
) -> Tuple[dict, dict]:
    """
    Preparing data for a request to the add_rules handle
    """
    body = _get_add_rule_body()
    body['data'] = add_rules_data[hierarchy_name][0]
    if discount_category is not None:
        body['data']['discount']['discount_meta'][
            'discount_category'
        ] = discount_category
    body['data']['hierarchy_name'] = hierarchy_name
    headers = copy.deepcopy(common.DEFAULT_DISCOUNTS_HEADERS)
    headers['X-YaTaxi-Draft-Id'] = 'grocery_discounts_draft_id'
    return headers, body


def _get_excepted_data(
        enabling_validation: Optional[bool],
        config_categories: Optional[List[str]],
        discount_category: Optional[str],
) -> Tuple[int, Optional[dict]]:
    """
    Depending on the input data,
    the "status code" and the expected error body are selected
    """
    if (
            enabling_validation is not True
            or config_categories is None
            or discount_category is None
            or discount_category in config_categories
    ):
        return 200, None
    return (
        400,
        {
            'code': 'Validation error',
            'message': (
                'Discount category \''
                + discount_category
                + '\' does not exist'
            ),
        },
    )


@pytest.mark.config(**common.DEFAULT_CONFIGS)
@pytest.mark.parametrize('enabling_validation', (None, True, False))
@pytest.mark.parametrize(
    'config_categories', (['category_1'], ['category_1', 'category_2']),
)
@pytest.mark.parametrize(
    'discount_category', (None, 'category_1', 'category_2', 'bad_category'),
)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2019-01-01T10:00:00+0000')
async def test_validate_categories(
        taxi_grocery_discounts,
        taxi_config,
        enabling_validation: Optional[bool],
        config_categories: List[str],
        discount_category: Optional[str],
):
    """
    Checking all hierarchies that validation
    of discount categories is supported
    """
    await _set_config(
        taxi_grocery_discounts,
        taxi_config,
        enabling_validation,
        config_categories,
    )
    add_rules_data = common.get_add_rules_data()
    for hierarchy_name in add_rules_data:
        headers, body = _preparing_parameters(
            add_rules_data, hierarchy_name, discount_category,
        )
        response = await taxi_grocery_discounts.post(
            'v3/admin/match-discounts/add-rules', body, headers=headers,
        )
        excepted_code, excepted_body_error = _get_excepted_data(
            enabling_validation, config_categories, discount_category,
        )
        assert response.status_code == excepted_code
        if excepted_code == 400:
            assert response.json() == excepted_body_error
