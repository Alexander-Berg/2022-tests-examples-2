import datetime
import freezegun
import pytest

from sqlalchemy.exc import IntegrityError

from taxi.robowarehouse.lib.concepts import courier_order_stages
from taxi.robowarehouse.lib.concepts import orders
from taxi.robowarehouse.lib.concepts import packages
from taxi.robowarehouse.lib.concepts import package_places
from taxi.robowarehouse.lib.concepts import warehouses
from taxi.robowarehouse.lib.concepts.orders.types import OrderState
from taxi.robowarehouse.lib.concepts.packages.types import PackageState
from taxi.robowarehouse.lib.misc import datetime_utils
from taxi.robowarehouse.lib.misc.helpers import generate_id
from taxi.robowarehouse.lib.misc.helpers import base64_encode
from taxi.robowarehouse.lib.test_utils.helpers import assert_items_equal


@pytest.mark.asyncio
async def test_get_all_empty():
    result = await orders.get_all()

    assert result == []


@pytest.mark.asyncio
async def test_get_all():
    order1 = await orders.factories.create()
    order2 = await orders.factories.create()

    result = await orders.get_all()

    assert_items_equal([r.to_dict() for r in result], [
                       order1.to_dict(), order2.to_dict()])


@pytest.mark.asyncio
async def test_get_all_history_empty():
    result = await orders.get_all_history()

    assert result == []


@pytest.mark.asyncio
async def test_get_all_history():
    order1 = await orders.factories.create_history()
    order2 = await orders.factories.create_history()

    result = await orders.get_all_history()

    assert_items_equal([r.to_dict() for r in result], [
                       order1.to_dict(), order2.to_dict()])


@pytest.mark.asyncio
async def test_get_by_order_id_not_exist_raise_not_found():
    await orders.factories.create()

    with pytest.raises(orders.exceptions.OrderNotFoundError):
        await orders.get_by_order_id(generate_id())


@pytest.mark.asyncio
async def test_get_by_order_id_not_exist_return_none():
    await orders.factories.create()

    result = await orders.get_by_order_id(generate_id(), raise_not_found=False)

    assert result is None


@pytest.mark.asyncio
async def test_get_by_order_id():
    order = await orders.factories.create()
    await orders.factories.create()

    result = await orders.get_by_order_id(order.order_id)

    assert result.to_dict() == order.to_dict()


@pytest.mark.asyncio
async def test_get_active_courier_stage_order_not_found():
    courier_id = generate_id()
    order = await orders.factories.create(state=orders.types.OrderState.RECEIVED)
    await courier_order_stages.factories.create(order_id=order.order_id, courier_id=courier_id)

    with pytest.raises(orders.exceptions.OrderNotFoundError):
        await orders.get_active_courier_stage(
            order_id=generate_id(),
            courier_id=courier_id,
            time=datetime_utils.timestamp_to_datetime(3),
        )


@pytest.mark.asyncio
async def test_get_active_courier_stage_order_stage_not_found():
    courier_id = generate_id()
    order = await orders.factories.create(state=orders.types.OrderState.RECEIVED)
    await courier_order_stages.factories.create(order_id=order.order_id, courier_id=courier_id, effective_time=4)

    with pytest.raises(courier_order_stages.exceptions.CourierOrderStageNotFoundError):
        await orders.get_active_courier_stage(
            order_id=order.order_id,
            courier_id=courier_id,
            time=datetime_utils.timestamp_to_datetime(3),
        )


@pytest.mark.asyncio
async def test_get_active_courier_stage_wrong_courier():
    courier_id = generate_id()
    order = await orders.factories.create(state=orders.types.OrderState.RECEIVED)
    await courier_order_stages.factories.create(order_id=order.order_id, courier_id=courier_id, effective_time=2)

    with pytest.raises(courier_order_stages.exceptions.CourierOrderStageWrongCourier):
        await orders.get_active_courier_stage(
            order_id=order.order_id,
            courier_id=generate_id(),
            time=datetime_utils.timestamp_to_datetime(3),
        )


@pytest.mark.parametrize('order_state', [
    orders.types.OrderState.NEW,
    orders.types.OrderState.CANCELLED,
    orders.types.OrderState.RESERVED,
    orders.types.OrderState.DELIVERED,
])
@pytest.mark.asyncio
async def test_get_active_courier_stage_order_not_on_warehouse(order_state):
    courier_id = generate_id()
    order = await orders.factories.create(state=order_state)
    await courier_order_stages.factories.create(order_id=order.order_id, courier_id=courier_id, effective_time=2)

    with pytest.raises(orders.exceptions.OrderNotOnWarehouse):
        await orders.get_active_courier_stage(
            order_id=order.order_id,
            courier_id=courier_id,
            time=datetime_utils.timestamp_to_datetime(3),
        )


@pytest.mark.parametrize('order_stage_state', [
    courier_order_stages.types.CourierOrderStageType.WAREHOUSE_CLOSED,
])
@pytest.mark.asyncio
async def test_get_active_courier_stage_stage_not_active(order_stage_state):
    courier_id = generate_id()
    order = await orders.factories.create(state=orders.types.OrderState.RECEIVED)
    await courier_order_stages.factories.create(
        order_id=order.order_id,
        courier_id=courier_id,
        type_=order_stage_state,
        effective_time=2,
    )

    with pytest.raises(courier_order_stages.exceptions.CourierOrderStageNotActive):
        await orders.get_active_courier_stage(
            order_id=order.order_id,
            courier_id=courier_id,
            time=datetime_utils.timestamp_to_datetime(3),
        )


