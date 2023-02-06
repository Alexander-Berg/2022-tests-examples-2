import pytest

TASK_START_ANNIHILATION = 'task-start-annihilation'


@pytest.mark.suspend_periodic_tasks(TASK_START_ANNIHILATION)
async def test_start_annihilation_disabled(taxi_cashback_annihilator, stq):
    await taxi_cashback_annihilator.run_periodic_task(TASK_START_ANNIHILATION)

    assert stq.cashback_start_annihilation.times_called == 0


@pytest.mark.suspend_periodic_tasks(TASK_START_ANNIHILATION)
@pytest.mark.config(
    CASHBACK_ANNIHILATOR_START_ANNIHILATION={
        'enabled': True,
        'butch_size': 2,
        'restart_ms': 10,
    },
)
async def test_start_annihilation_empty(taxi_cashback_annihilator, stq):
    await taxi_cashback_annihilator.run_periodic_task(TASK_START_ANNIHILATION)

    assert stq.cashback_start_annihilation.times_called == 0


@pytest.mark.suspend_periodic_tasks(TASK_START_ANNIHILATION)
@pytest.mark.parametrize(
    'stq_calls',
    [
        pytest.param(
            1,
            marks=[
                pytest.mark.config(
                    CASHBACK_ANNIHILATOR_START_ANNIHILATION={
                        'enabled': True,
                        'butch_size': 1,
                        'restart_ms': 10,
                    },
                ),
                pytest.mark.now('2024-07-13T20:00:00+0000'),
            ],
        ),
        pytest.param(
            2,
            marks=[
                pytest.mark.config(
                    CASHBACK_ANNIHILATOR_START_ANNIHILATION={
                        'enabled': True,
                        'butch_size': 100,
                        'restart_ms': 10,
                    },
                ),
                pytest.mark.now('2024-07-13T20:00:00+0000'),
            ],
        ),
    ],
)
@pytest.mark.pgsql(
    'cashback_annihilator', files=['balances.sql', 'transactions.sql'],
)
async def test_start_annihilation(taxi_cashback_annihilator, stq, stq_calls):
    await taxi_cashback_annihilator.run_periodic_task(TASK_START_ANNIHILATION)

    assert stq.cashback_start_annihilation.times_called == stq_calls


@pytest.mark.suspend_periodic_tasks(TASK_START_ANNIHILATION)
@pytest.mark.parametrize(
    'stq_calls',
    [
        pytest.param(
            0,
            marks=[
                pytest.mark.config(
                    CASHBACK_ANNIHILATOR_START_ANNIHILATION={
                        'enabled': True,
                        'butch_size': 1,
                        'restart_ms': 10,
                        'time_interval': {'time_start': 0, 'time_finish': 12},
                    },
                ),
                pytest.mark.now('2024-07-13T13:00:00+0000'),
            ],
        ),
        pytest.param(
            0,
            marks=[
                pytest.mark.config(
                    CASHBACK_ANNIHILATOR_START_ANNIHILATION={
                        'enabled': True,
                        'butch_size': 1,
                        'restart_ms': 10,
                        'time_interval': {'time_start': 23, 'time_finish': 5},
                    },
                ),
                pytest.mark.now('2024-07-13T13:00:00+0000'),
            ],
        ),
        pytest.param(
            0,
            marks=[
                pytest.mark.config(
                    CASHBACK_ANNIHILATOR_START_ANNIHILATION={
                        'enabled': True,
                        'butch_size': 1,
                        'restart_ms': 10,
                        'time_interval': {'time_start': 19, 'time_finish': 7},
                    },
                ),
                pytest.mark.now('2024-07-13T12:00:00+0000'),
            ],
        ),
        pytest.param(
            0,
            marks=[
                pytest.mark.config(
                    CASHBACK_ANNIHILATOR_START_ANNIHILATION={
                        'enabled': True,
                        'butch_size': 1,
                        'restart_ms': 10,
                        'time_interval': {'time_start': 19, 'time_finish': 7},
                    },
                ),
                pytest.mark.now('2024-07-12T12:00:00+0000'),
            ],
        ),
        pytest.param(
            1,
            marks=[
                pytest.mark.config(
                    CASHBACK_ANNIHILATOR_START_ANNIHILATION={
                        'enabled': True,
                        'butch_size': 1,
                        'restart_ms': 10,
                        'time_interval': {'time_start': 19, 'time_finish': 7},
                    },
                ),
                pytest.mark.now('2024-07-13T20:00:00+0000'),
            ],
        ),
        pytest.param(
            2,
            marks=[
                pytest.mark.config(
                    CASHBACK_ANNIHILATOR_START_ANNIHILATION={
                        'enabled': True,
                        'butch_size': 10,
                        'restart_ms': 10,
                        'time_interval': {'time_start': 19, 'time_finish': 7},
                    },
                ),
                pytest.mark.now('2024-07-13T23:00:00+0000'),
            ],
        ),
        pytest.param(
            2,
            marks=[
                pytest.mark.config(
                    CASHBACK_ANNIHILATOR_START_ANNIHILATION={
                        'enabled': True,
                        'butch_size': 10,
                        'restart_ms': 10,
                        'time_interval': {'time_start': 19, 'time_finish': 7},
                    },
                ),
                pytest.mark.now('2024-07-14T06:00:00+0000'),
            ],
        ),
        pytest.param(
            1,
            marks=[
                pytest.mark.config(
                    CASHBACK_ANNIHILATOR_START_ANNIHILATION={
                        'enabled': True,
                        'butch_size': 1,
                        'restart_ms': 10,
                        'time_interval': {'time_start': 19, 'time_finish': 7},
                    },
                ),
                pytest.mark.now('2024-07-14T19:00:00+0000'),
            ],
        ),
    ],
)
@pytest.mark.pgsql(
    'cashback_annihilator', files=['balances.sql', 'transactions.sql'],
)
async def test_is_correct_time(taxi_cashback_annihilator, stq, stq_calls):
    await taxi_cashback_annihilator.run_periodic_task(TASK_START_ANNIHILATION)

    assert stq.cashback_start_annihilation.times_called == stq_calls
