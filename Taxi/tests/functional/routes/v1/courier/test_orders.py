from unittest import mock
from typing import Optional

import freezegun
import pytest

from taxi.robowarehouse.lib.concepts import courier_order_stages
from taxi.robowarehouse.lib.concepts import devices
from taxi.robowarehouse.lib.concepts import orders
from taxi.robowarehouse.lib.concepts import packages
from taxi.robowarehouse.lib.concepts import warehouses
from taxi.robowarehouse.lib.concepts import celery as celery_concepts
from taxi.robowarehouse.lib.misc import datetime_utils
from taxi.robowarehouse.lib.concepts import package_places
from taxi.robowarehouse.lib.misc.helpers import drop_none
from taxi.robowarehouse.lib.misc.helpers import generate_id
from taxi.robowarehouse.lib.test_utils.helpers import assert_items_equal


def _get_order_response(order: orders.Order) -> dict:
    response = {
        'orderId': order.order_id,
        'warehouseId': order.warehouse_id,
        'state': order.state.value,
    }
    return drop_none(response)


def _get_package_response(package: packages.Package, rack: Optional[int] = None, place: Optional[int] = None) -> dict:
    response = {
        'packageId': package.package_id,
        'barcode': package.barcode,
        'measurements': package.measurements,
        'rack': rack,
        'place': place,
    }
    return drop_none(response)


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_order_not_found(client):
    courier_id = generate_id()
    order_id = generate_id()
    await orders.factories.create()

    response = await client.get(f'/courier/v1/orders/{order_id}/', headers={'X-Yandex-UID': courier_id})

    expected = {
        'code': 'ORDER_NOT_FOUND_ERROR',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00', 'order_id': order_id},
        'message': 'Order not found',
    }

    assert response.status_code == 404
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_order_without_packages(client):
    courier_id = generate_id()

    order1 = await orders.factories.create(state=orders.types.OrderState.RECEIVED)
    order2 = await orders.factories.create()
    await packages.factories.create(order_id=order2.order_id)
    await courier_order_stages.factories.create(order_id=order1.order_id, courier_id=courier_id)

    response = await client.get(f'/courier/v1/orders/{order1.order_id}/', headers={'X-Yandex-UID': courier_id})

    expected = {
        'code': 'PACKAGE_NOT_FOUND_ERROR',
        'message': 'Package not found',
        'details': {
            'occurred_at': '2020-01-02T00:04:05+00:00',
            'order_id': order1.order_id,
        },
    }

    assert response.status_code == 404
    assert response.json() == expected


@pytest.mark.asyncio
async def test_get_order_with_package(client):
    courier_id = generate_id()

    order1 = await orders.factories.create(state=orders.types.OrderState.RECEIVED)

    package1 = await packages.factories.create(order_id=order1.order_id, barcode='23456')
    place1 = await package_places.factories.create(
        package_id=package1.package_id,
        pallet={'rack': 1, 'place': 11},
    )

    order2 = await orders.factories.create()
    await packages.factories.create(order_id=order2.order_id)
    await courier_order_stages.factories.create(order_id=order1.order_id, courier_id=courier_id)

    response = await client.get(f'/courier/v1/orders/{order1.order_id}/', headers={'X-Yandex-UID': courier_id})

    expected = _get_order_response(order1)
    expected_package = _get_package_response(package1, place1.pallet['rack'], place1.pallet['place'])
    expected['package'] = expected_package

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.asyncio
async def test_get_order_with_package_without_places(client):
    courier_id = generate_id()

    order1 = await orders.factories.create(state=orders.types.OrderState.RECEIVED)

    package1 = await packages.factories.create(order_id=order1.order_id, barcode='23456')

    order2 = await orders.factories.create()
    await packages.factories.create(order_id=order2.order_id)
    await courier_order_stages.factories.create(order_id=order1.order_id, courier_id=courier_id)

    response = await client.get(f'/courier/v1/orders/{order1.order_id}/', headers={'X-Yandex-UID': courier_id})

    expected = _get_order_response(order1)
    expected_package = _get_package_response(package1)
    expected['package'] = expected_package

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.asyncio
async def test_get_order_with_packages(client):
    courier_id = generate_id()

    order1 = await orders.factories.create(state=orders.types.OrderState.RECEIVED)
    await courier_order_stages.factories.create(order_id=order1.order_id, courier_id=courier_id)

    package1 = await packages.factories.create(order_id=order1.order_id, barcode='12345', created_at=1)
    package2 = await packages.factories.create(order_id=order1.order_id, barcode='23456', created_at=2)

    place1 = await package_places.factories.create(
        package_id=package1.package_id,
        pallet={'rack': 1, 'place': 11},
    )
    await package_places.factories.create(
        package_id=package2.package_id,
        pallet={'rack': 2, 'place': 23},
    )

    order2 = await orders.factories.create()
    await packages.factories.create(order_id=order2.order_id)

    response = await client.get(f'/courier/v1/orders/{order1.order_id}/', headers={'X-Yandex-UID': courier_id})

    expected = _get_order_response(order1)
    expected_package = _get_package_response(package1, place1.pallet['rack'], place1.pallet['place'])
    expected['package'] = expected_package

    assert response.status_code == 200
    assert response.json() == expected


