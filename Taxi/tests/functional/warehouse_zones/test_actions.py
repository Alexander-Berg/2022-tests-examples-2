import freezegun
import pytest

from taxi.robowarehouse.lib.misc import datetime_utils
from taxi.robowarehouse.lib.concepts import warehouses
from taxi.robowarehouse.lib.concepts import package_places
from taxi.robowarehouse.lib.concepts import warehouse_zones
from taxi.robowarehouse.lib.concepts import devices
from taxi.robowarehouse.lib.concepts import locations
from taxi.robowarehouse.lib.concepts import packages
from taxi.robowarehouse.lib.concepts import measurements
from taxi.robowarehouse.lib.test_utils.helpers import assert_items_equal
from taxi.robowarehouse.lib.misc.helpers import generate_id
from taxi.robowarehouse.lib.misc.helpers import generate_string
from taxi.robowarehouse.lib.misc.helpers import base64_encode
from taxi.robowarehouse.lib.misc.exceptions import WrongCursorParam


@pytest.mark.parametrize('position, measurement_count, numbers_of_warehouses', [
    (locations.LocationRequest(lon=0, lat=0), 3, [0]),
    (locations.LocationRequest(lon=0.5, lat=0.5), 2, [0]),
    (locations.LocationRequest(lon=0, lat=0), 4, []),
    (locations.LocationRequest(lon=5, lat=12.5), 1, [0, 1, 2]),
    (locations.LocationRequest(lon=5, lat=12.5), 3, [0]),
    (locations.LocationRequest(lon=5, lat=12.5), 2, [0, 1]),
    (locations.LocationRequest(lon=2.5, lat=20), 2, [1]),
    (locations.LocationRequest(lon=10, lat=12.5), 1, [2]),
    (locations.LocationRequest(lon=10, lat=12.5), 2, []),
    (locations.LocationRequest(lon=100, lat=12.5), 1, []),
])
@pytest.mark.asyncio()
async def test_list_available_in_point(position, measurement_count, numbers_of_warehouses):
    warehouses_list: list = [await warehouses.factories.create() for _ in range(3)]
    warehouses_list.sort(key=lambda el: el.warehouse_id)

    # make three free places for first warehouse
    for _ in range(3):
        await package_places.factories.create(warehouse_id=warehouses_list[0].warehouse_id)

    # make two free place and one occupied for second
    for _ in range(2):
        await package_places.factories.create(warehouse_id=warehouses_list[1].warehouse_id)
    await package_places.factories.create(
        warehouse_id=warehouses_list[1].warehouse_id,
        state=package_places.types.PackagePlaceState.FILLED,
    )

    # one place for third warehouse
    await package_places.factories.create(warehouse_id=warehouses_list[2].warehouse_id)

    # make three warehouse_zones
    polygon2 = [
        locations.LocationRequest(lon=5, lat=10),
        locations.LocationRequest(lon=0, lat=15),
        locations.LocationRequest(lon=0, lat=25),
        locations.LocationRequest(lon=10, lat=25),
        locations.LocationRequest(lon=10, lat=15),
    ]

    polygon3 = [
        locations.LocationRequest(lon=2.5, lat=12.5),
        locations.LocationRequest(lon=10, lat=25),
        locations.LocationRequest(lon=10, lat=0),
    ]

    await warehouse_zones.factories.create(warehouse_id=warehouses_list[0].warehouse_id)
    await warehouse_zones.factories.create(warehouse_id=warehouses_list[1].warehouse_id, polygon=polygon2)
    await warehouse_zones.factories.create(warehouse_id=warehouses_list[2].warehouse_id, polygon=polygon3)

    package_placements = [
        packages.PackagePlacementRequest(
            measurements=measurements.factories.build_request()
        )
        for _ in range(measurement_count)
    ]

    result = await warehouse_zones.list_available_in_point(
        pos=position,
        measurements=package_placements,
    )
    assert len(result) == len(numbers_of_warehouses)

    for warehouse, expected_number in zip(result, numbers_of_warehouses):
        assert warehouse.warehouse_id == warehouses_list[expected_number].warehouse_id


