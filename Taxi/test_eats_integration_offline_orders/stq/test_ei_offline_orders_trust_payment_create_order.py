import pytest

from taxi.stq import async_worker_ng as async_worker

from eats_integration_offline_orders.internal import enums
from eats_integration_offline_orders.stq import (
    ei_offline_orders_trust_payment_create_order,
)


@pytest.mark.parametrize(
    'transaction_uuid,'
    'expected_order_create_times_called,'
    'expected_order_cancel_times_called,'
    'expected_status',
    (
        pytest.param(
            'transaction_uuid__1',
            1,
            0,
            enums.PaymentTransactionStatus.IN_PROGRESS,
            id='success',
        ),
        pytest.param(
            'transaction_uuid__2',
            0,
            1,
            enums.PaymentTransactionStatus.CANCELED,
            id='failed',
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
@pytest.mark.now('2022-06-29T00:00:35+00:00')
async def test_ei_offline_orders_trust_payment_create_order(
        stq3_context,
        mock_eats_payments_py3,
        # params:
        transaction_uuid,
        expected_order_create_times_called,
        expected_order_cancel_times_called,
        expected_status,
):
    @mock_eats_payments_py3('/v1/orders/create')
    async def _mock_v1_orders_create(request):
        # badge is replaced by corp
        assert request.json['payment_method']['type'] in {'corp'}
        return {}

    @mock_eats_payments_py3('/v1/orders/retrieve')
    async def _mock_v1_orders_retrieve(request):
        return {
            'id': '',
            'currency': '',
            'status': 'holding',
            'version': 3,
            'sum_to_pay': [],
            'held': [],
            'cleared': [],
            'debt': [],
            'yandex_uid': '',
            'payment_types': [],
            'payments': [],
        }

    @mock_eats_payments_py3('/v1/orders/cancel')
    async def _mock_v1_orders_cancel(request):
        assert request.json['version'] == 3
        return {}

    task_info = async_worker.TaskInfo(
        id='',
        exec_tries=1,
        reschedule_counter=1,
        queue='ei_offline_orders_trust_payment_create_order',
    )
    await ei_offline_orders_trust_payment_create_order.task(
        context=stq3_context,
        task_info=task_info,
        transaction_uuid=transaction_uuid,
        pay_method_id=None,
        payment_headers={
            'x_eats_user': 'personal_phone_id=PHONE_ID_1',
            'x_yandex_uid': 'yandex_uid__1',
        },
    )
    transaction = await stq3_context.pg.secondary.fetchrow(
        f'SELECT * FROM payment_transactions where uuid=$1;', transaction_uuid,
    )
    assert transaction['status'] == expected_status.value
    assert (
        _mock_v1_orders_create.times_called
        == expected_order_create_times_called
    )
    assert (
        _mock_v1_orders_cancel.times_called
        == expected_order_cancel_times_called
    )
