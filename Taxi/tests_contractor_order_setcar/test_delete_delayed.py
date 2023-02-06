import pytest

from tests_contractor_order_setcar import utils


@pytest.mark.parametrize(
    'client_events_enabled', [{'enable': True}, {'enable': False}],
)
@pytest.mark.redis_store(
    ['set', 'Order:Driver:CancelRequest:MD5:aaaa:bbbb', 'ETAG'],
    ['sadd', 'Order:Driver:Delayed:Items:aaaa:bbbb', 'delayed_order'],
    ['sadd', 'Order:Driver:Delayed:Items:aaaa:bbbb', 'delayed_order_2'],
)
async def test_add_delayed(
        taxi_contractor_order_setcar,
        redis_store,
        mockserver,
        taxi_config,
        client_events_enabled,
):
    taxi_config.set_values(
        {
            'CONTRACTOR_ORDER_SETCAR_ENABLE_CLIENT_EVENTS': (
                client_events_enabled
            ),
        },
    )

    @mockserver.json_handler('/client-events/push')
    def push(request):
        # check json request body
        assert 'update_type' in request.json['payload']
        assert (
            request.json['payload']['update_type'] == 'cancelled'
            or request.json['payload']['update_type'] == 'completed'
        )
        if request.json['payload']['update_type'] == 'cancelled':
            assert 'cancel_reason' in request.json['payload']
            assert 'message' in request.json['payload']['cancel_reason']
            assert 'category' in request.json['payload']['cancel_reason']
        else:
            assert 'cancel_reason' not in request.json['payload']
        return {'version': '123'}

    body = {'park_id': 'aaaa', 'profile_id': 'bbbb'}
    assert (
        redis_store.get('Order:Driver:CancelRequest:MD5:aaaa:bbbb') == b'ETAG'
    )
    response = await taxi_contractor_order_setcar.post(
        '/v1/order/cancel-delayed', json=body, headers=utils.HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'succeeded': True}
    assert (
        redis_store.get('Order:Driver:CancelRequest:MD5:aaaa:bbbb') != b'ETAG'
    )
    assert (
        redis_store.smembers('Order:Driver:Delayed:Items:aaaa:bbbb') == set()
    )
    assert push.times_called == 0
