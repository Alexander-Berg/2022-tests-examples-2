# pylint: disable=protected-access
import json

import pytest

from replication.api import queue_read_data

RULE_NAME = 'read_personal_data'


@pytest.mark.parametrize(
    'read_data_query, expected',
    [
        (
            {'targets': ['read_personal_data_without_pd']},
            {
                'confirm_id': 'dummy_id',
                'count': 3,
                'items': [
                    {
                        'data': '{"id": "id_1"}',
                        'id': 'id_1',
                        'upload_ts': '2020-02-01T12:00:00+0000',
                    },
                    {
                        'data': '{"id": "id_2"}',
                        'id': 'id_2',
                        'upload_ts': '2020-02-01T20:00:00+0000',
                    },
                    {
                        'data': '{"foo": {"bar": {"phone": "+71234567890"}}}',
                        'id': 'id_3',
                        'upload_ts': '2020-02-01T21:00:00+0000',
                    },
                ],
                'last_upload_ts': '2020-02-01T21:00:00+0000',
                'output_format': 'json',
                'try_next_read_after': (
                    queue_read_data._DEFAULT_NEXT_TRY_AFTER_SECONDS
                ),
            },
        ),
    ],
)
async def test_read_personal_data(
        monkeypatch,
        replication_client,
        mock_personal,
        read_data_query,
        expected,
):
    rule_name = RULE_NAME
    monkeypatch.setattr(
        queue_read_data, '_generate_confirm_id', lambda: 'dummy_id',
    )
    response = await replication_client.post(
        f'/v1/queue/read/{rule_name}', data=json.dumps(read_data_query),
    )
    assert response.status == 200, await response.text()
    response_json = await response.json()
    assert response_json == expected


@pytest.mark.parametrize(
    ['rule_name', 'input_json', 'expected', 'expected_response'],
    [
        (
            'read_personal_data',
            {
                'items': [
                    {'data': {'id': 'id_1'}, 'id': 'id_1'},
                    {'data': {'id': 'id_2'}, 'id': 'id_2'},
                    {
                        'data': {
                            'id': 'id_3',
                            'foo': {'bar': {'phone': '+71234567890'}},
                        },
                        'id': 'id_3',
                    },
                ],
            },
            {
                'id_1': {'id': 'id_1'},
                'id_2': {'id': 'id_2'},
                'id_3': {
                    'foo': {'bar': {'phone': '09876543217+'}},
                    'id': 'id_3',
                },
            },
            {
                'items': [
                    {'id': 'id_1', 'status': 'ok'},
                    {'id': 'id_2', 'status': 'ok'},
                    {'id': 'id_3', 'status': 'ok'},
                ],
            },
        ),
        (
            'read_personal_data',
            {
                'items': [
                    {
                        'data': {
                            'id': 'id_3',
                            'foo': {'bar': {'phone': '+71234567890'}},
                        },
                        'id': 'id_3',
                    },
                    {
                        'data': {
                            'id': 'id_4',
                            'foo': {'bar': {'phone': 'error'}},
                        },
                        'id': 'id_4',
                    },
                ],
            },
            {
                'id_1': {'id': 'id_1'},
                'id_2': {'id': 'id_2'},
                'id_3': {
                    'foo': {'bar': {'phone': '09876543217+'}},
                    'id': 'id_3',
                },
                'id_4': {'foo': {'bar': {'phone': None}}, 'id': 'id_4'},
            },
            {
                'items': [
                    {'id': 'id_3', 'status': 'ok'},
                    {
                        'error_message': (
                            'key=foo.bar.phone, '
                            'value=\'error\': unexpected error'
                        ),
                        'id': 'id_4',
                        'status': 'warn',
                    },
                ],
            },
        ),
    ],
)
async def test_put_personal_data(
        replication_client,
        replication_ctx,
        mock_personal,
        rule_name,
        input_json,
        expected,
        expected_response,
):
    response = await replication_client.post(
        f'/data/{rule_name}', json=input_json,
    )
    assert response.status == 200, await response.text()

    staging_db = replication_ctx.rule_keeper.staging_db
    docs = {
        doc['_id']: doc['data']
        async for doc in (
            staging_db.get_queue_mongo_shard(
                'read_personal_data',
            ).primary.find()
        )
    }
    assert docs == expected
    assert await response.json() == expected_response