@pytest.mark.asyncio
async def test_get_active_courier_stage():
    await courier_order_stages.factories.create()

    courier_id = generate_id()
    order = await orders.factories.create(state=orders.types.OrderState.RECEIVED)
    await courier_order_stages.factories.create(order_id=order.order_id, effective_time=2)
    order_stage = await courier_order_stages.factories.create(
        order_id=order.order_id,
        courier_id=courier_id,
        effective_time=3,
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED,
    )
    await courier_order_stages.factories.create(
        order_id=order.order_id,
        courier_id=courier_id,
        effective_time=4,
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN,
    )

    result = await orders.get_active_courier_stage(
        order_id=order.order_id,
        courier_id=courier_id,
        time=datetime_utils.timestamp_to_datetime(3),
    )

    assert (result[0].to_dict(), result[1].to_dict()) == (
        order.to_dict(), order_stage.to_dict())


@pytest.mark.asyncio
async def test_create():
    order1 = orders.factories.build(warehouse_id=None)
    order2 = await orders.factories.create()

    result = await orders.create(orders.CreateOrderRequest.from_orm(order1))

    assert result.to_dict() == order1.to_dict()

    db_orders = await orders.get_all()
    assert_items_equal([m.to_dict() for m in db_orders], [
                       order1.to_dict(), order2.to_dict()])

    db_history = await orders.get_all_history()
    assert_items_equal([m.to_dict() for m in db_history], [
                       orders.OrderHistoryResponse(**order1.to_dict())])


@pytest.mark.asyncio
async def test_create_with_warehouse_id():
    warehouse1 = await warehouses.factories.create()
    order1 = orders.factories.build(warehouse_id=warehouse1.warehouse_id)
    order2 = await orders.factories.create()

    result = await orders.create(orders.CreateOrderRequest.from_orm(order1))

    assert result.to_dict() == order1.to_dict()

    db_orders = await orders.get_all()
    assert_items_equal([m.to_dict() for m in db_orders], [
                       order1.to_dict(), order2.to_dict()])

    db_history = await orders.get_all_history()
    assert_items_equal([m.to_dict() for m in db_history], [
                       orders.OrderHistoryResponse(**order1.to_dict())])


@pytest.mark.asyncio
async def test_create_without_history():
    order1 = orders.factories.build()
    order2 = await orders.factories.create()

    result = await orders.create(orders.CreateOrderRequest.from_orm(order1), with_history=False)

    assert result.to_dict() == order1.to_dict()

    db_orders = await orders.get_all()
    assert_items_equal([m.to_dict() for m in db_orders], [
                       order1.to_dict(), order2.to_dict()])

    db_history = await orders.get_all_history()
    assert db_history == []


@pytest.mark.asyncio
async def test_create_no_warehouse():
    warehouse_id = generate_id()
    order1 = orders.factories.build(warehouse_id=warehouse_id)
    order2 = await orders.factories.create()

    with pytest.raises(IntegrityError) as e:
        await orders.create(orders.CreateOrderRequest.from_orm(order1))

    assert f'Key (warehouse_id)=({warehouse_id}) is not present in table "warehouses".' in str(
        e.value)

    db_orders = await orders.get_all()
    assert_items_equal([m.to_dict() for m in db_orders], [order2.to_dict()])


@pytest.mark.parametrize(
    'order_state, packages_state, package_changes, expected_order, expected_package',
    [
        (OrderState.NEW, (PackageState.NEW, PackageState.NEW), 2,
         OrderState.CANCELLED, (PackageState.CANCELLED, PackageState.CANCELLED)),
        (OrderState.EXPECTING_DELIVERY, (PackageState.READY_FOR_DELIVERY, PackageState.DELIVERED), 1,
         OrderState.CANCELLING, (PackageState.CANCELLING, PackageState.DELIVERED)),
        (OrderState.RECEIVED_PARTIALLY, (PackageState.EXPECTING_DELIVERY, PackageState.CANCELLED), 1,
         OrderState.CANCELLING, (PackageState.CANCELLING, PackageState.CANCELLED)),
        (OrderState.CANCELLING, (PackageState.CANCELLING, PackageState.CANCELLING), 2,
         OrderState.CANCELLED, (PackageState.CANCELLED, PackageState.CANCELLED)),
    ])
@pytest.mark.asyncio
async def test__cancel_order(order_state,
                             packages_state,
                             package_changes,
                             expected_order,
                             expected_package):
    order = await orders.factories.create(state=order_state)
    pack1 = await packages.factories.create(order_id=order.order_id, state=packages_state[0])
    pack2 = await packages.factories.create(order_id=order.order_id, state=packages_state[1])

    order, _ = await orders._cancel_order(order)
    package1 = await packages.get_by_package_id(pack1.package_id)
    package2 = await packages.get_by_package_id(pack2.package_id)
    order_history = await orders.get_all_history()
    package_history = await packages.get_all_history()
    assert len(order_history) == 1
    assert len(package_history) == package_changes
    assert order.state == expected_order
    assert package1.state == expected_package[0]
    assert package2.state == expected_package[1]


@pytest.mark.parametrize(
    'order_state, packages_state, package_changes, expected_exception, expected_order',
    [
        (OrderState.CANCELLING, (PackageState.CANCELLING, PackageState.CANCELLING), 2, False, OrderState.CANCELLED),
        (OrderState.CANCELLING, (PackageState.CANCELLING, PackageState.CANCELLED), 1, False, OrderState.CANCELLED),
        (OrderState.CANCELLING, (PackageState.CANCELLING, PackageState.DELIVERED), 1, False, OrderState.CANCELLED),
        (OrderState.CANCELLED, (PackageState.CANCELLED, PackageState.CANCELLED), 0, True, None),
        (OrderState.RECEIVED, (PackageState.IN_WAREHOUSE, PackageState.IN_WAREHOUSE), 0, True, None),
    ])
