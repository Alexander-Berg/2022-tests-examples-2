import datetime

import pytest


V1_PUSH = {
    'service': 'eda_courier',
    'client_id': 'courier1',
    'app_install_id': 'app-install-id',
    'intent': 'order_new',
    'ttl': 91,
    'data': {'payload': {}},
    'message_id': '123',
    'meta': {},
}

V2_PUSH = {
    'service': 'eda_courier',
    'message_id': '123',
    'client_id': 'client-id',
    'intent': 'order_new',
    'ttl': 91,
    'collapse_key': 'collapse_key',
    'notification': {
        'text': 'Пассажир добавил или изменил промежуточную точку',
        'title': 'Платформа',
        'sound': 'default',
    },
    'data': {'flags': ['high_priority']},
}


@pytest.mark.now('2020-06-26T14:00:00Z')
@pytest.mark.parametrize(
    'push_handler,push_request',
    [('/v1/push', V1_PUSH), ('/v2/push', V2_PUSH)],
)
@pytest.mark.parametrize(
    'send_mode,expected_code,xiva_called,queue_called',
    [
        ('no_queue', 502, 1, 0),
        ('fallback_queue', 200, 1, 1),
        ('force_queue', 200, 0, 1),
    ],
)
@pytest.mark.config(
    CLIENT_NOTIFY_PAYLOAD_REPACK={
        'repack_rules': [
            {
                'enabled': True,
                'conditions': {'services': ['eda_courier'], 'intents': []},
                'payload_repack': {'payload': {}},
            },
        ],
    },
)
async def test_queue_modes(
        taxi_client_notify,
        taxi_config,
        mockserver,
        stq,
        push_handler,
        push_request,
        send_mode,
        expected_code,
        xiva_called,
        queue_called,
):

    taxi_config.set_values(
        {
            'CLIENT_NOTIFY_SERVICES': {
                'eda_courier': {
                    'description': 'test',
                    'xiva_service': 'eda-courier-service',
                    'send_mode': send_mode,
                },
            },
        },
    )

    @mockserver.json_handler('/xiva/v2/send')
    def _xiva_send(request):
        return mockserver.make_response('InternalServerError', 500)

    response = await taxi_client_notify.post(
        push_handler,
        json=push_request,
        headers={'X-Idempotency-Token': 'test'},
    )
    assert response.status_code == expected_code

    assert _xiva_send.times_called == xiva_called
    assert stq.client_notify_fallback.times_called == queue_called


@pytest.mark.now('2020-06-26T14:00:00Z')
@pytest.mark.config(
    CLIENT_NOTIFY_SERVICES={
        'eda_courier': {
            'description': 'test',
            'xiva_service': 'eda-courier-service',
            'send_mode': 'fallback_queue',
        },
    },
)
async def test_queue_args(taxi_client_notify, mockserver, stq):
    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        return mockserver.make_response('InternalServerError', 500)

    response = await taxi_client_notify.post('v1/push', json=V1_PUSH)
    assert response.status_code == 200
    assert stq.client_notify_fallback.times_called == 1

    call = stq.client_notify_fallback.next_call()
    call.pop('id')
    link = call['kwargs']['log_extra']['_link']

    assert call == {
        'queue': 'client_notify_fallback',
        'args': [],
        'kwargs': {
            'client_id': 'courier1',
            'service': 'eda_courier',
            'intent': 'order_new',
            'body': {'payload': {}},
            'ttl': 91,
            'provider_name': 'xiva',
            'log_extra': {'_link': link},
            'device_id': '',
            'service_message_id': '123',
            'meta': '{}',
            'app_install_id': 'app-install-id',
        },
        'eta': datetime.datetime(2020, 6, 26, 14, 0),
    }


async def test_queue_task(taxi_client_notify, mockserver, stq_runner):
    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        assert request.json == {
            'payload': {'id': 'sample_task', 'alert': 'Hello'},
        }
        assert request.args == {
            'ttl': '91',
            'event': 'test',
            'user': 'courier1',
            'service': 'eda-courier-service',
        }
        return mockserver.make_response('OK', 200, headers={'TransitID': 'id'})

    await stq_runner.client_notify_fallback.call(
        task_id='sample_task',
        kwargs={
            'client_id': 'courier1',
            'service': 'eda_courier',
            'intent': 'test',
            'body': {'payload': {'alert': 'Hello'}},
            'ttl': 91,
            'provider_name': 'xiva',
            'app_install_id': '',
            'device_id': '',
            'service_message_id': '123',
            'meta': '{}',
        },
    )
