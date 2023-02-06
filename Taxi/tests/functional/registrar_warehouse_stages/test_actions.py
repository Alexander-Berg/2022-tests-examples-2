import pytest

from taxi.robowarehouse.lib.concepts import registrar_warehouse_stages
from taxi.robowarehouse.lib.concepts import registrars
from taxi.robowarehouse.lib.concepts import warehouses
from taxi.robowarehouse.lib.test_utils.helpers import assert_items_equal


@pytest.mark.asyncio
async def test_get_all():
    stage1 = await registrar_warehouse_stages.factories.create()
    stage2 = await registrar_warehouse_stages.factories.create(
        type=registrar_warehouse_stages.types.RegistrarWarehouseStageState.IN_WAREHOUSE,
    )

    result = await registrar_warehouse_stages.get_all()

    result = [el.to_dict() for el in result]
    expected = [el.to_dict() for el in (stage1, stage2)]

    assert_items_equal(result, expected)


@pytest.mark.asyncio
async def test_create():
    warehouse = await warehouses.factories.create()
    registrar = await registrars.factories.create()

    stage1 = await registrar_warehouse_stages.factories.create()
    stage2 = registrar_warehouse_stages.factories.build(warehouse_id=warehouse.warehouse_id,
                                                        registrar_id=registrar.registrar_id)

    result = await registrar_warehouse_stages.create(
        registrar_warehouse_stages.CreateRegistrarWarehouseStageRequest.from_orm(stage2)
    )

    stages = await registrar_warehouse_stages.get_all()
    stages = [el.to_dict() for el in stages]
    expected = [el.to_dict() for el in (stage1, stage2)]

    assert result.to_dict() == stage2.to_dict()
    assert_items_equal(stages, expected)
