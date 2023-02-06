import datetime
import freezegun
import pytest
from sqlalchemy.exc import IntegrityError

from taxi.robowarehouse.lib.concepts import measurements
from taxi.robowarehouse.lib.concepts import orders
from taxi.robowarehouse.lib.concepts import packages
from taxi.robowarehouse.lib.concepts import package_places
from taxi.robowarehouse.lib.concepts import warehouses
from taxi.robowarehouse.lib.misc import datetime_utils
from taxi.robowarehouse.lib.misc.helpers import generate_id
from taxi.robowarehouse.lib.test_utils.helpers import assert_items_equal


@pytest.mark.asyncio
async def test_get_all_empty():
    result = await packages.get_all()

    assert result == []


@pytest.mark.asyncio
async def test_get_all():
    package1 = await packages.factories.create()
    package2 = await packages.factories.create()

    result = await packages.get_all()

    assert_items_equal([r.to_response() for r in result], [
                       package1.to_response(), package2.to_response()])


@pytest.mark.asyncio
async def test_get_by_package_id_not_found():
    package_id = generate_id()

    with pytest.raises(packages.exceptions.PackageNotFoundError):
        await packages.get_by_package_id(package_id)


@pytest.mark.asyncio
async def test_get_by_package_id():
    package1 = await packages.factories.create()
    await packages.factories.create()

    result = await packages.get_by_package_id(package1.package_id)

    assert result.to_dict() == package1.to_dict()


@pytest.mark.asyncio
async def test_get_all_history_empty():
    result = await packages.get_all_history()

    assert result == []


@pytest.mark.asyncio
async def test_get_all_history():
    package1 = await packages.factories.create_history()
    package2 = await packages.factories.create_history()

    result = await packages.get_all_history()

    assert_items_equal([r.to_response() for r in result], [
                       package1.to_response(), package2.to_response()])


@pytest.mark.asyncio
async def test_create():
    package1 = await packages.factories.create()
    package2 = packages.factories.build(order_id=package1.order_id)

    result = await packages.create(packages.CreatePackageRequest.from_orm(package2))

    assert result.to_response() == package2.to_response()

    db_packages = await packages.get_all()
    assert_items_equal([m.to_response() for m in db_packages], [
                       package1.to_response(), package2.to_response()])

    db_history = await packages.get_all_history()
    assert_items_equal([m.to_response() for m in db_history], [
                       packages.PackageHistoryResponse(**package2.to_dict())])


@pytest.mark.asyncio
async def test_create_no_order():
    order_id = generate_id()
    package1 = packages.factories.build(order_id=order_id)

    with pytest.raises(IntegrityError) as e:
        await packages.create(packages.CreatePackageRequest.from_orm(package1))

    assert f'Key (order_id)=({order_id}) is not present in table "orders".' in str(
        e.value)

    db_packages = await packages.get_all()
    assert db_packages == []


@pytest.mark.asyncio
async def test_create_without_history():
    package1 = await packages.factories.create()
    package2 = packages.factories.build(order_id=package1.order_id)

    result = await packages.create(packages.CreatePackageRequest.from_orm(package2), with_history=False)

    assert result.to_response() == package2.to_response()

    db_packages = await packages.get_all()
    assert_items_equal([m.to_response() for m in db_packages], [
                       package1.to_response(), package2.to_response()])

    db_history = await packages.get_all_history()
    assert db_history == []


@pytest.mark.asyncio
async def test_get_package_on_warehouse_by_id_not_found():
    package_id = generate_id()
    order_id = generate_id()

    with pytest.raises(packages.exceptions.PackageNotFoundError):
        await packages.get_package_on_warehouse_by_id(package_id, order_id)


@pytest.mark.asyncio
async def test_get_package_on_warehouse_by_id_not_on_warehouse_error():
    package = await packages.factories.create()

    with pytest.raises(packages.exceptions.PackageNotOnWarehouse):
        await packages.get_package_on_warehouse_by_id(package.package_id, package.order_id)


@pytest.mark.asyncio
async def test_get_package_on_warehouse_by_id():
    package = await packages.factories.create(state=packages.types.PackageState.IN_WAREHOUSE)

    result = await packages.get_package_on_warehouse_by_id(package.package_id, package.order_id)

    assert package.to_response() == result.to_response()


