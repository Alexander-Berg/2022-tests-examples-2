import datetime

import pytest


@pytest.mark.pgsql('conditioned', files=['conditioned.sql'])
@pytest.mark.parametrize(
    'rule_name, expected',
    [
        (
            'pg_json',
            {
                'id_1': {
                    'json_type': '{"a": "b"}',
                    'jsonb_type': '{"foo": "bar"}',
                },
                'id_2': {
                    'json_type': '{"a2": "b2"}',
                    'jsonb_type': '{"foo2": "bar2"}',
                },
                'id_3_null': {'json_type': 'null', 'jsonb_type': 'null'},
                'id_4_null': {'json_type': None, 'jsonb_type': None},
            },
        ),
        (
            'pg_json_loads',
            {
                'id_1': {
                    'json_type': {'a': 'b'},
                    'jsonb_type': {'foo': 'bar'},
                },
                'id_2': {
                    'json_type': {'a2': 'b2'},
                    'jsonb_type': {'foo2': 'bar2'},
                },
                'id_3_null': {'json_type': None, 'jsonb_type': None},
                'id_4_null': {'json_type': None, 'jsonb_type': None},
            },
        ),
    ],
)
async def test_pg_replication_json(run_replication, rule_name, expected):
    targets_data = await run_replication(rule_name, source_type='postgres')
    queue_docs = targets_data.queue_data_by_id(drop_confirmations=True)
    queue_docs = {
        doc_id: {
            'json_type': doc['data']['json_type'],
            'jsonb_type': doc['data']['jsonb_type'],
        }
        for doc_id, doc in queue_docs.items()
    }
    assert queue_docs == expected


@pytest.mark.pgsql('conditioned', files=['conditioned.sql'])
async def test_pg_replication_json_array_agg(run_replication):
    targets_data = await run_replication(
        'pg_json_loads_array_agg', source_type='postgres',
    )
    queue_docs = targets_data.queue_data_by_id(drop_confirmations=True)
    data = queue_docs['111']['data']['raw']
    data = sorted(data, key=lambda v: v['id'])
    assert data == [
        {
            'created_at': datetime.datetime(2019, 1, 24, 11, 0),
            'id': 'id_1',
            'json_type': {'a': 'b'},
            'jsonb_type': {'foo': 'bar'},
        },
        {
            'created_at': datetime.datetime(2019, 1, 24, 11, 0),
            'id': 'id_2',
            'json_type': {'a2': 'b2'},
            'jsonb_type': {'foo2': 'bar2'},
        },
        {
            'created_at': datetime.datetime(2019, 1, 24, 11, 0),
            'id': 'id_3_null',
            'json_type': None,
            'jsonb_type': None,
        },
        {
            'created_at': datetime.datetime(2019, 1, 24, 11, 0),
            'id': 'id_4_null',
            'json_type': None,
            'jsonb_type': None,
        },
    ]
