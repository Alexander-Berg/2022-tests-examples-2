import pytest

BALANCE_ENTRY_ID = 8484848484
BALANCE_CHANGED_AT = '2020-09-27T09:00:00+00:00'

PARK_ID = 'park1'
CONTRACTOR_PROFILE_ID = 'driver11'


def _make_update_stq_args(park_id, new_balance):
    return {
        'park_id': park_id,
        'driver_uuid': CONTRACTOR_PROFILE_ID,
        'balance': str(new_balance),
        'currency': 'RUB',
        'last_entry_id': BALANCE_ENTRY_ID,
        'last_created': BALANCE_CHANGED_AT,
    }


@pytest.mark.parametrize('balance_deny_onlycard', [True, False])
@pytest.mark.parametrize(
    ('new_balance', 'old_balance', 'balance_limit'), [(123, 321, 231)],
)
async def test_update(
        stq_runner,
        balance_update_context,
        mock_contractor_balance_update,
        balance_deny_onlycard,
        new_balance,
        old_balance,
        balance_limit,
):
    balance_update_context.set_data(
        new_balance=new_balance,
        old_balance=old_balance,
        balance_limit=balance_limit,
        balance_last_entry_id=BALANCE_ENTRY_ID,
        balance_changed_at=BALANCE_CHANGED_AT,
        balance_deny_onlycard=balance_deny_onlycard,
    )

    await stq_runner.contractor_balances_update.call(
        task_id='task-id', kwargs=_make_update_stq_args(PARK_ID, new_balance),
    )


@pytest.mark.parametrize(
    ('contractor_balance_response_code', 'expect_fail'),
    [(200, False), (200, False), (400, True), (500, True), (409, False)],
)
async def test_stq_failing(
        stq_runner,
        balance_update_context,
        mock_contractor_balance_update,
        contractor_balance_response_code,
        expect_fail,
):
    new_balance = 123.0
    balance_update_context.set_data(
        new_balance=new_balance,
        response_code=contractor_balance_response_code,
    )

    await stq_runner.contractor_balances_update.call(
        task_id='task-id',
        kwargs=_make_update_stq_args(PARK_ID, new_balance),
        expect_fail=expect_fail,
    )


async def test_update_notification_stq_call(
        stq_runner,
        stq,
        balance_update_context,
        mock_contractor_balance_update,
):
    new_balance = 123
    old_balance = 322
    balance_limit = 10

    balance_update_context.set_data(
        new_balance=new_balance,
        old_balance=old_balance,
        balance_limit=balance_limit,
    )

    await stq_runner.contractor_balances_update.call(
        task_id='task-id', kwargs=_make_update_stq_args(PARK_ID, new_balance),
    )

    assert stq.contractor_balances_update_notification.has_calls

    task = stq.contractor_balances_update_notification.next_call()

    task['kwargs'].pop('log_extra')

    assert task.pop('id') == str(BALANCE_ENTRY_ID)
    assert float(task['kwargs'].pop('old_balance')) == old_balance
    assert float(task['kwargs'].pop('balance_limit')) == balance_limit
    assert task['kwargs'] == {
        'park_id': PARK_ID,
        'contractor_profile_id': CONTRACTOR_PROFILE_ID,
        'balance': str(new_balance),
        'currency': 'RUB',
        'block_orders_on_balance_below_limit': False,
        'balance_revision': BALANCE_ENTRY_ID,
        'balance_changed_at': BALANCE_CHANGED_AT,
    }
