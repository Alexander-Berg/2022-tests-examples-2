import json

import pytest

from tests_contractor_order_setcar import utils

ASSIGNED_TO_OTHER_DRIVER_KEY = 'assigned_to_other_driver'
ASSIGNED_TO_OTHER_DRIVER_MESSAGE = 'Назначен на другого водителя'
DEFAULT_CANCEL_REASON = 'Заказ отменен'


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
        'Order:Driver:CompleteRequest:Items:999:888',
        'Order1',
        'Order2',
    ],
    [
        'lpush',
        'Order:Driver:CancelReason:Items:999:888',
        json.dumps(
            {
                'alias_id': 'Order3',
                'message': ASSIGNED_TO_OTHER_DRIVER_KEY,
                'category': 'assigned_to_other_driver',
            },
        ),
        json.dumps(
            {
                'alias_id': 'Order4',
                'message': 'not_defined_message',
                'category': 'unknown',
            },
        ),
    ],
)
async def test_complete_request_setcar_statuses(
        taxi_contractor_order_setcar,
        redis_store,
        mockserver,
        taxi_config,
        stq_runner,
        experiments3,
):
    taxi_config.set_values(
        {'CONTRACTOR_ORDER_SETCAR_ENABLE_CLIENT_EVENTS': {'enable': True}},
    )

    @mockserver.json_handler('/client-events/push')
    def push(request):
        # check json request body
        assert 'setcar_statuses' in request.json['payload']
        assert request.json['payload']['setcar_statuses'] == [
            {'setcar_id': 'Order1', 'status': 'completed'},
            {'setcar_id': 'Order2', 'status': 'completed'},
            {'setcar_id': 'new_order', 'status': 'completed'},
            {
                'setcar_id': 'Order3',
                'status': 'cancelled',
                'reason': {
                    'category': 'assigned_to_other_driver',
                    'message': ASSIGNED_TO_OTHER_DRIVER_MESSAGE,
                },
            },
            {
                'setcar_id': 'Order4',
                'status': 'cancelled',
                'reason': {
                    'category': 'unknown',
                    'message': DEFAULT_CANCEL_REASON,
                },
            },
        ]
        return {'version': '123'}

    response = await taxi_contractor_order_setcar.post(
        '/v1/order/complete',
        headers=utils.HEADERS,
        json={'park_id': '999', 'profile_id': '888', 'alias_id': 'new_order'},
    )
    assert response.json() == {}
    assert response.status_code == 200
    await stq_runner.contractor_order_setcar_send_setcar_statuses.call(
        task_id='contractor_order_setcar_send_setcar_statuses',
        kwargs={
            'alias_id': 'new_order',
            'park_id': '999',
            'driver_profile_id': '888',
        },
    )
    assert push.times_called == 1


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
        'Order:Driver:CompleteRequest:Items:999:888',
        'Order1',
        'Order2',
    ],
    [
        'lpush',
        'Order:Driver:CancelReason:Items:999:888',
        json.dumps(
            {
                'alias_id': 'Order3',
                'message': ASSIGNED_TO_OTHER_DRIVER_KEY,
                'category': 'assigned_to_other_driver',
            },
        ),
        json.dumps(
            {
                'alias_id': 'Order4',
                'message': 'Why not?',
                'category': 'unknown',
            },
        ),
    ],
)
async def test_cancel_request_setcar_statuses(
        taxi_contractor_order_setcar,
        redis_store,
        mockserver,
        taxi_config,
        stq_runner,
):
    taxi_config.set_values(
        {'CONTRACTOR_ORDER_SETCAR_ENABLE_CLIENT_EVENTS': {'enable': True}},
    )

    @mockserver.json_handler('/client-events/push')
    def push(request):
        # check json request body
        assert 'setcar_statuses' in request.json['payload']
        assert request.json['payload']['setcar_statuses'] == [
            {'setcar_id': 'Order1', 'status': 'completed'},
            {'setcar_id': 'Order2', 'status': 'completed'},
            {
                'setcar_id': 'cancelled_order',
                'status': 'cancelled',
                'reason': {
                    'category': 'unknown',
                    'message': DEFAULT_CANCEL_REASON,
                },
            },
            {
                'setcar_id': 'Order3',
                'status': 'cancelled',
                'reason': {
                    'category': 'assigned_to_other_driver',
                    'message': ASSIGNED_TO_OTHER_DRIVER_MESSAGE,
                },
            },
            {
                'setcar_id': 'Order4',
                'status': 'cancelled',
                'reason': {
                    'category': 'unknown',
                    'message': DEFAULT_CANCEL_REASON,
                },
            },
        ]
        return {'version': '123'}

    body = {
        'park_id': '999',
        'profile_id': '888',
        'alias_id': 'cancelled_order',
        'cancel_reason': {'message': 'YA-message', 'category': 'unknown'},
    }

    response = await taxi_contractor_order_setcar.post(
        '/v1/order/cancel', headers=utils.HEADERS, json=body,
    )
    assert response.json() == {}
    assert response.status_code == 200
    await stq_runner.contractor_order_setcar_send_setcar_statuses.call(
        task_id='contractor_order_setcar_send_setcar_statuses',
        kwargs={
            'alias_id': 'cancelled_order',
            'park_id': '999',
            'driver_profile_id': '888',
        },
    )
    assert push.times_called == 1


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
@pytest.mark.redis_store()
async def test_first_complete_request(
        taxi_contractor_order_setcar,
        redis_store,
        mockserver,
        taxi_config,
        stq_runner,
):
    taxi_config.set_values(
        {'CONTRACTOR_ORDER_SETCAR_ENABLE_CLIENT_EVENTS': {'enable': True}},
    )

    @mockserver.json_handler('/client-events/push')
    def push(request):
        # check json request body
        assert 'setcar_statuses' in request.json['payload']
        assert request.json['payload']['setcar_statuses'] == [
            {'setcar_id': 'new_order', 'status': 'completed'},
        ]
        return {'version': '123'}

    response = await taxi_contractor_order_setcar.post(
        '/v1/order/complete',
        headers=utils.HEADERS,
        json={'park_id': '999', 'profile_id': '888', 'alias_id': 'new_order'},
    )
    assert response.json() == {}
    assert response.status_code == 200
    await stq_runner.contractor_order_setcar_send_setcar_statuses.call(
        task_id='contractor_order_setcar_send_setcar_statuses',
        kwargs={
            'alias_id': 'new_order',
            'park_id': '999',
            'driver_profile_id': '888',
        },
    )
    assert push.times_called == 1


