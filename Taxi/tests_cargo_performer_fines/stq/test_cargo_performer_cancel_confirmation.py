import pytest


@pytest.mark.pgsql('cargo_performer_fines', files=['cancellation.sql'])
async def test_stq_happy_path(
        stq_runner,
        default_cargo_order_id,
        default_taxi_order_id,
        default_dbid_uuid,
        fetch_cancellation,
        fetch_performer_statistics,
):
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

    cancellation = fetch_cancellation('id=1')
    assert cancellation.cancel_id == 1
    assert cancellation.cargo_order_id == default_cargo_order_id
    assert cancellation.completed

    statistics = fetch_performer_statistics(
        f'driver_id=\'{driver_id}\' and park_id=\'{park_id}\'',
    )
    assert statistics.completed_orders == 0
    assert statistics.cancel_count == 1


@pytest.mark.pgsql('cargo_performer_fines', files=['cancellation.sql'])
async def test_stq_statistics_cancel_count_check_idempotency(
        stq_runner,
        default_cargo_order_id,
        default_taxi_order_id,
        default_dbid_uuid,
        fetch_performer_statistics,
):
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

    statistics = fetch_performer_statistics(
        f'driver_id=\'{driver_id}\' and park_id=\'{park_id}\'',
    )
    assert statistics.completed_orders == 0
    assert statistics.cancel_count == 1
