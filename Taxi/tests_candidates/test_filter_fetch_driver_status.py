import pytest

DS_CACHE_IN_CANDIDATES_ENABLED = {
    '__default__': {
        'cache_enabled': True,
        'full_update_request_parts_count': 1,
        'last_revision_overlap_sec': 1,
    },
}

DS_CACHE_IN_CANDIDATES_DISABLED = {
    '__default__': {
        'cache_enabled': False,
        'full_update_request_parts_count': 1,
        'last_revision_overlap_sec': 1,
    },
}


@pytest.mark.parametrize(
    'expected_statuses',
    [
        pytest.param(
            {
                'uuid0': 'online',
                'uuid1': 'online',
                'uuid2': 'online',
                'uuid99': 'offline',
            },
            marks=[
                pytest.mark.config(
                    DRIVER_STATUSES_CACHE_SETTINGS=(
                        DS_CACHE_IN_CANDIDATES_ENABLED
                    ),
                ),
            ],
            id='DS driver statuses cache enabled',
        ),
        pytest.param(
            {
                'uuid0': 'offline',
                'uuid1': 'offline',
                'uuid2': 'offline',
                'uuid99': 'offline',
            },
            marks=[
                pytest.mark.config(
                    DRIVER_STATUSES_CACHE_SETTINGS=(
                        DS_CACHE_IN_CANDIDATES_DISABLED
                    ),
                ),
            ],
            id='DS driver statuses cache disabled by config',
        ),
    ],
)
async def test_filter_fetch_driver_status(
        taxi_candidates, driver_positions, expected_statuses,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [55, 35]},
        ],
    )
    request_body = {
        'driver_ids': [
            {'dbid': 'dbid0', 'uuid': 'uuid0'},
            {'dbid': 'dbid0', 'uuid': 'uuid1'},
            {'dbid': 'dbid0', 'uuid': 'uuid2'},
            {'dbid': 'dbid0', 'uuid': 'uuid99'},
        ],
        'data_keys': ['driver_status'],
    }
    response = await taxi_candidates.post('profiles', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == len(expected_statuses)
    for driver in drivers:
        assert (
            driver['driver_status']['status']
            == expected_statuses[driver['uuid']]
        )
