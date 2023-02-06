import datetime
import freezegun
import pytest
from sqlalchemy.exc import IntegrityError

from taxi.robowarehouse.lib.concepts import database
from taxi.robowarehouse.lib.concepts import measurements
from taxi.robowarehouse.lib.concepts import orders
from taxi.robowarehouse.lib.concepts import package_places
from taxi.robowarehouse.lib.concepts import packages
from taxi.robowarehouse.lib.concepts import warehouses
from taxi.robowarehouse.lib.misc.helpers import generate_id
from taxi.robowarehouse.lib.misc import datetime_utils
from taxi.robowarehouse.lib.test_utils.helpers import assert_items_equal


@pytest.mark.asyncio
async def test_get_all_empty():
    result = await package_places.get_all()

    assert result == []


@pytest.mark.asyncio
async def test_get_all():
    package_place1 = await package_places.factories.create()
    package_place2 = await package_places.factories.create()

    result = await package_places.get_all()

    assert_items_equal([r.to_response() for r in result], [
                       package_place1.to_response(), package_place2.to_response()])


@pytest.mark.asyncio
async def test_get_all_history_empty():
    result = await package_places.get_all_history()

    assert result == []


@pytest.mark.asyncio
async def test_get_all_history():
    package_place1 = await package_places.factories.create_history()
    package_place2 = await package_places.factories.create_history()

    result = await package_places.get_all_history()

    assert_items_equal([r.to_response() for r in result], [
                       package_place1.to_response(), package_place2.to_response()])


@pytest.mark.asyncio
async def test_create():
    package_place1 = await package_places.factories.create()
    package_place2 = package_places.factories.build(
        warehouse_id=package_place1.warehouse_id)

    result = await package_places.create(package_places.CreatePackagePlaceRequest.from_orm(package_place2))

    assert result.to_response() == package_place2.to_response()

    db_package_places = await package_places.get_all()
    assert_items_equal([m.to_response() for m in db_package_places],
                       [package_place1.to_response(), package_place2.to_response()])

    db_history = await package_places.get_all_history()
    assert_items_equal([m.to_response() for m in db_history],
                       [package_places.PackagePlaceHistoryResponse(**package_place2.to_dict())])


@pytest.mark.asyncio
async def test_create_with_package_id():
    package = await packages.factories.create()
    package_place1 = await package_places.factories.create()
    package_place2 = package_places.factories.build(warehouse_id=package_place1.warehouse_id,
                                                    package_id=package.package_id)

    result = await package_places.create(package_places.CreatePackagePlaceRequest.from_orm(package_place2))

    assert result.to_response() == package_place2.to_response()

    db_package_places = await package_places.get_all()
    assert_items_equal([m.to_response() for m in db_package_places],
                       [package_place1.to_response(), package_place2.to_response()])

    db_history = await package_places.get_all_history()
    assert_items_equal([m.to_response() for m in db_history],
                       [package_places.PackagePlaceHistoryResponse(**package_place2.to_dict())])


@pytest.mark.asyncio
async def test_create_without_history():
    package_place1 = await package_places.factories.create()
    package_place2 = package_places.factories.build(
        warehouse_id=package_place1.warehouse_id)

    result = await package_places.create(package_places.CreatePackagePlaceRequest.from_orm(package_place2),
                                         with_history=False)

    assert result.to_response() == package_place2.to_response()

    db_package_places = await package_places.get_all()
    assert_items_equal([m.to_response() for m in db_package_places],
                       [package_place1.to_response(), package_place2.to_response()])

    db_history = await package_places.get_all_history()
    assert db_history == []


@pytest.mark.asyncio
async def test_create_no_package():
    package_id = generate_id()
    package_place1 = await package_places.factories.create()
    package_place2 = package_places.factories.build(warehouse_id=package_place1.warehouse_id,
                                                    package_id=package_id)

    with pytest.raises(IntegrityError) as e:
        await package_places.create(package_places.CreatePackagePlaceRequest.from_orm(package_place2))

    assert f'Key (package_id)=({package_id}) is not present in table "packages".' in str(
        e.value)

    db_package_places = await package_places.get_all()
    assert_items_equal([m.to_response() for m in db_package_places], [
                       package_place1.to_response()])


@pytest.mark.asyncio
async def test_create_flush():
    warehouse = warehouses.factories.build()
    order = orders.factories.build(warehouse_id=warehouse.warehouse_id)
    package = packages.factories.build(order_id=order.order_id)
    package_place1 = package_places.factories.build(
        package_id=package.package_id, warehouse_id=warehouse.warehouse_id)

    async with database.db_session() as db:
        await warehouses.create(warehouses.CreateWarehouseRequest.from_orm(warehouse), db=db)
        await orders.create(orders.CreateOrderRequest.from_orm(order), db=db)
        await packages.create(packages.CreatePackageRequest.from_orm(package), db=db)
        await package_places.create(package_places.CreatePackagePlaceRequest.from_orm(package_place1), db=db)

    db_package_places = await package_places.get_all()
    assert [m.to_response() for m in db_package_places] == [
        package_place1.to_response()]


