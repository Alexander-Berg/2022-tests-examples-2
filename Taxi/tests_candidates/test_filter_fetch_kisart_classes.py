import pytest


@pytest.mark.config(
    DEPTRANS_DRIVER_STATUS_SUPPORTED_ZONES={'supported_zones': ['moscow']},
    DEPTRANS_DRIVER_STATUS_SUPPORTED_CATEGORIES={
        'supported_categories': ['econom'],
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='kis_art_classes_enabled',
    consumers=['candidates/filters'],
    default_value={},
)
@pytest.mark.parametrize(
    'status, zone_id, allowed_classes, expected_response',
    [
        pytest.param(
            'approved',
            'moscow',
            ['econom'],
            ['uuid0'],
            id='Allowed by profile',
        ),
        pytest.param(
            None, 'moscow', ['econom'], None, id='Rejected by profile',
        ),
        pytest.param(None, 'spb', ['econom'], ['uuid0'], id='Allowed by zone'),
        pytest.param(
            'temporary',
            'moscow',
            ['econom'],
            ['uuid0'],
            id='Allowed by temp profile',
        ),
        pytest.param(
            'temporary_requested',
            'moscow',
            ['econom'],
            ['uuid0'],
            id='Allowed by profile request',
        ),
        pytest.param(
            'missing', 'moscow', ['econom'], None, id='Rejected by missing',
        ),
        pytest.param(
            'temporary_outdated',
            'moscow',
            ['econom'],
            None,
            id='Rejected by outdated',
        ),
    ],
)
async def test_kisart_classes(
        taxi_candidates,
        driver_positions,
        deptrans_driver_status,
        status,
        zone_id,
        allowed_classes,
        expected_response,
):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )
    deptrans_driver_status.update_status(status)
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['infra/class', 'partners/fetch_kis_art_classes'],
        'point': [55, 35],
        'zone_id': zone_id,
        'allowed_classes': allowed_classes,
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    drivers = json['drivers']
    if expected_response:
        assert len(drivers) == len(expected_response)
        assert all([driver['uuid'] in expected_response for driver in drivers])
    else:
        assert not drivers


@pytest.mark.config(
    DEPTRANS_DRIVER_STATUS_SUPPORTED_ZONES={'supported_zones': ['moscow']},
    DEPTRANS_DRIVER_STATUS_SUPPORTED_CATEGORIES={
        'supported_categories': ['econom'],
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'false'}, 'enabled': True},
    name='kis_art_classes_enabled',
    consumers=['candidates/filters'],
    default_value={},
)
async def test_skip_on_exp(
        taxi_candidates, driver_positions, deptrans_driver_status,
):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )
    deptrans_driver_status.update_status(None)
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['infra/class', 'partners/fetch_kis_art_classes'],
        'point': [55, 35],
        'zone_id': 'moscow',
        'allowed_classes': ['econom'],
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    drivers = json['drivers']
    assert drivers == [
        {'dbid': 'dbid0', 'position': [55.0, 35.0], 'uuid': 'uuid0'},
    ]
