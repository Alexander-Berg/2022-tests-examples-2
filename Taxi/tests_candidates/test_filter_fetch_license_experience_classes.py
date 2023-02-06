import pytest

LICENSE_EXPERIENCE_SETTINGS = {
    'zones': {
        'moscow': {'econom': [{'category': 'B', 'experience': 2}]},
        'spb': {
            'econom': [
                {'category': 'B', 'experience': 2},
                {'category': 'C', 'experience': 1},
            ],
        },
    },
    'countries': {
        'rus': {
            'econom': [{'category': 'B', 'experience': 5}],
            'comfort': [{'category': 'B', 'experience': 2}],
        },
    },
    '__default__': {'business': [{'category': 'B', 'experience': 1}]},
}


@pytest.mark.config(LICENSE_EXPERIENCE_SETTINGS=LICENSE_EXPERIENCE_SETTINGS)
@pytest.mark.parametrize(
    'driver, zone_id, classes, count',
    [
        ('dbid0_uuid0', 'moscow', ['econom'], 0),
        ('dbid0_uuid0', 'spb', ['econom'], 1),
        ('dbid0_uuid0', 'moscow', ['minivan'], 1),
        ('dbid0_uuid0', 'moscow', ['comfortplus'], 0),
    ],
)
async def test_fetch_license_experience_classes(
        taxi_candidates, driver_positions, driver, zone_id, classes, count,
):
    await driver_positions([{'dbid_uuid': driver, 'position': [55, 35]}])

    request_body = {
        'geoindex': 'kdtree',
        'limit': 2,
        'filters': ['infra/class'],
        'point': [55, 35],
        'zone_id': zone_id,
        'allowed_classes': classes,
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json_resp = response.json()

    assert 'drivers' in json_resp
    assert len(json_resp['drivers']) == count


@pytest.mark.parametrize(
    'driver, zone_id, allow_empty, has_details',
    [
        ('dbid0_uuid0', 'moscow', True, True),
        ('dbid0_uuid2', 'moscow', True, False),
        ('dbid0_uuid2', 'moscow', False, True),
        ('dbid0_uuid2', 'moscow', None, True),
    ],
)
async def test_fetch_license_experience_satisfy(
        taxi_candidates,
        taxi_config,
        driver,
        zone_id,
        allow_empty,
        has_details,
):
    park_id, driver_id = driver.split('_')

    config = {}
    config.update(LICENSE_EXPERIENCE_SETTINGS)
    if allow_empty is not None:
        config['allow_empty'] = allow_empty
    taxi_config.set_values({'LICENSE_EXPERIENCE_SETTINGS': config})

    request_body = {
        'driver_ids': [{'dbid': park_id, 'uuid': driver_id}],
        'zone_id': zone_id,
    }
    response = await taxi_candidates.post('satisfy', json=request_body)
    assert response.status_code == 200
    json_resp = response.json()

    assert 'drivers' in json_resp
    assert len(json_resp['drivers']) == 1
    assert (
        'partners/fetch_license_experience_classes'
        in json_resp['drivers'][0]['details']
    ) == has_details