@pytest.mark.asyncio()
async def test_give_back_and_cancel(order_state, packages_state, package_changes, expected_exception, expected_order):
    order = await orders.factories.create(state=order_state)
    await packages.factories.create(order_id=order.order_id, state=packages_state[0])
    await packages.factories.create(order_id=order.order_id, state=packages_state[1])

    if expected_exception:
        with pytest.raises(orders.exceptions.OrderNotCancelling):
            await orders.give_back_and_cancel(order)
    else:
        order, _ = await orders.give_back_and_cancel(order)
        order_history = await orders.get_all_history()
        package_history = await packages.get_all_history()
        package_list = await packages.get_all()
        assert len(order_history) == 1
        assert len(package_history) == package_changes
        assert order.state == expected_order
        for package in package_list:
            assert package.state == PackageState.CANCELLED or not PackageState.is_active(package.state)


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio()
async def test_give_back_and_cancel_vacate_place():
    warehouse = await warehouses.factories.create()
    order = await orders.factories.create(state=OrderState.CANCELLING, warehouse_id=warehouse.warehouse_id)
    package1 = await packages.factories.create(order_id=order.order_id, state=packages.types.PackageState.CANCELLING)
    await packages.factories.create(order_id=order.order_id, state=packages.types.PackageState.DELIVERED)
    place1 = await package_places.factories.create(warehouse_id=order.warehouse_id,
                                                   package_id=package1.package_id,
                                                   state=package_places.types.PackagePlaceState.FILLED)
    place2 = await package_places.factories.create(warehouse_id=order.warehouse_id,
                                                   state=package_places.types.PackagePlaceState.FILLED)

    await orders.give_back_and_cancel(order)

    new_places = await package_places.get_all()
    new_place_history = await package_places.get_all_history()
    history = new_place_history[0]
    expected_new_place = {
        **place1.to_dict(),
        'updated_at': datetime_utils.get_now(),
        'state': package_places.types.PackagePlaceState.EMPTY,
        'package_id': None,
    }

    assert_items_equal([place.to_dict() for place in new_places],
                       [expected_new_place, place2.to_dict()])
    assert len(new_place_history) == 1
    assert history.to_dict() == expected_new_place


@pytest.mark.parametrize(
    'order_state, packages_state, package_changes, expected_exception, expected_order, expected_package',
    [
        (OrderState.NEW, (PackageState.NEW, PackageState.NEW), 2, False,
         OrderState.CANCELLED, (PackageState.CANCELLED, PackageState.CANCELLED)),
        (OrderState.RESERVED, (PackageState.RESERVED, PackageState.DELIVERED), 1, False,
         OrderState.CANCELLED, (PackageState.CANCELLED, PackageState.DELIVERED)),
        (OrderState.EXPECTING_DELIVERY, (PackageState.READY_FOR_DELIVERY, PackageState.DELIVERED), 1, False,
         OrderState.CANCELLING, (PackageState.CANCELLING, PackageState.DELIVERED)),
        (OrderState.RECEIVED_PARTIALLY, (PackageState.EXPECTING_DELIVERY, PackageState.CANCELLED), 1, False,
         OrderState.CANCELLING, (PackageState.CANCELLING, PackageState.CANCELLED)),
        (OrderState.DELIVERED_PARTIALLY, (PackageState.IN_WAREHOUSE, PackageState.ORDERED), 2, False,
         OrderState.CANCELLING, (PackageState.CANCELLING, PackageState.CANCELLED)),
        (OrderState.DELIVERING, (PackageState.DELIVERING, PackageState.DELIVERING), 2, False,
         OrderState.CANCELLING, (PackageState.CANCELLING, PackageState.CANCELLING)),
        (OrderState.CANCELLED, (PackageState.RESERVED, PackageState.DELIVERED), 0, True, None, []),
        (OrderState.DELIVERED, (PackageState.RESERVED, PackageState.DELIVERED), 0, True, None, []),
    ])
@pytest.mark.asyncio()
async def test_cancel_order(order_state,
                            packages_state,
                            package_changes,
                            expected_exception,
                            expected_order,
                            expected_package):
    order1 = await orders.factories.create(state=order_state)
    pack1 = await packages.factories.create(order_id=order1.order_id, state=packages_state[0])
    pack2 = await packages.factories.create(order_id=order1.order_id, state=packages_state[1])

    if expected_exception:
        with pytest.raises(orders.exceptions.OrderNotActive):
            await orders.cancel_order(order1)
    else:
        order1 = await orders.cancel_order(order1)
        package1 = await packages.get_by_package_id(pack1.package_id)
        package2 = await packages.get_by_package_id(pack2.package_id)
        order_history = await orders.get_all_history()
        package_history = await packages.get_all_history()
        assert len(order_history) == 1
        assert len(package_history) == package_changes
        assert order1.state == expected_order
        assert not PackageState.is_active(package1.state) or package1.state == expected_package[0]
        assert not PackageState.is_active(package2.state) or package2.state == expected_package[1]


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio()
async def test_cancel_order_with_vacate_place():
    warehouse = await warehouses.factories.create()
    order = await orders.factories.create(state=OrderState.DELIVERED_PARTIALLY, warehouse_id=warehouse.warehouse_id)
    order2 = await orders.factories.create(state=OrderState.DELIVERED_PARTIALLY, warehouse_id=warehouse.warehouse_id)
    package = await packages.factories.create(order_id=order.order_id, state=packages.types.PackageState.NEW)
    package2 = await packages.factories.create(order_id=order2.order_id, state=packages.types.PackageState.NEW)
    place1 = await package_places.factories.create(warehouse_id=order.warehouse_id,
                                                   package_id=package.package_id,
                                                   state=package_places.types.PackagePlaceState.FILLED,
                                                   )
    place2 = await package_places.factories.create(warehouse_id=order2.warehouse_id,
                                                   package_id=package2.package_id,
                                                   state=package_places.types.PackagePlaceState.FILLED,
                                                   )

    await orders.cancel_order(order)

    new_places = await package_places.get_all()
    new_place_history = await package_places.get_all_history()
    history = new_place_history[0]
    expected_new_place = {
        **place1.to_dict(),
        'updated_at': datetime_utils.get_now(),
        'state': package_places.types.PackagePlaceState.EMPTY,
        'package_id': None,
    }

    assert_items_equal([place.to_dict() for place in new_places],
                       [expected_new_place, place2.to_dict()])
    assert len(new_place_history) == 1
    assert history.to_dict() == expected_new_place


