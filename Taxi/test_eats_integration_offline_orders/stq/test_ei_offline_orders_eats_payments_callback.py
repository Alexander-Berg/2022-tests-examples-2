import pytest

from taxi.stq import async_worker_ng as async_worker

from eats_integration_offline_orders.internal import enums
from eats_integration_offline_orders.stq import (
    ei_offline_orders_eats_payments_callback,
)


@pytest.mark.parametrize(
    'transaction_uuid,ep_action,ep_status,expected_status',
    (
        pytest.param(
            'transaction_uuid__1',
            'purchase',
            'confirmed',
            enums.PaymentTransactionStatus.SUCCESS,
            id='success',
        ),
        pytest.param(
            'transaction_uuid__1',
            'purchase',
            'rejected',
            enums.PaymentTransactionStatus.CANCELED,
            id='failed',
        ),
        pytest.param(
            'transaction_uuid__not_committed_yet',
            'purchase',
            'confirmed',
            None,
            id='not committed transaction yet',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=[
        'tables.sql',
        'orders.sql',
        'restaurants.sql',
        'payment_transactions.sql',
    ],
)
async def test_ei_offline_orders_eats_payments_callback(
        stq3_context,
        mock_eats_payments_py3,
        # params:
        transaction_uuid,
        ep_action,
        ep_status,
        expected_status,
):
    @mock_eats_payments_py3('/v1/orders/close')
    async def _mock_v1_orders_close(request):
        return {}

    task_info = async_worker.TaskInfo(
        id='',
        exec_tries=1,
        reschedule_counter=1,
        queue='ei_offline_orders_eats_payments_callback',
    )
    await ei_offline_orders_eats_payments_callback.task(
        context=stq3_context,
        task_info=task_info,
        order_id=transaction_uuid,
        action=ep_action,
        status=ep_status,
    )
    transaction = await stq3_context.pg.secondary.fetchrow(
        f'SELECT * FROM payment_transactions where uuid=$1;', transaction_uuid,
    )
    if transaction:
        assert transaction['status'] == expected_status.value
        if expected_status is enums.EatsPaymentsStatus.CONFIRMED:
            assert _mock_v1_orders_close.times_called == 1
    else:
        assert expected_status is None
