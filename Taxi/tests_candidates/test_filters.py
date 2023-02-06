import pytest


@pytest.mark.config(EXTRA_EXAMS_BY_ZONE={})
async def test_pass_all(
        taxi_candidates, driver_positions, driver_status_request,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': [
            'infra/car_number',
            'infra/country',
            'infra/deactivated_park_v2',
            'infra/driver_id',
            'infra/frozen',
            'infra/park_id',
            'infra/requirements',
            'infra/status',
            'infra/status_active',
            'infra/search_area',
            'efficiency/driver_metrics',
            'efficiency/driver_weariness',
            'efficiency/experiments_intersection',
            'efficiency/explicit_antisurge',
        ],
        'point': [55, 35],
        'excluded_car_numbers': ['A000AA00'],
        'excluded_ids': ['clidX_uuidX'],
        'excluded_park_ids': ['clidX'],
        'requirements': {'conditioner': True},
        'allowed_classes': ['econom', 'vip'],
        'zone_id': 'moscow',
        'on_order': False,
        'payment_method': 'cash',
        'check_contracts': True,
        'city_id': 'Москва',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    assert len(response.json()['drivers']) == 2


async def test_frozen(
        taxi_candidates, driver_positions, mockserver, load_binary,
):
    @mockserver.json_handler('/driver-freeze/frozen')
    def _mock_local_frozen(request):
        return mockserver.make_response(
            response=load_binary('frozen_response.fb.gz'),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [55, 35]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['infra/fetch_unique_driver', 'infra/frozen'],
        'point': [55, 35],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    assert len(response.json()['drivers']) == 1


@pytest.mark.config(
    TARIFF_CLASSES_MAPPING={'uberx': {'classes': ['econom']}},
    CHILDSEAT_MAPPING=[{'groups': [1, 2, 3], 'categories': [1, 3, 7]}],
)
async def test_classifier(taxi_candidates, driver_positions):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )
    request_body = {
        'limit': 3,
        'point': [55, 35],
        'zone_id': 'moscow',
        'allowed_classes': ['econom', 'comfort', 'minivan', 'vip', 'uberx'],
    }
    response = await taxi_candidates.post('searchable', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 1
    assert {'econom', 'minivan', 'uberx'} == set(drivers[0]['classes'])


@pytest.mark.config(
    TARIFF_CLASSES_MAPPING={
        'uberblack': {'classes': ['vip']},
        'uberkids': {'classes': ['child_tariff']},
        'uberselect': {'classes': ['business', 'business2', 'comfortplus']},
        'uberx': {'classes': ['econom']},
    },
    CHILDSEAT_MAPPING=[{'groups': [1, 2, 3], 'categories': [1, 3, 7]}],
)
async def test_classifier_allow_all(taxi_candidates, driver_positions):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]}],
    )
    request_body = {'limit': 3, 'point': [55, 35], 'zone_id': 'moscow'}
    response = await taxi_candidates.post('searchable', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 1
    assert set(drivers[0]['classes']) == {
        'econom',
        'minivan',
        'uberx',
        'uberkids',
    }


async def test_driver_id(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [55, 35]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['infra/driver_id'],
        'point': [55, 35],
        'excluded_ids': ['clid0_uuid0', 'clid0_uuid1'],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 1
    assert drivers[0]['uuid'] == 'uuid2'


async def test_park_id(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [55, 35]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['infra/park_id'],
        'point': [55, 35],
        'excluded_park_ids': ['clid0'],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    assert not response.json()['drivers']


async def test_any_of_dummy(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [55, 35]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [55, 35]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['test/any_of_dummy'],
        'point': [55, 35],
        'sleep_ms': 30,
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    assert len(response.json()['drivers']) == 2
