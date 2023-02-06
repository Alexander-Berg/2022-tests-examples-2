import json
from typing import Optional

import pytest

from tests_eats_discounts import common


def update_row(pgsql):
    pg_cursor = pgsql['eats_discounts'].cursor()
    pg_cursor.execute(
        'UPDATE eats_discounts.match_rules_menu_discounts '
        'SET active_period = 1 '
        f'WHERE __revision = {common.START_REVISION};',
    )


def _prepare_response(response: Optional[dict]) -> Optional[dict]:
    if response:
        for data in response:
            data['data']['data']['meta'].pop('create_draft_id', None)
    return response


@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@pytest.mark.parametrize(
    'rules, expected_data',
    (
        pytest.param(
            [
                {
                    'condition_name': 'active_period',
                    'values': [
                        {
                            'start': '2020-01-01T09:00:01+00:00',
                            'is_start_utc': True,
                            'end': '2021-01-01T00:00:00+00:00',
                            'is_end_utc': True,
                        },
                    ],
                },
                {
                    'condition_name': 'region',
                    'values': 'Any',
                    'exclusions': [12345],
                },
                {'condition_name': 'brand', 'values': [1]},
                {'condition_name': 'place', 'values': [1]},
            ],
            [
                {
                    'data': {
                        'created_at': '2019-01-01 00:00:00',
                        'data': {
                            'match_data_id': int(common.START_DATA_ID),
                            'meta': {
                                'create_draft_id': (
                                    'draft_id_check_add_rules_validation'
                                ),
                            },
                            'rules': {
                                'active_period': {
                                    'end': '2021-01-01T03:00:00+03:00',
                                    'is_end_utc': True,
                                    'is_start_utc': True,
                                    'start': '2020-01-01T12:00:01+03:00',
                                },
                                'tag': {'type': 'Other'},
                                'experiment': {'type': 'Other'},
                                'country': {'type': 'Other'},
                                'region': {'type': 'Any'},
                                'brand': {'value': 1},
                                'place': {'value': 1},
                                'place_business': {'type': 'Other'},
                                'product': {'type': 'Other'},
                                'shipping_type': {'type': 'Other'},
                                'orders_count': {'type': 'Other'},
                                'brand_orders_count': {'type': 'Other'},
                                'place_orders_count': {'type': 'Other'},
                                'restaurant_orders_count': {'type': 'Other'},
                                'retail_orders_count': {'type': 'Other'},
                                'time_from_last_order_range': {
                                    'type': 'Other',
                                },
                                'brand_time_from_last_order_range': {
                                    'type': 'Other',
                                },
                                'place_time_from_last_order_range': {
                                    'type': 'Other',
                                },
                            },
                        },
                        'id': str(common.START_REVISION),
                    },
                    'id': str(common.START_REVISION),
                },
            ],
            id='menu_discounts',
        ),
    ),
)
@pytest.mark.config(
    DISCOUNTS_MATCH_REPLICATION_SETTINGS={
        '__default__': {'match_rules': {'enabled': True, 'chunk_size': 10}},
    },
)
async def test_match_rules_replication(
        client, mockserver, check_add_rules_validation, rules, expected_data,
):
    data = []
    is_check = False
    hierarchy_name = 'menu_discounts'
    await check_add_rules_validation(
        is_check,
        {'affected_discount_ids': [], 'revisions': []},
        hierarchy_name,
        rules,
    )

    @mockserver.json_handler('/replication/data/eats_discounts_match_rules')
    def _put_data_handler(request):
        items = json.loads(request.get_data())['items']
        data.extend(items)
        return {
            'items': [{'id': item['id'], 'status': 'ok'} for item in items],
        }

    await client.run_task('match-rules-replication-task')
    await client.run_task('match-rules-replication-task')
    assert _prepare_response(data) == _prepare_response(expected_data)


