import pytest


@pytest.mark.config(PLUS_MIGRATION_ENABLED=False)
async def test_migration_disabled(web_plus, stq):
    result = await web_plus.uid_notify_handle.request(
        phonish_uid='phonish', portal_uid='portal',
    ).perform()

    assert result.status_code == 200
    assert stq.subscription_transfer.times_called == 0


async def test_migration_on_unbinding(web_plus, stq):
    result = await web_plus.uid_notify_handle.request(
        phonish_uid='phonish', portal_uid='portal', event='unbind',
    ).perform()

    assert result.status_code == 200
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
        web_plus, mock_mediabilling, status, order_id, stq,
):
    mock_mediabilling.transfer.status(status).order_id(order_id)
    result = await web_plus.uid_notify_handle.request(
        phonish_uid='phonish', portal_uid='portal',
    ).perform()

    assert result.status_code == 500
    assert stq.subscription_transfer.times_called == 0


async def test_migration_impossible_transfer(web_plus, mock_mediabilling, stq):
    mock_mediabilling.transfer.set_http_status(400).error_id(40601)
    result = await web_plus.uid_notify_handle.request(
        phonish_uid='phonish', portal_uid='portal',
    ).perform()

    assert result.status_code == 200
    assert stq.subscription_transfer.times_called == 0


async def test_migration_ok(web_plus, mock_mediabilling, stq):
    mock_mediabilling.transfer.status('success').order_id(123456)
    result = await web_plus.uid_notify_handle.request(
        phonish_uid='phonish', portal_uid='portal',
    ).perform()

    assert result.status_code == 200

    assert stq.subscription_transfer.times_called == 1
    stq_call = stq.subscription_transfer.next_call()
    assert stq_call['id'] == '123456'
    assert stq_call['args'] == ['123456', 'portal']
