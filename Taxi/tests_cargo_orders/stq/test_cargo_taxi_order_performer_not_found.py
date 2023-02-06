import pytest


async def test_waybill_basic(
        stq_runner, mock_dispatch_mark_fail, default_order_id,
):
    await stq_runner.cargo_taxi_order_performer_not_found.call(
        task_id='test_stq',
        kwargs={
            'claim_id': f'order/{default_order_id}',
            'order_id': 'taxi-order',
            'lookup_version': 1,
            'has_performer': False,
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

    await stq_runner.cargo_taxi_order_performer_not_found.call(
        task_id='test_stq',
        kwargs={
            'claim_id': f'order/{default_order_id}',
            'order_id': 'taxi-order',
            'lookup_version': 1,
            'has_performer': False,
        },
        expect_fail=expect_fail,
    )

    assert mock_dispatch_mark_fail.handler.times_called == 1


@pytest.mark.now('2021-11-01T13:35:01+0000')
@pytest.mark.config(
    CARGO_ORDERS_ORDER_CANCEL_CHECK_DRAFT_ALIVE={
        'enabled': True,
        'waiting_time_after_expired_sec': 60,
    },
)
async def test_commit_state_draft(
        taxi_cargo_orders,
        default_order_id,
        stq_runner,
        set_order_properties,
        mock_dispatch_mark_fail,
):
    mock_dispatch_mark_fail.status_code = 200
    set_order_properties(
        default_order_id,
        commit_state='draft',
        created='2021-11-01T13:30:01+0000',
    )

    await stq_runner.cargo_taxi_order_performer_not_found.call(
        task_id=default_order_id,
        kwargs={
            'claim_id': 'order/' + default_order_id,
            'order_id': 'taxi-order',
            'lookup_version': 1,
            'has_performer': False,
        },
        expect_fail=False,
    )
