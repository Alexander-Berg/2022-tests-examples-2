import pytest


CONFIG = {
    'example-replica': {
        'incremental_merge_time_limit_ms': 5000,
        'max_x_polling_delay_ms': 10,
        'min_x_polling_delay_ms': 0,
        'max_answer_data_size_bytes': 250,
        'updates_max_documents_count': 10,
        'is_dumper_enabled': False,
        'deleted_documents_ttl_seconds': 4294967294,
        'lagging_cursor_delay_seconds': 120,
    },
}


@pytest.mark.config(API_OVER_DATA_SERVICES=CONFIG)
async def test_examples_retrieve(taxi_example_replica):
    response = await taxi_example_replica.post(
        'v1/examples/retrieve',
        json={'id_in_set': ['example_1', 'unknown_id']},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'examples': [
            {
                'revision': '0_1234567_1',
                'example_id': 'example_1',
                'example_id_old': 'example_1',
                'data': {
                    'example_main_field': 'example_1_main_field',
                    'example_additional_field': 'example_1_additional_field',
                    'example_object_type_field': {'bool_field': True},
                },
            },
            {'example_id': 'unknown_id', 'example_id_old': 'unknown_id'},
        ],
    }


@pytest.mark.config(API_OVER_DATA_SERVICES=CONFIG)
async def test_examples_retrieve_empty_array(taxi_example_replica):
    response = await taxi_example_replica.post(
        'v1/examples/retrieve',
        json={'id_in_set': []},
        params={'consumer': 'test'},
    )
    assert response.status_code == 400
    assert response.content == b''


@pytest.mark.config(API_OVER_DATA_SERVICES=CONFIG)
async def test_examples_retrieve_projection(taxi_example_replica):
    response = await taxi_example_replica.post(
        'v1/examples/retrieve',
        json={
            'id_in_set': ['example_1', 'unknown_id'],
            'projection': [
                'data.example_main_field',
                'data.example_object_type_field',
            ],
        },
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'examples': [
            {
                'example_id': 'example_1',
                'example_id_old': 'example_1',
                'data': {
                    'example_main_field': 'example_1_main_field',
                    'example_object_type_field': {'bool_field': True},
                },
            },
            {'example_id': 'unknown_id', 'example_id_old': 'unknown_id'},
        ],
    }


@pytest.mark.config(API_OVER_DATA_SERVICES=CONFIG)
async def test_examples_retrieve_projection_empty_data(taxi_example_replica):
    response = await taxi_example_replica.post(
        'v1/examples/retrieve',
        json={
            'id_in_set': ['example_1', 'example_2', 'unknown_id'],
            'projection': ['data.example_additional_field'],
        },
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'examples': [
            {
                'example_id': 'example_1',
                'example_id_old': 'example_1',
                'data': {
                    'example_additional_field': 'example_1_additional_field',
                },
            },
            {
                'example_id': 'example_2',
                'example_id_old': 'example_2',
                'data': {},
            },
            {'example_id': 'unknown_id', 'example_id_old': 'unknown_id'},
        ],
    }


@pytest.mark.config(API_OVER_DATA_SERVICES=CONFIG)
@pytest.mark.pgsql('example_pg', files=['example_pg.sql'])
async def test_examples_pg_retrieve(taxi_example_replica):
    response = await taxi_example_replica.post(
        '/v1/example-pg/retrieve',
        json={'id_in_set': ['example_1']},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'examples_pg': [
            {
                'data': {
                    'example_bool_array_field': [True, False],
                    'increment': 1,
                    'some_field': 'some_field1',
                    'updated_ts': '2020-06-22T09:56:00.000',
                },
                'example_id': 'example_1',
                'revision': '2020-06-22T09:56:00+0000_1',
            },
        ],
    }


@pytest.mark.config(API_OVER_DATA_SERVICES=CONFIG)
@pytest.mark.pgsql('example_pg', files=['example_pg.sql'])
async def test_examples_pg_retrieve_projection(taxi_example_replica):
    response = await taxi_example_replica.post(
        '/v1/example-pg/retrieve',
        json={'id_in_set': ['example_2'], 'projection': ['data.some_field']},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'examples_pg': [
            {'data': {'some_field': 'some_field2'}, 'example_id': 'example_2'},
        ],
    }