@pytest.mark.asyncio()
async def test_cancel_order_without_vacate_place():
    warehouse = await warehouses.factories.create()
    order = await orders.factories.create(state=OrderState.DELIVERED_PARTIALLY, warehouse_id=warehouse.warehouse_id)
    order2 = await orders.factories.create(state=OrderState.DELIVERING, warehouse_id=warehouse.warehouse_id)
    package = await packages.factories.create(order_id=order.order_id,
                                              state=packages.types.PackageState.IN_WAREHOUSE)
    package2 = await packages.factories.create(order_id=order2.order_id,
                                               state=packages.types.PackageState.DELIVERING)
    place1 = await package_places.factories.create(warehouse_id=order.warehouse_id,
                                                   package_id=package.package_id,
                                                   state=package_places.types.PackagePlaceState.FILLED,
                                                   )
    place2 = await package_places.factories.create(warehouse_id=order2.warehouse_id,
                                                   package_id=package2.package_id,
                                                   state=package_places.types.PackagePlaceState.FILLED,
                                                   )

    await orders.cancel_order(order)

    new_places = await package_places.get_all()
    new_place_history = await package_places.get_all_history()

    assert_items_equal([place.to_dict() for place in new_places],
                       [place1.to_dict(), place2.to_dict()])
    assert new_place_history == []


@pytest.mark.asyncio()
async def test_get_states_list_without_order():
    await orders.factories.create()

    results = await orders.get_states_list([generate_id()])

    assert results == []


@pytest.mark.asyncio()
async def test_get_states_list_without_package():
    warehouse = await warehouses.factories.create()
    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id)
    order_history = await orders.factories.create_history(**order.to_dict())
    order_event = orders.OrderEventResponse(
        **order_history.to_dict(), timestamp=order_history.updated_at)
    expected = orders.OrderHistoryWithPackagesResponse(
        **order.to_dict(), events=[order_event], items=[])

    results = await orders.get_states_list([order.order_id])

    assert results == [expected]


@pytest.mark.asyncio()
async def test_get_states_list_without_events():
    warehouse = await warehouses.factories.create()

    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id)
    await orders.factories.create()

    package = await packages.factories.create(order_id=order.order_id)

    package_response = packages.PackageWithHistoryResponse(
        **package.to_dict(), events=[])
    expected = orders.OrderHistoryWithPackagesResponse(
        **order.to_dict(), events=[], items=[package_response])

    results = await orders.get_states_list([order.order_id])

    assert results == [expected]


@pytest.mark.asyncio()
async def test_get_states_list_with_multiple_packages():
    warehouse = await warehouses.factories.create()

    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id)
    await orders.factories.create()

    package_list = [await packages.factories.create(order_id=order.order_id) for _ in range(3)]
    package_list.sort(key=lambda el: el.package_id)

    package_response_list = [
        packages.PackageWithHistoryResponse(**package.to_dict(), events=[])
        for package in package_list
    ]
    expected = orders.OrderHistoryWithPackagesResponse(
        **order.to_dict(), events=[], items=package_response_list)

    results = await orders.get_states_list([order.order_id])

    assert results == [expected]


@pytest.mark.asyncio()
async def test_get_states_list_with_multiple_order_events():
    warehouse = await warehouses.factories.create()

    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id, updated_at=3)
    await orders.factories.create()

    package = await packages.factories.create(order_id=order.order_id)
    package_response = packages.PackageWithHistoryResponse(
        **package.to_dict(), events=[])
    await packages.factories.create()

    order_events = []
    history = order.to_dict()
    for upd in range(3, 0, -1):
        history['updated_at'] = upd
        order_history = await orders.factories.create_history(**history)
        event = orders.OrderEventResponse(
            **order_history.to_dict(), timestamp=order_history.updated_at)
        order_events.insert(0, event)

    expected = orders.OrderHistoryWithPackagesResponse(
        **order.to_dict(),
        events=order_events,
        items=[package_response]
    )

    results = await orders.get_states_list([order.order_id])

    assert results == [expected]


@pytest.mark.asyncio()
async def test_get_states_list_with_multiple_package_events():
    warehouse = await warehouses.factories.create()

    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id, updated_at=3)
    await orders.factories.create()

    package = await packages.factories.create(order_id=order.order_id)
    package_response = packages.PackageWithHistoryResponse(
        **package.to_dict(), events=[])
    await packages.factories.create()

    history = package.to_dict()
    for upd in range(3, 0, -1):
        history['updated_at'] = upd
        package_history = await packages.factories.create_history(**history)
        event = orders.OrderEventResponse(
            **package_history.to_dict(), timestamp=package_history.updated_at)
        package_response.events.insert(0, event)

    expected = orders.OrderHistoryWithPackagesResponse(
        **order.to_dict(),
        events=[],
        items=[package_response]
    )

    results = await orders.get_states_list([order.order_id])

    assert results == [expected]


@pytest.mark.asyncio()
async def test_update_to_delivery_with_history():
    order = await orders.factories.create(state=orders.types.OrderState.RECEIVED)
    now = datetime_utils.get_now()
    await orders.update_to_delivery(order_id=order.order_id, updated_at=now)

    new_order = await orders.get_by_order_id(order_id=order.order_id)
    order_history = await orders.get_all_history()

    assert new_order.to_dict() == {
        **order.to_dict(),
        'state': orders.types.OrderState.DELIVERING,
        'updated_at': now
    }
    assert len(order_history) == 1
    assert order_history[0].to_dict() == new_order.to_dict()


@pytest.mark.asyncio()
async def test_update_to_delivery_without_history():
    order = await orders.factories.create(state=orders.types.OrderState.RECEIVED)
    now = datetime_utils.get_now()
    await orders.update_to_delivery(order_id=order.order_id, updated_at=now, with_history=False)

    new_order = await orders.get_by_order_id(order_id=order.order_id)
    order_history = await orders.get_all_history()

    assert new_order.to_dict() == {
        **order.to_dict(),
        'state': orders.types.OrderState.DELIVERING,
        'updated_at': now
    }
    assert len(order_history) == 0