@mock.patch.object(devices, 'unlock_lock')
@pytest.mark.asyncio
async def test_open_warehouse(mock_unlock_lock, client):
    courier_id = generate_id()

    warehouse = await warehouses.factories.create()
    device = await devices.factories.create(
        warehouse_id=warehouse.warehouse_id,
        type_=devices.types.DeviceType.ENTRANCE_LOCK,
    )

    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id, state=orders.types.OrderState.RECEIVED)
    order_stage1 = await courier_order_stages.factories.create(order_id=order.order_id, effective_time=2)
    order_stage2 = await courier_order_stages.factories.create(
        order_id=order.order_id,
        courier_id=courier_id,
        effective_time=3,
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        type_meta={'a': 1},
    )
    order_stage3 = await courier_order_stages.factories.create(
        order_id=order.order_id,
        courier_id=courier_id,
        effective_time=4,
        type_=courier_order_stages.types.CourierOrderStageType.NEW,
        type_meta={'a': 1},
    )

    mock_unlock_lock.return_value = True

    with mock.patch.object(datetime_utils, 'get_now') as mock_now:
        mock_now.return_value = datetime_utils.timestamp_to_datetime(10)
        response = await client.post(f'/courier/v1/orders/{order.order_id}/open-warehouse/',
                                     headers={'X-Yandex-UID': courier_id})

    mock_unlock_lock.assert_called_once_with(
        source=device.source,
        source_device_id=device.source_device_id,
        sub_type=device.sub_type,
    )

    expected_order_stage = courier_order_stages.factories.build(
        courier_id=courier_id,
        order_id=order.order_id,
        effective_time=10,
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
        type_meta={},
    )

    expected_response = {
        'orderId': order.order_id,
        'stage': expected_order_stage.type.value,
    }

    assert response.status_code == 200
    assert response.json() == expected_response

    expected_order_stages = [
        expected_order_stage.to_dict(),
        order_stage1.to_dict(),
        order_stage2.to_dict(),
        order_stage3.to_dict(),
    ]
    order_stages_db = await courier_order_stages.get_all()
    assert_items_equal([s.to_dict() for s in order_stages_db], expected_order_stages)


@mock.patch.object(devices, 'check_lock_opened')
@pytest.mark.asyncio
async def test_get_warehouse_entrance_lock_status(mock_check_lock_opened, client):
    courier_id = generate_id()

    warehouse = await warehouses.factories.create()
    device = await devices.factories.create(
        warehouse_id=warehouse.warehouse_id,
        type_=devices.types.DeviceType.ENTRANCE_LOCK,
    )

    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id, state=orders.types.OrderState.RECEIVED)
    await courier_order_stages.factories.create(
        order_id=order.order_id,
        courier_id=courier_id,
        effective_time=3,
        type_=courier_order_stages.types.CourierOrderStageType.NEW,
    )

    mock_check_lock_opened.return_value = True

    with mock.patch.object(datetime_utils, 'get_now') as mock_now:
        now = datetime_utils.timestamp_to_datetime(100)
        mock_now.return_value = now

        response = await client.get(f'/courier/v1/orders/{order.order_id}/warehouse-entrance-lock-status/',
                                    headers={'X-Yandex-UID': courier_id})

        mock_check_lock_opened.assert_called_once_with(
            source=device.source,
            source_device_id=device.source_device_id,
            start_time=datetime_utils.timestamp_to_datetime(40),
            end_time=now,
        )

    assert response.status_code == 200
    assert response.json() == {'success': True}


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_courier_order_stage_wrong_courier(client):
    order = await orders.factories.create()
    await courier_order_stages.factories.create(order_id=order.order_id)
    courier_id = generate_id()

    expected = {
        'code': 'COURIER_ORDER_STAGE_WRONG_COURIER',
        'message': 'Courier order stage has wrong courier',
        'details': {
            'occurred_at': '2020-01-02T00:04:05+00:00',
            'order_id': order.order_id,
            'courier_id': courier_id,
        },
    }

    response = await client.get(f'/courier/v1/orders/{order.order_id}/stage/',
                                headers={'X-Yandex-UID': courier_id})

    assert response.status_code == 409
    assert response.json() == expected


