from typing import Dict
from typing import List
from typing import Optional

import pytest

from tests_grocery_discounts import common

PARAMETRIZE = pytest.mark.parametrize(
    'add_rules_data, all_conditions, hierarchy_name, new_end_time,'
    'expected_status_code, expected_response',
    (
        pytest.param(
            {
                'cart_discounts': [
                    {
                        'rules': [
                            {
                                'condition_name': 'active_period',
                                'values': [
                                    {
                                        'start': '2020-01-01T09:00:01+00:00',
                                        'is_start_utc': False,
                                        'is_end_utc': False,
                                        'end': '2021-01-01T00:00:00+00:00',
                                    },
                                ],
                            },
                            {
                                'condition_name': 'depot',
                                'values': ['some_depot', 'some_depot_2'],
                            },
                        ],
                        'discount': common.small_cart_discount('1'),
                    },
                ],
            },
            [
                [
                    {
                        'condition_name': 'active_period',
                        'values': [
                            {
                                'start': '2020-01-01T09:00:01+00:00',
                                'is_start_utc': False,
                                'is_end_utc': False,
                                'end': '2021-01-01T00:00:00+00:00',
                            },
                        ],
                    },
                    {'condition_name': 'depot', 'values': ['some_depot']},
                ],
                [
                    {
                        'condition_name': 'active_period',
                        'values': [
                            {
                                'start': '2020-01-01T09:00:01+00:00',
                                'is_start_utc': False,
                                'is_end_utc': False,
                                'end': '2021-01-01T00:00:00+00:00',
                            },
                        ],
                    },
                    {'condition_name': 'depot', 'values': ['some_depot_2']},
                ],
            ],
            'cart_discounts',
            '2020-01-01T09:00:01',
            200,
            None,
            id='ok',
        ),
        pytest.param(
            common.get_add_rules_data(),
            [[{'condition_name': 'depot', 'values': ['some_depot']}]],
            'menu_discounts',
            '2020-01-01T09:00:02',
            400,
            {
                'code': 'Validation error',
                'message': 'Rules must contain active_period field',
            },
            id='no_active_period',
        ),
    ),
)


@PARAMETRIZE
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(**common.DEFAULT_CONFIGS)
async def test_change_rules_end_time_bulk_check(
        taxi_grocery_discounts,
        hierarchy_name: str,
        add_rules_data: Dict[str, List[dict]],
        all_conditions: List[dict],
        new_end_time: str,
        expected_status_code: int,
        expected_response: Optional[dict],
        add_rules,
):
    await add_rules(add_rules_data)

    request: dict = {
        'items': [
            {
                'hierarchy_name': hierarchy_name,
                'conditions': conditions,
                'new_end_time': new_end_time,
            }
            for conditions in all_conditions
        ],
    }
    response = await taxi_grocery_discounts.post(
        'v3/admin/match-discounts/change-end-rules-time/bulk/check',
        json=request,
        headers=common.get_headers(),
    )
    assert response.status_code == expected_status_code
    if expected_response is None:
        expected_response = {'data': request}
    response_data = response.json()
    for item in response_data.get('data', {}).get('items', []):
        item.pop('revisions')
    response_data.pop('lock_ids', None)
    assert response_data == expected_response


@PARAMETRIZE
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
@pytest.mark.config(**common.DEFAULT_CONFIGS)
async def test_change_rules_end_time_bulk(
        taxi_grocery_discounts,
        pgsql,
        hierarchy_name: str,
        add_rules_data: Dict[str, List[dict]],
        all_conditions: List[dict],
        new_end_time: str,
        expected_status_code: int,
        expected_response: Optional[dict],
        add_rules,
):
    pgsql['grocery_discounts'].cursor().execute(
        'ALTER SEQUENCE grocery_discounts.match_rules_revision '
        'RESTART WITH 1;',
    )
    await add_rules(add_rules_data)

    request: dict = {
        'items': [
            {
                'hierarchy_name': hierarchy_name,
                'conditions': conditions,
                'new_end_time': new_end_time,
                'revisions': [index],
            }
            for index, conditions in enumerate(all_conditions, start=1)
        ],
    }
    response = await taxi_grocery_discounts.post(
        'v3/admin/match-discounts/change-end-rules-time/bulk',
        json=request,
        headers=common.get_draft_headers(),
    )
    assert response.status_code == expected_status_code, response.json()

    assert response.json() == (expected_response or {})
