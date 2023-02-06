import pytest


@pytest.mark.parametrize(
    'version,application,expected_candidates',
    [('8.6.0', 'taximeter', ['uuid2']), ('1.0.0', 'taximeter-ios', ['uuid1'])],
)
async def test_explicit_antisurge(
        taxi_candidates,
        experiments3,
        driver_positions,
        version,
        application,
        expected_candidates,
):
    experiments3.add_experiment(
        match={
            'predicate': {'type': 'true'},
            'enabled': True,
            'applications': [
                {'name': application, 'version_range': {'from': version}},
            ],
        },
        name='explicit_antisurge',
        consumers=['candidates/filters'],
        clauses=[],
        default_value={},
    )

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
        'filters': ['efficiency/explicit_antisurge'],
        'point': [55, 35],
        'zone_id': 'moscow',
        'order': {'calc': {'alternative_type': 'explicit_antisurge'}},
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']

    assert len(drivers) == len(expected_candidates)
    for driver in drivers:
        assert driver['uuid'] in expected_candidates