@pytest.mark.asyncio
async def test_get_courier_order_stage(client):
    order = await orders.factories.create()
    courier_order = await courier_order_stages.factories.create(order_id=order.order_id, effective_time=3)
    await courier_order_stages.factories.create(order_id=order.order_id, effective_time=2)
    await courier_order_stages.factories.create(order_id=order.order_id, effective_time=1)
    await courier_order_stages.factories.create(effective_time=4)

    expected = {'orderId': courier_order.order_id, 'stage': courier_order.type}

    response = await client.get(f'/courier/v1/orders/{order.order_id}/stage/',
                                headers={'X-Yandex-UID': courier_order.courier_id})

    assert response.status_code == 200
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_pickup_order(client):
    warehouse = await warehouses.factories.create()
    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id, state=orders.types.OrderState.RECEIVED)
    package = await packages.factories.create(order_id=order.order_id, state=packages.types.PackageState.IN_WAREHOUSE)
    courier_id = generate_id()
    await courier_order_stages.factories.create(courier_id=courier_id, order_id=order.order_id, type_meta={'a': 1})

    expected = {
        'orderId': order.order_id,
        'stage': courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
    }

    response = await client.post(f'/courier/v1/orders/{order.order_id}/packages/{package.package_id}/pickup/',
                                 headers={'X-Yandex-UID': courier_id})

    order_stage_list = sorted(await courier_order_stages.get_all(), key=lambda el: el.effective_time)
    new_order_stage = order_stage_list[-1]

    assert response.status_code == 200
    assert response.json() == expected
    assert len(order_stage_list) == 2
    assert new_order_stage.type == courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN
    assert new_order_stage.effective_time == datetime_utils.get_now()
    assert new_order_stage.type_meta == {}


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_pickup_order_package_not_found(client):
    warehouse = await warehouses.factories.create()
    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id, state=orders.types.OrderState.RECEIVED)
    package_id = generate_id()
    courier_id = generate_id()
    await courier_order_stages.factories.create(courier_id=courier_id, order_id=order.order_id, type_meta={'a': 1})

    expected = {
        'code': 'PACKAGE_NOT_FOUND_ERROR',
        'message': 'Package not found',
        'details': {
            'occurred_at': '2020-01-02T00:04:05+00:00',
            'package_id': package_id,
        },
    }

    response = await client.post(f'/courier/v1/orders/{order.order_id}/packages/{package_id}/pickup/',
                                 headers={'X-Yandex-UID': courier_id})

    assert response.status_code == 404
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@mock.patch.object(celery_concepts.tasks.courier_order_stage_tasks.send_courier_stages_time, 'apply_async')
@pytest.mark.asyncio
async def test_close_warehouse_package_not_on_warehouse(mock_send_courier_stages_time, client):
    mock_send_courier_stages_time.return_value = None

    warehouse = await warehouses.factories.create()
    await devices.factories.create(
        warehouse_id=warehouse.warehouse_id,
        type_=devices.types.DeviceType.ENTRANCE_LOCK,
    )
    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id, state=orders.types.OrderState.RECEIVED)
    courier_id = generate_id()

    await packages.factories.create(order_id=order.order_id)
    await courier_order_stages.factories.create(
        courier_id=courier_id,
        order_id=order.order_id,
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
        type_meta={'a': 1},
    )

    expected = {
        'code': 'PACKAGE_NOT_ON_WAREHOUSE_ACTIVE',
        'message': 'Package is not on warehouse',
        'details': {
            'occurred_at': '2020-01-02T00:04:05+00:00',
            'order_id': order.order_id,
        },
    }

    response = await client.post(f'/courier/v1/orders/{order.order_id}/finish/',
                                 headers={'X-Yandex-UID': courier_id})

    assert response.status_code == 409
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@mock.patch.object(celery_concepts.tasks.courier_order_stage_tasks.send_courier_stages_time, 'apply_async')
@pytest.mark.asyncio
async def test_close_warehouse(mock_send_courier_stages_time, client):
    mock_send_courier_stages_time.return_value = None

    warehouse = await warehouses.factories.create()
    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id, state=orders.types.OrderState.RECEIVED)
    courier_id = generate_id()
    package = await packages.factories.create(order_id=order.order_id, state=packages.types.PackageState.IN_WAREHOUSE)

    order_stage = await courier_order_stages.factories.create(
        courier_id=courier_id,
        order_id=order.order_id,
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
        type_meta={'a': 1},
    )

    expected = {
        'orderId': order.order_id,
        'stage': courier_order_stages.types.CourierOrderStageType.WAREHOUSE_CLOSED,
    }

    response = await client.post(f'/courier/v1/orders/{order.order_id}/finish/',
                                 headers={'X-Yandex-UID': courier_id})

    assert response.status_code == 200
    assert response.json() == expected

    order_history = await orders.get_all_history()
    package_history = await packages.get_all_history()
    order_stage_list = sorted(await courier_order_stages.get_all(), key=lambda el: el.effective_time)

    new_order = await orders.get_by_order_id(order_id=order.order_id)
    new_package = (await packages.list_by_order_id(order_id=order.order_id))[0]
    new_order_stage = order_stage_list[-1]
    now = datetime_utils.get_now()

    assert len(order_stage_list) == 2
    assert len(package_history) == 1
    assert len(order_history) == 1
    assert order_history[0].to_dict() == {
        **order.to_dict(),
        'state': orders.types.OrderState.DELIVERING,
        'updated_at': now,
    }
    assert package_history[0].to_dict() == {
        **package.to_dict(),
        'state': packages.types.PackageState.DELIVERING,
        'updated_at': now,
    }
    assert new_order_stage.to_dict() == {
        **order_stage.to_dict(),
        'type': courier_order_stages.types.CourierOrderStageType.WAREHOUSE_CLOSED,
        'effective_time': now,
        'type_meta': {},
    }
    assert new_order.to_dict() == order_history[0].to_dict()
    assert new_package.to_dict() == package_history[0].to_dict()


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_emergency_exit(client):
    courier_id = generate_id()
    order = await orders.factories.create(state=orders.types.OrderState.RECEIVED)
    package = await packages.factories.create(order_id=order.order_id, state=packages.types.PackageState.IN_WAREHOUSE)

    order_stage = await courier_order_stages.factories.create(
        courier_id=courier_id,
        order_id=order.order_id,
        effective_time=1,
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
        type_meta={'a': 1},
    )

    response = await client.post(f'/courier/v1/orders/{order.order_id}/emergencyExit/',
                                 json={'reason': 'great', 'reasonComment': 'problem'},
                                 headers={'X-Yandex-UID': courier_id})

    expected_stage = courier_order_stages.factories.build(
        courier_id=courier_id,
        order_id=order.order_id,
        effective_time=datetime_utils.get_now(),
        type_=courier_order_stages.types.CourierOrderStageType.EXITED_EMERGENCY,
        type_meta={'reason': 'great', 'reason_comment': 'problem'},
    )

    assert response.status_code == 200
    assert response.json() == {'orderId': expected_stage.order_id, 'stage': expected_stage.type}

    order_stage_db = sorted(await courier_order_stages.get_all(), key=lambda el: el.effective_time)

    assert [r.to_dict() for r in order_stage_db] == [order_stage.to_dict(), expected_stage.to_dict()]

    assert [r.to_dict() for r in await orders.get_all()] == [order.to_dict()]
    assert [r.to_dict() for r in await packages.get_all()] == [package.to_dict()]