@pytest.mark.asyncio()
async def test_update_to_delivery_raise_not_found():
    order_id = generate_id()
    now = datetime_utils.get_now()

    with pytest.raises(orders.exceptions.OrderNotFoundError):
        await orders.update_to_delivery(order_id=order_id, updated_at=now)


@pytest.mark.asyncio()
async def test_update_to_delivery_not_on_warehouse():
    order = await orders.factories.create()
    now = datetime_utils.get_now()

    with pytest.raises(orders.exceptions.OrderNotFoundError):
        await orders.update_to_delivery(order_id=order.order_id, updated_at=now)


@pytest.mark.asyncio()
async def test_update_to_delivery_without_raise_not_found():
    order_id = generate_id()
    now = datetime_utils.get_now()
    order = await orders.update_to_delivery(order_id=order_id, updated_at=now, raise_not_found=False)

    assert order is None


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_update_order():
    order = await orders.factories.create()
    updated_order = await orders.update_order(
        order_id=order.order_id,
        delivery_date=datetime_utils.get_now(),
        customer_meta={},
    )

    expected_order = orders.factories.build(
        order_id=order.order_id,
        delivery_date=datetime.datetime(
            2020, 1, 2, 0, 4, 5, tzinfo=datetime.timezone.utc
        ),
        external_order_id=updated_order.external_order_id,
        customer_meta={},
        customer_uid=updated_order.customer_uid,
        updated_at=datetime.datetime(
            2020, 1, 2, 0, 4, 5, tzinfo=datetime.timezone.utc
        ),
    )

    assert updated_order.to_response() == expected_order.to_response()

    order_list = await orders.get_all()
    assert len(order_list) == 1
    assert order_list[0].to_response() == updated_order.to_response()

    db_history = await orders.get_all_history()
    assert len(db_history) == 1


@pytest.mark.asyncio
async def test_get_all_info_by_order_id():
    warehouse = await warehouses.factories.create()
    order1 = await orders.factories.create(warehouse_id=warehouse.warehouse_id)
    order2 = await orders.factories.create(warehouse_id=warehouse.warehouse_id)
    package1 = await packages.factories.create(order_id=order1.order_id)
    package2 = await packages.factories.create(order_id=order2.order_id)
    package_place1 = await package_places.factories.create(
        warehouse_id=warehouse.warehouse_id,
        package_id=package1.package_id,
    )
    await package_places.factories.create(
        warehouse_id=warehouse.warehouse_id,
        package_id=package2.package_id,
    )

    info = await orders.get_all_info_by_order_id(order_id=order1.order_id)
    expected_info = {
        **order1.to_dict(),
        **package1.to_dict(),
        **package_place1.to_dict(),
    }

    assert info == expected_info


@pytest.mark.asyncio
async def test_get_all_info_by_non_existent_order_id():
    await orders.factories.create()

    with pytest.raises(orders.exceptions.OrderNotFoundError):
        await orders.get_all_info_by_order_id(generate_id())


@pytest.mark.asyncio
async def test_get_all_info_with_non_existent_package():
    order = await orders.factories.create()
    info = await orders.get_all_info_by_order_id(order_id=order.order_id)
    assert info == {**order.to_dict(), 'package_id': None}


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_all_picking_up_by_warehouse_id():
    now = datetime_utils.get_now()
    delta_20m = datetime.timedelta(minutes=20)
    delta_10m = datetime.timedelta(minutes=10)
    delta_5m = datetime.timedelta(minutes=5)

    warehouse = await warehouses.factories.create()
    order1 = await orders.factories.create(warehouse_id=warehouse.warehouse_id,
                                           state=orders.types.OrderState.RECEIVED,)
    order2 = await orders.factories.create(warehouse_id=warehouse.warehouse_id,
                                           state=orders.types.OrderState.RECEIVED)
    await courier_order_stages.factories.create(
        order_id=order1.order_id,
        effective_time=now - delta_20m,
        type_=courier_order_stages.types.CourierOrderStageType.NEW
    )
    await courier_order_stages.factories.create(
        order_id=order1.order_id,
        effective_time=now - delta_10m,
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED
    )
    await courier_order_stages.factories.create(
        order_id=order2.order_id,
        effective_time=now - delta_10m,
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN
    )
    await courier_order_stages.factories.create(
        order_id=order2.order_id,
        effective_time=now - delta_5m,
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_CLOSED
    )

    result = await orders.get_all_picking_up_by_warehouse_id(warehouse_id=warehouse.warehouse_id, now=now)

    assert result


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_all_picking_up_by_warehouse_id_not_found():
    now = datetime_utils.get_now()
    delta_20m = datetime.timedelta(minutes=20)
    delta_10m = datetime.timedelta(minutes=10)
    delta_5m = datetime.timedelta(minutes=5)

    warehouse = await warehouses.factories.create()
    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id,
                                          state=orders.types.OrderState.DELIVERED_PARTIALLY)
    await courier_order_stages.factories.create(
        order_id=order.order_id,
        effective_time=now - delta_20m,
        type_=courier_order_stages.types.CourierOrderStageType.NEW
    )
    await courier_order_stages.factories.create(
        order_id=order.order_id,
        effective_time=now - delta_10m,
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED
    )
    await courier_order_stages.factories.create(
        order_id=order.order_id,
        effective_time=now - delta_5m,
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_CLOSED
    )

    result = await orders.get_all_picking_up_by_warehouse_id(warehouse_id=warehouse.warehouse_id, now=now)

    assert not result


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_all_picking_up_by_warehouse_id_few_found():
    now = datetime_utils.get_now()
    delta_20m = datetime.timedelta(minutes=20)
    delta_10m = datetime.timedelta(minutes=10)
    delta_5m = datetime.timedelta(minutes=5)

    warehouse = await warehouses.factories.create()

    order1 = await orders.factories.create(warehouse_id=warehouse.warehouse_id,
                                           state=orders.types.OrderState.RECEIVED)
    order2 = await orders.factories.create(warehouse_id=warehouse.warehouse_id,
                                           state=orders.types.OrderState.RECEIVED)

    await courier_order_stages.factories.create(
        order_id=order1.order_id,
        effective_time=now - delta_20m,
        type_=courier_order_stages.types.CourierOrderStageType.NEW
    )
    await courier_order_stages.factories.create(
        order_id=order1.order_id,
        effective_time=now - delta_10m,
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED
    )
    await courier_order_stages.factories.create(
        order_id=order2.order_id,
        effective_time=now - delta_5m,
        type_=courier_order_stages.types.CourierOrderStageType.PACKAGE_TAKEN
    )

    result = await orders.get_all_picking_up_by_warehouse_id(warehouse_id=warehouse.warehouse_id, now=now)

    assert result


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_all_picking_up_by_warehouse_id_order_not_on_warehouse():
    now = datetime_utils.get_now()
    delta_20m = datetime.timedelta(minutes=20)
    delta_10m = datetime.timedelta(minutes=10)

    warehouse = await warehouses.factories.create()
    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id,
                                          state=orders.types.OrderState.DELIVERED)
    await courier_order_stages.factories.create(
        order_id=order.order_id,
        effective_time=now - delta_20m,
        type_=courier_order_stages.types.CourierOrderStageType.NEW
    )
    await courier_order_stages.factories.create(
        order_id=order.order_id,
        effective_time=now - delta_10m,
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_OPENED
    )

    result = await orders.get_all_picking_up_by_warehouse_id(warehouse_id=warehouse.warehouse_id, now=now)

    assert not result


