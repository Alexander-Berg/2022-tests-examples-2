# pylint: disable=C1801
import pytest


async def test_wrong_format_post(taxi_candidates):
    response = await taxi_candidates.post('deptrans', json={'format': 'wrong'})
    assert response.status_code == 400


async def test_response_format_post(taxi_candidates, driver_positions):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [37.619757, 55.753215]}],
    )

    response = await taxi_candidates.post('deptrans')
    assert response.status_code == 200
    drivers = response.json()['drivers']
    assert len(drivers) == 1
    car = drivers[0]
    assert car['id'] == '7b18551a390219976da357e490f638a7'
    assert 'car_number' not in car


async def test_extended_format_post(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {
                'dbid_uuid': 'dbid0_uuid0',
                'position': [37.619757, 55.753215],
                'direction': 128,
                'speed': 72,
            },
        ],
    )

    response = await taxi_candidates.post(
        'deptrans', json={'format': 'extended'},
    )
    assert response.status_code == 200
    drivers = response.json()['drivers']
    assert len(drivers) == 1
    car = drivers[0]
    assert car['id'] == '7b18551a390219976da357e490f638a7'
    assert car['car_number'] == 'Х492НК77'
    assert car['direction'] == 128
    assert car['speed'] == 72
    assert car['permit'] == 'permit_1'
    assert car['no_permission_classes'] == []


async def test_check_order_statuses(taxi_candidates, driver_positions):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [37.619757, 55.753215]}],
    )

    response = await taxi_candidates.post('deptrans')
    assert response.status_code == 200
    drivers = response.json()['drivers']
    drivers.sort(key=lambda x: x['id'])
    assert len(drivers) == 1
    car = drivers[0]
    assert car['id'] == '7b18551a390219976da357e490f638a7'
    assert car['status'] == {
        'status': 'online',
        'orders': [{'status': 'driving'}],
        'driver': 'verybusy',
        'taximeter': 'order_free',
    }


@pytest.mark.config(
    DEPTRANS_MKAD_AREA=[
        [37.309394, 55.914744],
        [37.884803, 55.911659],
        [37.942481, 55.520175],
        [37.242102, 55.499913],
        [37.309394, 55.914744],
    ],
)
async def test_outside_search_area_post(taxi_candidates, driver_positions):
    await driver_positions(
        [
            # with moscow permit, outside mo area
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.619757, 56.753215]},
            # with mo permit, outside mkad area, inside mo area
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.512910, 55.997496]},
        ],
    )
    response = await taxi_candidates.post('deptrans')
    assert response.status_code == 200
    assert not response.json()['drivers']


@pytest.mark.config(
    DEPTRANS_MKAD_AREA=[
        [37.309394, 55.914744],
        [37.884803, 55.911659],
        [37.942481, 55.520175],
        [37.242102, 55.499913],
        [37.309394, 55.914744],
    ],
)
@pytest.mark.parametrize('full_classification', [False, True])
async def test_inside_search_area_post(
        taxi_candidates, driver_positions, full_classification, taxi_config,
):
    await driver_positions(
        [
            # with moscow permit, inside mo area, outside mkad area
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.512910, 55.997496]},
            # with mo permit, inside mkad area, has 'uberblack'
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.630971, 55.743789]},
        ],
    )
    taxi_config.set_values(
        {'DEPTRANS_FULL_CLASSIFICATION': full_classification},
    )
    response = await taxi_candidates.post(
        'deptrans',
        json={
            'format': 'extended',
            'deptrans': {'classes_without_permission': ['uberblack']},
        },
    )
    assert response.status_code == 200
    drivers = response.json()['drivers']
    assert len(drivers) == 2
    # check classes wo permissions
    for driver in drivers:
        if driver['park_driver_id'] == 'dbid0_uuid1':
            assert driver['no_permission_classes'] == ['uberblack']


@pytest.mark.config(DEPTRANS_MKAD_AREA=[])
async def test_empty_search_area_post(taxi_candidates, driver_positions):
    await driver_positions(
        [
            # with moscow permit, outside mo area
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.619757, 56.753215]},
            # with mo permit, outside mkad area, inside mo area
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.512910, 55.997496]},
        ],
    )
    response = await taxi_candidates.post('deptrans')
    assert response.status_code == 200
    assert len(response.json()['drivers']) == 1


@pytest.mark.config(
    DEPTRANS_MKAD_AREA=[
        [37.309394, 55.914744],
        [37.884803, 55.911659],
        [37.942481, 55.520175],
        [37.242102, 55.499913],
        [37.309394, 55.914744],
    ],
)
async def test_business_permission_license_outside_mkad(
        taxi_candidates, driver_positions,
):
    await driver_positions(
        [
            # with mo permit, outside mkad area,
            # inside mo area, but business driver
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.512910, 55.997496]},
        ],
    )

    response = await taxi_candidates.post(
        'deptrans',
        json={
            'format': 'extended',
            'deptrans': {'classes_without_permission': ['vip']},
        },
    )
    assert response.status_code == 200
    # even if driver has business tariff, we do not send him to deptrans
    assert len(response.json()['drivers']) == 0


@pytest.mark.config(
    DEPTRANS_MKAD_AREA=[
        [37.309394, 55.914744],
        [37.884803, 55.911659],
        [37.942481, 55.520175],
        [37.242102, 55.499913],
        [37.309394, 55.914744],
    ],
    DEPTRANS_SKIP_CLASSES=['uberblack', 'uberx'],
)
async def test_skip_categories(taxi_candidates, driver_positions):
    await driver_positions(
        [
            # has 'uberx', 'econom', 'minivan'
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.512910, 55.997496]},
            # has 'uberblack' only, would be filtered
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.630971, 55.743789]},
        ],
    )
    response = await taxi_candidates.post('deptrans')
    assert response.status_code == 200
    assert len(response.json()['drivers']) == 1
