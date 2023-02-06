import pytest
import freezegun
from sqlalchemy.exc import IntegrityError

from taxi.robowarehouse.lib.concepts import devices
from taxi.robowarehouse.lib.concepts import warehouses
from taxi.robowarehouse.lib.concepts.adapters.types import AdapterType
from taxi.robowarehouse.lib.misc import datetime_utils
from taxi.robowarehouse.lib.misc.helpers import generate_id
from taxi.robowarehouse.lib.test_utils.helpers import assert_items_equal


@pytest.mark.asyncio
async def test_get_all_empty():
    result = await devices.get_all()

    assert result == []


@pytest.mark.asyncio
async def test_get_all():
    device1 = await devices.factories.create()
    device2 = await devices.factories.create()

    result = await devices.get_all()

    assert_items_equal([r.to_dict() for r in result], [device1.to_dict(), device2.to_dict()])


@pytest.mark.asyncio
async def test_get_all_active_empty():
    await devices.factories.create(state=devices.types.DeviceState.INACTIVE)

    result = await devices.get_all_active()

    assert result == []


@pytest.mark.asyncio
async def test_get_all_active():
    device1 = await devices.factories.create()
    device2 = await devices.factories.create()
    await devices.factories.create(state=devices.types.DeviceState.INACTIVE)

    result = await devices.get_all_active()

    assert_items_equal([r.to_dict() for r in result], [device1.to_dict(), device2.to_dict()])


@pytest.mark.asyncio
async def test_get_by_device_id_not_exist():
    await devices.factories.create()

    result = await devices.get_by_device_id(generate_id())

    assert result is None


@pytest.mark.asyncio
async def test_get_by_device_id():
    device = await devices.factories.create()
    await devices.factories.create()

    result = await devices.get_by_device_id(device.device_id)

    assert result.to_dict() == device.to_dict()


@pytest.mark.asyncio
async def test_get_by_source_device_id_not_exist():
    await devices.factories.create()

    result = await devices.get_by_source_device_id(source=AdapterType.TUYA, source_device_id=generate_id())

    assert result is None


@pytest.mark.asyncio
async def test_get_by_source_device_id():
    device = await devices.factories.create()
    await devices.factories.create()

    result = await devices.get_by_source_device_id(source=device.source, source_device_id=device.source_device_id)

    assert result.to_dict() == device.to_dict()


@pytest.mark.parametrize('created_types, filter_type, expected_indexes', [
    ([], None, []),
    ([], 'ENTRANCE_LOCK', []),
    (['ENTRANCE_LOCK'], 'ENTRANCE_LOCK', [0]),
    (['ENTRANCE_LOCK'], 'IP_CAMERA', []),
    (['ENTRANCE_LOCK', 'ENTRANCE_LOCK'], 'ENTRANCE_LOCK', [0, 1]),
    (['ENTRANCE_LOCK', 'IP_CAMERA'], 'ENTRANCE_LOCK', [0]),
    (['ENTRANCE_LOCK', 'IP_CAMERA'], None, [0, 1]),
    (['ENTRANCE_LOCK', 'IP_CAMERA', 'ENTRANCE_LOCK'], 'ENTRANCE_LOCK', [0, 2]),
])
@pytest.mark.asyncio
async def test_list_by_warehouse_id(created_types, filter_type, expected_indexes):
    await devices.factories.create()

    warehouse = await warehouses.factories.create()
    devices_created = []
    for type_ in created_types:
        devices_created.append(await devices.factories.create(warehouse_id=warehouse.warehouse_id, type_=type_))

    result = await devices.list_by_warehouse_id(warehouse_id=warehouse.warehouse_id, type_=filter_type)

    assert_items_equal([r.to_dict() for r in result], [devices_created[i].to_dict() for i in expected_indexes])


@pytest.mark.asyncio
async def test_get_warehouse_entrance_lock_not_found():
    await devices.factories.create()

    warehouse = await warehouses.factories.create()
    await devices.factories.create(warehouse_id=warehouse.warehouse_id, type_=devices.types.DeviceType.IP_CAMERA)

    with pytest.raises(ValueError) as e:
        await devices.get_warehouse_entrance_lock(warehouse_id=warehouse.warehouse_id)

    assert str(e.value) == f'Unexpected number of entrance locks for the warehouse {warehouse.warehouse_id}.' \
                           f' Expected 1, found 0'


@pytest.mark.asyncio
async def test_get_warehouse_entrance_lock_multiple():
    await devices.factories.create()

    warehouse = await warehouses.factories.create()
    await devices.factories.create(warehouse_id=warehouse.warehouse_id, type_=devices.types.DeviceType.ENTRANCE_LOCK)
    await devices.factories.create(warehouse_id=warehouse.warehouse_id, type_=devices.types.DeviceType.ENTRANCE_LOCK)

    with pytest.raises(ValueError) as e:
        await devices.get_warehouse_entrance_lock(warehouse_id=warehouse.warehouse_id)

    assert str(e.value) == f'Unexpected number of entrance locks for the warehouse {warehouse.warehouse_id}.' \
                           f' Expected 1, found 2'


@pytest.mark.asyncio
async def test_get_warehouse_entrance_lock():
    await devices.factories.create()

    warehouse = await warehouses.factories.create()
    device = await devices.factories.create(
        warehouse_id=warehouse.warehouse_id,
        type_=devices.types.DeviceType.ENTRANCE_LOCK,
    )
    await devices.factories.create(warehouse_id=warehouse.warehouse_id, type_=devices.types.DeviceType.IP_CAMERA)

    result = await devices.get_warehouse_entrance_lock(warehouse_id=warehouse.warehouse_id)

    assert result.to_dict() == device.to_dict()


@pytest.mark.asyncio
async def test_create():
    device1 = devices.factories.build()
    device2 = await devices.factories.create()

    result = await devices.create(devices.CreateDeviceRequest.from_orm(device1))

    assert result.to_dict() == device1.to_dict()

    db_devices = await devices.get_all()
    assert_items_equal([m.to_dict() for m in db_devices], [device1.to_dict(), device2.to_dict()])


@pytest.mark.asyncio
async def test_create_duplicate():
    device1 = await devices.factories.create()
    device2 = await devices.factories.create()

    with pytest.raises(IntegrityError) as e:
        await devices.create(devices.CreateDeviceRequest.from_orm(device1))

    assert 'duplicate key value violates unique constraint' in str(e.value)

    db_devices = await devices.get_all()
    assert_items_equal([m.to_dict() for m in db_devices], [device1.to_dict(), device2.to_dict()])


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_update_state():
    now = datetime_utils.get_now()
    device1 = await devices.factories.create(state=devices.types.DeviceState.ACTIVE)

    new_device = await devices.update_state(device_id=device1.device_id, state=devices.types.DeviceState.INACTIVE)

    assert new_device.to_dict() == {
        **device1.to_dict(),
        'state': devices.types.DeviceState.INACTIVE,
        'updated_at': now
    }
