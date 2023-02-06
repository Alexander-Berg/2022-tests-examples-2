import pytest

from tests_multiclass_pricing_storage import tvm_tickets


@pytest.mark.tvm2_ticket(
    {
        2001716: tvm_tickets.MULTICLASS_PRICING_STORAGE_SERVICE_TICKET,
        111: tvm_tickets.MOCK_SERVICE_TICKET,
    },
)
async def test_prices_remove(taxi_multiclass_pricing_storage):
    response = await taxi_multiclass_pricing_storage.post(
        'v1/prices/remove', headers=tvm_tickets.TVM_HEADER, json={'id': '1'},
    )
    assert response.status_code == 200

    response = await taxi_multiclass_pricing_storage.post(
        'v1/prices/remove', headers=tvm_tickets.TVM_HEADER, json={'id': '2'},
    )
    assert response.status_code == 404
