import pytest


pytest.CONFIG = {
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


@pytest.mark.config(API_OVER_DATA_SERVICES=pytest.CONFIG)
async def test_example_retrieve_by_main(taxi_example_replica):
    response = await taxi_example_replica.post(
        'v1/examples/retrieve_by_main',
        json={'main_field_in_set': ['example_1_main_field', 'unknown']},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'examples_by_main': [
            {
                'main_field': 'example_1_main_field',
                'examples': [
                    {
                        'example_id': 'example_1',
                        'example_id_old': 'example_1',
                        'revision': '0_1234567_1',
                        'data': {
                            'example_additional_field': (
                                'example_1_additional_field'
                            ),
                            'example_main_field': 'example_1_main_field',
                            'example_object_type_field': {'bool_field': True},
                        },
                    },
                ],
            },
            {'examples': [], 'main_field': 'unknown'},
        ],
    }


@pytest.mark.config(API_OVER_DATA_SERVICES=pytest.CONFIG)
@pytest.mark.pgsql('example_pg', files=['example_pg.sql'])
async def test_example_pg_retrieve_by_some_field(taxi_example_replica):
    response = await taxi_example_replica.post(
        '/v1/example-pg/retrieve-by-some-field',
        json={'some_field_in_set': ['some_field1', 'unknown']},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'examples_pg_by_some_field': [
            {
                'examples_pg': [
                    {
                        'data': {
                            'increment': 1,
                            'example_bool_array_field': [True, False],
                            'some_field': 'some_field1',
                            'updated_ts': '2020-06-22T09:56:00.000',
                        },
                        'example_id': 'example_1',
                        'revision': '2020-06-22T09:56:00+0000_1',
                    },
                ],
                'some_field': 'some_field1',
            },
            {'examples_pg': [], 'some_field': 'unknown'},
        ],
    }


@pytest.mark.config(API_OVER_DATA_SERVICES=pytest.CONFIG)
async def test_example_only_index_retrieve_by_main(taxi_example_replica):
    response = await taxi_example_replica.post(
        'v1/examples_only_index/retrieve_by_main',
        json={'main_field_in_set': ['example_1_main_field', 'unknown']},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'examples_by_main': [
            {
                'main_field': 'example_1_main_field',
                'examples': [
                    {
                        'example_id': 'example_1',
                        'revision': '0_1234567_1',
                        'data': {'example_main_field': 'example_1_main_field'},
                    },
                ],
            },
            {'examples': [], 'main_field': 'unknown'},
        ],
    }


@pytest.mark.config(API_OVER_DATA_SERVICES=pytest.CONFIG)
async def test_example_retrieve_by_main_empty_array(taxi_example_replica):
    response = await taxi_example_replica.post(
        'v1/examples/retrieve_by_main',
        json={'main_field_in_set': []},
        params={'consumer': 'test'},
    )
    assert response.status_code == 400
    assert response.content == b''


@pytest.mark.config(API_OVER_DATA_SERVICES=pytest.CONFIG)
async def test_example_retrieve_by_main_projection(taxi_example_replica):
    response = await taxi_example_replica.post(
        'v1/examples/retrieve_by_main',
        json={
            'main_field_in_set': ['example_2_main_field', 'unknown'],
            'projection': ['data.example_additional_field'],
        },
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'examples_by_main': [
            {
                'main_field': 'example_2_main_field',
                'examples': [
                    {
                        'example_id': 'example_2',
                        'example_id_old': 'example_2',
                        'data': {},
                    },
                ],
            },
            {'main_field': 'unknown', 'examples': []},
        ],
    }
