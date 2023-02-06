import pytest


@pytest.mark.parametrize('status', ['ok', 'refund'])
async def test_transfer_completed(stq_runner, mock_mediabilling, status, stq):
    order_id = '123456'
    yandex_uid = '400000'
    args = [order_id, yandex_uid]

    mock_mediabilling.order_info.order_id(int(order_id)).status(status)

    await stq_runner.subscription_transfer.call(task_id=order_id, args=args)

    assert stq.subscription_transfer.times_called == 0


async def test_transfer_pending(stq_runner, mock_mediabilling, stq):
    order_id = '123456'
    yandex_uid = '400000'
    args = [order_id, yandex_uid]

    mock_mediabilling.order_info.order_id(int(order_id)).status('pending')

    await stq_runner.subscription_transfer.call(task_id=order_id, args=args)

    assert stq.subscription_transfer.times_called == 1
    stq_call = stq.subscription_transfer.next_call()

    assert stq_call['id'] == order_id
    assert stq_call['args'] == args


@pytest.mark.parametrize('status', ['error', 'cancelled'])
async def test_transfer_failed(stq_runner, mock_mediabilling, status, stq):
    order_id = '123456'
    yandex_uid = '400000'
    args = [order_id, yandex_uid]

    mock_mediabilling.order_info.order_id(int(order_id)).status(status)

    await stq_runner.subscription_transfer.call(task_id=order_id, args=args)

    assert stq.subscription_transfer.times_called == 0


@pytest.mark.parametrize('status_code', [400, 500])
async def test_transfer_order_info_err(
        stq_runner, mock_mediabilling, status_code, stq,
):
    order_id = '123456'
    yandex_uid = '400000'
    args = [order_id, yandex_uid]

    mock_mediabilling.order_info.set_http_status(status_code)

    await stq_runner.subscription_transfer.call(
        task_id=order_id, args=args, expect_fail=True,
    )

    assert stq.subscription_transfer.times_called == 0
