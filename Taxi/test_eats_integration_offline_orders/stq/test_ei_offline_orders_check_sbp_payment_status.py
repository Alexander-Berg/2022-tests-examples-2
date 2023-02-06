import datetime

import pytest

from taxi.stq import async_worker_ng
from taxi.util import dates

from eats_integration_offline_orders.internal import enums
from eats_integration_offline_orders.stq import check_sbp_payment_status


def build_task_info():
    return async_worker_ng.TaskInfo(
        id=2,
        exec_tries=1,
        reschedule_counter=1,
        queue='check_sbp_payment_status',
    )


def check_task_rescheduled(stq, queue, eta):
    task = queue.next_call()
    assert task.pop('id')
    assert task.pop('queue')
    assert task == {
        'eta': eta.replace(tzinfo=None),
        'args': None,
        'kwargs': None,
    }
    assert stq.is_empty


@pytest.mark.parametrize(
    'timedelta, get_state_suffix, transaction_payment_id, transaction_uuid, '
    'expected_status, rescheduled',
    (
        pytest.param(
            100,
            'fail',
            '1',
            'transaction_uuid__1',
            enums.PaymentTransactionStatus.IN_PROGRESS,
            True,
            id='fail request, rescheduled',
        ),
        pytest.param(
            -100,
            '',
            '1',
            'transaction_uuid__1',
            enums.PaymentTransactionStatus.ORDER_TIME_OUT,
            False,
            id='lifetime timeout, rollback',
        ),
        pytest.param(
            100,
            'authorizing',
            '1',
            'transaction_uuid__1',
            enums.PaymentTransactionStatus.IN_PROGRESS,
            True,
            id='middle status, rescheduled',
        ),
        pytest.param(
            100,
            'canceled',
            '1',
            'transaction_uuid__1',
            enums.PaymentTransactionStatus.CANCELED,
            False,
            id='canceled status, rollback',
        ),
        pytest.param(
            100,
            'confirmed',
            '1',
            'transaction_uuid__1',
            enums.PaymentTransactionStatus.SUCCESS,
            False,
            id='confirmed status, finalize',
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
async def test_ei_offline_orders_check_sbp_payment_status(
        stq3_context,
        mockserver,
        load_json,
        mock_tinkoff_securepay,
        stq,
        timedelta,
        get_state_suffix,
        transaction_payment_id,
        transaction_uuid,
        expected_status,
        rescheduled,
):
    @mock_tinkoff_securepay('/v2/GetState')
    def _mock_get_qr(request):
        return mockserver.make_response(
            json=load_json(
                f'tinkoff/response_get_state_{get_state_suffix}.json',
            ),
        )

    @mock_tinkoff_securepay('/v2/Cancel')
    def _mock_cancel(request):
        return mockserver.make_response(
            json=load_json(f'tinkoff/response_cancel.json'),
        )

    await check_sbp_payment_status.task(
        context=stq3_context,
        payment_id=transaction_payment_id,
        expired_time=dates.utcnow() + datetime.timedelta(seconds=timedelta),
        task_info=build_task_info(),
        transaction_uuid=transaction_uuid,
    )
    transaction = await stq3_context.pg.secondary.fetchrow(
        f'SELECT * FROM payment_transactions where side_payment_id=$1;',
        transaction_payment_id,
    )
    order = await stq3_context.pg.secondary.fetchrow(
        'SELECT * FROM orders where id=$1;', 1,
    )
    assert transaction['status'] == expected_status.value
    if expected_status == enums.PaymentTransactionStatus.SUCCESS:
        assert order['status'] == 'paid'
    if rescheduled:
        check_task_rescheduled(
            stq,
            stq.ei_offline_orders_check_sbp_payment_status,
            dates.utcnow() + datetime.timedelta(seconds=3),
        )
