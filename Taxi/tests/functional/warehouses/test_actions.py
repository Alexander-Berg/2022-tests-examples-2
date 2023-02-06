import freezegun
import pytest

from unittest import mock
from sqlalchemy.exc import IntegrityError

from taxi.robowarehouse.lib.concepts import devices
from taxi.robowarehouse.lib.concepts import orders
from taxi.robowarehouse.lib.concepts import warehouses
from taxi.robowarehouse.lib.misc import datetime_utils
from taxi.robowarehouse.lib.misc.helpers import generate_id
from taxi.robowarehouse.lib.test_utils.helpers import assert_items_equal


@pytest.mark.asyncio
async def test_get_all_empty():
    result = await warehouses.get_all()

    assert result == []


@pytest.mark.asyncio
async def test_get_all():
    warehouse1 = await warehouses.factories.create()
    warehouse2 = await warehouses.factories.create()

    result = await warehouses.get_all()

    assert_items_equal([r.to_dict() for r in result], [warehouse1.to_dict(), warehouse2.to_dict()])


@pytest.mark.asyncio
async def test_get_by_warehouse_id_not_exist():
    await warehouses.factories.create()

    result = await warehouses.get_by_warehouse_id(generate_id())

    assert result is None


@pytest.mark.asyncio
async def test_get_by_warehouse_id():
    warehouse = await warehouses.factories.create()
    await warehouses.factories.create()

    result = await warehouses.get_by_warehouse_id(warehouse.warehouse_id)

    assert result.to_dict() == warehouse.to_dict()


@pytest.mark.asyncio
async def test_create():
    warehouse1 = warehouses.factories.build()
    warehouse2 = await warehouses.factories.create()

    result = await warehouses.create(warehouses.CreateWarehouseRequest.from_orm(warehouse1))

    assert result.to_dict() == warehouse1.to_dict()

    db_warehouses = await warehouses.get_all()
    assert_items_equal([m.to_dict() for m in db_warehouses], [warehouse1.to_dict(), warehouse2.to_dict()])


@pytest.mark.asyncio
async def test_create_duplicate():
    warehouse1 = await warehouses.factories.create()
    warehouse2 = await warehouses.factories.create()

    with pytest.raises(IntegrityError) as e:
        await warehouses.create(warehouses.CreateWarehouseRequest.from_orm(warehouse1))

    assert 'duplicate key value violates unique constraint' in str(e.value)

    db_warehouses = await warehouses.get_all()
    assert_items_equal([m.to_dict() for m in db_warehouses], [warehouse1.to_dict(), warehouse2.to_dict()])


@pytest.mark.asyncio
async def test_create_duplicate_address():
    warehouse1 = warehouses.factories.build(address='qwerty')
    await warehouses.factories.create(address='qwerty')

    with pytest.raises(IntegrityError) as e:
        await warehouses.create(warehouses.CreateWarehouseRequest.from_orm(warehouse1))

    assert 'duplicate key value violates unique constraint' in str(e.value)


@mock.patch.object(devices, 'unlock_lock')
@pytest.mark.asyncio
async def test_open_entrance_lock(mock_unlock_lock):
    await devices.factories.create()

    warehouse = await warehouses.factories.create()
    device = await devices.factories.create(
        warehouse_id=warehouse.warehouse_id,
        type_=devices.types.DeviceType.ENTRANCE_LOCK,
    )
    await devices.factories.create(warehouse_id=warehouse.warehouse_id, type_=devices.types.DeviceType.IP_CAMERA)

    mock_unlock_lock.return_value = True

    result = await warehouses.open_entrance_lock(warehouse_id=warehouse.warehouse_id)

    mock_unlock_lock.assert_called_once_with(
        source=device.source,
        source_device_id=device.source_device_id,
        sub_type=device.sub_type,
    )
    assert result is True


@mock.patch.object(datetime_utils, 'get_now')
@mock.patch.object(devices, 'check_lock_opened')
@pytest.mark.asyncio
async def test_check_opened_entrance_lock(mock_check_lock_opened, mock_get_now):
    await devices.factories.create()

    warehouse = await warehouses.factories.create()
    device = await devices.factories.create(
        warehouse_id=warehouse.warehouse_id,
        type_=devices.types.DeviceType.ENTRANCE_LOCK,
    )
    await devices.factories.create(warehouse_id=warehouse.warehouse_id, type_=devices.types.DeviceType.IP_CAMERA)

    mock_check_lock_opened.return_value = True

    now = datetime_utils.timestamp_to_datetime(100)
    mock_get_now.return_value = now

    result = await warehouses.check_opened_entrance_lock(warehouse_id=warehouse.warehouse_id)

    mock_get_now.assert_called_once_with()
    mock_check_lock_opened.assert_called_once_with(
        source=device.source,
        source_device_id=device.source_device_id,
        start_time=datetime_utils.timestamp_to_datetime(40),
        end_time=now,
    )
    assert result is True


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_update():
    warehouse = await warehouses.factories.create()
    updated_warehouse = await warehouses.update(
        warehouse_id=warehouse.warehouse_id,
        update_request=warehouses.UpdateWarehouseRequest(address='address'),
        updated_at=datetime_utils.get_now(),
        )
    warehouses_list = await warehouses.get_all()

    assert [w.to_dict() for w in warehouses_list] == [updated_warehouse.to_dict()]


@pytest.mark.parametrize('order_states, warehouse_count', [
    (
        [orders.types.OrderState.RECEIVED, orders.types.OrderState.DELIVERING, orders.types.OrderState.DELIVERED],
        0
    ),
    (
        [orders.types.OrderState.NEW, orders.types.OrderState.DELIVERING, orders.types.OrderState.DELIVERED],
        1
    ),
    (
        [orders.types.OrderState.NEW, orders.types.OrderState.NEW, orders.types.OrderState.DELIVERED],
        2
    ),
    (
        [orders.types.OrderState.NEW, orders.types.OrderState.NEW, orders.types.OrderState.NEW],
        3
    ),

])
@pytest.mark.asyncio
async def test_get_all_receiving(order_states, warehouse_count):
    warehouse_list = [await warehouses.factories.create() for _ in range(3)]
    warehouse_list.sort(key=lambda el: el.warehouse_id)

    for warehouse, state in zip(warehouse_list, order_states):
        await orders.factories.create(warehouse_id=warehouse.warehouse_id, state=state)

    result = await warehouses.get_all_receiving()

    result = [res.to_dict() for res in result]
    warehouse_list = [warehouse.to_dict() for warehouse in warehouse_list[:warehouse_count]]
    assert_items_equal(result, warehouse_list)
