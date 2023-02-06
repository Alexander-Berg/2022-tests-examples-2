import pytest

from tests_multiclass_pricing_storage import tvm_tickets


@pytest.mark.parametrize(
    'add_request_file, get_response_file, storage_id, performer_class',
    [
        ('prices.json', 'price_econom.json', 'some_id', 'econom'),
        (
            'prices_decoupling.json',
            'price_econom_decoupling.json',
            'some_id',
            'econom',
        ),
        (
            'prices_with_pdp_data.json',
            'price_econom_with_pdp_data.json',
            'some_id',
            'econom',
        ),
        (
            'prices_without_max_distance_from_b.json',
            'price_econom_without_max_distance_from_b.json',
            'some_id',
            'econom',
        ),
        (
            'current_prices.json',
            'current_prices_econom.json',
            'some_id',
            'econom',
        ),
    ],
)
@pytest.mark.tvm2_ticket(
    {
        2001716: tvm_tickets.MULTICLASS_PRICING_STORAGE_SERVICE_TICKET,
        111: tvm_tickets.MOCK_SERVICE_TICKET,
    },
)
async def test_prices_add(
        taxi_multiclass_pricing_storage,
        load_json,
        add_request_file,
        get_response_file,
        storage_id,
        performer_class,
):
    response = await taxi_multiclass_pricing_storage.post(
        'v1/prices/add',
        headers=tvm_tickets.TVM_HEADER,
        json=load_json(add_request_file),
    )
    assert response.status_code == 200

    response = await taxi_multiclass_pricing_storage.post(
        'v1/prices/get',
        headers=tvm_tickets.TVM_HEADER,
        json={'id': storage_id, 'class': performer_class},
    )
    assert response.status_code == 200
    assert response.json() == load_json(get_response_file)

    response = await taxi_multiclass_pricing_storage.post(
        'v1/prices/remove',
        headers=tvm_tickets.TVM_HEADER,
        json={'id': storage_id},
    )
    assert response.status_code == 200

    response = await taxi_multiclass_pricing_storage.post(
        'v1/prices/get',
        headers=tvm_tickets.TVM_HEADER,
        json={'id': storage_id, 'class': performer_class},
    )
    assert response.status_code == 404
