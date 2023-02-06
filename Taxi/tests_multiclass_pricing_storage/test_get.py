import pytest

from tests_multiclass_pricing_storage import tvm_tickets


@pytest.mark.tvm2_ticket(
    {
        2001716: tvm_tickets.MULTICLASS_PRICING_STORAGE_SERVICE_TICKET,
        111: tvm_tickets.MOCK_SERVICE_TICKET,
    },
)
async def test_prices_get_business(taxi_multiclass_pricing_storage, load_json):
    response = await taxi_multiclass_pricing_storage.post(
        'v1/prices/get',
        headers=tvm_tickets.TVM_HEADER,
        json={'id': '1', 'class': 'business'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('price_business.json')

    response = await taxi_multiclass_pricing_storage.post(
        'v1/prices/get',
        headers=tvm_tickets.TVM_HEADER,
        json={'id': '2', 'class': 'business'},
    )
    assert response.status_code == 404

    response = await taxi_multiclass_pricing_storage.post(
        'v1/prices/get',
        headers=tvm_tickets.TVM_HEADER,
        json={'id': '1', 'class': 'child_tariff'},
    )
    assert response.status_code == 409


@pytest.mark.tvm2_ticket(
    {
        2001716: tvm_tickets.MULTICLASS_PRICING_STORAGE_SERVICE_TICKET,
        111: tvm_tickets.MOCK_SERVICE_TICKET,
    },
)
async def test_prices_get_econom(taxi_multiclass_pricing_storage, load_json):
    response = await taxi_multiclass_pricing_storage.post(
        'v1/prices/get',
        headers=tvm_tickets.TVM_HEADER,
        json={'id': '1', 'class': 'econom'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('price_econom.json')
