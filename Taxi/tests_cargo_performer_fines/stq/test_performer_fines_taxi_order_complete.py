import pytest


@pytest.mark.parametrize('order_complete_first_call', [True, False])
@pytest.mark.parametrize('required_completed_orders', [1, 2])
@pytest.mark.pgsql('cargo_performer_fines', files=['cancellation.sql'])
async def test_stq_happy_path(
        stq_runner,
        default_cargo_order_id,
        default_taxi_order_id,
        default_dbid_uuid,
        fetch_performer_statistics,
        mock_create_event,
        start_stq_event,
        mock_fetch_events,
        exp3_performer_cancel_limits,
        order_complete_first_call,
        required_completed_orders,
):
    mock_create_event()
    mock_fetch_events(
        events=[] if order_complete_first_call else [start_stq_event()],
    )
    await exp3_performer_cancel_limits(
        required_completed_orders=required_completed_orders,
    )

    park_id = default_dbid_uuid['dbid']
    driver_id = default_dbid_uuid['uuid']

    await stq_runner.cargo_performer_cancel_confirmation.call(
        task_id='test_stq',
        kwargs={
            'cargo_order_id': default_cargo_order_id,
            'taxi_order_id': default_taxi_order_id,
            'cancel_id': 1,
            'park_id': park_id,
            'driver_id': driver_id,
        },
    )

    await stq_runner.cargo_performer_fines_taxi_order_complete.call(
        task_id='test_stq',
        kwargs={
            'cargo_order_id': default_cargo_order_id,
            'park_id': park_id,
            'driver_id': driver_id,
            'tariff_class': 'courier',
        },
    )

    statistics = fetch_performer_statistics(
        f'driver_id=\'{driver_id}\' and park_id=\'{park_id}\'',
    )
    assert statistics.completed_orders == 1
    assert statistics.cancel_count == required_completed_orders - 1


@pytest.mark.pgsql('cargo_performer_fines', files=['cancellation.sql'])
async def test_stq_idempotency(
        stq_runner,
        default_cargo_order_id,
        default_taxi_order_id,
        default_dbid_uuid,
        fetch_performer_statistics,
        mock_create_event,
        start_stq_event,
        mock_fetch_events,
        exp3_performer_cancel_limits,
):
    mock_create_event()
    mock_fetch_events(events=[start_stq_event(stq_task_id='other')])
    await exp3_performer_cancel_limits(required_completed_orders=1)

    park_id = default_dbid_uuid['dbid']
    driver_id = default_dbid_uuid['uuid']

    await stq_runner.cargo_performer_cancel_confirmation.call(
        task_id='test_stq',
        kwargs={
            'cargo_order_id': default_cargo_order_id,
            'taxi_order_id': default_taxi_order_id,
            'cancel_id': 1,
            'park_id': park_id,
            'driver_id': driver_id,
        },
    )

    await stq_runner.cargo_performer_fines_taxi_order_complete.call(
        task_id='test_stq',
        kwargs={
            'cargo_order_id': default_cargo_order_id,
            'park_id': park_id,
            'driver_id': driver_id,
            'tariff_class': 'courier',
        },
    )

    statistics = fetch_performer_statistics(
        f'driver_id=\'{driver_id}\' and park_id=\'{park_id}\'',
    )
    assert statistics.completed_orders == 0
    assert statistics.cancel_count == 1
