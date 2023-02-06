import json

import pytest

from tests_contractor_orders_polling import utils


@pytest.mark.parametrize('md5_requestcar', (('', None)))
async def test_request_order_no_md5(
        taxi_contractor_orders_polling, md5_requestcar,
):
    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        params={'md5_requestcar': md5_requestcar}
        if md5_requestcar is not None
        else None,
        headers=utils.HEADERS,
    )
    assert response.status_code == 200
    response_obj = response.json()
    assert response_obj.get('md5_requestcar') is None
    assert response_obj.get('requestcar') is None


@pytest.mark.redis_store(
    ['set', 'RequestOrder:MD5999:888', 'REQUEST_ORDER_ETAG'],
    [
        'lpush',
        'RequestOrder:Taximeter:List:999:888',
        json.dumps({'Action': 'Hello'}),
        json.dumps({'Action': 'World'}),
    ],
)
async def test_request_order(taxi_contractor_orders_polling, redis_store):
    # From https://nda.ya.ru/t/bDH4Jvgn3Za4fN

    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        params={'md5_requestcar': 'REQUEST_ORDER_ETAG'},
        headers=utils.HEADERS,
    )
    assert response.status_code == 200
    response_obj = response.json()
    assert response_obj['md5_requestcar'] == 'REQUEST_ORDER_ETAG'
    assert response_obj.get('requestcar') is None

    for md5_requestcar in (
            None,
            '',
            'REQUEST_ORDER_ETAG_BAD',
            '"REQUEST_ORDER_ETAG_BAD"',  # Quoted tag
    ):
        # fast requests do not fail because of the missing key
        response = await taxi_contractor_orders_polling.get(
            utils.HANDLER_URL,
            params={'md5_requestcar': md5_requestcar}
            if md5_requestcar
            else None,
            headers=utils.HEADERS,
        )
        assert response.status_code == 200
        response_obj = response.json()
        assert response_obj['md5_requestcar'] == 'REQUEST_ORDER_ETAG'
        assert response_obj['requestcar'] == [
            {'Action': 'World'},
            {'Action': 'Hello'},
        ]

    redis_store.delete('tmp:{RequestOrder:Taximeter:List:999:888}')

    # collection expired after getting
    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        params={'md5_requestcar': 'REQUEST_ORDER_ETAG_BAD'},
        headers=utils.HEADERS,
    )
    assert response.status_code == 200
    response_obj = response.json()
    assert response_obj['md5_requestcar'] == 'REQUEST_ORDER_ETAG'
    assert response_obj.get('requestcar') is None


async def test_request_order_no_md5_on_server(taxi_contractor_orders_polling):
    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        params={'md5_requestcar': 'REQUEST_ORDER_ETAG'},
        headers=utils.HEADERS,
    )
    assert response.status_code == 200
    response_obj = response.json()
    assert response_obj['md5_requestcar'] == 'REQUEST_ORDER_ETAG'
    assert response_obj.get('requestcar') is None
