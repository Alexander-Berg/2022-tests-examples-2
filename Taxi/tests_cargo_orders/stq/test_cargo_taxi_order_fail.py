import pytest


async def test_waybill_basic(
        stq_runner, mock_dispatch_mark_fail, default_order_id,
):
    await stq_runner.cargo_taxi_order_fail.call(
        task_id='test_stq',
        kwargs={
            'claim_id': f'order/{default_order_id}',
            'order_id': 'taxi-order',
            'lookup_version': 1,
            'taxi_status': 'expired',
        },
    )

    assert mock_dispatch_mark_fail.handler.times_called == 1


@pytest.mark.parametrize(
    'cargo_dispatch_status, expect_fail', [(404, False), (409, True)],
)
async def test_bad_waybill_4xx(
        stq_runner,
        mock_dispatch_mark_fail,
        default_order_id,
        cargo_dispatch_status: int,
        expect_fail: bool,
):
    mock_dispatch_mark_fail.status_code = cargo_dispatch_status

    await stq_runner.cargo_taxi_order_fail.call(
        task_id='test_stq',
        kwargs={
            'claim_id': f'order/{default_order_id}',
            'order_id': 'taxi-order',
            'lookup_version': 1,
            'taxi_status': 'expired',
        },
        expect_fail=expect_fail,
    )

    assert mock_dispatch_mark_fail.handler.times_called == 1


@pytest.mark.parametrize('taxi_status', ['estimating', None])
async def test_cargo_taxi_order_fail_wrong_status(
        stq_runner, mock_dispatch_mark_fail, default_order_id, taxi_status,
):
    await stq_runner.cargo_taxi_order_fail.call(
        task_id='test_stq',
        kwargs={
            'claim_id': f'order/{default_order_id}',
            'order_id': 'taxi-order',
            'lookup_version': 1,
            'taxi_status': taxi_status,
        },
        expect_fail=False,
    )
    assert mock_dispatch_mark_fail.handler.times_called == 0
