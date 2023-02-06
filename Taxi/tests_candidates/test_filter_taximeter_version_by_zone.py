import pytest


@pytest.mark.experiments3(filename='version_settings_by_zone_exp.json')
@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_ZONE={
        'moscow': {'taximeter': {'min': '10.00'}},
    },
)
async def test_partners_taximeter_version_zone_settings(
        taxi_candidates, driver_positions,
):
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
        'filters': ['partners/taximeter_version_by_zone'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()

    assert len(json['drivers']) == 1
    assert json['drivers'][0]['uuid'] == 'uuid3'
