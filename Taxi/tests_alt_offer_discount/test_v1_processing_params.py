import json

import pytest


@pytest.mark.parametrize('testcase', ['ok', 'not_found'])
async def test_base(taxi_alt_offer_discount, redis_store, load_json, testcase):
    value = load_json(f'{testcase}_response.json')
    redis_store.set(
        'proc_params:perfect_chain:prepare_link', json.dumps(value),
    )

    body = load_json(f'{testcase}_request.json')
    response = await taxi_alt_offer_discount.post(
        '/v1/order-proc-params', json=body,
    )
    assert response.status_code == 200
    assert response.json() == value
