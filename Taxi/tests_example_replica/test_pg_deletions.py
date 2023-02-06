import datetime

import pytest


CONFIG = {
    'example-replica': {
        'incremental_merge_time_limit_ms': 5000,
        'max_x_polling_delay_ms': 10,
        'min_x_polling_delay_ms': 0,
        'max_answer_data_size_bytes': 250,
        'updates_max_documents_count': 10,
        'is_dumper_enabled': False,
        'deleted_documents_ttl_seconds': 86400,
        'lagging_cursor_delay_seconds': 120,
    },
}


@pytest.mark.config(API_OVER_DATA_SERVICES=CONFIG)
@pytest.mark.pgsql('example_pg', files=['example_pg_with_deletions.sql'])
@pytest.mark.now('2020-06-23T09:57:01Z')
async def test_deletions(taxi_example_replica, pgsql, mocked_time):
    response = await taxi_example_replica.post(
        'v1/example-pg-with-deletions/retrieve',
        json={'id_in_set': ['example_1', 'example_2', 'example_3']},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'examples_pg': [
            {
                'data': {'increment': 1, 'some_field': 'some_field1'},
                'example_id': 'example_1',
                'updated_ts': '2020-06-22T09:56:00.000',
                'revision': '2020-06-22T09:56:00+0000_1',
            },
            {
                'data': {'increment': 2, 'some_field': 'some_field2'},
                'example_id': 'example_2',
                'updated_ts': '2020-06-23T09:56:00.000',
                'revision': '2020-06-23T09:56:00+0000_2',
            },
            {'example_id': 'example_3'},
        ],
    }

    response = await taxi_example_replica.post(
        'v1/example-pg-with-deletions/updates',
        json={},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'cache_lag' in response_json
    assert isinstance(response_json['cache_lag'], int)
    response_json.pop('cache_lag')
    assert response_json == {
        'last_modified': '2020-06-23T09:57:00Z',
        'last_revision': '2020-06-23T09:57:00+0000_3',
        'examples_pg': [
            {
                'data': {'increment': 1, 'some_field': 'some_field1'},
                'example_id': 'example_1',
                'updated_ts': '2020-06-22T09:56:00.000',
                'revision': '2020-06-22T09:56:00+0000_1',
            },
            {
                'data': {'increment': 2, 'some_field': 'some_field2'},
                'example_id': 'example_2',
                'updated_ts': '2020-06-23T09:56:00.000',
                'revision': '2020-06-23T09:56:00+0000_2',
            },
            {
                'data': {'increment': 3, 'some_field': 'some_field3'},
                'example_id': 'example_3',
                'updated_ts': '2020-06-23T09:57:00.000',
                'revision': '2020-06-23T09:57:00+0000_3',
                'is_deleted': True,
            },
        ],
    }

    cursor = pgsql['example_pg'].cursor()
    cursor.execute(
        'update example_pg.table_with_deletions set is_deleted=true, '
        'updated_ts=TIMESTAMPTZ('
        ' \'2020-06-23T09:58:00.00Z\' '
        '), increment=4 where id='
        '\'example_2\'',
    )

    mocked_time.set(datetime.datetime.fromisoformat('2020-06-23T09:59:00'))

    await taxi_example_replica.invalidate_caches(
        clean_update=False, cache_names=['example-pg-with-deletions-cache'],
    )

    response = await taxi_example_replica.post(
        'v1/example-pg-with-deletions/retrieve',
        json={'id_in_set': ['example_1', 'example_2', 'example_3']},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'examples_pg': [
            {
                'data': {'increment': 1, 'some_field': 'some_field1'},
                'example_id': 'example_1',
                'updated_ts': '2020-06-22T09:56:00.000',
                'revision': '2020-06-22T09:56:00+0000_1',
            },
            {'example_id': 'example_2'},
            {'example_id': 'example_3'},
        ],
    }

    response = await taxi_example_replica.post(
        'v1/example-pg-with-deletions/updates',
        json={'last_known_revision': '2020-06-23T09:57:00+0000_3'},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'cache_lag' in response_json
    assert isinstance(response_json['cache_lag'], int)
    response_json.pop('cache_lag')
    assert response_json == {
        'last_modified': '2020-06-23T09:58:00Z',
        'last_revision': '2020-06-23T09:58:00+0000_4',
        'examples_pg': [
            {
                'data': {'increment': 4, 'some_field': 'some_field2'},
                'example_id': 'example_2',
                'updated_ts': '2020-06-23T09:58:00.000',
                'revision': '2020-06-23T09:58:00+0000_4',
                'is_deleted': True,
            },
        ],
    }
    # after deleted_documents_ttl
    mocked_time.set(datetime.datetime.fromisoformat('2020-06-24T09:59:00'))

    await taxi_example_replica.invalidate_caches(
        clean_update=False, cache_names=['example-pg-with-deletions-cache'],
    )

    response = await taxi_example_replica.post(
        'v1/example-pg-with-deletions/retrieve',
        json={'id_in_set': ['example_1', 'example_2', 'example_3']},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'examples_pg': [
            {
                'data': {'increment': 1, 'some_field': 'some_field1'},
                'example_id': 'example_1',
                'updated_ts': '2020-06-22T09:56:00.000',
                'revision': '2020-06-22T09:56:00+0000_1',
            },
            {'example_id': 'example_2'},
            {'example_id': 'example_3'},
        ],
    }

    response = await taxi_example_replica.post(
        'v1/example-pg-with-deletions/updates',
        json={'last_known_revision': '2020-06-23T09:58:00+0000_4'},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'cache_lag' in response_json
    assert isinstance(response_json['cache_lag'], int)
    response_json.pop('cache_lag')
    assert response_json == {
        'last_modified': '2020-06-23T09:58:00Z',
        'last_revision': '2020-06-23T09:58:00+0000_4',
        'examples_pg': [],
    }

    # test whole cache content, deleted items should have been removed
    response = await taxi_example_replica.post(
        'v1/example-pg-with-deletions/updates',
        json={},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'cache_lag' in response_json
    assert isinstance(response_json['cache_lag'], int)
    response_json.pop('cache_lag')
    assert response_json == {
        'last_modified': '2020-06-22T09:56:00Z',
        'last_revision': '2020-06-22T09:56:00+0000_1',
        'examples_pg': [
            {
                'data': {'increment': 1, 'some_field': 'some_field1'},
                'example_id': 'example_1',
                'updated_ts': '2020-06-22T09:56:00.000',
                'revision': '2020-06-22T09:56:00+0000_1',
            },
        ],
    }


@pytest.mark.config(API_OVER_DATA_SERVICES=CONFIG)
async def test_deletions_in_client(taxi_example_replica):
    response = await taxi_example_replica.get(
        'v1/client-cache/test',
        params={'cache_name': 'example-pg-with-deletions-client-cache'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'cache_content': [
            {
                'example_id': 'example_1',
                'is_deleted': False,
                'revision': '2020-06-22T09:56:00+0000_1',
                'some_field': 'some_field1',
                'updated_ts': '2020-06-22T09:56:00+0000',
            },
            {
                'example_id': 'example_2',
                'is_deleted': False,
                'revision': '2020-06-23T09:56:00+0000_2',
                'some_field': 'some_field2',
                'updated_ts': '2020-06-23T09:56:00+0000',
            },
        ],
    }
