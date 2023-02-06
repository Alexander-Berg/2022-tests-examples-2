import pytest
import freezegun
import datetime

from taxi.robowarehouse.lib.concepts import device_messages
from taxi.robowarehouse.lib.concepts import courier_order_stages
from taxi.robowarehouse.lib.concepts import devices
from taxi.robowarehouse.lib.concepts import warehouses
from taxi.robowarehouse.lib.concepts import orders
from taxi.robowarehouse.lib.concepts import solomon
from taxi.robowarehouse.lib.misc import datetime_utils


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_check_open_legality_no_error(solomon_client):
    now = datetime_utils.get_now()

    warehouse = await warehouses.factories.create()
    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id,
                                          state=orders.types.OrderState.RECEIVED)
    device = await devices.factories.create(warehouse_id=warehouse.warehouse_id)
    await courier_order_stages.factories.create(
        order_id=order.order_id,
        effective_time=now,
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
    )

    await device_messages.tasks.check_open_legality(device.device_id, now.timestamp())

    assert not solomon_client.sensors


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_check_open_legality_cancelling(solomon_client):
    now = datetime_utils.get_now()
    delta_10m = datetime.timedelta(minutes=10)
    delta_5m = datetime.timedelta(minutes=5)
    warehouse = await warehouses.factories.create()
    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id,
                                          state=orders.types.OrderState.CANCELLING)
    device = await devices.factories.create(warehouse_id=warehouse.warehouse_id)

    await courier_order_stages.factories.create(
        order_id=order.order_id,
        effective_time=now - delta_10m,
        type_=courier_order_stages.types.CourierOrderStageType.EXITED_EMERGENCY,
    )
    await courier_order_stages.factories.create(
        order_id=order.order_id,
        effective_time=now - delta_5m,
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
    )
    await courier_order_stages.factories.create(
        order_id=order.order_id,
        effective_time=now,
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_CLOSED,
    )

    await device_messages.tasks.check_open_legality(device.device_id, (now - delta_5m).timestamp())

    assert not solomon_client.sensors


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_check_open_legality_with_error(solomon_client):
    now = datetime_utils.get_now()
    delta_10m = datetime.timedelta(minutes=10)

    warehouse = await warehouses.factories.create()
    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id,
                                          state=orders.types.OrderState.DELIVERING)
    device = await devices.factories.create(warehouse_id=warehouse.warehouse_id, name='test_lock')
    await courier_order_stages.factories.create(
        order_id=order.order_id,
        effective_time=now - delta_10m,
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
    )
    await courier_order_stages.factories.create(
        order_id=order.order_id,
        effective_time=now,
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_CLOSED,
    )

    await device_messages.tasks.check_open_legality(device.device_id, now.timestamp())

    expected = {
        'labels': {
            'sensor': 'unexpected_unlock',
            'device_id': device.device_id,
            'name': device.name,
        },
        'value': 1,
        'ts': datetime_utils.get_now_timestamp()
    }

    assert solomon_client.sensors[solomon.types.Service.ALERTS.value] == [expected]
