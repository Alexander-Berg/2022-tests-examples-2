import datetime

import pytest


async def test_2can_metrics(
        state_payment_confirmed,
        taxi_cargo_payments,
        load_json_var,
        taxi_cargo_payments_monitor,
):
    state = await state_payment_confirmed()

    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='40',
        ),
    )
    assert response.status_code == 200
    metric = await taxi_cargo_payments_monitor.get_metric('all_signals')
    assert '2can_status_Payment_PAY' in metric


@pytest.mark.config(
    CARGO_PAYMENTS_METRICS_COLLECTOR={
        'enabled': True,
        'unprocessed_limit_payments_history': 10,
        'unprocessed_limit_payments': 10,
        'soon': {'left': 2147483647, 'right': 0},
        'delayed': {'left': 2147483647, 'right': 0},
        'history_poll_duration': 1,
        'selected_statuses': ['new', 'confirmed', 'authorized', 'finished'],
    },
)
async def test_metrics_collector(
        state_payment_authorized,
        taxi_cargo_payments,
        run_metrics_collector,
        testpoint,
        mocked_time,
):
    """
      Database uses real time and metrics_collector uses mocked time, so we are
      setting now to year 2081 and set left border of time interval to INT_MAX
      (around 65 years in seconds).

      During chosen period of time the only confirmed payment became authorized
      so all rates should be 1.
    """
    await state_payment_authorized()
    mocked_time.set(datetime.datetime(2081, 1, 1, 0, 0, 3))

    @testpoint('metrics_collector::result')
    def _metrics_collector_result(data):
        assert data['soon_confirmed_rate'] == 1
        assert data['soon_authorized_rate'] == 1
        assert data['delayed_confirmed_rate'] == 1
        assert data['delayed_authorized_rate'] == 1

        assert data['payments']['new']['labeled'] == 1
        assert data['payments']['confirmed']['labeled'] == 1
        assert data['payments']['authorized']['labeled'] == 1
        assert data['payments']['finished']['labeled'] == 0

    @testpoint('metrics_collector::stop_poll')
    async def _metrics_collector_stop_poll(data):
        mocked_time.sleep(5)
        await taxi_cargo_payments.update_server_state()

    await run_metrics_collector()
