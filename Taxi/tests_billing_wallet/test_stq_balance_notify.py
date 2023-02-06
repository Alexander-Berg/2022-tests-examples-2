import pytest


@pytest.mark.config(
    BILLING_WALLET_BALANCE_NOTIFY=[
        {
            'delivery_settings': {
                'stq': {'queue': 'personal_wallet_update_balance'},
            },
            'delivery_type': 'stq',
            'enabled': True,
        },
    ],
)
async def test_balance_notify_happy_path(stq_runner, stq):

    args = ['yandex_uid', 'wallet_id']
    task_id = 'task_id'
    await stq_runner.billing_wallet_balance_notify.call(
        task_id=task_id, args=args,
    )

    assert not stq.billing_wallet_balance_notify.times_called

    called_stq = stq['personal_wallet_update_balance']
    assert called_stq.times_called == 1
    next_call = called_stq.next_call()
    assert next_call['args'] == args
    assert next_call['id'] == task_id


@pytest.mark.config(
    BILLING_WALLET_BALANCE_NOTIFY=[
        {'delivery_settings': {}, 'delivery_type': 'stq', 'enabled': True},
    ],
)
async def test_balance_notify_wrong_settings(stq_runner, stq):

    args = ['yandex_uid', 'wallet_id']
    task_id = 'task_id'
    await stq_runner.billing_wallet_balance_notify.call(
        task_id=task_id, args=args,
    )

    assert not stq.billing_wallet_balance_notify.times_called
    assert not stq['personal_wallet_update_balance'].times_called


@pytest.mark.config(
    BILLING_WALLET_BALANCE_NOTIFY=[
        {
            'delivery_settings': {
                'stq': {'queue': 'personal_wallet_update_balance'},
            },
            'delivery_type': 'stq',
            'enabled': False,
        },
    ],
)
async def test_balance_notify_consumer_disable(stq_runner, stq):

    args = ['yandex_uid', 'wallet_id']
    task_id = 'task_id'
    await stq_runner.billing_wallet_balance_notify.call(
        task_id=task_id, args=args,
    )

    assert not stq.billing_wallet_balance_notify.times_called
    assert not stq['personal_wallet_update_balance'].times_called
