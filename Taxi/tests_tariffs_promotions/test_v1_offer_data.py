import json


BASE_REQUEST = {
    'offers': [
        {
            'offer_id': 'some_offer_id_1',
            'data': {
                'route_info': {
                    'distance': '1234',
                    'time': '5678',
                    'points': [
                        {'type': 'a', 'title': 'Moscow, Main Street'},
                        {'type': 'b', 'title': 'Moscow, Middle Street'},
                    ],
                },
                'currency': 'RUB',
                'categories': [
                    {
                        'name': 'econom',
                        'final_price': '132',
                        'surge_value': '2.3',
                    },
                    {
                        'name': 'business',
                        'final_price': '150',
                        'surge_value': '1',
                        'driver_funded_discount_value': '3',
                    },
                ],
            },
        },
        {
            'offer_id': 'some_offer_id_2',
            'data': {
                'currency': 'USD',
                'categories': [
                    {'name': 'express', 'final_price': '23.2'},
                    {'name': 'vip', 'final_price': '55'},
                ],
            },
        },
    ],
}
REDIS_TTL = 10


def build_redis_key(offer_id):
    return 'offer:{}'.format(offer_id)


async def test_post(taxi_tariffs_promotions, redis_store):

    response = await taxi_tariffs_promotions.post(
        'v1/offer-data', json=BASE_REQUEST,
    )

    assert response.status_code == 200

    value = redis_store.get(build_redis_key('some_offer_id_1'))
    assert json.loads(value) == BASE_REQUEST['offers'][0]['data']
    value = redis_store.get(build_redis_key('some_offer_id_2'))
    assert json.loads(value) == BASE_REQUEST['offers'][1]['data']


async def test_get(taxi_tariffs_promotions, redis_store):
    offer_id = BASE_REQUEST['offers'][0]['offer_id']

    redis_store.setex(
        build_redis_key('some_offer_id_1'),
        REDIS_TTL,
        json.dumps(BASE_REQUEST['offers'][0]['data']),
    )

    response = await taxi_tariffs_promotions.get(
        'v1/offer-data?offer_id={}'.format(offer_id),
    )

    assert response.status_code == 200
    assert response.json() == BASE_REQUEST['offers'][0]['data']