HEADERS = {
    'User-Agent': 'Taximeter 9.1 (1234)',
    'Accept-Language': 'ru',
    'X-Request-Application-Version': '9.1',
    'X-YaTaxi-Park-Id': '999',
    'X-YaTaxi-Driver-Profile-Id': '888',
}

PAYLOAD = {
    'setcar_statuses': [
        {'setcar_id': 'Order1', 'status': 'completed'},
        {'setcar_id': 'Order2', 'status': 'completed'},
        {
            'setcar_id': 'Order3',
            'status': 'cancelled',
            'reason': {
                'category': 'assigned_to_other_driver',
                'message': ASSIGNED_TO_OTHER_DRIVER_MESSAGE,
            },
        },
        {
            'setcar_id': 'Order4',
            'status': 'cancelled',
            'reason': {
                'category': 'unknown',
                'message': DEFAULT_CANCEL_REASON,
            },
        },
    ],
}


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
@pytest.mark.experiments3(
    name='driver_orders_common_use_client_events_for_send_fields',
    consumers=['driver-orders-common/contractor_park'],
    default_value={'enabled': True, 'fields': ['setcar_statuses']},
    is_config=True,
)
@pytest.mark.redis_store(
    [
        'rpush',
        'Order:Driver:CompleteRequest:Items:999:888',
        'Order1',
        'Order2',
    ],
    [
        'lpush',
        'Order:Driver:CancelReason:Items:999:888',
        json.dumps(
            {
                'alias_id': 'Order3',
                'message': ASSIGNED_TO_OTHER_DRIVER_KEY,
                'category': 'assigned_to_other_driver',
            },
        ),
        json.dumps(
            {
                'alias_id': 'Order4',
                'message': 'Why not?',
                'category': 'unknown',
            },
        ),
    ],
)
async def test_state_handler_setcar_statuses(
        taxi_contractor_order_setcar,
        redis_store,
        mockserver,
        taxi_config,
        stq_runner,
):
    taxi_config.set_values(
        {'CONTRACTOR_ORDER_SETCAR_ENABLE_CLIENT_EVENTS': {'enable': True}},
    )

    @mockserver.json_handler('/client-events/push')
    def push(request):
        # check json request body
        assert 'setcar_statuses' in request.json['payload']
        assert request.json['payload'] == PAYLOAD
        return {'version': '124'}

    response = await taxi_contractor_order_setcar.post(
        '/driver/v1/order/setcar_statuses/pull', data={}, headers=HEADERS,
    )
    assert response.json() == {'version': '124', 'payload': PAYLOAD}
    assert response.status_code == 200
    assert push.times_called == 1


@pytest.mark.experiments3(
    name='driver_orders_common_use_client_events_for_send_fields',
    consumers=['driver-orders-common/contractor_park'],
    default_value={'enabled': True, 'fields': ['setcar_statuses']},
    is_config=True,
)
async def test_state_handler_setcar_statuses_first_pull(
        taxi_contractor_order_setcar,
        redis_store,
        mockserver,
        taxi_config,
        stq_runner,
):
    taxi_config.set_values(
        {'CONTRACTOR_ORDER_SETCAR_ENABLE_CLIENT_EVENTS': {'enable': True}},
    )

    @mockserver.json_handler('/client-events/push')
    def push(request):
        # check json request body
        assert 'setcar_statuses' in request.json['payload']
        return {'version': '124'}

    response = await taxi_contractor_order_setcar.post(
        '/driver/v1/order/setcar_statuses/pull', data={}, headers=HEADERS,
    )
    assert response.json() == {
        'version': '124',
        'payload': {'setcar_statuses': []},
    }
    assert response.status_code == 200
    assert push.times_called == 1