@pytest.mark.parametrize('order_filters, package_filters', [
    ({'external_system': 'LP', 'external_order_id': 'abcd'}, {}),
    ({'warehouse_id': '68a4144a-1b05-45cb-af80-c556acb6a578'}, {}),
    ({}, {'barcode': '1234'}),
])
@pytest.mark.asyncio
async def test_get_paginated_orders_with_filters(order_filters, package_filters):
    await warehouses.factories.create(warehouse_id=order_filters.get('warehouse_id'))
    order_list = [await orders.factories.create(**order_filters) for i in range(2)]
    order_list.sort(key=lambda el: el.order_id)
    order3 = await orders.factories.create()

    for order in order_list:
        await packages.factories.create(order_id=order.order_id, **package_filters)

    await packages.factories.create(order_id=order3.order_id)

    result = (await orders.get_paginated_orders(order_filters, package_filters)).orders
    expected_result = [orders.OrderResponse(**order.to_dict()) for order in order_list]

    assert result == expected_result


@pytest.mark.asyncio
async def test_get_paginated_orders_filter_by_order_id():
    order1 = await orders.factories.create()
    order2 = await orders.factories.create(order_id=order1.order_id[:-4] + '1234')
    await orders.factories.create()

    order_list = sorted([order1, order2], key=lambda el: el.order_id)
    expected_result = [orders.OrderResponse(**order.to_dict()) for order in order_list]

    result = (await orders.get_paginated_orders({'order_id': order1.order_id[:-5]})).orders

    assert result == expected_result


@pytest.mark.asyncio
async def test_get_paginated_orders_filter_by_package_id():
    order_list = sorted([await orders.factories.create() for _ in range(2)], key=lambda el: el.order_id)
    order3 = await orders.factories.create()

    package1 = await packages.factories.create(order_id=order_list[0].order_id)
    await packages.factories.create(package_id=package1.package_id[:-4] + '1234',
                                    order_id=order_list[1].order_id)
    await packages.factories.create(order_id=order3.order_id)

    expected_result = [orders.OrderResponse(**order.to_dict()) for order in order_list]

    result = (await orders.get_paginated_orders(package_filters={'package_id': package1.package_id[:-5]})).orders

    assert result == expected_result


@pytest.mark.parametrize('newer_than, start, expected_n_t, expected_o_t', [
    (None, 0, 2, None),
    (2, 3, 5, 3),
    (5, 6, None, 6),
])
@pytest.mark.asyncio
async def test_get_paginated_orders_forward(newer_than, start, expected_n_t, expected_o_t):
    order_list = sorted([await orders.factories.create() for _ in range(7)], key=lambda el: el.order_id)
    limit = 3

    expexted_orders = [orders.OrderResponse(**order.to_dict()) for order in order_list]
    expexted_orders = expexted_orders[start:start + limit]
    expected_n_t = expected_n_t and base64_encode(order_list[expected_n_t].order_id)
    expected_o_t = expected_o_t and base64_encode(order_list[expected_o_t].order_id)

    newer_than = newer_than and base64_encode(order_list[newer_than].order_id)

    result = await orders.get_paginated_orders({}, {}, newer_than=newer_than, limit=limit)

    assert result.newer_than == expected_n_t
    assert result.older_than == expected_o_t
    assert result.orders == expexted_orders


@pytest.mark.parametrize('older_than, start, end, expected_n_t, expected_o_t', [
    (5, 2, 5, 4, 2),
    (2, 0, 2, 1, None),
])
@pytest.mark.asyncio
async def test_get_paginated_orders_backward(older_than, start, end, expected_n_t, expected_o_t):
    order_list = sorted([await orders.factories.create() for _ in range(6)], key=lambda el: el.order_id)
    limit = 3

    expexted_orders = [orders.OrderResponse(**order.to_dict()) for order in order_list]
    expexted_orders = expexted_orders[start:end]
    expected_n_t = expected_n_t and base64_encode(order_list[expected_n_t].order_id)
    expected_o_t = expected_o_t and base64_encode(order_list[expected_o_t].order_id)

    older_than = older_than and base64_encode(order_list[older_than].order_id)

    result = await orders.get_paginated_orders({}, {}, older_than=older_than, limit=limit)

    assert result.newer_than == expected_n_t
    assert result.older_than == expected_o_t
    assert result.orders == expexted_orders


@pytest.mark.asyncio
async def test_get_paginated_without_orders():
    result = await orders.get_paginated_orders()

    assert result.newer_than is None
    assert result.older_than is None
    assert result.orders == []


