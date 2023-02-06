import pytest

DS_CACHE_IN_CANDIDATES_ENABLED = {
    'cache_enabled': True,
    'full_update_request_parts_count': 1,
    'last_revision_overlap_sec': 1,
}

DS_CACHE_IN_CANDIDATES_DISABLED = {
    'cache_enabled': False,
    'full_update_request_parts_count': 1,
    'last_revision_overlap_sec': 1,
}


@pytest.mark.parametrize(
    'expected_uuids',
    [
        pytest.param(
            ['uuid2'],
            marks=[
                pytest.mark.config(
                    DRIVER_STATUS_BLOCKS_CACHE_IN_CANDIDATES=(
                        DS_CACHE_IN_CANDIDATES_ENABLED
                    ),
                    DRIVER_STATUS_NETWORK_COMPRESSION={'compression': 'lz4'},
                ),
            ],
            id='DS driver blocks cache enabled',
        ),
        pytest.param(
            ['uuid0', 'uuid1', 'uuid2'],
            marks=[
                pytest.mark.config(
                    DRIVER_STATUS_BLOCKS_CACHE_IN_CANDIDATES=(
                        DS_CACHE_IN_CANDIDATES_DISABLED
                    ),
                ),
            ],
            id='DS driver blocks cache disabled by config',
        ),
    ],
)
async def test_filter_driver_blocks(
        taxi_candidates, driver_positions, expected_uuids,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [55, 35]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['infra/driver_blocks'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == len(expected_uuids)
    assert set(map(lambda driver: driver['uuid'], drivers)) == set(
        expected_uuids,
    )
