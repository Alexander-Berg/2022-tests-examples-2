from typing import Any
from typing import Dict

import pytest


_RESPONSES = [
    {
        'provider_name': 'first_name',
        'query': 'query text',
        'enabled': False,
        'period': 60,
        'author': 'иванов',
        'last_modifier': 'иванов',
        'changed': '2018-08-30T12:34:56+0000',
        'created': '2018-08-22T02:34:56+0000',
        'name': 'first_name',
        'entity_type': 'user_id',
        'syntax': 'SQL',
        'tags': ['developer', 'yandex'],
        'last_run': {
            'operation_id': '5d92f9b968a6f554a5a8fbee',
            'started': '2018-08-22T02:37:56+0000',
            'status': 'aborted',
        },
    },
    {
        'provider_name': 'c5c97dfb70404435a6ba4a57',
        'query': 'select * from abc',
        'enabled': False,
        'period': 600,
        'author': 'ivanov',
        'last_modifier': 'ivanov',
        'changed': '2018-08-25T12:34:57+0000',
        'created': '2018-08-22T02:34:56+0000',
        'name': 'name_extended',
        'entity_type': 'udid',
        'syntax': 'SQL',
        'tags': [],
        'last_run': {
            'operation_id': '5d92f414095c4eba55ccfe48',
            'started': '2018-08-22T02:34:56+0000',
            'status': 'completed',
            'total_count': 8,
        },
    },
    {
        'provider_name': '3f4d6a2d929d4377ac3060c3',
        'query': 'select * from abc',
        'enabled': False,
        'period': 1200,
        'author': 'ivanov',
        'last_modifier': 'ivanov',
        'changed': '2018-08-22T12:34:56+0000',
        'created': '2018-08-22T02:34:56+0000',
        'name': 'nayme_with_error',
        'entity_type': 'dbid_uuid',
        'syntax': 'SQLv1',
        'tags': [],
        'last_run': {
            'operation_id': '5d92fa319dee76d0a1e0a6d3',
            'started': '2018-08-22T03:00:56+0000',
            'status': 'completed',
            'total_count': 1,
        },
    },
    {
        'provider_name': '6f9492477dda43fc9a36647a',
        'query': 'select * from abc',
        'enabled': True,
        'period': 1800,
        'author': 'ivanov',
        'last_modifier': 'petrov',
        'changed': '2018-08-22T03:34:56+0000',
        'created': '2018-08-22T02:34:56+0000',
        'name': 'surname_not_last',
        'entity_type': 'car_number',
        'syntax': 'SQLv1',
        'tags': [],
        'last_run': {
            'operation_id': '5d92f79b9f4b9eac6652cf6e',
            'started': '2018-08-22T03:04:56+0000',
            'status': 'failed',
        },
    },
    {
        'provider_name': 'dynamic_query',
        'query': 'select * from abc',
        'enabled': True,
        'period': 3540,
        'author': 'ivanov',
        'last_modifier': 'petrov',
        'changed': '2018-08-22T02:35:56+0000',
        'created': '2018-08-22T02:34:56+0000',
        'name': 'the_last_dynamic_query',
        # 'entity_type': 'does not have',
        'syntax': 'SQLv1',
        'tags': [],
        'last_run': {
            'operation_id': '5d92f79b9f4b9eac6652cf6f',
            'started': '2018-08-22T03:14:56+0000',
            'status': 'failed',
        },
    },
    {
        'provider_name': '489f019592ce4cf69184073e',
        'query': 'original query',
        'enabled': True,
        'period': 3600,
        'author': 'ivanov',
        'last_modifier': 'petrov',
        'changed': '2018-08-22T02:34:56+0000',
        'created': '2018-08-22T02:34:56+0000',
        'name': 'the_last_name',
        'entity_type': 'park',
        'syntax': 'SQL',
        'tags': [],
        'custom_execution_time': '2018-08-22T03:00:00+0000',
        'disable_at': '2018-08-23T09:00:00+0000',
        'ticket': 'TASKTICKET-1234',
        'tags_limit': 2000,
    },
]


@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', files=['pg_tags_queries.sql'])
@pytest.mark.parametrize(
    'index, query_name, response_code',
    [
        (0, 'first_name', 200),
        (1, 'name_extended', 200),
        (2, 'nayme_with_error', 200),
        (3, 'surname_not_last', 200),
        (4, 'the_last_dynamic_query', 200),
        (5, 'the_last_name', 200),
        (None, 'name_404', 404),
    ],
)
async def test_admin_queries_item(
        taxi_tags, index: int, query_name: str, response_code: int,
):
    response = await taxi_tags.get(
        'v1/admin/queries/item?id={}'.format(query_name),
    )
    assert response.status_code == response_code
    assert (index is None) or (response.json() == _RESPONSES[index])


