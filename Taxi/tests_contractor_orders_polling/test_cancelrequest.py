import pytest

from tests_contractor_orders_polling import utils


@pytest.mark.redis_store(
    ['set', 'Order:Driver:CancelRequest:MD5:999:888', 'CANCEL_REQUEST_ETAG'],
    ['lpush', 'Order:Driver:CancelRequest:Items:999:888', 'Hello'],
)
async def test_cancelrequest(taxi_contractor_orders_polling):
    # Same tag -> return only incoming tag
    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        headers=utils.HEADERS,
        params={'md5_cancelrequest': 'CANCEL_REQUEST_ETAG'},
    )
    assert response.status_code == 200
    response_obj = response.json()
    assert response_obj['md5_cancelrequest'] == 'CANCEL_REQUEST_ETAG'
    assert response_obj.get('cancelrequest') is None

    # Different or no tag -> return tag & data
    for tag in ['', 'CANCEL_REQUEST_ETAG_BAD', None]:
        response = await taxi_contractor_orders_polling.get(
            utils.HANDLER_URL,
            headers=utils.HEADERS,
            params={'md5_cancelrequest': tag},
        )
        assert response.status_code == 200
        response_obj = response.json()
        assert response_obj['md5_cancelrequest'] == 'CANCEL_REQUEST_ETAG'
        assert response_obj['cancelrequest'] == ['Hello']


async def test_cancelrequest_no_server_tag(taxi_contractor_orders_polling):
    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        headers=utils.HEADERS,
        params={'md5_cancelrequest': 'CANCEL_REQUEST_ETAG'},
    )
    assert response.status_code == 200
    response_obj = response.json()
    assert response_obj['md5_cancelrequest'] == 'CANCEL_REQUEST_ETAG'
    assert response_obj.get('cancelrequest') is None


@pytest.mark.redis_store(
    ['set', 'Order:Driver:CancelRequest:MD5:999:888', 'CANCEL_REQUEST_ETAG'],
    ['lpush', 'Order:Driver:CancelRequest:Items:999:888', 'canceled_order_id'],
    ['sadd', 'Order:Driver:Delayed:Items:999:888', 'delayed_order_id'],
)
async def test_cancelrequest_delayed_items(taxi_contractor_orders_polling):
    # Same tag -> return only incoming tag
    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL, headers=utils.HEADERS,
    )
    assert response.status_code == 200
    response_obj = response.json()
    assert response_obj['cancelrequest'] == [
        'canceled_order_id',
        'delayed_order_id',
    ]
