import json
from typing import Optional

import pytest


REVISION_ID = '105'


@pytest.fixture(autouse=True)
def set_revision(pgsql):
    pg_cursor = pgsql['ride_discounts'].cursor()
    revision_id = '105'
    pg_cursor.execute(
        'ALTER SEQUENCE ride_discounts.match_rules_revision RESTART '
        f'WITH {revision_id};',
    )


def update_row(pgsql):
    pg_cursor = pgsql['ride_discounts'].cursor()
    pg_cursor.execute(
        'UPDATE ride_discounts.match_rules_payment_method_money_discounts '
        'SET active_period = 1 '
        f'WHERE __revision = {REVISION_ID};',
    )


def _prepare_response(response: Optional[dict]) -> Optional[dict]:
    if response:
        for data in response:
            data['data']['data']['meta'].pop('create_draft_id', None)
    return response


@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@pytest.mark.parametrize(
    'hierarchy_name, rules, expected_data',
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
            [
                {
                    'data': {
                        'created_at': '2019-01-01 00:00:00',
                        'data': {
                            'match_data_id': 1,
                            'meta': {
                                'create_draft_id': (
                                    'draft_id_check_add_rules_validation'
                                ),
                                'create_tickets': ['ticket-1', 'ticket-2'],
                                'replaced': False,
                            },
                            'rules': {
                                'active_period': {
                                    'end': '2021-01-01T03:00:00+03:00',
                                    'is_end_utc': False,
                                    'is_start_utc': False,
                                    'start': '2020-01-01T12:00:01+03:00',
                                },
                                'application_brand': {'type': 'Other'},
                                'application_platform': {'type': 'Other'},
                                'application_type': {'type': 'Any'},
                                'bins': {'value': 'Other'},
                                'has_yaplus': {'type': 'Other'},
                                'intermediate_point_is_set': {'value': 1},
                                'order_type': {'type': 'Other'},
                                'payment_method': {'type': 'Other'},
                                'point_b_is_set': {'type': 'Other'},
                                'tag': {'type': 'Other'},
                                'tariff': {'value': 'econom'},
                                'trips_restriction': {'type': 'Other'},
                                'zone': {
                                    'is_prioritized': False,
                                    'name': 'br_moscow',
                                    'type': 'geonode',
                                },
                            },
                        },
                        'id': REVISION_ID,
                    },
                    'id': REVISION_ID,
                },
            ],
            id='payment_method_money_discounts',
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
        is_check, {'affected_discount_ids': []}, hierarchy_name, rules,
    )

    @mockserver.json_handler('/replication/data/ride_discounts_match_rules')
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
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@pytest.mark.parametrize(
    'hierarchy_name, rules, expected_data',
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
            [
                {
                    'data': {
                        'created_at': '2019-01-01 00:00:00',
                        'data': {
                            'match_data_id': 1,
                            'meta': {
                                'create_draft_id': (
                                    'draft_id_check_add_rules_validation'
                                ),
                                'create_tickets': ['ticket-1', 'ticket-2'],
                                'replaced': False,
                            },
                            'rules': {
                                'active_period': {
                                    'end': '2021-01-01T03:00:00+03:00',
                                    'is_end_utc': False,
                                    'is_start_utc': False,
                                    'start': '2020-01-01T12:00:01+03:00',
                                },
                                'application_brand': {'type': 'Other'},
                                'application_platform': {'type': 'Other'},
                                'application_type': {'type': 'Any'},
                                'bins': {'value': 'Other'},
                                'has_yaplus': {'type': 'Other'},
                                'intermediate_point_is_set': {'value': 1},
                                'order_type': {'type': 'Other'},
                                'payment_method': {'type': 'Other'},
                                'point_b_is_set': {'type': 'Other'},
                                'tag': {'type': 'Other'},
                                'tariff': {'value': 'econom'},
                                'trips_restriction': {'type': 'Other'},
                                'zone': {
                                    'is_prioritized': False,
                                    'name': 'br_moscow',
                                    'type': 'geonode',
                                },
                            },
                        },
                        'id': REVISION_ID,
                    },
                    'id': REVISION_ID,
                },
                {
                    'data': {
                        'created_at': '2019-01-01 00:00:00',
                        'data': {
                            'match_data_id': 1,
                            'meta': {
                                'create_draft_id': (
                                    'draft_id_check_add_rules_validation'
                                ),
                                'create_tickets': ['ticket-1', 'ticket-2'],
                                'replaced': False,
                            },
                            'rules': {
                                'active_period': {
                                    'end': '2200-01-01T03:00:00+03:00',
                                    'is_end_utc': False,
                                    'is_start_utc': False,
                                    'start': '1970-01-01T03:00:00+03:00',
                                },
                                'application_brand': {'type': 'Other'},
                                'application_platform': {'type': 'Other'},
                                'application_type': {'type': 'Any'},
                                'bins': {'value': 'Other'},
                                'has_yaplus': {'type': 'Other'},
                                'intermediate_point_is_set': {'value': 1},
                                'order_type': {'type': 'Other'},
                                'payment_method': {'type': 'Other'},
                                'point_b_is_set': {'type': 'Other'},
                                'tag': {'type': 'Other'},
                                'tariff': {'value': 'econom'},
                                'trips_restriction': {'type': 'Other'},
                                'zone': {
                                    'is_prioritized': False,
                                    'name': 'br_moscow',
                                    'type': 'geonode',
                                },
                            },
                        },
                        'id': REVISION_ID,
                    },
                    'id': REVISION_ID,
                },
            ],
            id='payment_method_money_discounts',
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
        hierarchy_name,
        rules,
        expected_data,
        pgsql,
):
    data = []
    is_check = False
    await check_add_rules_validation(
        is_check, {'affected_discount_ids': []}, hierarchy_name, rules,
    )

    @mockserver.json_handler('/replication/data/ride_discounts_match_rules')
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
