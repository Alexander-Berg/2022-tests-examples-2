import datetime
import json

import pytest


@pytest.mark.parametrize(
    'event_request,client_notify_request',
    [
        # with payload and event id
        (
            {
                'service': 'service',
                'channel': 'contractor:dbid1_uuid1',
                'event': 'event',
                'event_id': 'event_id',
                'payload': {'some': 'data'},
                'ttl': 300,
            },
            {
                'service': 'taximeter',
                'client_id': 'dbid1-uuid1',
                'intent': 'ClientEvent',
                'data': {
                    'event': 'event',
                    'id': 'event_id',
                    'payload': {'some': 'data'},
                },
                'ttl': 300,
            },
        ),
        # without payload and event id
        (
            {
                'service': 'service',
                'channel': 'contractor:dbid1_uuid1',
                'event': 'event',
                'ttl': 300,
            },
            {
                'service': 'taximeter',
                'client_id': 'dbid1-uuid1',
                'intent': 'ClientEvent',
                'data': {'event': 'event', 'has_payload': False},
                'ttl': 300,
            },
        ),
    ],
)
async def test_request(
        taxi_client_events, mockserver, event_request, client_notify_request,
):
    @mockserver.json_handler('/client-notify/v2/push')
    def _client_notify_push(request):
        assert 'version' in request.json['data']
        assert request.json['data']['version']

        del request.json['data']['version']

        assert request.json == client_notify_request

        return mockserver.make_response(
            json.dumps({'notification_id': 'some_id'}), status=200,
        )

    response = await taxi_client_events.post('push', json=event_request)
    assert response.status_code == 200

    await _client_notify_push.wait_call()


@pytest.mark.parametrize('send_notification', [True, False])
@pytest.mark.now('2021-02-20T00:00:00Z')
async def test_push_with_notification_field(
        taxi_client_events, mockserver, mongodb, send_notification,
):
    @mockserver.json_handler('/client-notify/v2/push')
    def _client_notify_push():
        return {'notification_id': 'some_id'}

    response = await taxi_client_events.post(
        'push',
        json={
            'service': 'service',
            'channel': 'contractor:dbid1_uuid1',
            'event': 'event',
            'event_id': 'event_id',
            'payload': {'some': 'data'},
            'send_notification': send_notification,
            'ttl': 600,
        },
    )
    assert response.status_code == 200
    assert 'version' in response.json()

    events = list(mongodb.client_events_events.find({}))

    if send_notification:
        assert events[0]['notification_sent'] == datetime.datetime(
            2021, 2, 20, 0, 0,
        )
    else:
        assert 'notification_sent' not in events[0]


@pytest.mark.config(CLIENT_EVENTS_NOTIFIERS_SETTINGS={'max_payload_size': 15})
async def test_large_payload(taxi_client_events, mockserver):
    @mockserver.json_handler('/client-notify/v2/push')
    def _client_notify_push(request):
        return mockserver.make_response(json.dumps({}), status=200)

    request_body = {
        'service': 'service',
        'channel': 'contractor:dbid_uuid',
        'event': 'event',
        'payload': {'some': 'toolargedata'},
    }
    response = await taxi_client_events.post('push', json=request_body)
    assert response.status_code == 200

    assert not _client_notify_push.has_calls


async def test_invalid_channel(taxi_client_events, mockserver):
    @mockserver.json_handler('/client-notify/v2/push')
    def _client_notify_push(request):
        return mockserver.make_response(json.dumps({}), status=200)

    request_body = {
        'service': 'service',
        'channel': 'invalid',
        'event': 'event',
    }
    response = await taxi_client_events.post('push', json=request_body)
    assert response.status_code == 200

    assert not _client_notify_push.has_calls
