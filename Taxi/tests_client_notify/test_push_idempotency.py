import pytest


INTENTS = {
    'eda_courier': {
        'idempotent': {
            'description': 'test',
            'idempotency': {'enabled': True, 'token_ttl_ms': 1000},
        },
        'not_idempotent': {
            'description': 'test',
            'idempotency': {'enabled': False},
        },
    },
}

PAYLOAD_REPACK = {
    'repack_rules': [
        {
            'enabled': True,
            'conditions': {'services': ['eda_courier'], 'intents': []},
            'payload_repack': {'payload': {}},
        },
    ],
}


@pytest.mark.config(
    CLIENT_NOTIFY_INTENTS={
        'eda_courier': {
            'idempotent': {
                'description': 'test',
                'idempotency': {'enabled': True, 'token_ttl_ms': 1000},
            },
        },
    },
    CLIENT_NOTIFY_PAYLOAD_REPACK=PAYLOAD_REPACK,
)
@pytest.mark.parametrize('push_handler', ['v1/push', 'v2/push'])
async def test_push_idempotent(
        taxi_client_notify, mockserver, mocked_time, push_handler,
):
    @mockserver.json_handler('/xiva/v2/send')
    def _xiva_send(request):
        return mockserver.make_response('OK', 200, headers={'TransitID': 'id'})

    headers = {'X-Idempotency-Token': '12345'}

    request = {
        'service': 'eda_courier',
        'client_id': 'client1',
        'intent': 'idempotent',
        'data': {'payload': {}},
    }

    # Request 1: executed
    response = await taxi_client_notify.post(
        push_handler, headers=headers, json=request,
    )
    assert response.status_code == 200
    notification_id = response.json()['notification_id']
    assert notification_id is not None
    assert _xiva_send.times_called == 1

    # Request 2: not executed, return same notification id
    response = await taxi_client_notify.post(
        push_handler, headers=headers, json=request,
    )
    assert response.status_code == 200
    assert response.json()['notification_id'] == notification_id
    assert _xiva_send.times_called == 1

    # Request 3: executed because token ttl exceed, return new notification id
    mocked_time.sleep(1001)
    await taxi_client_notify.invalidate_caches()

    response = await taxi_client_notify.post(
        push_handler, headers=headers, json=request,
    )
    assert response.status_code == 200
    assert response.json()['notification_id'] != notification_id
    assert _xiva_send.times_called == 2


@pytest.mark.config(
    CLIENT_NOTIFY_INTENTS={
        'eda_courier': {
            'not_idempotent': {
                'description': 'test',
                'idempotency': {'enabled': False},
            },
        },
    },
    CLIENT_NOTIFY_PAYLOAD_REPACK=PAYLOAD_REPACK,
)
@pytest.mark.parametrize('push_handler', ['v1/push', 'v2/push'])
async def test_push_not_idempotent(
        taxi_client_notify, mockserver, push_handler,
):
    @mockserver.json_handler('/xiva/v2/send')
    def _xiva_send(request):
        return mockserver.make_response('OK', 200, headers={'TransitID': 'id'})

    headers = {'X-Idempotency-Token': '12345'}

    request = {
        'service': 'eda_courier',
        'client_id': 'client1',
        'intent': 'not_idempotent',
        'data': {'payload': {}},
    }

    response = await taxi_client_notify.post(
        push_handler, headers=headers, json=request,
    )
    assert response.status_code == 200
    notification_id = response.json()['notification_id']
    assert notification_id is not None

    response = await taxi_client_notify.post(
        push_handler, headers=headers, json=request,
    )
    assert response.status_code == 200
    assert response.json()['notification_id'] != notification_id

    assert _xiva_send.times_called == 2
