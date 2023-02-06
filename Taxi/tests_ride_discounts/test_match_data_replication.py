import json
from typing import Optional

import pytest

from tests_ride_discounts import common


@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@pytest.mark.parametrize(
    'hierarchy_name, rules, expected_exclusions',
    (
        pytest.param(
            'payment_method_money_discounts',
            [
                {
                    'condition_name': 'active_period',
                    'values': [
                        {
                            'start': '2020-01-01T09:00:01+00:00',
                            'is_start_utc': False,
                            'end': '2021-01-01T00:00:00+00:00',
                            'is_end_utc': False,
                        },
                    ],
                },
                {
                    'condition_name': 'application_type',
                    'values': 'Any',
                    'exclusions': ['uber'],
                },
                {
                    'condition_name': 'zone',
                    'values': [
                        {
                            'is_prioritized': False,
                            'name': 'br_moscow',
                            'type': 'geonode',
                        },
                    ],
                },
                {'condition_name': 'tariff', 'values': ['econom']},
                {'condition_name': 'intermediate_point_is_set', 'values': [1]},
            ],
            {'application_type': ['uber']},
            id='payment_method_money_discounts',
        ),
    ),
)
@pytest.mark.config(
    DISCOUNTS_MATCH_REPLICATION_SETTINGS={
        '__default__': {'match_data': {'enabled': True, 'chunk_size': 10}},
    },
)
async def test_match_data_replication(
        client,
        mockserver,
        check_add_rules_validation,
        hierarchy_name,
        rules,
        expected_exclusions,
):
    def _prepare_response(response: Optional[dict]) -> Optional[dict]:
        if response:
            for data in response:
                data['data']['data'].pop('create_draft_id', None)
        return response

    data = []

    is_check = False
    await check_add_rules_validation(
        is_check, {'affected_discount_ids': []}, hierarchy_name, rules,
    )

    @mockserver.json_handler('/replication/data/ride_discounts_match_data')
    def _put_data_handler(request):
        items = json.loads(request.get_data())['items']
        data.extend(items)
        return {
            'items': [{'id': item['id'], 'status': 'ok'} for item in items],
        }

    await client.run_task('match-data-replication-task')
    assert _prepare_response(data) == [
        {
            'id': '1',
            'data': {
                'id': '1',
                'created_at': '2019-01-01 00:00:00',
                'data': {
                    'discount': common.make_discount(
                        hierarchy_name=hierarchy_name,
                    ),
                    'hierarchy_name': hierarchy_name,
                    'exclusions': expected_exclusions,
                },
            },
        },
    ]
    data.clear()
    await client.run_task('match-data-replication-task')
    assert _prepare_response(data) == []
