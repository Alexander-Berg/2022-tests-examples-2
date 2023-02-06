import pytest


async def _test_base(
        taxi_candidates,
        driver_positions,
        mockserver,
        mock_results,
        expected_response,
):
    @mockserver.json_handler('/antifraud/v1/client/driver/frauders')
    def _mock_antifraud(_):
        _udi_prefix = '56f968f07c0aa65c44998e4'
        return {
            'drivers': [
                {
                    'unique_driver_id': _udi_prefix + driver[0],
                    'frauder': True,
                    'reason': driver[1],
                }
                for driver in mock_results
            ],
        }

    def _make_response(*args):
        _positions = [55.0, 35.0]
        _drivers_by_udi = {
            'b': {'dbid': 'dbid0', 'uuid': 'uuid0'},
            'e': {'dbid': 'dbid0', 'uuid': 'uuid1'},
            'f': {'dbid': 'dbid1', 'uuid': 'uuid3'},
        }
        return [
            {**_drivers_by_udi[arg], 'position': _positions}
            for arg in args
            if arg in _drivers_by_udi
        ]

    def _sort(drivers):
        return sorted(drivers, key=lambda driver: driver['uuid'])

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
            {'dbid_uuid': 'dbid1_uuid3', 'position': [55, 35]},
        ],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['infra/afs_bad_signature'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)

    assert response.status_code == 200
    json = response.json()

    assert _sort(json['drivers']) == _sort(_make_response(*expected_response))


def _make_params(with_fraud=True):
    _params = [
        ([], ['b', 'e', 'f']),
        ([['b', 'fake_gps'], ['e', '']], ['e', 'f']),
        ([['b', 'emulator'], ['e', 'hook'], ['f', 'fake_gps']], []),
    ]
    return [
        (param[0], param[1] if with_fraud else ['b', 'e', 'f'])
        for param in _params
    ]


@pytest.mark.parametrize('mock_results,expected_response', _make_params())
@pytest.mark.config(
    AFS_CANDIDATES_DRIVER_CLIENT_CACHE_ENABLED=True,
    AFS_CANDIDATES_BAD_SIGNATURE_BLOCK_ENABLED=True,
    EXTRA_EXAMS_BY_ZONE={},
    CLASSES_WITHOUT_PERMIT_BY_ZONES_FILTER_ENABLED=True,
)
async def test_filter_afs_bad_signature_base(
        taxi_candidates,
        driver_positions,
        mockserver,
        mock_results,
        expected_response,
):
    await _test_base(
        taxi_candidates,
        driver_positions,
        mockserver,
        mock_results,
        expected_response,
    )


@pytest.mark.parametrize('mock_results,expected_response', _make_params(False))
@pytest.mark.config(
    AFS_CANDIDATES_DRIVER_CLIENT_CACHE_ENABLED=False,
    AFS_CANDIDATES_BAD_SIGNATURE_BLOCK_ENABLED=True,
)
async def test_filter_afs_bad_signature_with_out_cache(
        taxi_candidates,
        driver_positions,
        mockserver,
        mock_results,
        expected_response,
):
    await _test_base(
        taxi_candidates,
        driver_positions,
        mockserver,
        mock_results,
        expected_response,
    )


@pytest.mark.parametrize('mock_results,expected_response', _make_params(False))
@pytest.mark.config(
    AFS_CANDIDATES_DRIVER_CLIENT_CACHE_ENABLED=True,
    AFS_CANDIDATES_BAD_SIGNATURE_BLOCK_ENABLED=False,
)
async def test_filter_afs_bad_signature_with_out_block(
        taxi_candidates,
        driver_positions,
        mockserver,
        mock_results,
        expected_response,
):
    await _test_base(
        taxi_candidates,
        driver_positions,
        mockserver,
        mock_results,
        expected_response,
    )
