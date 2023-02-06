import pytest

from taxi_shared_payments.repositories import accounts as accounts_repo
from taxi_shared_payments.stq import handle_order_completed


@pytest.mark.parametrize('account_id', ['ok_account', 'ok_account_with_rides'])
async def test_handle_order_completed(stq3_context, account_id):
    await handle_order_completed.task(stq3_context, account_id, 'order_id')

    account = await accounts_repo.get_one_by_id(stq3_context, account_id)
    assert account.has_rides


async def test_account_does_not_exist(stq3_context):
    await handle_order_completed.task(
        stq3_context, 'non_existent_account_id', 'order_id',
    )
