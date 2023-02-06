import json

import pytest


@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.parametrize(
    'hierarchy_name, rules, expected_data',
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
            [
                {
                    'data': {
                        'created_at': '2019-01-01 00:00:00',
                        'data': {
                            'match_data_id': 123,
                            'meta': {
                                'create_draft_id': (
                                    'draft_id_check_add_rules_validation'
                                ),
                                'create_author': 'user',
                            },
                            'rules': {
                                'active_period': {
                                    'end': '2021-01-01T03:00:00+03:00',
                                    'is_end_utc': False,
                                    'is_start_utc': False,
                                    'start': '2020-01-01T12:00:01+03:00',
                                },
                                'application_name': {'type': 'Other'},
                                'bins': {'type': 'Other'},
                                'city': {'type': 'Other'},
                                'class': {'value': 'No class'},
                                'country': {'type': 'Other'},
                                'depot': {'type': 'Other'},
                                'experiment': {'type': 'Other'},
                                'master_group': {'type': 'Other'},
                                'group': {'type': 'Other'},
                                'has_yaplus': {'type': 'Other'},
                                'payment_method': {'type': 'Other'},
                                'product': {'type': 'Other'},
                            },
                        },
                        'id': '1234',
                    },
                    'id': '1234',
                },
            ],
            id='payment_method_discounts',
        ),
    ),
)
@pytest.mark.config(
    DISCOUNTS_MATCH_REPLICATION_SETTINGS={
        '__default__': {'match_rules': {'enabled': True, 'chunk_size': 10}},
    },
)
async def test_match_rules_replication(
        client,
        mockserver,
        check_add_rules_validation,
        hierarchy_name,
        rules,
        expected_data,
):
    data = []
    is_check = False
    await check_add_rules_validation(
        is_check, {'revisions': []}, hierarchy_name, rules,
    )

    @mockserver.json_handler('/replication/data/grocery_discounts_match_rules')
    def _put_data_handler(request):
        items = json.loads(request.get_data())['items']
        data.extend(items)
        return {
            'items': [{'id': item['id'], 'status': 'ok'} for item in items],
        }

    await client.run_task('match-rules-replication-task')
    assert data == expected_data
    data.clear()
    await client.run_task('match-rules-replication-task')
    assert data == []