@pytest.mark.asyncio()
async def test_update_to_delivery_with_history_with_single_package():
    package = await packages.factories.create(state=packages.types.PackageState.IN_WAREHOUSE)
    now = datetime_utils.get_now()
    await packages.update_to_delivery(order_id=package.order_id, updated_at=now)

    new_package = (await packages.list_by_order_id(order_id=package.order_id))[0]
    package_history = await packages.get_all_history()

    assert new_package.to_dict() == {
        **package.to_dict(),
        'state': packages.types.PackageState.DELIVERING,
        'updated_at': now
    }
    assert len(package_history) == 1
    assert package_history[0].to_dict() == new_package.to_dict()


@pytest.mark.asyncio()
async def test_update_to_delivery_with_history_with_multiple_package():
    order = await orders.factories.create()
    package_1 = await packages.factories.create(order_id=order.order_id, state=packages.types.PackageState.IN_WAREHOUSE)
    package_2 = await packages.factories.create(order_id=order.order_id, state=packages.types.PackageState.EXPECTING_DELIVERY)
    package_3 = await packages.factories.create(order_id=order.order_id)

    to_update = {package_1.package_id: package_1, package_2.package_id: package_2}
    now = datetime_utils.get_now()

    changed_packages_list = await packages.update_to_delivery(order_id=order.order_id, updated_at=now)

    new_packages = await packages.list_by_order_id(order_id=order.order_id)
    package_history = await packages.get_all_history()

    assert len(package_history) == 2
    assert len(changed_packages_list) == 2

    for changed_package in changed_packages_list:
        assert changed_package.to_dict() == {
            **to_update[changed_package.package_id].to_dict(),
            'state': packages.types.PackageState.DELIVERING,
            'updated_at': now,
        }

    for package in new_packages:
        if package.package_id in to_update:
            assert package.to_dict() == {
                **to_update[package.package_id].to_dict(),
                'state': packages.types.PackageState.DELIVERING,
                'updated_at': now,
            }
        else:
            assert package.to_dict() == package_3.to_dict()

    for history in package_history:
        assert history.to_dict() == {
            **to_update[history.package_id].to_dict(),
            'state': packages.types.PackageState.DELIVERING,
            'updated_at': now,
        }


@pytest.mark.asyncio()
async def test_update_to_delivery_without_history():
    package = await packages.factories.create(state=packages.types.PackageState.IN_WAREHOUSE)
    now = datetime_utils.get_now()
    await packages.update_to_delivery(order_id=package.order_id, updated_at=now, with_history=False)

    new_package = (await packages.list_by_order_id(order_id=package.order_id))[0]
    package_history = await packages.get_all_history()

    assert new_package.to_dict() == {
        **package.to_dict(),
        'state': packages.types.PackageState.DELIVERING,
        'updated_at': now
    }
    assert len(package_history) == 0


@pytest.mark.asyncio()
async def test_update_to_delivery_raise_not_on_warehouse():
    package = await packages.factories.create()
    now = datetime_utils.get_now()

    with pytest.raises(packages.exceptions.PackageNotOnWarehouse):
        await packages.update_to_delivery(order_id=package.order_id, updated_at=now)


@pytest.mark.asyncio()
async def test_update_to_delivery_without_raise_not_found():
    order_id = generate_id()
    now = datetime_utils.get_now()
    package_list = await packages.update_to_delivery(order_id=order_id, updated_at=now, raise_not_on_warehouse=False)

    assert package_list == []


@pytest.mark.asyncio
async def test_get_by_order_id_with_place_without_package():
    order_id = generate_id()

    with pytest.raises(packages.exceptions.PackageNotFoundError):
        await packages.get_by_order_id_with_place(order_id)


@pytest.mark.asyncio
async def test_get_by_order_id_with_place_with_package():
    order = await orders.factories.create()
    package1 = await packages.factories.create(order_id=order.order_id, created_at=1)
    package2 = await packages.factories.create(order_id=order.order_id, created_at=2)
    await package_places.factories.create(
        package_id=package1.package_id,
        pallet={'rack': 1, 'place': 11}
    )
    await package_places.factories.create(
        package_id=package2.package_id,
        pallet={'rack': 2, 'place': 24}
    )

    result = await packages.get_by_order_id_with_place(order.order_id)
    assert result == packages.PublicPackageResponse(
        **package1.to_dict(),
        rack=1,
        place=11,
    )


