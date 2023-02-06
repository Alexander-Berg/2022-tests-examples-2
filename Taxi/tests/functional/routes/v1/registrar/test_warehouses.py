import pytest
import freezegun

from taxi.robowarehouse.lib.concepts import warehouses
from taxi.robowarehouse.lib.concepts import orders
from taxi.robowarehouse.lib.test_utils.helpers import convert_to_frontend_response
from taxi.robowarehouse.lib.misc.helpers import generate_id


@pytest.mark.asyncio
async def test_get_all_receiving_warehouses(client):
    warehouse1 = await warehouses.factories.create()
    warehouse2 = await warehouses.factories.create()

    await orders.factories.create(warehouse_id=warehouse1.warehouse_id,
                                  state=orders.types.OrderState.RECEIVED)
    await orders.factories.create(warehouse_id=warehouse1.warehouse_id,
                                  state=orders.types.OrderState.NEW)
    await orders.factories.create(warehouse_id=warehouse2.warehouse_id,
                                  state=orders.types.OrderState.RECEIVED)

    response = await client.get('/registrar/v1/warehouses/available/')

    warehouse_response = warehouses.RegistrarWarehouseResponse(**warehouse1.to_dict())
    expected = convert_to_frontend_response({'warehouses': [warehouse_response.dict()]})

    assert response.status_code == 200
    assert response.json() == expected


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_get_warehouse_not_found(client):
    await warehouses.factories.create()

    warehouse_id = generate_id()

    response = await client.get(f'/registrar/v1/warehouses/{warehouse_id}/')

    expected = {
        'code': 'WAREHOUSE_NOT_FOUND_ERROR',
        'details': {'occurred_at': '2020-01-02T00:04:05+00:00', 'warehouse_id': warehouse_id},
        'message': 'Warehouse not found',
    }

    assert response.status_code == 404
    assert response.json() == expected


@pytest.mark.asyncio
async def test_get_warehouse(client):
    warehouse = await warehouses.factories.create()
    await warehouses.factories.create()

    response = await client.get(f'/registrar/v1/warehouses/{warehouse.warehouse_id}/')

    warehouse_response = warehouses.RegistrarWarehouseResponse(**warehouse.to_dict())
    expected = convert_to_frontend_response(warehouse_response.dict())

    assert response.status_code == 200
    assert response.json() == expected
