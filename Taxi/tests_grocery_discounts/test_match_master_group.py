import copy
from typing import Any
from typing import Dict
from typing import List

import pytest

from tests_grocery_discounts import common

COMMON_CONDITIONS = {
    'cities': ['213'],
    'countries': ['RUS'],
    'depots': ['some_depot'],
}


def _get_header():
    headers = copy.deepcopy(common.DEFAULT_DISCOUNTS_HEADERS)
    headers['X-YaTaxi-Draft-Id'] = 'grocery_discounts_draft_id'
    return headers


async def _create_discounts(taxi_grocery_discounts, load_json):
    add_rules_body = load_json('add_rules_request.json')
    additional_conditions = (['cereals'], ['food'])
    for master_group in additional_conditions:
        request_body = copy.deepcopy(add_rules_body)
        request_body['rules'] += [
            {
                'condition_name': 'master_group',
                'values': master_group or 'Other',
            },
        ]
        response = await taxi_grocery_discounts.post(
            'v3/admin/match-discounts/add-rules',
            request_body,
            headers=_get_header(),
        )
        assert response.status_code == 200


@pytest.mark.parametrize(
    'subqueries, expected_data_name',
    (
        pytest.param(
            [
                {
                    'subquery_id': '1234',
                    'conditions': {
                        'master_groups': ['cereals', 'food'],
                        'product': 'buckwheat',
                    },
                },
            ],
            'cereals',
            id='child_master_group',
        ),
        pytest.param(
            [
                {
                    'subquery_id': '2345',
                    'conditions': {
                        'master_groups': ['chocolate', 'food'],
                        'product': 'alyonka_chocolate',
                    },
                },
            ],
            'food',
            id='root_master_group',
        ),
    ),
)
@pytest.mark.config(**common.DEFAULT_CONFIGS)
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+0000')
async def test_validate_categories(
        client,
        taxi_grocery_discounts,
        taxi_config,
        load_json,
        subqueries: List[Dict[str, Any]],
        expected_data_name: str,
):
    await _create_discounts(taxi_grocery_discounts, load_json)
    await taxi_grocery_discounts.invalidate_caches()
    await common.check_match_discounts(
        client,
        ['markdown_discounts'],
        subqueries,
        COMMON_CONDITIONS,
        '2020-01-10T10:00:00+0000',  # Friday
        request_time_zone='UTC',
        show_match_parameters=False,
        expected_data=load_json('response.json')[expected_data_name],
        expected_status_code=200,
    )
