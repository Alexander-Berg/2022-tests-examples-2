import pytest


async def test_ok(
        get_taxi_orders_to_refs,
        happy_path_state_orders_created,
        get_waybill_ref_by_taxi_order_id,
):
    mapping = get_taxi_orders_to_refs()
    assert mapping
    for taxi_order_id, waybill_ref in mapping.items():
        response = await get_waybill_ref_by_taxi_order_id(taxi_order_id)
        assert response['waybill_external_ref'] == waybill_ref


async def test_not_found(
        happy_path_state_orders_created, request_waybill_ref_by_taxi_order_id,
):
    response = await request_waybill_ref_by_taxi_order_id('unknown')
    assert response.status_code == 404


@pytest.fixture(name='get_taxi_orders_to_refs')
def _get_taxi_orders_to_refs(cargo_orders_db):
    def _wrapper():
        mapping = {}
        for order_id, waybill_ref in cargo_orders_db.uuids2refs.items():
            if order_id in cargo_orders_db.committed_orders:
                taxi_order_id = cargo_orders_db.taxi_order_id_from_order_id(
                    order_id,
                )
                mapping[taxi_order_id] = waybill_ref
        return mapping

    return _wrapper
