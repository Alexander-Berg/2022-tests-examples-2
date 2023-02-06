import pytest

TASK_START_NOTIFY = 'task-start-notify'


@pytest.mark.suspend_periodic_tasks(TASK_START_NOTIFY)
async def test_start_notfy_disabled(taxi_cashback_annihilator, stq):
    await taxi_cashback_annihilator.run_periodic_task(TASK_START_NOTIFY)

    assert stq.cashback_annihilation_notify.times_called == 0


@pytest.mark.suspend_periodic_tasks(TASK_START_NOTIFY)
@pytest.mark.config(
    CASHBACK_ANNIHILATOR_START_NOTIFY={
        'enabled': True,
        'butch_size': 2,
        'restart_ms': 10,
        'time_interval': {'time_start': 0, 'time_finish': 24},
    },
)
async def test_start_notfy_empty(taxi_cashback_annihilator, stq):
    await taxi_cashback_annihilator.run_periodic_task(TASK_START_NOTIFY)

    assert stq.cashback_annihilation_notify.times_called == 0


@pytest.mark.suspend_periodic_tasks(TASK_START_NOTIFY)
@pytest.mark.parametrize(
    'stq_calls',
    [
        pytest.param(
            2,
            marks=pytest.mark.config(
                CASHBACK_ANNIHILATOR_START_NOTIFY={
                    'enabled': True,
                    'butch_size': 2,
                    'restart_ms': 10,
                    'time_interval': {'time_start': 0, 'time_finish': 24},
                },
            ),
        ),
        pytest.param(
            4,
            marks=pytest.mark.config(
                CASHBACK_ANNIHILATOR_START_NOTIFY={
                    'enabled': True,
                    'butch_size': 100,
                    'restart_ms': 10,
                    'time_interval': {'time_start': 0, 'time_finish': 24},
                },
            ),
        ),
    ],
)
@pytest.mark.pgsql('cashback_annihilator', files=['balances.sql'])
async def test_start_notfy_happy_path(
        taxi_cashback_annihilator, stq, stq_calls,
):
    await taxi_cashback_annihilator.run_periodic_task(TASK_START_NOTIFY)

    assert stq.cashback_annihilation_notify.times_called == stq_calls

    stq_call = stq.cashback_annihilation_notify.next_call()
    assert stq_call['id'] == 'w/eb92da32-3174-5ca0-9df5-d42db472a355'
    assert stq_call['args'] == ['1111111']


# @pytest.mark.suspend_periodic_tasks(TASK_START_NOTIFY)
# @pytest.mark.config(
#     CASHBACK_ANNIHILATOR_START_NOTIFY={
#         'enabled': True,
#         'butch_size': 2,
#         'restart_ms': 10,
#         'time_interval': {
#             'time_start': 0,
#             'time_finish': 12,
#         },
#     },
# )
# @pytest.mark.now('2020-03-28T20:00:00+0000')
# @pytest.mark.pgsql('cashback_annihilator', files=['balances.sql'])
# async def test_wrong_time(taxi_cashback_annihilator, stq):
#     await taxi_cashback_annihilator.run_periodic_task(TASK_START_NOTIFY)
#
#     assert stq.cashback_annihilation_notify.times_called == 0
#
#
# @pytest.mark.suspend_periodic_tasks(TASK_START_NOTIFY)
# @pytest.mark.config(
#     CASHBACK_ANNIHILATOR_START_NOTIFY={
#         'enabled': True,
#         'butch_size': 2,
#         'restart_ms': 10,
#         'time_interval': {
#             'time_start': 23,
#             'time_finish': 5,
#         },
#     },
# )
# @pytest.mark.now('2020-03-28T20:00:00+0000')
# @pytest.mark.pgsql('cashback_annihilator', files=['balances.sql'])
# async def test_wrong_time2(taxi_cashback_annihilator, stq):
#     await taxi_cashback_annihilator.run_periodic_task(TASK_START_NOTIFY)
#
#     assert stq.cashback_annihilation_notify.times_called == 0


@pytest.mark.suspend_periodic_tasks(TASK_START_NOTIFY)
@pytest.mark.config(
    CASHBACK_ANNIHILATOR_START_NOTIFY={
        'enabled': True,
        'butch_size': 2,
        'restart_ms': 10,
        'time_interval': {'time_start': 23, 'time_finish': 20},
    },
)
@pytest.mark.now('2020-03-28T20:00:00+0000')
@pytest.mark.pgsql('cashback_annihilator', files=['balances.sql'])
async def test_good_time(taxi_cashback_annihilator, stq):
    await taxi_cashback_annihilator.run_periodic_task(TASK_START_NOTIFY)

    assert stq.cashback_annihilation_notify.times_called != 0


@pytest.mark.suspend_periodic_tasks(TASK_START_NOTIFY)
@pytest.mark.config(
    CASHBACK_ANNIHILATOR_START_NOTIFY={
        'enabled': True,
        'butch_size': 2,
        'restart_ms': 10,
        'time_interval': {'time_start': 19, 'time_finish': 23},
    },
)
@pytest.mark.now('2020-03-28T20:00:00+0000')
@pytest.mark.pgsql('cashback_annihilator', files=['balances.sql'])
async def test_good_time2(taxi_cashback_annihilator, stq):
    await taxi_cashback_annihilator.run_periodic_task(TASK_START_NOTIFY)

    assert stq.cashback_annihilation_notify.times_called != 0
