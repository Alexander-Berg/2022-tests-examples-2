import freezegun
import pytest
from unittest import mock

from taxi.robowarehouse.lib.concepts import warehouses
from taxi.robowarehouse.lib.concepts import warehouse_zones
from taxi.robowarehouse.lib.concepts import package_places
from taxi.robowarehouse.lib.concepts import devices
from taxi.robowarehouse.lib.misc import datetime_utils
from taxi.robowarehouse.lib.test_utils.helpers import convert_to_frontend_response
from taxi.robowarehouse.lib.misc.helpers import generate_id
from taxi.robowarehouse.lib.misc.helpers import base64_encode


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_warehouse_not_found(client):
    warehouse_id = generate_id()

    response = await client.get(f'/admin/v1/warehouses/{warehouse_id}/')

    expected = {
        'code': 'WAREHOUSE_NOT_FOUND_ERROR',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00', 'warehouse_id': warehouse_id},
        'message': 'Warehouse not found',
    }

    assert response.status_code == 404
    assert response.json() == expected


@pytest.mark.asyncio
async def test_get_warehouse(client):
    warehouse = await warehouses.factories.create()
    zone = await warehouse_zones.factories.create(warehouse_id=warehouse.warehouse_id)
    place = await package_places.factories.create(warehouse_id=warehouse.warehouse_id)
    device = await devices.factories.create(warehouse_id=warehouse.warehouse_id)

    response = await client.get(f'/admin/v1/warehouses/{warehouse.warehouse_id}/')

    expected = {
        'warehouse': warehouse.to_dict(),
        'package_places': [place.to_dict()],
        'warehouse_zones': [zone.to_dict()],
        'device': device.to_dict()
    }

    expected = convert_to_frontend_response(expected)

    assert response.status_code == 200
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_warehouse_list_wrong_cursor_params(client):
    warehouse = await warehouses.factories.create()

    token = base64_encode(warehouse.warehouse_id)
    response = await client.get(f'/admin/v1/warehouses/?newer_than={token}&older_than={token}')

    expected = {
        'code': 'WRONG_CURSOR_PARAM',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00', 'newer_than': token, 'older_than': token},
        'message': 'Wrong cursor params was given.',
    }

    assert response.status_code == 400
    assert response.json() == expected


@pytest.mark.asyncio
async def test_get_warehouse_list_with_address(client):
    warehouse = await warehouses.factories.create(address='addr1')
    await warehouses.factories.create(address='other')

    response = await client.get('/admin/v1/warehouses/?address=addr1')

    expected_results = [{**warehouse.to_dict(), 'warehouse_zones': []}]

    expected_results = convert_to_frontend_response(expected_results)

    assert response.status_code == 200
    assert response.json() == {'warehouses': expected_results}


@pytest.mark.asyncio
async def test_get_warehouse_list(client):
    warehouses_list = sorted([await warehouses.factories.create() for _ in range(10)], key=lambda el: el.warehouse_id)

    newer_than = base64_encode(warehouses_list[1].warehouse_id)
    next = base64_encode(warehouses_list[3].warehouse_id)
    prev = base64_encode(warehouses_list[2].warehouse_id)

    response = await client.get(f'/admin/v1/warehouses/?newer_than={newer_than}&limit=2')

    expected_results = [{**warehouse.to_dict(), 'warehouse_zones': []} for warehouse in warehouses_list]
    expected_results = convert_to_frontend_response(expected_results[2:4])

    assert response.status_code == 200
    assert response.json() == {
        'newerThan': next,
        'olderThan': prev,
        'warehouses': expected_results
    }