@pytest.mark.asyncio
async def test_get_full_by_order_id_not_found():
    order_id = generate_id()

    with pytest.raises(orders.exceptions.OrderNotFoundError):
        await orders.get_full_by_order_id(order_id)


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_full_by_order():
    now = datetime_utils.get_now()
    delta_20m = datetime.timedelta(minutes=20)
    delta_10m = datetime.timedelta(minutes=10)

    order = await orders.factories.create()
    package = await packages.factories.create(order_id=order.order_id)
    place = await package_places.factories.create(package_id=package.package_id)
    stage = await courier_order_stages.factories.create(order_id=order.order_id, effective_time=now - delta_10m)
    await courier_order_stages.factories.create(order_id=order.order_id, effective_time=now - delta_20m)
    await courier_order_stages.factories.create(order_id=order.order_id)

    result = await orders.get_full_by_order_id(order.order_id)

    expected = orders.AdminOrderResponse(
        **order.to_dict(),
        packages=[packages.PackageResponse(**package.to_dict())],
        package_places=[package_places.PackagePlaceResponse(**place.to_dict())],
        courier_order_stage=courier_order_stages.CourierOrderStageResponse(**stage.to_dict())
    )

    assert result == expected


@pytest.mark.asyncio
async def test_get_merged_history_empty_list():
    result = await orders.get_merged_history(generate_id())

    assert result == []


@pytest.mark.asyncio
async def test_update_to_delivered_by_order_id_not_found():
    with pytest.raises(orders.exceptions.OrderNotFoundError):
        await orders.update_to_delivered_by_order_id(generate_id())


@pytest.mark.asyncio
async def test_update_to_delivered_by_order_id_order_not_delivering():
    order = await orders.factories.create()

    with pytest.raises(orders.exceptions.OrderNotFoundError):
        await orders.update_to_delivered_by_order_id(order.order_id)


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_merged_history():
    now = datetime_utils.get_now()
    delta_30m = datetime.timedelta(minutes=30)
    delta_20m = datetime.timedelta(minutes=20)
    delta_10m = datetime.timedelta(minutes=10)

    order = await orders.factories.create()
    await orders.factories.create_history()
    await packages.factories.create_history()

    order_history1 = await orders.factories.create_history(order_id=order.order_id,
                                                           updated_at=now - delta_30m,
                                                           state=orders.types.OrderState.NEW)
    package_history1 = await packages.factories.create_history(updated_at=now - delta_30m,
                                                               order_id=order_history1.order_id,
                                                               state=packages.types.PackageState.NEW)
    order_history2 = await orders.factories.create_history(updated_at=now - delta_20m,
                                                           order_id=order_history1.order_id,
                                                           state=orders.types.OrderState.RECEIVED)
    package_history2 = await packages.factories.create_history(updated_at=now - delta_20m,
                                                               order_id=order_history1.order_id,
                                                               package_id=package_history1.package_id,
                                                               state=packages.types.PackageState.IN_WAREHOUSE)
    stage1 = await courier_order_stages.factories.create(order_id=order_history1.order_id,
                                                         effective_time=now - delta_20m,
                                                         type_=courier_order_stages.types.CourierOrderStageType.NEW)
    stage2 = await courier_order_stages.factories.create(
        order_id=order_history1.order_id,
        effective_time=now - delta_10m,
        type_=courier_order_stages.types.CourierOrderStageType.WAREHOUSE_CLOSED
    )
    order_history3 = await orders.factories.create_history(updated_at=now - delta_10m,
                                                           order_id=order_history1.order_id,
                                                           state=orders.types.OrderState.DELIVERING)
    package_history3 = await packages.factories.create_history(updated_at=now - delta_10m,
                                                               order_id=order_history1.order_id,
                                                               package_id=package_history1.package_id,
                                                               state=packages.types.PackageState.DELIVERING)

    get_params_from_order = lambda order: {
        'updated_at': order.updated_at,
        'state': order.state,
        'state_meta': order.state_meta,
        'delivery_date': order.delivery_date,
        'order_id': order.order_id,
        'model': 'Order',
        'metadata': orders.HistoryMetaDataResponse(**{
            'external_system': order.external_system,
            'external_order_id': order.external_order_id,
            'warehouse_id': order.warehouse_id,
            'customer_address': order.customer_address,
            'customer_location': order.customer_location,
            'customer_meta': order.customer_meta,
            'customer_phone': order.customer_phone,
            'customer_uid': order.customer_uid,
        }),
    }

    get_params_from_package = lambda package: {
        'updated_at': package.updated_at,
        'state': package.state,
        'state_meta': package.state_meta,
        'barcode': package.barcode,
        'order_id': package.order_id,
        'package_id': package.package_id,
        'model': 'Package',
        'metadata': orders.HistoryMetaDataResponse(**{
            'description': package.description,
            'measurements': package.measurements,
        }),
    }

    get_params_from_stage = lambda stage: {
        'updated_at': stage.effective_time,
        'state': stage.type,
        'state_meta': stage.type_meta,
        'courier_id': stage.courier_id,
        'order_id': stage.order_id,
        'model': 'CourierOrderStage',
    }

    expected = [
        orders.AdminHistoryResponse(**get_params_from_order(order_history1)),
        orders.AdminHistoryResponse(**get_params_from_package(package_history1)),
        orders.AdminHistoryResponse(**get_params_from_order(order_history2)),
        orders.AdminHistoryResponse(**get_params_from_package(package_history2)),
        orders.AdminHistoryResponse(**get_params_from_stage(stage1)),
        orders.AdminHistoryResponse(**get_params_from_order(order_history3)),
        orders.AdminHistoryResponse(**get_params_from_package(package_history3)),
        orders.AdminHistoryResponse(**get_params_from_stage(stage2)),
    ]

    result = await orders.get_merged_history(order_history1.order_id)
    assert result == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.parametrize('state, package_state', [
    (orders.types.OrderState.RECEIVED, packages.types.PackageState.IN_WAREHOUSE),
    (orders.types.OrderState.DELIVERING, packages.types.PackageState.DELIVERING),
])
@pytest.mark.asyncio
async def test_update_to_delivered_by_order_id(state, package_state):
    now = datetime_utils.get_now()

    order1 = await orders.factories.create(state=state)
    package1_1 = await packages.factories.create(state=package_state, order_id=order1.order_id)
    package1_2 = await packages.factories.create(state=package_state, order_id=order1.order_id)
    place1_1 = await package_places.factories.create(package_id=package1_1.package_id,
                                                     state=package_places.types.PackagePlaceState.FILLED)
    place1_2 = await package_places.factories.create(package_id=package1_2.package_id,
                                                     state=package_places.types.PackagePlaceState.FILLED)
    order2 = await orders.factories.create()
    package2_1 = await packages.factories.create(order_id=order2.order_id)
    place2_1 = await package_places.factories.create(package_id=package2_1.package_id,
                                                     state=package_places.types.PackagePlaceState.FILLED)

    await orders.update_to_delivered_by_order_id(order_id=order1.order_id, updated_at=now)

    new_order = await orders.get_by_order_id(order_id=order1.order_id)
    new_package1 = await packages.get_by_package_id(package1_1.package_id)
    new_package2 = await packages.get_by_package_id(package1_2.package_id)
    new_places = await package_places.get_all()

    order_history = await orders.get_all_history()
    package_history = await packages.get_all_history()
    place_history = await package_places.get_all_history()

    assert new_order.to_dict() == {**order1.to_dict(),
                                   'state': orders.types.OrderState.DELIVERED,
                                   'updated_at': now,
                                   'delivery_date': now}
    assert new_package1.to_dict() == {**package1_1.to_dict(),
                                      'state': packages.types.PackageState.DELIVERED,
                                      'updated_at': now}
    assert new_package2.to_dict() == {**package1_2.to_dict(),
                                      'state': packages.types.PackageState.DELIVERED,
                                      'updated_at': now}
    expected_places = [
        place2_1.to_dict(),
        {
            **place1_1.to_dict(),
            'package_id': None,
            'state': package_places.types.PackagePlaceState.EMPTY,
            'updated_at': now
        },
        {
            **place1_2.to_dict(),
            'package_id': None,
            'state': package_places.types.PackagePlaceState.EMPTY,
            'updated_at': now
        },
    ]
    assert_items_equal([place.to_dict() for place in new_places], expected_places)

    assert order_history[0].to_dict() == new_order.to_dict()
    assert_items_equal([package.to_dict() for package in package_history],
                       [new_package1.to_dict(), new_package2.to_dict()])
    assert_items_equal([place.to_dict() for place in place_history],
                       [place for place in expected_places[1:]])


