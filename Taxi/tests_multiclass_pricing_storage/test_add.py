import json

import pytest

from tests_multiclass_pricing_storage import tvm_tickets


@pytest.mark.tvm2_ticket(
    {
        2001716: tvm_tickets.MULTICLASS_PRICING_STORAGE_SERVICE_TICKET,
        111: tvm_tickets.MOCK_SERVICE_TICKET,
    },
)
async def test_prices_add(taxi_multiclass_pricing_storage, load_json):
    response = await taxi_multiclass_pricing_storage.post(
        'v1/prices/add',
        headers=tvm_tickets.TVM_HEADER,
        json=load_json('prices.json'),
    )
    assert response.status_code == 200

    # try breaking unique violation
    response = await taxi_multiclass_pricing_storage.post(
        'v1/prices/add',
        headers=tvm_tickets.TVM_HEADER,
        json=load_json('prices.json'),
    )
    assert response.status_code == 200


@pytest.mark.tvm2_ticket(
    {
        2001716: tvm_tickets.MULTICLASS_PRICING_STORAGE_SERVICE_TICKET,
        111: tvm_tickets.MOCK_SERVICE_TICKET,
    },
)
@pytest.mark.parametrize(
    'due, generated_due',
    [
        ('2017-11-26T10:24:10.000+0000', '2020-06-01 12:10:00'),
        ('2020-11-26T07:24:10.000+0000', '2020-11-26 10:34:10'),
        (None, '2020-06-01 12:10:00'),
    ],
)
@pytest.mark.config(MULTICLASS_PRICING_STORAGE_TTL=10)
@pytest.mark.now('2020-06-01T12:00:00+03:00')
async def test_prices_add_with_due(
        taxi_multiclass_pricing_storage, due, generated_due, load_json, pgsql,
):
    request = load_json('prices.json')
    if due:
        request['due'] = due
    response = await taxi_multiclass_pricing_storage.post(
        'v1/prices/add', headers=tvm_tickets.TVM_HEADER, json=request,
    )
    assert response.status_code == 200
    cursor = pgsql['multiclass_prices'].cursor()
    cursor.execute('SELECT doc, due FROM info  WHERE id=\'some_id\'')
    price_info, new_due = cursor.fetchall()[0]
    assert str(new_due) == generated_due
    assert json.loads(price_info) == request
