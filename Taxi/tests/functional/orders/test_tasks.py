import datetime
import freezegun
import pytest

from taxi.robowarehouse.lib.concepts import orders
from taxi.robowarehouse.lib.concepts import packages
from taxi.robowarehouse.lib.concepts import package_places
from taxi.robowarehouse.lib.concepts import warehouses
from taxi.robowarehouse.lib.misc import datetime_utils
from taxi.robowarehouse.lib.test_utils.helpers import assert_items_equal


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_cancel_testing_orders():
    deltas = [datetime.timedelta(days=n) for n in range(1, 5)]
    now = datetime_utils.get_now()
    order_states = [
        orders.types.OrderState.NEW,
        orders.types.OrderState.NEW,
        orders.types.OrderState.NEW,
        orders.types.OrderState.NEW,
    ]
    package_satate = [
        packages.types.PackageState.NEW,
        packages.types.PackageState.NEW,
        packages.types.PackageState.NEW,
        packages.types.PackageState.NEW,
    ]

    warehouse = await warehouses.factories.create()

    orders_list = []
    packages_list = []
    places = []

    for o_sate, p_state, delta, created_at in zip(order_states, package_satate, deltas, range(1, 5)):
        order = await orders.factories.create(
            warehouse_id=warehouse.warehouse_id,
            state=o_sate,
            delivery_date=now - delta,
            created_at=created_at,
        )
        package = await packages.factories.create(
            order_id=order.order_id,
            state=p_state,
            created_at=created_at,
        )
        place = await package_places.factories.create(
            package_id=package.package_id,
            warehouse_id=warehouse.warehouse_id,
            state=package_places.types.PackagePlaceState.FILLED,
            created_at=created_at,
        )
        orders_list.append(order), packages_list.append(package), places.append(place)

    await orders.tasks.cancel_testing_orders(2)

    result_orders = sorted(await orders.get_all(), key=lambda el: el.created_at)
    result_orders_history = sorted(await orders.get_all_history(), key=lambda el: el.created_at)
    result_packages = sorted(await packages.get_all(), key=lambda el: el.created_at)
    result_packages_history = sorted(await packages.get_all_history(), key=lambda el: el.created_at)
    result_places = sorted(await package_places.get_all(), key=lambda el: el.created_at)
    result_places_history = sorted(await package_places.get_all_history(), key=lambda el: el.created_at)
    expected_orders = [
        {
            **order.to_dict(),
            'updated_at': now,
            'state': orders.types.OrderState.CANCELLED,
            'state_meta': {'reason': 'auto_cancelling'},
        }
        for order in orders_list[1:]
    ]
    expected_packages = [
        {
            **package.to_dict(),
            'updated_at': now,
            'state': packages.types.PackageState.CANCELLED,
            'state_meta': {'reason': 'auto_cancelling'},
        }
        for package in packages_list[1:]
    ]
    expected_places = [
        {
            **place.to_dict(),
            'updated_at': now,
            'state': package_places.types.PackagePlaceState.EMPTY,
            'package_id': None
        }
        for place in places[1:]
    ]

    assert len(result_orders_history) == 3
    assert len(result_packages_history) == 3
    assert len(result_places_history) == 3

    assert result_orders[0].to_dict() == orders_list[0].to_dict()
    assert result_packages[0].to_dict() == packages_list[0].to_dict()
    assert result_places[0].to_dict() == places[0].to_dict()

    assert_items_equal([o.to_dict() for o in result_orders[1:]], expected_orders)
    assert_items_equal([o_h.to_dict() for o_h in result_orders_history], expected_orders)
    assert_items_equal([p.to_dict() for p in result_packages[1:]], expected_packages)
    assert_items_equal([p_h.to_dict() for p_h in result_packages_history], expected_packages)
    assert_items_equal([pp.to_dict() for pp in result_places[1:]], expected_places)
    assert_items_equal([pp_h.to_dict() for pp_h in result_places_history], expected_places)


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_cancel_testing_orders_other_state():
    delta_2d = datetime.timedelta(days=2)
    delta_3d = datetime.timedelta(days=3)
    now = datetime_utils.get_now()

    warehouse = await warehouses.factories.create()

    orders_list = []
    packages_list = []
    places = []

    for delta, created_at in zip((delta_2d, delta_3d), (2, 3)):
        order = await orders.factories.create(
            warehouse_id=warehouse.warehouse_id,
            state=orders.types.OrderState.RECEIVED,
            delivery_date=now - delta,
            created_at=created_at,
        )
        package = await packages.factories.create(
            order_id=order.order_id,
            state=packages.types.PackageState.IN_WAREHOUSE,
            created_at=created_at,
        )
        place = await package_places.factories.create(
            warehouse_id=warehouse.warehouse_id,
            state=package_places.types.PackagePlaceState.FILLED,
            package_id=package.package_id,
            created_at=created_at,
        )
        orders_list.append(order), packages_list.append(package), places.append(place)

    await orders.tasks.cancel_testing_orders(2)

    result_orders = sorted(await orders.get_all(), key=lambda el: el.created_at)
    result_orders_history = sorted(await orders.get_all_history(), key=lambda el: el.created_at)
    result_packages = sorted(await packages.get_all(), key=lambda el: el.created_at)
    result_packages_history = sorted(await packages.get_all_history(), key=lambda el: el.created_at)
    result_places = sorted(await package_places.get_all(), key=lambda el: el.created_at)
    result_places_history = sorted(await package_places.get_all_history(), key=lambda el: el.created_at)

    expected_orders = [o.to_dict() for o in orders_list]
    expected_packages = [p.to_dict() for p in packages_list]
    expected_places = [pp.to_dict() for pp in places]

    assert len(result_orders_history) == 0
    assert len(result_packages_history) == 0
    assert len(result_places_history) == 0

    assert_items_equal([o.to_dict() for o in result_orders], expected_orders)
    assert_items_equal([p.to_dict() for p in result_packages], expected_packages)
    assert_items_equal([pp.to_dict() for pp in result_places], expected_places)