@pytest.mark.asyncio
async def test_receive_order_by_order_id_already_receive_error():
    order = await orders.factories.create(state=orders.types.OrderState.DELIVERING)
    await packages.factories.create(order_id=order.order_id)

    with pytest.raises(orders.exceptions.OrderAlreadyReceived):
        await orders.receive_order_by_order_id(order.order_id)


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_receive_order_by_order_id():
    now = datetime_utils.get_now()

    order = await orders.factories.create()
    order2 = await orders.factories.create()
    package = await packages.factories.create(order_id=order.order_id)
    package2 = await packages.factories.create(order_id=order2.order_id)

    await orders.receive_order_by_order_id(order.order_id, now)

    new_order = await orders.get_by_order_id(order.order_id)
    not_changed_order = await orders.get_by_order_id(order2.order_id)
    new_package = await packages.get_by_package_id(package.package_id)
    not_changed_package = await packages.get_by_package_id(package2.package_id)
    order_history = await orders.get_all_history()
    package_history = await packages.get_all_history()
    order_history = [history.to_dict() for history in order_history]
    package_history = [history.to_dict() for history in package_history]

    assert new_order.to_dict() == {**order.to_dict(),
                                   'updated_at': now,
                                   'state': orders.types.OrderState.RECEIVED}
    assert new_package.to_dict() == {**package.to_dict(),
                                     'updated_at': now,
                                     'state': packages.types.PackageState.IN_WAREHOUSE}
    assert not_changed_order.to_dict() == order2.to_dict()
    assert not_changed_package.to_dict() == package2.to_dict()
    assert order_history == [new_order.to_dict()]
    assert package_history == [new_package.to_dict()]


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_receive_order_by_barcode():
    now = datetime_utils.get_now()

    warehouse = await warehouses.factories.create()
    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id)
    order2 = await orders.factories.create(warehouse_id=warehouse.warehouse_id)
    package = await packages.factories.create(order_id=order.order_id, barcode='1234')
    package2 = await packages.factories.create(order_id=order2.order_id, barcode='12345')
    await package_places.factories.create(warehouse_id=warehouse.warehouse_id,
                                          package_id=package.package_id)

    await orders.receive_order_by_barcode(package.barcode, warehouse.warehouse_id, now)

    new_order = await orders.get_by_order_id(order.order_id)
    not_changed_order = await orders.get_by_order_id(order2.order_id)
    new_package = await packages.get_by_package_id(package.package_id)
    not_changed_package = await packages.get_by_package_id(package2.package_id)
    order_history = await orders.get_all_history()
    package_history = await packages.get_all_history()
    order_history = [history.to_dict() for history in order_history]
    package_history = [history.to_dict() for history in package_history]

    assert new_order.to_dict() == {**order.to_dict(),
                                   'updated_at': now,
                                   'state': orders.types.OrderState.RECEIVED}
    assert new_package.to_dict() == {**package.to_dict(),
                                     'updated_at': now,
                                     'state': packages.types.PackageState.IN_WAREHOUSE}
    assert not_changed_order.to_dict() == order2.to_dict()
    assert not_changed_package.to_dict() == package2.to_dict()
    assert order_history == [new_order.to_dict()]
    assert package_history == [new_package.to_dict()]
