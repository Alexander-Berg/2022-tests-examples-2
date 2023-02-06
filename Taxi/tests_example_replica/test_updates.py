import pytest

pytest.CONFIG = {
    'example-replica': {
        'incremental_merge_time_limit_ms': 5000,
        'max_x_polling_delay_ms': 10,
        'min_x_polling_delay_ms': 0,
        'max_answer_data_size_bytes': 10000,
        'updates_max_documents_count': 10,
        'is_dumper_enabled': False,
        'deleted_documents_ttl_seconds': 4294967294,
        'lagging_cursor_delay_seconds': 120,
        'return_429_on_too_fresh_revision': True,
    },
}

NO_429_CONFIG = {
    'example-replica': {
        'incremental_merge_time_limit_ms': 5000,
        'max_x_polling_delay_ms': 10,
        'min_x_polling_delay_ms': 0,
        'max_answer_data_size_bytes': 10000,
        'updates_max_documents_count': 10,
        'is_dumper_enabled': False,
        'deleted_documents_ttl_seconds': 4294967294,
        'lagging_cursor_delay_seconds': 120,
        'return_429_on_too_fresh_revision': False,
    },
}


@pytest.mark.config(API_OVER_DATA_SERVICES=pytest.CONFIG)
async def test_examples_update(taxi_example_replica):
    response = await taxi_example_replica.post(
        'v1/examples/updates', params={'consumer': 'test'}, json={},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'cache_lag' in response_json
    assert isinstance(response_json['cache_lag'], int)
    response_json.pop('cache_lag')
    assert response_json == {
        'last_modified': '1970-01-15T06:56:08Z',
        'last_revision': '0_1234568_1',
        'examples': [
            {
                'data': {
                    'example_additional_field': 'example_1_additional_field',
                    'example_main_field': 'example_1_main_field',
                    'example_object_type_field': {'bool_field': True},
                },
                'example_id': 'example_1',
                'example_id_old': 'example_1',
                'revision': '0_1234567_1',
            },
            {
                'data': {
                    'example_main_field': 'example_2_main_field',
                    'example_object_type_field': {'bool_field': True},
                },
                'example_id': 'example_2',
                'example_id_old': 'example_2',
                'revision': '0_1234568_1',
            },
        ],
    }


@pytest.mark.config(API_OVER_DATA_SERVICES=pytest.CONFIG)
@pytest.mark.pgsql('example_pg', files=['example_pg.sql'])
async def test_examples_update_with_429(taxi_example_replica):
    response = await taxi_example_replica.post(
        'v1/examples/updates',
        params={'consumer': 'test'},
        json={'last_known_revision': '0_1234568_2'},
    )
    assert response.status_code == 429

    response = await taxi_example_replica.post(
        'v1/example-pg/updates',
        params={'consumer': 'test'},
        json={'last_known_revision': '2020-06-23T09:56:00+0000_3'},
    )
    assert response.status_code == 429


@pytest.mark.config(API_OVER_DATA_SERVICES=NO_429_CONFIG)
@pytest.mark.pgsql('example_pg', files=['example_pg.sql'])
async def test_examples_update_no_429(taxi_example_replica):
    response = await taxi_example_replica.post(
        'v1/examples/updates',
        params={'consumer': 'test'},
        json={'last_known_revision': '0_1234568_2'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'cache_lag' in response_json
    assert isinstance(response_json['cache_lag'], int)
    response_json.pop('cache_lag')
    assert response_json == {
        'last_modified': '1970-01-15T06:56:08Z',
        'last_revision': '0_1234568_1',
        'examples': [],
    }

    response = await taxi_example_replica.post(
        'v1/example-pg/updates',
        params={'consumer': 'test'},
        json={'last_known_revision': '2020-06-23T09:56:00+0000_3'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'cache_lag' in response_json
    assert isinstance(response_json['cache_lag'], int)
    response_json.pop('cache_lag')
    assert response_json == {
        'examples_pg': [],
        'last_modified': '2020-06-23T09:56:00Z',
        'last_revision': '2020-06-23T09:56:00+0000_2',
    }


@pytest.mark.config(API_OVER_DATA_SERVICES=pytest.CONFIG)
@pytest.mark.pgsql('example_pg', files=['example_pg.sql'])
async def test_examples_pg_update(taxi_example_replica):
    response = await taxi_example_replica.post(
        'v1/example-pg/updates', params={'consumer': 'test'}, json={},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'cache_lag' in response_json
    assert isinstance(response_json['cache_lag'], int)
    response_json.pop('cache_lag')
    assert response_json == {
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
            {
                'data': {
                    'increment': 2,
                    'example_bool_array_field': [True, False],
                    'some_field': 'some_field2',
                    'updated_ts': '2020-06-23T09:56:00.000',
                },
                'example_id': 'example_2',
                'revision': '2020-06-23T09:56:00+0000_2',
            },
        ],
        'last_modified': '2020-06-23T09:56:00Z',
        'last_revision': '2020-06-23T09:56:00+0000_2',
    }


@pytest.mark.config(API_OVER_DATA_SERVICES=pytest.CONFIG)
async def test_examples_update_with_revision(taxi_example_replica):
    response = await taxi_example_replica.post(
        'v1/examples/updates',
        params={'consumer': 'test'},
        json={'last_known_revision': '0_1234568_0'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'cache_lag' in response_json
    response_json.pop('cache_lag')
    assert response_json == {
        'last_modified': '1970-01-15T06:56:08Z',
        'last_revision': '0_1234568_1',
        'examples': [
            {
                'data': {
                    'example_main_field': 'example_2_main_field',
                    'example_object_type_field': {'bool_field': True},
                },
                'example_id': 'example_2',
                'example_id_old': 'example_2',
                'revision': '0_1234568_1',
            },
        ],
    }


@pytest.mark.config(API_OVER_DATA_SERVICES=pytest.CONFIG)
@pytest.mark.pgsql('example_pg', files=['example_pg.sql'])
async def test_examples_pg_update_with_revision(taxi_example_replica):
    response = await taxi_example_replica.post(
        'v1/example-pg/updates',
        params={'consumer': 'test'},
        json={'last_known_revision': '2020-06-22T09:56:00Z_1'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'cache_lag' in response_json
    assert isinstance(response_json['cache_lag'], int)
    response_json.pop('cache_lag')
    assert response_json == {
        'examples_pg': [
            {
                'data': {
                    'increment': 2,
                    'example_bool_array_field': [True, False],
                    'some_field': 'some_field2',
                    'updated_ts': '2020-06-23T09:56:00.000',
                },
                'example_id': 'example_2',
                'revision': '2020-06-23T09:56:00+0000_2',
            },
        ],
        'last_modified': '2020-06-23T09:56:00Z',
        'last_revision': '2020-06-23T09:56:00+0000_2',
    }


@pytest.mark.config(API_OVER_DATA_SERVICES=pytest.CONFIG)
async def test_examples_update_projection(taxi_example_replica):
    response = await taxi_example_replica.post(
        'v1/examples/updates',
        params={'consumer': 'test'},
        json={'projection': ['revision', 'data.example_additional_field']},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'cache_lag' in response_json
    response_json.pop('cache_lag')
    assert response_json == {
        'last_modified': '1970-01-15T06:56:08Z',
        'last_revision': '0_1234568_1',
        'examples': [
            {
                'data': {
                    'example_additional_field': 'example_1_additional_field',
                },
                'example_id': 'example_1',
                'example_id_old': 'example_1',
                'revision': '0_1234567_1',
            },
            {
                'data': {},
                'example_id': 'example_2',
                'example_id_old': 'example_2',
                'revision': '0_1234568_1',
            },
        ],
    }
