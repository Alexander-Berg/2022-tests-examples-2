import pytest


@pytest.mark.parametrize(
    'classses_map, count',
    [
        ({}, 2),
        ({'econom': {'taximeter': {'android': '10.0'}}}, 0),
        ({'econom': {'taximeter': {'android': '8.6'}}}, 1),
        ({'econom': {'taximeter': {'android': '8.5'}}}, 1),
        ({'econom': {'taximeter': {'android': '8.1'}}}, 2),
        ({'econom': {'taximeter': {'android': '8.0'}}}, 2),
    ],
)
async def test_fetch_version_classes(
        taxi_candidates, driver_positions, taxi_config, classses_map, count,
):
    taxi_config.set_values(
        dict(TAXIMETER_VERSION_FEATURES={'classes': classses_map}),
    )
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid1_uuid3', 'position': [55, 35]},
        ],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 2,
        'filters': ['infra/class'],
        'point': [55, 35],
        'zone_id': 'moscow',
        'allowed_classes': ['econom'],
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json_resp = response.json()

    assert 'drivers' in json_resp
    assert len(json_resp['drivers']) == count