@pytest.mark.asyncio
async def test_get_by_order_id_with_place_with_package_without_place():
    order = await orders.factories.create()
    package1 = await packages.factories.create(order_id=order.order_id, created_at=1)
    await packages.factories.create(order_id=order.order_id, created_at=2)

    result = await packages.get_by_order_id_with_place(order.order_id)
    assert result == packages.PublicPackageResponse(
        **package1.to_dict(),
        rack=None,
        place=None,
    )


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_update():
    order = await orders.factories.create()
    await packages.factories.create(order_id=order.order_id)

    package_objects = await packages.update(
        warehouse_id=order.warehouse_id,
        order_id=order.order_id,
        package=packages.PackagePlacementRequest(
            barcode='test_barcode',
            partner_id='test_partner_id',
            description='test_description',
            measurements=measurements.factories.build_request(
                width=1,
                height=2,
                length=3,
                weight=4,
            )
        ),
    )

    assert len(package_objects) == 1

    expected_package_objects = [
        packages.factories.build(
            order_id=order.order_id,
            package_id=package_objects[0].package_id,
            barcode='test_barcode',
            description='test_description',
            measurements=measurements.factories.build_request(
                width=1,
                height=2,
                length=3,
                weight=4,
            ),
            created_at=package_objects[0].created_at,
            updated_at=package_objects[0].updated_at,
        )
    ]

    assert_items_equal([m.to_response() for m in package_objects],
                       [m.to_response() for m in expected_package_objects])

    db_packages = await packages.get_all()
    assert_items_equal([m.to_response() for m in db_packages],
                       [m.to_response() for m in package_objects])

    db_history = await packages.get_all_history()
    assert_items_equal(
        [m.to_response() for m in db_history],
        [packages.PackageHistoryResponse(**package.to_dict())
         for package in package_objects]
    )


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_update_with_not_unique_barcode():
    warehouse = await warehouses.factories.create()
    order1 = await orders.factories.create(warehouse_id=warehouse.warehouse_id)
    order2 = await orders.factories.create(warehouse_id=warehouse.warehouse_id)
    package_with_same_barcode_in_another_order = await packages.factories.create(order_id=order2.order_id, barcode='test_barcode')
    await package_places.factories.create(warehouse_id=warehouse.warehouse_id,
                                          package_id=package_with_same_barcode_in_another_order.package_id)
    package = await packages.factories.create(order_id=order1.order_id)
    await package_places.factories.create(warehouse_id=warehouse.warehouse_id,
                                          package_id=package.package_id)

    with pytest.raises(packages.exceptions.PackageBarcodeNotUniqueError):
        await packages.update(
            warehouse_id=warehouse.warehouse_id,
            order_id=order1.order_id,
            package=packages.PackagePlacementRequest(
                barcode='test_barcode',
                partner_id='test_partner_id',
                description='test_description',
                measurements=measurements.factories.build_request()
            ),
        )
    db_packages = await packages.get_all()
    assert len(db_packages) == 2
    assert_items_equal(
        [package_with_same_barcode_in_another_order.to_response(), package.to_response()],
        [m.to_response() for m in db_packages],
    )


