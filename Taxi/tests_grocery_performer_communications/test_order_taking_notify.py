import pytest

import tests_grocery_performer_communications.constants as consts

# (performer_id)_(order_id)
TASK_ID = f'{consts.PERFORMER_ID}_{consts.ORDER["order_id"]}'

# idempotency key for driver-wall service is sha256 hash of
# {performer_id}_{task_id}
PERFORMER_ID_ORDER_ID_SHA256 = (
    'd1c31ed52fb7152361c38f1f435bfda627ca542e06980b8a1b52bb3b698dfcc4'
)


@pytest.mark.experiments3(filename='experiments3.json')
async def test_grocery_performer_communications_order_taking_notify_success(
        stq_runner, mockserver, testpoint,
):
    @mockserver.json_handler('driver-wall/internal/driver-wall/v1/add')
    def driver_wall_add(request):
        assert request.json == {
            'id': PERFORMER_ID_ORDER_ID_SHA256,
            'service': 'test_service',
            'template': {
                'title': {
                    'keyset': consts.KEYSET,
                    'key': 'order_taking_notification_title',
                    'params': {},
                },
                'text': {
                    'keyset': consts.KEYSET,
                    'key': 'order_taking_notification_template',
                    'params': {
                        'currency': 'RUB',
                        'deliver_by': '22-06-2021 13:00:00',
                        'depot_short_address': consts.DEPOT_SHORT_ADDRESS,
                        'order_id': consts.ORDER['short_order_id'],
                        'total_price': '101.21',
                    },
                },
                'type': 'newsletter',
                'format': 'markdown',
            },
            'drivers': [{'driver': consts.PERFORMER_ID}],
        }
        assert (
            request.headers['X-Idempotency-Token']
            == PERFORMER_ID_ORDER_ID_SHA256
        )
        return mockserver.make_response(status=200, json={'id': '1'})

    @testpoint('order_taking_notify_task_finished_success')
    def task_finished(param):
        pass

    await stq_runner.grocery_performer_communications_order_taking_notify.call(
        task_id=TASK_ID, args=[consts.PERFORMER_ID, consts.ORDER],
    )

    assert driver_wall_add.times_called == 1
    assert task_finished.times_called == 1


@pytest.mark.config(
    GROCERY_PERFORMER_COMMUNICATIONS_STQ_SETTINGS={
        '__default__': {'max-reschedules': 30, 'reschedule-sleep-ms': 1000},
        'grocery_performer_communications_order_taking_notify': {
            'max-reschedules': 10,
            'reschedule-sleep-ms': 2000,
        },
    },
)
@pytest.mark.experiments3(filename='experiments3.json')
async def test_order_taking_notify_reschedule_if_error_driver_wall_return(
        stq_runner, mockserver, testpoint,
):
    @mockserver.json_handler('driver-wall/internal/driver-wall/v1/add')
    def driver_wall_add(request):
        return mockserver.make_response(
            status=409, json={'code': '409', 'message': 'conflict'},
        )

    @testpoint(
        'grocery_performer_communications_order_taking_notify_'
        'task_rescheduled',
    )
    def task_rescheduled(param):
        assert param['task_id'] == TASK_ID
        assert param['delay'] == 2000

    await stq_runner.grocery_performer_communications_order_taking_notify.call(
        task_id=TASK_ID, args=[consts.PERFORMER_ID, consts.ORDER],
    )

    assert driver_wall_add.times_called == 1
    assert task_rescheduled.times_called == 1


@pytest.mark.config(
    GROCERY_PERFORMER_COMMUNICATIONS_STQ_SETTINGS={
        '__default__': {'max-reschedules': 30, 'reschedule-sleep-ms': 1000},
        'grocery_performer_communications_order_taking_notify': {
            'max-reschedules': 10,
            'reschedule-sleep-ms': 2000,
        },
    },
)
@pytest.mark.experiments3(filename='experiments3.json')
async def test_order_taking_notify_stop_reschedule_when_exceed_counter(
        stq_runner, mockserver, testpoint,
):
    @mockserver.json_handler('driver-wall/internal/driver-wall/v1/add')
    def driver_wall_add(request):
        return mockserver.make_response(
            status=409, json={'code': '409', 'message': 'conflict'},
        )

    @testpoint(
        'grocery_performer_communications_order_taking_notify_'
        'task_finished_count_reached',
    )
    def task_reschedule_finished(param):
        pass

    await stq_runner.grocery_performer_communications_order_taking_notify.call(
        task_id=TASK_ID,
        args=[consts.PERFORMER_ID, consts.ORDER],
        reschedule_counter=11,
    )

    assert driver_wall_add.times_called == 1
    assert task_reschedule_finished.times_called == 1
