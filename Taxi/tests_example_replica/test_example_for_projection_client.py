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
async def test_example_for_projection_client(mockserver, taxi_example_replica):
    # await taxi_example_replica.tests_control()
    response = await taxi_example_replica.get(
        '/v1/client_cache_projection/test',
    )
    assert response.status_code == 200
