# pylint: disable=invalid-name
import pytest


async def test_poll(db, taxi_billing_buffer_proxy_client, request_headers):
    await db.taximeter_buffer.insert(
        {
            'request_id': 'quas',
            'response': {
                'json': {'Hello': 'world'},
                'text': None,
                'http_status': 200,
            },
        },
    )

    response = await taxi_billing_buffer_proxy_client.post(
        'v1/poll/taximeter',
        json={'request_id': 'quas'},
        headers=request_headers,
    )
    assert response.status == 200
    assert await response.json() == {
        'status': 'sent',
        'response': {
            'json': {'Hello': 'world'},
            'text': None,
            'http_status': 200,
        },
    }


async def test_poll_not_found(
        taxi_billing_buffer_proxy_client, request_headers,
):
    response = await taxi_billing_buffer_proxy_client.post(
        'v1/poll/taximeter',
        json={'request_id': 'not_existing_request_id'},
        headers=request_headers,
    )
    assert response.status == 404

    response = await taxi_billing_buffer_proxy_client.post(
        'v1/poll/not_existing_buffer',
        json={'request_id': 'wex'},
        headers=request_headers,
    )
    assert response.status == 404

    response = await taxi_billing_buffer_proxy_client.post(
        'v1/push/taximeter',
        json={'request_id': 'wex', 'request': {'foo': 'bar'}},
        headers=request_headers,
    )
    assert response.status == 200
    response = await taxi_billing_buffer_proxy_client.post(
        'v1/poll/taximeter',
        json={'request_id': 'wex'},
        headers=request_headers,
    )
    assert response.status == 200
    json = await response.json()
    assert json['status'] == 'new'
    assert 'response' not in json


@pytest.mark.config(TVM_ENABLED=True)
async def test_poll_api_token(taxi_billing_buffer_proxy_client):
    response = await taxi_billing_buffer_proxy_client.post(
        'v1/poll/taximeter', json={'request_id': 'wex'},
    )
    assert response.status == 403
