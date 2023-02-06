import json

import pytest

from tests_grocery_discounts import common


@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.parametrize(
    'hierarchy_name, rules',
    (
        pytest.param(
            'payment_method_discounts',
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
            ],
            id='payment_method_discounts',
        ),
    ),
)
@pytest.mark.config(
    DISCOUNTS_MATCH_REPLICATION_SETTINGS={
        '__default__': {'match_data': {'enabled': True, 'chunk_size': 10}},
    },
)
async def test_match_data_replication(
        client, mockserver, check_add_rules_validation, hierarchy_name, rules,
):
    data = []
    discount = common.small_payment_method_discount()
    discount['active_with_surge'] = False

    is_check = False
    await check_add_rules_validation(
        is_check, {'revisions': []}, hierarchy_name, rules, discount,
    )

    @mockserver.json_handler('/replication/data/grocery_discounts_match_data')
    def _put_data_handler(request):
        items = json.loads(request.get_data())['items']
        data.extend(items)
        return {
            'items': [{'id': item['id'], 'status': 'ok'} for item in items],
        }

    await client.run_task('match-data-replication-task')
    assert data == [
        {
            'id': '123',
            'data': {
                'id': '123',
                'created_at': '2019-01-01 00:00:00',
                'data': {
                    'hierarchy_name': hierarchy_name,
                    'discount': discount,
                    'create_draft_id': 'draft_id_check_add_rules_validation',
                },
            },
        },
    ]
    data.clear()
    await client.run_task('match-data-replication-task')
    assert data == []
