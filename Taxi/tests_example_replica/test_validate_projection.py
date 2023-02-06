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
    },
}


@pytest.mark.parametrize(
    ['path', 'body'],
    [
        ('v1/examples/updates', {}),
        ('v1/examples/retrieve', {'id_in_set': ['example_1', 'unknown_id']}),
        (
            'v1/examples/proxy_retrieve',
            {'id_in_set': ['example_1', 'unknown_id']},
        ),
        (
            'v1/examples/retrieve_by_main',
            {'main_field_in_set': ['example_1_main_field', 'unknown']},
        ),
    ],
)
@pytest.mark.config(API_OVER_DATA_SERVICES=pytest.CONFIG)
async def test_validate_projection(taxi_example_replica, path, body):
    body['projection'] = [
        'data.example_additional_field',
        'data.example_additional_field.incorrect_field',
    ]
    response = await taxi_example_replica.post(
        path, json=body, params={'consumer': 'test'},
    )
    assert response.status_code == 400
    assert response.content == b''

    body['projection'] = [
        'data.example_additional_field',
        'completely_incorrect_field',
    ]
    response = await taxi_example_replica.post(
        path, json=body, params={'consumer': 'test'},
    )
    assert response.status_code == 400
    assert response.content == b''

    body['projection'] = ['completely_incorrect_field']
    response = await taxi_example_replica.post(
        path, json=body, params={'consumer': 'test'},
    )
    assert response.status_code == 400
    assert response.content == b''