@pytest.mark.parametrize('status, expected_count', [
    (warehouse_zones.types.WarehouseStatus.CLOSE, 0),
    (warehouse_zones.types.WarehouseStatus.OPEN, 1),
])
@pytest.mark.asyncio()
async def test_list_available_in_point_warehouse_status(status, expected_count):
    warehouse = await warehouses.factories.create()

    polygon = [
        locations.LocationRequest(lon=5, lat=10),
        locations.LocationRequest(lon=0, lat=15),
        locations.LocationRequest(lon=0, lat=25),
        locations.LocationRequest(lon=10, lat=25),
        locations.LocationRequest(lon=10, lat=15),
    ]

    await warehouse_zones.factories.create(warehouse_id=warehouse.warehouse_id,
                                           polygon=polygon,
                                           status=status)

    await package_places.factories.create(warehouse_id=warehouse.warehouse_id)

    pos = locations.LocationRequest(lon=5, lat=12.5)
    package_placements = [packages.PackagePlacementRequest(
        measurements=measurements.factories.build_request()
    )]

    result = await warehouse_zones.list_available_in_point(
        pos=pos,
        measurements=package_placements,
    )

    assert len(result) == expected_count


@pytest.mark.asyncio
async def test_get_all_warehouses_with_detailed_zones():
    warehouse = await warehouses.factories.create()
    zone1 = await warehouse_zones.factories.create(warehouse_id=warehouse.warehouse_id)
    zone2 = await warehouse_zones.factories.create(warehouse_id=warehouse.warehouse_id,
                                                   type=warehouse_zones.types.DeliveryType.YANDEX_TAXI)

    result = await warehouse_zones.get_all_warehouses_with_detailed_zones()
    expected_zones = [
        {
            'zone_type': zone.type,
            **zone.to_dict()
        }
        for zone in (zone1, zone2)
    ]
    assert result == [{
        **warehouse.to_dict(),
        'detailed_zones': expected_zones
        }]


@pytest.mark.asyncio
async def test_get_all_warehouses_without_detailed_zones():
    warehouse = await warehouses.factories.create()

    result = await warehouse_zones.get_all_warehouses_with_detailed_zones()

    assert result == [{
        **warehouse.to_dict(),
        'detailed_zones': []
        }]


@pytest.mark.asyncio
async def test_get_all_empty():
    result = await warehouse_zones.get_all()

    assert result == []


@pytest.mark.asyncio
async def test_get_all():
    warehouse_zone_1 = await warehouse_zones.factories.create()
    warehouse_zone_2 = await warehouse_zones.factories.create()

    result = await warehouse_zones.get_all()

    assert_items_equal([r.to_dict() for r in result], [warehouse_zone_1.to_dict(), warehouse_zone_2.to_dict()])


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_update():
    warehouse_zone = await warehouse_zones.factories.create()
    updated_warehouse_zone = await warehouse_zones.update(
        warehouse_id=warehouse_zone.warehouse_id,
        type=warehouse_zones.types.DeliveryType.FOOT,
        update_request=warehouse_zones.UpdateWarehouseZoneRequest(status='CLOSE'),
        updated_at=datetime_utils.get_now(),
        )
    warehouse_zones_list = await warehouse_zones.get_all()

    assert [w.to_dict() for w in warehouse_zones_list] == [updated_warehouse_zone.to_dict()]


@pytest.mark.asyncio
async def test_get_full_by_warehouse_id_not_found():
    warehouse_id = generate_id()

    with pytest.raises(warehouses.exceptions.WarehouseNotFoundError):
        await warehouse_zones.get_full_by_warehouse_id(warehouse_id)


@pytest.mark.asyncio
async def test_get_full_by_warehouse_id():
    warehouse = await warehouses.factories.create()
    place1 = await package_places.factories.create(warehouse_id=warehouse.warehouse_id)
    place2 = await package_places.factories.create(warehouse_id=warehouse.warehouse_id)
    zone1 = await warehouse_zones.factories.create(warehouse_id=warehouse.warehouse_id,
                                                   type=warehouse_zones.types.DeliveryType.FOOT)
    zone2 = await warehouse_zones.factories.create(warehouse_id=warehouse.warehouse_id,
                                                   type=warehouse_zones.types.DeliveryType.YANDEX_TAXI)

    device = await devices.factories.create(warehouse_id=warehouse.warehouse_id)

    await warehouses.factories.create()
    await warehouse_zones.factories.create()
    await package_places.factories.create()
    await devices.factories.create()

    result = await warehouse_zones.get_full_by_warehouse_id(warehouse_id=warehouse.warehouse_id)

    assert result.warehouse.dict() == warehouse.to_dict()
    assert result.device.dict() == device.to_dict()

    assert_items_equal([p.dict() for p in result.package_places], (place1.to_dict(), place2.to_dict()))
    assert_items_equal([wz.dict() for wz in result.warehouse_zones], (zone1.to_dict(), zone2.to_dict()))


