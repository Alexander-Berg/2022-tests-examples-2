import pytest

EXPIRED_ID = '61234567-89ab-cdef-0123-456789abcdeb'
WINNER_NOT_DRIVING_ACCEPT_ID = '61234567-89ab-cdef-0123-456789abcdec'
WINNER_DRIVING_ACCEPT_ID = '61234567-89ab-cdef-0123-456789abcdef'


@pytest.mark.now('2022-02-08T12:00:00+0300')
@pytest.mark.pgsql(
    'contractor_orders_multioffer', files=['multioffer_multi_with_winner.sql'],
)
@pytest.mark.parametrize(
    'multioffer_id, multioffer_ok',
    [(WINNER_DRIVING_ACCEPT_ID, True), (EXPIRED_ID, False)],
)
@pytest.mark.parametrize(
    'order_proc_fields, order_proc_ok',
    [
        ({'order': {'status': 'cancelled'}}, False),
        ({'order': {'status': 'pending', 'taxi_status': 'cancelled'}}, False),
        ({'order': {'status': 'pending', 'taxi_status': 'expired'}}, False),
        ({'order': {'status': 'driving'}}, False),
        (
            {
                'order': {
                    'status': 'driving',
                    'performer': {
                        'db_id': 'park_id',
                        'uuid': 'driver_profile_id2',
                        'taxi_alias': {'id': 'alias_id2'},
                    },
                },
            },
            False,
        ),
        (
            {
                'order': {
                    'status': 'driving',
                    'performer': {
                        'db_id': 'park_id',
                        'uuid': 'driver_profile_id1',
                        'taxi_alias': {'id': 'alias_id1'},
                    },
                },
            },
            True,
        ),
    ],
)
@pytest.mark.parametrize('ready_for_finalize', [True, False])
@pytest.mark.config(
    CONTRACTOR_ORDERS_MULTIOFFER_FINALIZE_SETTINGS={
        'enable': True,
        'finalize_timeout': 20,
        'dead_timeout': 60,
        'cancel_expired': True,
    },
    CONTRACTOR_ORDERS_MULTIOFFER_STQ_MAX_RETRIES={
        'contractor_orders_multioffer_finalize': {'max_retries': 1},
    },
)
async def test_stq_finalize(
        stq,
        stq_runner,
        mocked_time,
        order_proc,
        multioffer_id,
        multioffer_ok,
        order_proc_fields,
        order_proc_ok,
        ready_for_finalize,
        driver_orders_app_api,
        taxi_config,
):
    if ready_for_finalize:
        mocked_time.sleep(60)
    order_proc.set_response(order_proc_fields)

    await stq_runner.contractor_orders_multioffer_finalize.call(
        task_id='task-id',
        args=[multioffer_id, 'order_id'],
        expect_fail=False,
        reschedule_counter=0,
    )

    dead_happy = all((order_proc_ok, multioffer_ok))
    stq_finalize = stq.contractor_orders_multioffer_finalize
    cancels = driver_orders_app_api.bulk_cancel_called

    assert cancels == int(ready_for_finalize and not dead_happy)
    assert stq_finalize.times_called == int(not ready_for_finalize)
    if not ready_for_finalize:
        assert stq_finalize.next_call()['id'] == 'task-id'