@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', files=['pg_tags_queries.sql'])
@pytest.mark.parametrize(
    'response_code, response_body, data',
    [
        (400, None, {'sort_order': {'entity': 'not_from_enum'}}),
        (400, None, {'filters': {'changed': {'from': 'not_timestamp'}}}),
        (400, None, {'filters': {'changed': {}}}),  # missed properties from/to
        (400, None, {'filters': {'enabled': 'not_bool'}}),
        (400, None, {'filters': {'name_part': ''}}),
        (200, _RESPONSES, {}),
        (200, _RESPONSES[2:], {'offset': 2}),
        (200, _RESPONSES, {'filters': {}}),
        (200, _RESPONSES, {'filters': {'name_part': '_'}}),
        (200, _RESPONSES[:2], {'limit': 2}),
        (200, _RESPONSES[1:2], {'limit': 1, 'offset': 1}),
        (200, _RESPONSES[:4], {'limit': 4}),
        (
            200,
            _RESPONSES[3:],
            {
                'limit': 5,
                'filters': {'changed': {'to': '2018-08-22T06:34:56+0000'}},
            },
        ),
        (
            200,
            _RESPONSES[:1],
            {
                'limit': 1,
                'filters': {'changed': {'from': '2018-08-22T06:34:56+0000'}},
            },
        ),
        (
            200,
            _RESPONSES[:4],
            {
                'limit': 5,
                'filters': {'changed': {'from': '2018-08-22T06:34:56+0300'}},
            },
        ),
        (
            200,
            _RESPONSES[:1],
            {
                'limit': 5,
                'filters': {'changed': {'from': '2018-08-25T16:34:56+0000'}},
            },
        ),
        (
            200,
            _RESPONSES[2:],
            {
                'limit': 5,
                'filters': {
                    'changed': {
                        'from': '2018-08-22T02:00:00+0000',
                        'to': '2018-08-22T13:00:00+0000',
                    },
                },
            },
        ),
        (200, _RESPONSES[:3], {'filters': {'enabled': False}}),
        (200, _RESPONSES[3:], {'filters': {'enabled': True}}),
        (
            200,
            _RESPONSES[::-1],
            {'sort_order': {'direction': 'DESC', 'entity': 'period'}},
        ),
        (200, _RESPONSES, {'sort_order': {'entity': 'period'}}),
        (200, _RESPONSES[::-1], {'sort_order': {'entity': 'changed'}}),
        (
            200,
            _RESPONSES[::-1],
            {'sort_order': {'direction': 'DESC', 'entity': 'period'}},
        ),
        (
            200,
            _RESPONSES[5:] + _RESPONSES[1::-1] + _RESPONSES[2:5],
            {'sort_order': {'entity': 'last_run'}},
        ),
        (
            200,
            _RESPONSES[4:1:-1] + _RESPONSES[0:2] + _RESPONSES[5:],
            {'sort_order': {'entity': 'last_run', 'direction': 'DESC'}},
        ),
        (
            200,
            _RESPONSES[:2:-1],
            {
                'sort_order': {'direction': 'DESC', 'entity': 'period'},
                'filters': {'last_modifier': 'petrov'},
            },
        ),
        (
            200,
            _RESPONSES[-1:] + _RESPONSES[-2:-1],
            {
                'sort_order': {'direction': 'ASC', 'entity': 'disable_at'},
                'filters': {'name_part': 'the_last'},
            },
        ),
        (200, _RESPONSES[::-1], {'sort_order': {'entity': 'changed'}}),
        (200, _RESPONSES, {'sort_order': {'entity': 'name'}}),
        (200, _RESPONSES[1:], {'filters': {'author': 'ivanov'}}),
        (200, _RESPONSES[3:], {'filters': {'last_modifier': 'petrov'}}),
        (200, _RESPONSES[:1], {'filters': {'name_part': 'first'}}),
        (200, _RESPONSES[2:3], {'filters': {'name_part': 'ayme'}}),
        (200, _RESPONSES[3:], {'filters': {'name_part': 'last'}}),
        (200, _RESPONSES[4:], {'filters': {'name_part': 'THE_last'}}),
        (200, [], {'filters': {'last_run_status': 'running'}}),
        (200, _RESPONSES[1:3], {'filters': {'last_run_status': 'completed'}}),
        (200, _RESPONSES[3:5], {'filters': {'last_run_status': 'failed'}}),
        (200, _RESPONSES[:1], {'filters': {'last_run_status': 'aborted'}}),
        (
            200,
            _RESPONSES[2:3],
            {'offset': 1, 'filters': {'last_run_status': 'completed'}},
        ),
        (200, _RESPONSES[1:5], {'filters': {'query_part': 'aBc'}}),
        (200, [], {'filters': {'query_part': 'abcd'}}),
        (
            200,
            _RESPONSES[1:4],
            {'filters': {'name_part': 'me_', 'query_part': 'abc'}},
        ),
        (
            200,
            _RESPONSES[3:],
            {
                'filters': {
                    'author': 'ivanov',
                    'changed': {'to': '2018-8-22T06:34:56+0300'},
                },
            },
        ),
        (
            200,
            _RESPONSES[1:3],
            {'filters': {'last_modifier': 'ivanov', 'enabled': False}},
        ),
        (
            200,
            _RESPONSES[1:2],
            {
                'filters': {
                    'author': 'ivanov',
                    'changed': {
                        'from': '2018-08-25T12:34:57+0000',
                        'to': '2018-08-25T12:34:57+0000',
                    },
                    'created': {
                        'from': '2018-08-22T02:34:56+0000',
                        'to': '2018-08-22T02:34:56+0000',
                    },
                    'enabled': False,
                    'last_modifier': 'ivanov',
                    'last_run_status': 'completed',
                },
            },
        ),
    ],
)
async def test_admin_queries_list(
        taxi_tags,
        response_code: int,
        response_body: Dict[str, Any],
        data: Dict[str, Any],
):
    response = await taxi_tags.post('v1/admin/queries/list', data)
    assert response.status_code == response_code
    if response_body is not None:
        assert response.json() == response_body


@pytest.mark.nofilldb()
async def test_admin_queries_syntaxes(taxi_tags):
    response = await taxi_tags.get('v1/admin/queries/syntaxes')
    assert response.status_code == 200
    assert response.json() == {
        'syntaxes': [
            {'syntax': 'CLICKHOUSE', 'label': 'ClickHouse'},
            {'syntax': 'SQLv1', 'label': 'SQLv1'},
        ],
    }