@pytest.mark.asyncio
async def test_get_paginated_warehouse_with_zones_not_found():
    result = await warehouse_zones.get_paginated_warehouse_with_zones()
    assert result.dict() == {'newer_than': None, 'older_than': None, 'warehouses': []}


@pytest.mark.parametrize('newer_than, next, prev', [
    (None, 1, None),
    (1, 2, 0),
    (2, None, 1),
])
@pytest.mark.asyncio
async def test_get_paginated_warehouse_with_zones_to_forward(newer_than, next, prev):
    limit = 5
    warehouse_list = sorted([await warehouses.factories.create() for _ in range(limit*3)], key=lambda el: el.warehouse_id)
    zones = {}
    for warehouse in warehouse_list:
        zones[warehouse.warehouse_id] = [
            (await warehouse_zones.factories.create(warehouse_id=warehouse.warehouse_id,
                                                    type=warehouse_zones.types.DeliveryType.FOOT)).to_dict(),
            (await warehouse_zones.factories.create(warehouse_id=warehouse.warehouse_id,
                                                    type=warehouse_zones.types.DeliveryType.YANDEX_TAXI)).to_dict(),
        ]

    expected_results = [
        {**warehouse.to_dict(), 'warehouse_zones': zones[warehouse.warehouse_id]}
        for warehouse in warehouse_list
    ]

    start, end = (newer_than or 0) * limit, ((newer_than or 0) + 1) * limit
    newer_than = newer_than and base64_encode(expected_results[(newer_than * limit) - 1].get('warehouse_id'))

    expected_results = expected_results[start:end]
    next = next if next is None else base64_encode(expected_results[-1].get('warehouse_id'))
    prev = prev if prev is None else base64_encode(expected_results[0].get('warehouse_id'))

    result = await warehouse_zones.get_paginated_warehouse_with_zones(limit=limit, newer_than=newer_than)
    assert result.dict() == {'newer_than': next, 'older_than': prev, 'warehouses': expected_results}


@pytest.mark.parametrize('older_than, next, prev', [
    (0, 1, None),
    (1, 2, 1),
])
@pytest.mark.asyncio
async def test_get_paginated_warehouse_with_zones_to_back(older_than, next, prev):
    limit = 5
    warehouse_list = sorted([await warehouses.factories.create() for _ in range(limit*3)], key=lambda el: el.warehouse_id)
    zones = {}
    for warehouse in warehouse_list:
        zones[warehouse.warehouse_id] = [
            (await warehouse_zones.factories.create(warehouse_id=warehouse.warehouse_id,
                                                    type=warehouse_zones.types.DeliveryType.FOOT)).to_dict(),
            (await warehouse_zones.factories.create(warehouse_id=warehouse.warehouse_id,
                                                    type=warehouse_zones.types.DeliveryType.YANDEX_TAXI)).to_dict(),
        ]

    expected_results = [
        {**warehouse.to_dict(), 'warehouse_zones': zones[warehouse.warehouse_id]}
        for warehouse in warehouse_list
    ]

    start, end = (older_than) * limit, (older_than + 1) * limit
    older_than = base64_encode(expected_results[(older_than + 1) * limit].get('warehouse_id'))

    expected_results = expected_results[start:end]
    next = next if next is None else base64_encode(expected_results[-1].get('warehouse_id'))
    prev = prev if prev is None else base64_encode(expected_results[0].get('warehouse_id'))

    result = await warehouse_zones.get_paginated_warehouse_with_zones(limit=limit, older_than=older_than)
    assert result.dict() == {'newer_than': next, 'older_than': prev, 'warehouses': expected_results}


@pytest.mark.asyncio
async def test_get_paginated_warehouse_with_zones_wrong_cursor_params():
    await warehouses.factories.create()

    with pytest.raises(WrongCursorParam):
        await warehouse_zones.get_paginated_warehouse_with_zones(newer_than=generate_string(10),
                                                                 older_than=generate_string(10))


@pytest.mark.asyncio
async def test_get_paginated_warehouse_with_zones_address_filter():
    warehouse_list = [
        await warehouses.factories.create(address='addr 1'),
        await warehouses.factories.create(address='addr 2'),
    ]
    await warehouses.factories.create(address='unknown')

    warehouse_list.sort(key=lambda el: el.warehouse_id)
    expected_results = [{**warehouse.to_dict(), 'warehouse_zones': []} for warehouse in warehouse_list]

    result = await warehouse_zones.get_paginated_warehouse_with_zones(address='ddr')
    result = result.dict()

    assert result == {'newer_than': None, 'older_than': None, 'warehouses': expected_results}