@pytest.mark.asyncio
async def test_barcode_exists_by_warehouse_id():
    warehouse1 = await warehouses.factories.create()
    order1 = await orders.factories.create(warehouse_id=warehouse1.warehouse_id)
    package1 = await packages.factories.create(order_id=order1.order_id, barcode='barcode')
    await package_places.factories.create(warehouse_id=warehouse1.warehouse_id,
                                          package_id=package1.package_id)

    warehouse2 = await warehouses.factories.create()
    order2 = await orders.factories.create(warehouse_id=warehouse2.warehouse_id)
    package2 = await packages.factories.create(order_id=order2.order_id, barcode='BARCODE')
    await package_places.factories.create(warehouse_id=warehouse2.warehouse_id,
                                          package_id=package2.package_id)

    same_barcodes_in_one_order = await packages.barcode_exists_by_warehouse_id(
        warehouse_id=warehouse1.warehouse_id,
        barcode=package1.barcode,
        order_id=order1.order_id,
    )
    assert not same_barcodes_in_one_order

    same_barcodes_in_different_orders = await packages.barcode_exists_by_warehouse_id(
        warehouse_id=warehouse1.warehouse_id,
        barcode=package1.barcode,
        order_id=order2.order_id,
    )
    assert same_barcodes_in_different_orders

    diff_barcode = await packages.barcode_exists_by_warehouse_id(
        warehouse_id=warehouse1.warehouse_id,
        barcode='BARCODE',
        order_id=order1.order_id,
    )
    assert not diff_barcode


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_create_batch():
    warehouse = await warehouses.factories.create()
    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id)

    package_objects = await packages.create_batch(
        order_id=order.order_id,
        packages=[
            packages.PackagePlacementRequest(
                barcode='test_barcode1',
                partner_id='test_partner_id',
                description='test_description1',
                measurements=measurements.factories.build_request(),
            ),
            packages.PackagePlacementRequest(
                barcode='test_barcode2',
                partner_id='test_partner_id',
                description='test_description2',
                measurements=measurements.factories.build_request(),
            )
        ],
    )

    assert len(package_objects) == 2

    expected_package_objects = [
        packages.factories.build(
            order_id=order.order_id,
            package_id=package_objects[0].package_id,
            barcode='test_barcode1',
            description='test_description1',
            measurements=measurements.factories.build_request(),
            created_at=datetime.datetime(
                2020, 1, 2, 0, 4, 5, tzinfo=datetime.timezone.utc),
            updated_at=datetime.datetime(
                2020, 1, 2, 0, 4, 5, tzinfo=datetime.timezone.utc),
        ),
        packages.factories.build(
            order_id=order.order_id,
            package_id=package_objects[1].package_id,
            barcode='test_barcode2',
            description='test_description2',
            measurements=measurements.factories.build_request(),
            created_at=datetime.datetime(
                2020, 1, 2, 0, 4, 5, tzinfo=datetime.timezone.utc),
            updated_at=datetime.datetime(
                2020, 1, 2, 0, 4, 5, tzinfo=datetime.timezone.utc),
        ),
    ]

    assert_items_equal([m.to_response() for m in package_objects],
                       [m.to_response() for m in expected_package_objects])

    db_packages = await packages.get_all()
    assert_items_equal([m.to_response() for m in db_packages],
                       [m.to_response() for m in package_objects])

    db_history = await packages.get_all_history()
    assert_items_equal(
        [m.to_response() for m in db_history],
        [packages.PackageHistoryResponse(**package.to_dict())
         for package in package_objects]
    )


@pytest.mark.asyncio
async def test_get_package_by_barcode_not_found():
    warehouse = await warehouses.factories.create()
    package = await packages.factories.create(state=packages.types.PackageState.CANCELLED,
                                              barcode='12345')
    await package_places.factories.create(warehouse_id=warehouse.warehouse_id,
                                          package_id=package.package_id)

    with pytest.raises(packages.exceptions.PackageNotFoundError):
        await packages.get_package_by_barcode(barcode='12345', warehouse_id=warehouse.warehouse_id)


@pytest.mark.asyncio
async def test_get_package_by_barcode_actives_duplicate():
    warehouse = await warehouses.factories.create()
    package1 = await packages.factories.create(state=packages.types.PackageState.NEW,
                                               barcode='12345')
    package2 = await packages.factories.create(state=packages.types.PackageState.IN_WAREHOUSE,
                                               barcode='12345')
    await package_places.factories.create(warehouse_id=warehouse.warehouse_id,
                                          package_id=package1.package_id)
    await package_places.factories.create(warehouse_id=warehouse.warehouse_id,
                                          package_id=package2.package_id)

    with pytest.raises(packages.exceptions.PackageNotFoundError):
        await packages.get_package_by_barcode(barcode='12345', warehouse_id=warehouse.warehouse_id)


@pytest.mark.asyncio
async def test_get_package_by_barcode_legal_duplicate():
    warehouse = await warehouses.factories.create()
    package1 = await packages.factories.create(state=packages.types.PackageState.NEW,
                                               barcode='12345')
    package2 = await packages.factories.create(state=packages.types.PackageState.CANCELLED,
                                               barcode='12345')
    place1 = await package_places.factories.create(warehouse_id=warehouse.warehouse_id,
                                                   package_id=package1.package_id)
    await package_places.factories.create(warehouse_id=warehouse.warehouse_id,
                                          package_id=package2.package_id)

    pack, place = await packages.get_package_by_barcode(barcode='12345', warehouse_id=warehouse.warehouse_id)

    assert pack.to_dict() == package1.to_dict()
    assert place.to_dict() == place1.to_dict()


@pytest.mark.asyncio
async def test_get_package_by_barcode_only_one():
    warehouse = await warehouses.factories.create()
    package1 = await packages.factories.create(state=packages.types.PackageState.NEW,
                                               barcode='12345')
    place1 = await package_places.factories.create(warehouse_id=warehouse.warehouse_id,
                                                   package_id=package1.package_id)

    pack, place = await packages.get_package_by_barcode(barcode='12345', warehouse_id=warehouse.warehouse_id)

    assert pack.to_dict() == package1.to_dict()
    assert place.to_dict() == place1.to_dict()
