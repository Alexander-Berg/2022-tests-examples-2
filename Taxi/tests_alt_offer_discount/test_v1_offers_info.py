import json


async def test_base_ok(taxi_alt_offer_discount, redis_store):
    value = {
        'offers_info': [
            {'alternative_type': 'perfect_chain', 'info': {'eta': 12}},
        ],
    }
    redis_store.set(
        'offers_info:prepare_link', json.dumps(value['offers_info']),
    )

    body = {
        'request_id': 'prepare_link',
        'alternatives': [{'type': 'perfect_chain'}],
    }
    response = await taxi_alt_offer_discount.post('/v1/offers-info', json=body)
    assert response.status_code == 200
    assert response.json() == value


async def test_base_not_found(taxi_alt_offer_discount):
    body = {
        'request_id': 'prepare_link',
        'alternatives': [{'type': 'perfect_chain'}],
    }
    response = await taxi_alt_offer_discount.post('/v1/offers-info', json=body)
    assert response.status_code == 404


async def test_base_empty_request(taxi_alt_offer_discount, redis_store):
    body = {'request_id': 'prepare_link', 'alternatives': []}
    response = await taxi_alt_offer_discount.post('/v1/offers-info', json=body)
    assert response.status_code == 400
