import pytest


@pytest.mark.config(PLUS_MIGRATION_ENABLED=False)
async def test_migration_disabled(stq_runner, stq):
    kwargs = dict(
        event_type='bind', phonish_uid='phonish', portal_uid='portal',
    )
    await stq_runner.plus_uid_notify.call(
        task_id='task', args=[], kwargs=kwargs, expect_fail=False,
    )

    assert stq.subscription_transfer.times_called == 0


async def test_migration_on_unbinding(stq_runner, stq):
    kwargs = dict(
        event_type='unbind', phonish_uid='phonish', portal_uid='portal',
    )
    await stq_runner.plus_uid_notify.call(
        task_id='task', args=[], kwargs=kwargs, expect_fail=False,
    )

    assert stq.subscription_transfer.times_called == 0


@pytest.mark.parametrize(
    'status,order_id',
    [
        ('success', None),
        ('already-purchased', None),
        ('already-pending', None),
        ('error', 123),
        ('need-supply-payment-data', 123),
    ],
)
async def test_migration_wrong_transfer(
        stq_runner, mock_mediabilling, status, order_id, stq,
):
    mock_mediabilling.transfer.status(status).order_id(order_id)
    kwargs = dict(
        event_type='bind', phonish_uid='phonish', portal_uid='portal',
    )
    await stq_runner.plus_uid_notify.call(
        task_id='task', args=[], kwargs=kwargs, expect_fail=True,
    )
    assert stq.subscription_transfer.times_called == 0


async def test_migration_impossible_transfer(
        stq_runner, mock_mediabilling, stq,
):
    mock_mediabilling.transfer.set_http_status(400).error_id(40601)
    kwargs = dict(
        event_type='bind', phonish_uid='phonish', portal_uid='portal',
    )
    await stq_runner.plus_uid_notify.call(
        task_id='task', args=[], kwargs=kwargs, expect_fail=False,
    )

    assert stq.subscription_transfer.times_called == 0


async def test_migration_ok(stq_runner, mock_mediabilling, stq):
    mock_mediabilling.transfer.status('success').order_id(123456)
    kwargs = dict(
        event_type='bind', phonish_uid='phonish', portal_uid='portal',
    )
    await stq_runner.plus_uid_notify.call(
        task_id='task', args=[], kwargs=kwargs, expect_fail=False,
    )

    assert stq.subscription_transfer.times_called == 1
    stq_call = stq.subscription_transfer.next_call()
    assert stq_call['id'] == '123456'
    assert stq_call['args'] == ['123456', 'portal']
