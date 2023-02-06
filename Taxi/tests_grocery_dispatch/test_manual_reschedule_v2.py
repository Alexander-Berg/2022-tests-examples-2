from tests_grocery_dispatch import configs


@configs.DISPATCH_PRIORITY_CONFIG_TEST
@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_reschedule_v2(
        taxi_grocery_dispatch, grocery_dispatch_pg, testpoint, stq, stq_runner,
):
    @testpoint('test_dispatch_cancel')
    def check_cancellation_data(data):
        dispatch_info = data['dispatch']
        assert dispatch_info['wave'] == 0

    @testpoint('test_dispatch_schedule')
    def check_scheduling_data(data):
        dispatch_info = data['dispatch']
        assert dispatch_info['wave'] == 1
        order_info = data['order']
        assert 'due' not in order_info

    dispatch = grocery_dispatch_pg.create_dispatch(status='scheduled')

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v2/manual/reschedule',
        json={
            'order_id': dispatch.order_id,
            'options': {},
            'idempotency_token': 'token',
        },
    )

    assert response.status_code == 200
    assert stq.grocery_dispatch_reschedule_executor.times_called == 1
    assert check_cancellation_data.times_called == 0
    assert check_scheduling_data.times_called == 0

    call_data = stq.grocery_dispatch_reschedule_executor.next_call()
    task_id = f'{dispatch.dispatch_id}_token'
    assert call_data['id'] == task_id
    assert call_data['kwargs']['dispatch_id'] == dispatch.dispatch_id
    assert call_data['kwargs']['idempotency_token'] == 'token'

    await stq_runner.grocery_dispatch_reschedule_executor.call(
        task_id=task_id,
        kwargs={
            'dispatch_id': dispatch.dispatch_id,
            'idempotency_token': 'token',
        },
    )

    assert check_cancellation_data.times_called == 1
    assert check_scheduling_data.times_called == 1
    assert dispatch.status == 'scheduled'
    assert dispatch.wave == 1


@configs.DISPATCH_PRIORITY_CONFIG_FULL
@configs.DISPATCH_CLAIM_CONFIG_PULL_DISPATCH
@configs.DISPATCH_GENERAL_CONFIG
@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_reschedule_v2_change_dispatch_type(
        taxi_grocery_dispatch,
        grocery_dispatch_pg,
        testpoint,
        stq,
        stq_runner,
        pgsql,
        cargo,
):
    dispatch = grocery_dispatch_pg.create_dispatch(
        status='scheduled', dispatch_name='cargo_sync',
    )
    assert dispatch.dispatch_name == 'cargo_sync'

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v2/manual/reschedule',
        json={
            'order_id': dispatch.order_id,
            'options': {'taxi_only': True},
            'idempotency_token': 'token',
        },
    )

    assert response.status_code == 200
    assert stq.grocery_dispatch_reschedule_executor.times_called == 1

    call_data = stq.grocery_dispatch_reschedule_executor.next_call()
    task_id = f'{dispatch.dispatch_id}_token'
    assert call_data['id'] == task_id
    assert call_data['kwargs']['dispatch_id'] == dispatch.dispatch_id
    assert call_data['kwargs']['idempotency_token'] == 'token'

    await stq_runner.grocery_dispatch_reschedule_executor.call(
        task_id=task_id,
        kwargs={
            'dispatch_id': dispatch.dispatch_id,
            'idempotency_token': 'token',
        },
    )

    assert dispatch.status == 'scheduled'
    assert dispatch.wave == 1
    assert dispatch.dispatch_name == 'cargo_taxi'