@pytest.mark.asyncio
async def test_put_packages():
    warehouse = await warehouses.factories.create()
    package = await packages.factories.create()
    await package_places.factories.create(warehouse_id=warehouse.warehouse_id)
    await package_places.factories.create(warehouse_id=warehouse.warehouse_id)
    await package_places.put_packages(warehouse.warehouse_id, [package])

    cnt = 0
    db_package_places = await package_places.get_all()
    for pp in db_package_places:
        if pp.package_id == package.package_id:
            cnt += 1
            package_place = pp
    package_place_history = await package_places.get_all_history()

    assert cnt == 1
    assert package_place.warehouse_id == warehouse.warehouse_id
    assert package_place.state == package_places.types.PackagePlaceState.FILLED
    assert len(package_place_history) == 1


@pytest.mark.asyncio
async def test_put_packages_on_filled_place():
    warehouse = await warehouses.factories.create()
    package = await packages.factories.create()
    await package_places.factories.create(warehouse_id=warehouse.warehouse_id)
    await package_places.put_packages(warehouse.warehouse_id, [package])

    before = await package_places.get_all()
    with pytest.raises(package_places.exceptions.PackagePlaceNotFoundError):
        await package_places.put_packages(warehouse.warehouse_id, [package])
    after = await package_places.get_all()

    assert_items_equal([package_place.to_response() for package_place in before], [
                       package_place.to_response() for package_place in after])


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_create_with_packages():
    warehouse = await warehouses.factories.create()
    order = await orders.factories.create(warehouse_id=warehouse.warehouse_id)
    await package_places.factories.create(warehouse_id=warehouse.warehouse_id)

    package_objects = await package_places.create_with_packages(
        order_id=order.order_id,
        warehouse_id=warehouse.warehouse_id,
        packages=[packages.PackagePlacementRequest(
            barcode='test_barcode',
            partner_id='test_partner_id',
            description='test_description',
            measurements=measurements.factories.build_request()
        )],
    )
    db_packages = await packages.get_all()
    assert_items_equal([m.to_response() for m in db_packages],
                       [m.to_response() for m in package_objects])

    db_package_places = await package_places.get_all()
    assert len(db_package_places) == 1

    expected_package_place = [package_places.factories.build(
        warehouse_id=warehouse.warehouse_id,
        package_place_id=db_package_places[0].package_place_id,
        state=package_places.types.PackagePlaceState.FILLED,
        package_id=db_package_places[0].package_id,
        updated_at=datetime.datetime(
            2020, 1, 2, 0, 4, 5, tzinfo=datetime.timezone.utc),
    )]
    assert_items_equal([m.to_response() for m in db_package_places],
                       [m.to_response() for m in expected_package_place])


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_update_place():
    now = datetime_utils.get_now()
    warehouse1 = await warehouses.factories.create()
    place1 = await package_places.factories.create(warehouse_id=warehouse1.warehouse_id, created_at=1)
    place2 = await package_places.factories.create(warehouse_id=warehouse1.warehouse_id, created_at=2)

    update_body = package_places.UpdatePackagePlaceRequest(
        state='FILLED',
        state_meta={'reason': 'test data'},
        directions='test',
        pallet={'rack': 1, 'place': 11},
        measurements={'width': 100, 'height': 100, 'length': 100, 'weight': 100},
    )
    result = await package_places.update_place(place1.package_place_id, update_body)

    places = sorted(await package_places.get_all(), key=lambda el: el.created_at)
    places_history = await package_places.get_all_history()

    assert places[1].to_dict() == place2.to_dict()
    assert places[0].to_dict() == {
        **place1.to_dict(),
        **update_body.dict(),
        'updated_at': now,
    }
    assert result.to_dict() == places[0].to_dict()
    assert len(places_history) == 1
    assert places_history[0].to_dict() == result.to_dict()


@pytest.mark.parametrize('body, exception', [
    ({'drections': None}, package_places.exceptions.PackagePlaceNothingUpdate),
    ({'directions': 'test'}, package_places.exceptions.PackagePlaceNotFoundError),
])
@pytest.mark.asyncio
async def test_update_place_with_errors(body, exception):
    body = package_places.UpdatePackagePlaceRequest(**body)
    pacakge_place_id = generate_id()
    with pytest.raises(exception):
        await package_places.update_place(pacakge_place_id, body)
