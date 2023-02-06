TAXIMETER_UPDATE_STATUS_PUSH_CODE = 1600
FORCE_POLLING_ORDER_ACTION = 'ForcePollingOrder'
COLLAPSE_KEY = 'I_AM_SO_COLLAPSED'


async def test_stq_send_force_push(stq_runner, client_notify):
    await stq_runner.driver_orders_send_communications_notifications.call(
        task_id='task-id',
        args=[
            'park_id',
            'driver_id',
            'order_id',
            TAXIMETER_UPDATE_STATUS_PUSH_CODE,
            FORCE_POLLING_ORDER_ACTION,
        ],
        expect_fail=False,
    )

    assert client_notify.times_called == 1
    assert client_notify.next_call()['request'].json == {
        'client_id': 'park_id-driver_id',
        'service': 'taximeter',
        'intent': FORCE_POLLING_ORDER_ACTION,
        'data': {'code': TAXIMETER_UPDATE_STATUS_PUSH_CODE},
    }


async def test_stq_send_force_push_data(stq_runner, client_notify):
    await stq_runner.driver_orders_send_communications_notifications.call(
        task_id='task-id',
        args=[
            'park_id',
            'driver_id',
            'order_id',
            TAXIMETER_UPDATE_STATUS_PUSH_CODE,
            FORCE_POLLING_ORDER_ACTION,
            {'test': 1},
        ],
        expect_fail=False,
    )

    assert client_notify.times_called == 1
    assert client_notify.next_call()['request'].json == {
        'client_id': 'park_id-driver_id',
        'service': 'taximeter',
        'intent': FORCE_POLLING_ORDER_ACTION,
        'data': {'code': TAXIMETER_UPDATE_STATUS_PUSH_CODE, 'test': 1},
    }


async def test_stq_send_force_push_(stq_runner, client_notify):
    await stq_runner.driver_orders_send_communications_notifications.call(
        task_id='task-id',
        args=[
            'park_id',
            'driver_id',
            'order_id',
            TAXIMETER_UPDATE_STATUS_PUSH_CODE,
            FORCE_POLLING_ORDER_ACTION,
            None,
            None,
            COLLAPSE_KEY,
        ],
        expect_fail=False,
    )

    assert client_notify.times_called == 1
    assert client_notify.next_call()['request'].json == {
        'client_id': 'park_id-driver_id',
        'service': 'taximeter',
        'intent': FORCE_POLLING_ORDER_ACTION,
        'collapse_key': COLLAPSE_KEY,
        'data': {'code': TAXIMETER_UPDATE_STATUS_PUSH_CODE},
    }
