import pytest


async def test_waybill_basic(
        stq_runner, mock_dispatch_mark_fail, default_order_id,
):
    await stq_runner.cargo_taxi_order_cancel.call(
        task_id='test_stq',
        kwargs={
            'claim_id': f'order/{default_order_id}',
            'order_id': 'taxi-order',
            'lookup_version': 1,
            'has_performer': True,
        },
    )

    assert mock_dispatch_mark_fail.handler.times_called == 1


@pytest.mark.config(
    CARGO_TAXI_REORDER_REASONS={
        '__default__': 'provider_cancel',
        'manual': 'performer_cancel',
        'cancelled_by_early_hold': 'cancelled_by_early_hold',
    },
)
async def test_early_hold_reason(stq_runner, default_order_id, mockserver):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/mark/order-fail')
    def _mock_cargo_dispatch(request):
        assert request.json['reason'] == 'cancelled_by_early_hold'
        return {'id': 'waybill-ref', 'status': 'resolved'}

    await stq_runner.cargo_taxi_order_cancel.call(
        task_id='test_stq',
        kwargs={
            'claim_id': f'order/{default_order_id}',
            'order_id': 'taxi-order',
            'lookup_version': 1,
            'reason': 'cancelled_by_early_hold',
            'has_performer': True,
        },
    )


async def test_bad_waybill_wrong_taxi_order_id(
        stq_runner, mock_dispatch_mark_fail, default_order_id,
):
    await stq_runner.cargo_taxi_order_cancel.call(
        task_id='test_stq',
        kwargs={
            'claim_id': f'order/{default_order_id}',
            'order_id': 'taxi-order-bad',
            'lookup_version': 1,
            'has_performer': True,
        },
    )

    assert mock_dispatch_mark_fail.handler.times_called == 0


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

    await stq_runner.cargo_taxi_order_cancel.call(
        task_id='test_stq',
        kwargs={
            'claim_id': f'order/{default_order_id}',
            'order_id': 'taxi-order',
            'lookup_version': 1,
            'has_performer': True,
        },
        expect_fail=expect_fail,
    )

    assert mock_dispatch_mark_fail.handler.times_called == 1


@pytest.mark.parametrize(
    'taxi_fail_reason, expecting_reason',
    [('manual', 'performer_cancel'), ('park', 'provider_cancel')],
)
async def test_reason(
        stq_runner,
        mock_dispatch_mark_fail,
        default_order_id,
        taxi_fail_reason: str,
        expecting_reason: str,
):
    mock_dispatch_mark_fail.expecting_reason = expecting_reason
    await stq_runner.cargo_taxi_order_cancel.call(
        task_id='test_stq',
        kwargs={
            'claim_id': f'order/{default_order_id}',
            'order_id': 'taxi-order',
            'lookup_version': 1,
            'has_performer': True,
            'reason': taxi_fail_reason,
        },
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

    await stq_runner.cargo_taxi_order_cancel.call(
        task_id=default_order_id,
        kwargs={
            'claim_id': 'order/' + default_order_id,
            'order_id': 'taxi-order',
            'lookup_version': 1,
            'has_performer': True,
        },
        expect_fail=False,
    )


@pytest.mark.parametrize(
    'cancel_request_token', [None, 'cargo-dispatch/some_token'],
)
async def test_cancel_request_token(
        stq_runner,
        mock_dispatch_mark_fail,
        set_order_properties,
        default_order_id,
        cancel_request_token,
):
    mock_dispatch_mark_fail.expecting_cancel_request_token = (
        cancel_request_token
    )
    set_order_properties(
        default_order_id, cancel_request_token=cancel_request_token,
    )

    await stq_runner.cargo_taxi_order_cancel.call(
        task_id='test_stq',
        kwargs={
            'claim_id': f'order/{default_order_id}',
            'order_id': 'taxi-order',
            'lookup_version': 1,
            'has_performer': True,
            'reason': 'manual',
        },
    )

    assert mock_dispatch_mark_fail.handler.times_called == 1


@pytest.mark.pgsql('cargo_orders', files=['pg_performer_order_cancel.sql'])
async def test_performer_fines_flow(
        stq_runner,
        mock_dispatch_mark_fail,
        default_order_id,
        stq,
        exp_cargo_orders_use_performer_fines_service,
):
    await stq_runner.cargo_taxi_order_cancel.call(
        task_id='test_stq',
        kwargs={
            'claim_id': f'order/{default_order_id}',
            'order_id': 'taxi-order',
            'lookup_version': 1,
            'has_performer': True,
            'reason': 'performer_cancel',
        },
    )

    assert mock_dispatch_mark_fail.handler.times_called == 1
    stq_call = stq.cargo_performer_cancel_confirmation.next_call()
    assert stq_call['kwargs']['cancel_id'] == 1
    assert (
        stq_call['kwargs']['cargo_order_id']
        == '9db1622e-582d-4091-b6fc-4cb2ffdc12c0'
    )
    assert stq_call['kwargs']['driver_id'] == 'driver'
    assert stq_call['kwargs']['park_id'] == 'park'
    assert stq_call['kwargs']['taxi_order_id'] == 'taxi-order'
