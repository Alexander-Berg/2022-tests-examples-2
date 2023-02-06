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
async def test_example_retrieve_by_custom(taxi_example_replica):
    response = await taxi_example_replica.post(
        'v1/examples/retrieve_by_custom',
        json={'upper_main_in_set': ['EXAMPLE_1_MAIN_FIELD', 'unknown']},
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'examples_by_main': [
            {
                'upper_main': 'EXAMPLE_1_MAIN_FIELD',
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
            {'upper_main': 'unknown', 'examples': []},
        ],
    }
