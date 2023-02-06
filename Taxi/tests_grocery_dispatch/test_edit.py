from tests_grocery_dispatch import configs
from tests_grocery_dispatch import constants
from tests_grocery_dispatch.plugins import models


@configs.DISPATCH_PRIORITY_CONFIG_TEST
@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_edit_order_info(
        taxi_grocery_dispatch, grocery_dispatch_pg, stq, stq_runner,
):
    order = models.OrderInfo(depot_id=constants.DEPOT_ID)
    dispatch = grocery_dispatch_pg.create_dispatch(
        dispatch_name='cargo_sync', status='matched', order=order,
    )

    assert dispatch.order.street == order.street

    new_street = 'New awesome street'

    request_data = {
        'dispatch_id': dispatch.dispatch_id,
        'idempotency_token': 'token',
        'new_data': {'street': new_street},
    }
    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/edit', request_data,
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

    assert dispatch.order.street == new_street


@configs.MODELER_DECISION_CONFIG_DISABLED
async def test_edit_409(taxi_grocery_dispatch, grocery_dispatch_pg):
    dispatch = grocery_dispatch_pg.create_dispatch(
        dispatch_name='cargo_sync',
        status='delivering',
        order=models.OrderInfo(depot_id=constants.DEPOT_ID),
    )

    request_data = {
        'dispatch_id': dispatch.dispatch_id,
        'idempotency_token': '',
        'new_data': {},
    }
    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/edit', request_data,
    )

    assert response.status_code == 409


async def test_edit_404(taxi_grocery_dispatch):
    request_data = {
        'dispatch_id': constants.DISPATCH_ID,
        'idempotency_token': '',
        'new_data': {},
    }
    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/edit', request_data,
    )

    assert response.status_code == 404
