import json

import pytest


@pytest.mark.experiments3(
    name='driver_orders_common_hide_reasons_in_setcar_statuses',
    consumers=['driver-orders-common/contractor_park'],
    default_value={'default': False, 'enabled': True},
    clauses=[
        {
            'predicate': {'type': 'true'},
            'value': {'default': False, 'enabled': True},
        },
    ],
    is_config=True,
)
@pytest.mark.redis_store(
    [
        'rpush',
        'Order:Driver:CompleteRequest:Items:park_id_0:driver_id_0',
        'completed_id_1',
        'completed_id_2',
    ],
    [
        'lpush',
        'Order:Driver:CancelReason:Items:park_id_0:driver_id_0',
        json.dumps(
            {
                'alias_id': 'multioffer_cancelled_id',
                'message': 'assigned_to_other_driver',
                'category': 'assigned_to_other_driver',
            },
        ),
        json.dumps(
            {
                'alias_id': 'undefined_cancelled_id',
                'message': 'undefined message',
                'category': 'unknown',
            },
        ),
    ],
    ['sadd', 'Order:Driver:Delayed:Items:park_id_0:driver_id_0', 'delayed_id'],
)
@pytest.mark.parametrize('use_client_event', [False, True])
@pytest.mark.config(
    CONTRACTOR_ORDER_SETCAR_ENABLE_CLIENT_EVENTS={'enable': True},
)
async def test_setcar_statuses_pull(
        taxi_contractor_order_setcar,
        redis_store,
        mockserver,
        taxi_config,
        experiments3,
        use_client_event,
):
    auth = {
        'Accept-Language': 'ru',
        'User-Agent': 'Taximeter 9.07 (1234)',
        'X-Request-Application': 'taximeter',
        'X-Request-Application-Version': '9.07 (1234)',
        'X-Request-Platform': 'android',
        'X-Request-Version-Type': '',
        'X-YaTaxi-Driver-Profile-Id': 'driver_id_0',
        'X-YaTaxi-Park-Id': 'park_id_0',
    }

    experiments3.add_config(
        name='driver_orders_common_use_client_events_for_send_fields',
        match={'predicate': {'type': 'true'}, 'enabled': use_client_event},
        consumers=['driver-orders-common/contractor_park'],
        clauses=[],
        default_value={
            'enabled': use_client_event,
            'fields': ['setcar_statuses'],
        },
    )
    await taxi_contractor_order_setcar.invalidate_caches()

    @mockserver.json_handler('/client-events/push')
    def push(request):
        return {'version': '123'}

    expected_setcar_statuses = [
        {'setcar_id': 'completed_id_1', 'status': 'completed'},
        {'setcar_id': 'completed_id_2', 'status': 'completed'},
        {
            'setcar_id': 'multioffer_cancelled_id',
            'status': 'cancelled',
            'reason': {
                'category': 'assigned_to_other_driver',
                'message': 'Назначен на другого водителя',
            },
        },
        {
            'setcar_id': 'undefined_cancelled_id',
            'status': 'cancelled',
            'reason': {'category': 'unknown', 'message': 'Заказ отменен'},
        },
        {
            'setcar_id': 'delayed_id',
            'status': 'cancelled',
            'reason': {
                'category': 'unknown',
                'message': 'Order was cancelled',
            },
        },
    ]

    response = await taxi_contractor_order_setcar.post(
        '/driver/v1/order/setcar_statuses/pull', headers=auth,
    )

    if use_client_event:
        assert push.has_calls

        assert response.status_code == 200
        assert response.json()['version'] == '123'
        assert (
            response.json()['payload']['setcar_statuses']
            == expected_setcar_statuses
        )
    else:
        assert not push.has_calls
        assert response.status_code == 400