@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.pgsql('eats_discounts', files=['init.sql'])
@pytest.mark.parametrize(
    'rules, expected_data',
    (
        pytest.param(
            [
                {
                    'condition_name': 'active_period',
                    'values': [
                        {
                            'start': '2020-01-01T09:00:01+00:00',
                            'is_start_utc': True,
                            'end': '2021-01-01T00:00:00+00:00',
                            'is_end_utc': True,
                        },
                    ],
                },
                {
                    'condition_name': 'region',
                    'values': 'Any',
                    'exclusions': [12345],
                },
                {'condition_name': 'brand', 'values': [1]},
                {'condition_name': 'place', 'values': [1]},
            ],
            [
                {
                    'data': {
                        'created_at': '2019-01-01 00:00:00',
                        'data': {
                            'match_data_id': int(common.START_DATA_ID),
                            'meta': {
                                'create_draft_id': (
                                    'draft_id_check_add_rules_validation'
                                ),
                            },
                            'rules': {
                                'active_period': {
                                    'end': '2021-01-01T03:00:00+03:00',
                                    'is_end_utc': True,
                                    'is_start_utc': True,
                                    'start': '2020-01-01T12:00:01+03:00',
                                },
                                'tag': {'type': 'Other'},
                                'experiment': {'type': 'Other'},
                                'country': {'type': 'Other'},
                                'region': {'type': 'Any'},
                                'brand': {'value': 1},
                                'place': {'value': 1},
                                'product': {'type': 'Other'},
                                'shipping_type': {'type': 'Other'},
                                'place_business': {'type': 'Other'},
                                'restaurant_orders_count': {'type': 'Other'},
                                'retail_orders_count': {'type': 'Other'},
                                'orders_count': {'type': 'Other'},
                                'brand_orders_count': {'type': 'Other'},
                                'place_orders_count': {'type': 'Other'},
                                'time_from_last_order_range': {
                                    'type': 'Other',
                                },
                                'brand_time_from_last_order_range': {
                                    'type': 'Other',
                                },
                                'place_time_from_last_order_range': {
                                    'type': 'Other',
                                },
                            },
                        },
                        'id': str(common.START_REVISION),
                    },
                    'id': str(common.START_REVISION),
                },
                {
                    'data': {
                        'created_at': '2019-01-01 00:00:00',
                        'data': {
                            'match_data_id': int(common.START_DATA_ID),
                            'meta': {
                                'create_draft_id': (
                                    'draft_id_check_add_rules_validation'
                                ),
                            },
                            'rules': {
                                'active_period': {
                                    'end': '2200-01-01T03:00:00+03:00',
                                    'is_end_utc': False,
                                    'is_start_utc': False,
                                    'start': '1970-01-01T03:00:00+03:00',
                                },
                                'tag': {'type': 'Other'},
                                'experiment': {'type': 'Other'},
                                'country': {'type': 'Other'},
                                'region': {'type': 'Any'},
                                'brand': {'value': 1},
                                'place': {'value': 1},
                                'product': {'type': 'Other'},
                                'shipping_type': {'type': 'Other'},
                                'place_business': {'type': 'Other'},
                                'restaurant_orders_count': {'type': 'Other'},
                                'retail_orders_count': {'type': 'Other'},
                                'orders_count': {'type': 'Other'},
                                'brand_orders_count': {'type': 'Other'},
                                'place_orders_count': {'type': 'Other'},
                                'time_from_last_order_range': {
                                    'type': 'Other',
                                },
                                'brand_time_from_last_order_range': {
                                    'type': 'Other',
                                },
                                'place_time_from_last_order_range': {
                                    'type': 'Other',
                                },
                            },
                        },
                        'id': str(common.START_REVISION),
                    },
                    'id': str(common.START_REVISION),
                },
            ],
            id='menu_discounts',
        ),
    ),
)
@pytest.mark.config(
    DISCOUNTS_MATCH_REPLICATION_SETTINGS={
        '__default__': {'match_rules': {'enabled': True, 'chunk_size': 10}},
    },
)
async def test_match_rules_replication_with_updated_row(
        client,
        mockserver,
        check_add_rules_validation,
        rules,
        expected_data,
        pgsql,
):
    data = []
    is_check = False
    hierarchy_name = 'menu_discounts'
    await check_add_rules_validation(
        is_check,
        {'affected_discount_ids': [], 'revisions': []},
        hierarchy_name,
        rules,
    )

    @mockserver.json_handler('/replication/data/eats_discounts_match_rules')
    def _put_data_handler(request):
        items = json.loads(request.get_data())['items']
        data.extend(items)
        return {
            'items': [{'id': item['id'], 'status': 'ok'} for item in items],
        }

    await client.run_task('match-rules-replication-task')
    update_row(pgsql)
    await client.run_task('match-rules-replication-task')
    assert _prepare_response(data) == _prepare_response(expected_data)