@pytest.mark.asyncio
async def test_get_warehouse_list_with_zones(client):
    warehouse = await warehouses.factories.create()

    zone1 = await warehouse_zones.factories.create(warehouse_id=warehouse.warehouse_id)
    zone2 = await warehouse_zones.factories.create(warehouse_id=warehouse.warehouse_id,
                                                   type=warehouse_zones.types.DeliveryType.YANDEX_TAXI)

    response = await client.get('/admin/v1/warehouses/')

    expected_result = [{
        **warehouse.to_dict(),
        'warehouse_zones': [{**zone1.to_dict()}, {**zone2.to_dict()}]
    }]
    expected_result = convert_to_frontend_response(expected_result)

    assert response.status_code == 200
    assert response.json() == {'warehouses': expected_result}


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_update_warehouse_not_found(client):
    warehouse_id = generate_id()

    response = await client.put(f'/admin/v1/warehouses/{warehouse_id}/', json={'phone_number': '1234'})

    expected = {
        'code': 'WAREHOUSE_NOT_FOUND_ERROR',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00', 'warehouse_id': warehouse_id},
        'message': 'Warehouse not found',
    }

    assert response.status_code == 404
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_update_warehouse(client):
    warehouse = await warehouses.factories.create()
    now = datetime_utils.get_now()

    body = warehouses.UpdateWarehouseRequest(
        address='new address',
        phone_number='1234',
        directions='directions1',
        email='test@test.ru',
        measurements_limits={'width': 1, 'height': 2, 'length': 3, 'weight': 4},
        position={'lat': 2.0, 'lon': 3.0}
    )

    response = await client.put(f'/admin/v1/warehouses/{warehouse.warehouse_id}/', json=body.dict())

    expected = {
        'warehouse_id': warehouse.warehouse_id,
        'created_at': warehouse.created_at,
        'updated_at': now,
        **body.dict(),
    }
    expected = convert_to_frontend_response(expected)

    assert response.status_code == 200
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_create_warehouse(client):
    now = datetime_utils.get_now()

    warehouse = warehouses.factories.build(address='test_adr')
    body = warehouses.UpdateWarehouseRequest(
        **warehouse.to_dict(),
    )

    response = await client.post('/admin/v1/warehouses/', json=body.dict())

    warehouses_list = await warehouses.get_all()

    assert response.status_code == 201
    assert len(warehouses_list) == 1

    expected = {
        **warehouse.to_dict(),
        'created_at': now,
        'updated_at': now,
        'warehouse_id': warehouses_list[0].warehouse_id,
    }
    expected = convert_to_frontend_response(expected)

    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_update_warehouse_zone_not_found(client):
    warehouse_id = generate_id()
    type = warehouse_zones.types.DeliveryType.FOOT

    response = await client.put(f'/admin/v1/warehouses/{warehouse_id}/zones/{type}/',
                                json={'status': 'CLOSE'})

    expected = {
        'code': 'WAREHOUSE_ZONE_NOT_FOUND_ERROR',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00', 'warehouse_id': warehouse_id, 'type': type},
        'message': 'Warehouse zone not found',
    }

    assert response.status_code == 404
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_update_warehouse_zone(client):
    warehouse = await warehouses.factories.create()
    zone = await warehouse_zones.factories.create(warehouse_id=warehouse.warehouse_id,
                                                  status=warehouse_zones.types.WarehouseStatus.OPEN)
    now = datetime_utils.get_now()

    body = warehouse_zones.UpdateWarehouseZoneRequest(
        status=warehouse_zones.types.WarehouseStatus.CLOSE,
        polygon=[{'lat': 0.0, 'lon': 0.0}, {'lat': 1.0, 'lon': 0.0}, {'lat': 3.0, 'lon': 3.0}],
        timetable=[
            {'day_type': 'WORKDAY', 'hours_from': {'hour': 0, 'minute': 0}, 'hours_to': {'hour': 23, 'minute': 0}}
        ]
    )

    response = await client.put(f'/admin/v1/warehouses/{zone.warehouse_id}/zones/{zone.type}/',
                                json=body.dict())

    expected = {
        'warehouse_id': zone.warehouse_id,
        'type': zone.type,
        'created_at': zone.created_at,
        'updated_at': now,
        **body.dict(),
    }
    expected = convert_to_frontend_response(expected)

    assert response.status_code == 200
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_create_warehouse_zone(client):
    now = datetime_utils.get_now()

    warehouse = await warehouses.factories.create()
    zone = warehouse_zones.factories.build()
    data = warehouse_zones.AdminCreateWarehouseZoneRequest(**zone.to_dict())

    response = await client.post(f'/admin/v1/warehouses/{warehouse.warehouse_id}/zones/',
                                 json=data.dict())

    zones = await warehouse_zones.get_all()

    assert response.status_code == 201
    assert len(zones) == 1

    expected = {
        **data.dict(),
        'created_at': now,
        'updated_at': now,
        'warehouse_id': warehouse.warehouse_id,
    }
    expected = convert_to_frontend_response(expected)

    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_create_warehouse_zone_not_found(client):
    warehouse_id = generate_id()
    zone = warehouse_zones.factories.build()
    data = warehouse_zones.AdminCreateWarehouseZoneRequest(**zone.to_dict())

    response = await client.post(f'/admin/v1/warehouses/{warehouse_id}/zones/',
                                 json=data.dict())

    expected = {
        'code': 'WAREHOUSE_NOT_FOUND_ERROR',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00', 'warehouse_id': warehouse_id},
        'message': 'Warehouse not found',
    }

    assert response.status_code == 404
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_create_warehouse_zone_request_error(client):
    warehouse_id = generate_id()
    zone = warehouse_zones.factories.build()
    data = warehouse_zones.AdminCreateWarehouseZoneRequest(**zone.to_dict()).dict()
    data.pop('type'), data.pop('status')

    response = await client.post(f'/admin/v1/warehouses/{warehouse_id}/zones/',
                                 json=data)

    expected = {
        'code': 'REQUEST_VALIDATION_ERROR',
        'message': '2 validation errors occurred',
        'details': {
            'occurred_at': '2020-01-02T00:04:05+00:00',
            'errors': [
                {'loc': ['body', 'type'], 'msg': 'field required', 'type': 'value_error.missing'},
                {'loc': ['body', 'status'], 'msg': 'field required', 'type': 'value_error.missing'},
            ],
        },
    }

    assert response.status_code == 400
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@mock.patch.object(devices, 'unlock_lock')
@pytest.mark.asyncio
async def test_open_entrance_lock(mock_unlock, client):
    mock_unlock.return_value = True

    warehouse = await warehouses.factories.create()
    await devices.factories.create(warehouse_id=warehouse.warehouse_id)

    response = await client.post(f'/admin/v1/warehouses/{warehouse.warehouse_id}/open-entrance-lock/')

    assert response.status_code == 200
    assert response.json() == {'success': True}


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@mock.patch.object(devices, 'unlock_lock')
@pytest.mark.asyncio
async def test_open_entrance_lock_not_found(mock_unlock, client):
    mock_unlock.return_value = True

    warehouse_id = generate_id()

    response = await client.post(f'/admin/v1/warehouses/{warehouse_id}/open-entrance-lock/')

    assert response.status_code == 404
    assert response.json() == {
        'code': 'DEVICE_NOT_FOUND_ERROR',
        'message': 'Device not found',
        'details': {
            'occurred_at': '2020-01-02T00:04:05+00:00',
            'warehouse_id': warehouse_id,
            'content': ('Unexpected number of entrance locks for the warehouse'
                        f' {warehouse_id}. Expected 1, found 0')
        }
    }


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_close_entrance_lock(client):
    warehouse = await warehouses.factories.create()
    await devices.factories.create(warehouse_id=warehouse.warehouse_id)

    response = await client.post(f'/admin/v1/warehouses/{warehouse.warehouse_id}/close-entrance-lock/')

    assert response.status_code == 409
    assert response.json() == {
        'code': 'COMMAND_NOT_IMPLEMENTED',
        'message': 'Command has not been implemented yet',
        'details': {
            'occurred_at': '2020-01-02T00:04:05+00:00',
            'warehouse_id': warehouse.warehouse_id,
        }
    }
