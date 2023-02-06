import pytest

from taxi.robowarehouse.lib.concepts import warehouses
from taxi.robowarehouse.lib.concepts import locations
from taxi.robowarehouse.lib.concepts import package_places
from taxi.robowarehouse.lib.concepts import warehouse_zones


def _get_warehouse_response(warehouse: warehouses.Warehouse, **kwargs) -> dict:
    response = {
        'warehouse_id': warehouse.warehouse_id,
        'position': warehouse.position,
        'address': warehouse.address,
        'directions': warehouse.directions,
        'measurements_limits': warehouse.measurements_limits,
        'email': warehouse.email,
        'phone_number': warehouse.phone_number,
        'created_at': warehouse.created_at.isoformat(),
        'updated_at': warehouse.updated_at.isoformat(),
    }
    for key, value in kwargs.items():
        response[key] = value
    return response


@pytest.mark.asyncio
async def test_list_warehouses_empty(client):
    response = await client.post('/dealer/v1/warehouses/list/')

    assert response.status_code == 200
    assert response.json() == {'warehouses': []}


@pytest.mark.asyncio
async def test_list_warehouses(client):
    warehouse = await warehouses.factories.create()

    response = await client.post('/dealer/v1/warehouses/list/')

    expected = _get_warehouse_response(warehouse, detailed_zones=[])

    assert response.status_code == 200
    assert response.json() == {'warehouses': [expected]}


@pytest.mark.asyncio
async def test_list_warehouses_with_detailed_zones(client):
    warehouse = await warehouses.factories.create()
    warehouse_zone = await warehouse_zones.factories.create(warehouse_id=warehouse.warehouse_id)

    response = await client.post('/dealer/v1/warehouses/list/')

    expected = _get_warehouse_response(warehouse,
                                       detailed_zones=[{
                                           'zone_type': warehouse_zone.type,
                                           'status': warehouse_zone.status,
                                           'timetable': warehouse_zone.timetable,
                                       }])

    assert response.status_code == 200
    assert response.json() == {'warehouses': [expected]}


@pytest.mark.asyncio
async def test_availability_without_warehouses(client):
    data = {
        'position': {
            'lat': 0,
            'lon': 0
        },
        'delivery_date': '2021-10-30T13:21:45.656Z',
        'items': [
            {
                'measurements': {
                    'width': 10,
                    'height': 10,
                    'length': 10,
                    'weight': 10
                }
            }
        ]
    }

    response = await client.post('/dealer/v1/warehouses/availability/', json=data)

    assert response.status_code == 200
    assert response.json() == {'delivery_options': []}


@pytest.mark.parametrize('position, measurement_count, numbers_of_warehouses', [
    (locations.LocationRequest(lon=0, lat=0), 3, []),
    (locations.LocationRequest(lon=0, lat=0), 1, [0, 1]),
    (locations.LocationRequest(lon=0, lat=0), 2, []),
    (locations.LocationRequest(lon=25, lat=25), 1, [2]),
    (locations.LocationRequest(lon=25, lat=25), 2, []),
    (locations.LocationRequest(lon=125, lat=125), 1, []),
])
@pytest.mark.asyncio
async def test_availability_with_warehouses(client, position, measurement_count, numbers_of_warehouses):
    warehouses_list: list = [await warehouses.factories.create(phone_number=i) for i in range(3)]
    warehouses_list.sort(key=lambda el: el.warehouse_id)

    # make different count of place for warehouses
    for _ in range(3):
        await package_places.factories.create(warehouse_id=warehouses_list[0].warehouse_id)

    for _ in range(2):
        await package_places.factories.create(warehouse_id=warehouses_list[1].warehouse_id)
    await package_places.factories.create(
        warehouse_id=warehouses_list[1].warehouse_id,
        state=package_places.types.PackagePlaceState.FILLED
    )

    await package_places.factories.create(warehouse_id=warehouses_list[2].warehouse_id)

    polygon3 = [
        locations.LocationRequest(lon=20, lat=20),
        locations.LocationRequest(lon=20, lat=30),
        locations.LocationRequest(lon=30, lat=30),
        locations.LocationRequest(lon=30, lat=20),
    ]

    warehouse_zones_list = [
        await warehouse_zones.factories.create(warehouse_id=warehouses_list[0].warehouse_id),
        await warehouse_zones.factories.create(warehouse_id=warehouses_list[1].warehouse_id),
        await warehouse_zones.factories.create(warehouse_id=warehouses_list[2].warehouse_id, polygon=polygon3)
    ]

    measurements_list = [
        {
            'measurements': {
                'width': 10,
                'height': 10,
                'length': 10,
                'weight': 10
            }
        }
        for _ in range(measurement_count)
    ]

    data = {
        'position': {
            'lat': position.lon,
            'lon': position.lat
        },
        'delivery_date': '2021-10-30T13:21:45.656Z',
        'items': measurements_list
    }

    response = await client.post('/dealer/v1/warehouses/availability/', json=data)
    assert response.status_code == 200

    response = response.json()
    assert len(response['delivery_options']) == len(numbers_of_warehouses)

    expected_zones = (warehouse_zones_list[num] for num in numbers_of_warehouses)
    expected_warehouses = (warehouses_list[num] for num in numbers_of_warehouses)

    for option, warehouse, zone in zip(response['delivery_options'], expected_warehouses, expected_zones):
        assert option == {
            'warehouse_id': warehouse.warehouse_id,
            'delivery_type': zone.type,
            'working_hours': zone.timetable,
            'phone_number': warehouse.phone_number
        }
