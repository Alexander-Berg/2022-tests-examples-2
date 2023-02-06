import datetime
from unittest import mock

import freezegun
import pytest


from taxi.robowarehouse.lib.concepts import solomon
from taxi.robowarehouse.lib.concepts import orders
from taxi.robowarehouse.lib.concepts import courier_order_stages
from taxi.robowarehouse.lib.misc import datetime_utils
from taxi.robowarehouse.lib.test_utils.helpers import assert_items_equal


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@mock.patch.object(solomon.client.SolomonClient, 'send')
@pytest.mark.asyncio
async def test_monitoing_courier_stage(solomon_send_mock):
    now = datetime_utils.get_now()
    timestamp = datetime_utils.get_now_timestamp()
    delta_5m = datetime.timedelta(minutes=5)
    delta_2m = datetime.timedelta(minutes=2)

    order1 = await orders.factories.create()
    order2 = await orders.factories.create()
    order3 = await orders.factories.create()

    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
        effective_time=now - delta_5m,
        order_id=order1.order_id
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now - delta_2m,
        order_id=order1.order_id
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now - delta_5m,
        order_id=order2.order_id
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now - delta_2m,
        order_id=order3.order_id
    )

    solomon_send_mock.return_value = None
    solomon_client = await solomon.get_solomon_client()

    await courier_order_stages.tasks.monitoing_courier_stage()

    expected_metrics = [
        {
            'labels': {'sensor': 'courier_freeze', 'order_id': order1.order_id, 'stage': 'package_taken'},
            'value': delta_5m.total_seconds(),
            'ts': timestamp,
        },
        {
            'labels': {'sensor': 'courier_freeze', 'order_id': order2.order_id, 'stage': 'warehouse_opened'},
            'value': delta_5m.total_seconds(),
            'ts': timestamp,
        },
    ]

    assert len(solomon_client.sensors['alerts']) == 2
    assert_items_equal(solomon_client.sensors['alerts'], expected_metrics)

    await solomon_client._clear_sensors()


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_send_courier_stages_time(solomon_client):
    now = datetime_utils.get_now()
    timestamp = datetime_utils.get_now_timestamp()
    delta_5m = datetime.timedelta(minutes=5)
    delta_2m = datetime.timedelta(minutes=2)

    order1 = await orders.factories.create()

    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now - delta_5m,
        order_id=order1.order_id
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
        effective_time=now - delta_2m,
        order_id=order1.order_id
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_CLOSED,
        effective_time=now,
        order_id=order1.order_id
    )

    await courier_order_stages.tasks.send_courier_stages_time(order_id=order1.order_id)

    expected_metrics = [
        {
            'labels': {'sensor': 'courier_stage_time', 'stage': 'open_taken'},
            'value': (delta_5m - delta_2m).total_seconds(),
            'ts': timestamp,
        },
        {
            'labels': {'sensor': 'courier_stage_time', 'stage': 'taken_close'},
            'value': delta_2m.total_seconds(),
            'ts': timestamp,
        },
    ]

    assert len(solomon_client.sensors['courier_stage']) == 2
    assert_items_equal(solomon_client.sensors['courier_stage'], expected_metrics)


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_send_courier_stages_time_without_metrics(solomon_client):
    now = datetime_utils.get_now()
    delta_5m = datetime.timedelta(minutes=5)
    delta_2m = datetime.timedelta(minutes=2)

    order1 = await orders.factories.create()

    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        effective_time=now - delta_5m,
        order_id=order1.order_id
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
        effective_time=now - delta_2m,
        order_id=order1.order_id
    )
    await courier_order_stages.factories.create(
        type_=courier_order_stages.types.CourierOrderStageType.EXITED_EMERGENCY,
        effective_time=now,
        order_id=order1.order_id
    )

    await courier_order_stages.tasks.send_courier_stages_time(order_id=order1.order_id)

    assert len(solomon_client.sensors['courier_stage']) == 0
