import pytest

CONFIG = {
    'blocklist': {
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


async def get_next_blocks(taxi_blocklist, last_revision: str):
    return await taxi_blocklist.post(
        '/v1/blocks/updates',
        json={'last_known_revision': last_revision},
        params={'consumer': 'test'},
    )


@pytest.mark.config(API_OVER_DATA_SERVICES=CONFIG)
async def test_all_blocks(taxi_blocklist, load_json):
    response = await get_next_blocks(
        taxi_blocklist, '2021-01-01T00:00:00+0000_0',
    )

    assert response.status_code == 200
    result = response.json()

    assert len(result['blocks']) == 5

    etalon_response = load_json('full_response.json')
    assert result['blocks'] == etalon_response['blocks']
    assert result['last_modified'] == etalon_response['last_modified']
    assert result['last_revision'] == etalon_response['last_revision']
    assert result['cache_lag'] is not None


@pytest.mark.config(API_OVER_DATA_SERVICES=CONFIG)
async def test_last_blocks(taxi_blocklist, load_json):
    response = await get_next_blocks(
        taxi_blocklist, '2021-03-01T00:00:00+0000_3',
    )
    assert response.status_code == 200
    result = response.json()
    blocks = result['blocks']
    assert len(blocks) == 2

    assert {block['block_id'] for block in blocks} == {
        '50000000-0000-0000-0000-000000000000',
        '40000000-0000-0000-0000-000000000000',
    }

    response = await get_next_blocks(
        taxi_blocklist, '2021-04-01T00:00:00+0000_4',
    )

    assert response.status_code == 200
    result = response.json()
    blocks = result['blocks']
    assert len(blocks) == 1

    assert blocks[0]['block_id'] == '50000000-0000-0000-0000-000000000000'
    last_revision = result['last_revision']
    response = await get_next_blocks(taxi_blocklist, last_revision)
    assert response.status_code == 200
    result = response.json()
    assert result['blocks'] == []
