# pylint: disable=invalid-name
import pytest


async def test_push(db, taxi_billing_buffer_proxy_client, request_headers):
    request = {'request_id': 'quas', 'request': {'foo': 'bar'}}
    response = await taxi_billing_buffer_proxy_client.post(
        'v1/push/taximeter', json=request, headers=request_headers,
    )
    assert response.status == 200

    response = await taxi_billing_buffer_proxy_client.post(
        'v1/push/taximeter', json=request, headers=request_headers,
    )
    assert response.status == 200

    count = await db.taximeter_buffer.find({'request_id': 'quas'}).count()
    assert count == 1

    doc = await db.taximeter_buffer.find_one({'request_id': 'quas'})
    assert doc['request'] == request['request']
    assert doc['status'] == 'new'


async def test_push_not_found(
        taxi_billing_buffer_proxy_client, request_headers,
):
    response = await taxi_billing_buffer_proxy_client.post(
        'v1/push/not_existing_buffer',
        json={'request_id': 'wex', 'request': {'foo': 'bar'}},
        headers=request_headers,
    )
    assert response.status == 404


@pytest.mark.config(TVM_ENABLED=True)
async def test_push_api_token(taxi_billing_buffer_proxy_client):
    response = await taxi_billing_buffer_proxy_client.post(
        'v1/push/taximeter',
        json={'request_id': 'wex', 'request': {'foo': 'bar'}},
    )
    assert response.status == 403
