import datetime

import pytest

from taxi.stq import async_worker_ng

from eats_tips_payments.stq import poll_plus_status
from test_eats_tips_payments import conftest

ORDER_ID = 43
CASHBACK = {
    'status': 'init',
    'version': 1,
    'rewarded': [],
    'transactions': [],
    'operations': [],
    'commit_version': 1,
}
NOW = datetime.datetime(2021, 6, 15, 14, 30, 15, tzinfo=datetime.timezone.utc)
INVOICE = {
    'id': str(ORDER_ID),
    'invoice_due': '2021-09-11T08:44:26+03:00',
    'created': '2021-09-11T08:44:26+03:00',
    'currency': 'RUB',
    'status': 'init',
    'payment_types': [],
    'sum_to_pay': [],
    'held': [],
    'cleared': [],
    'debt': [],
    'operation_info': {},
    'transactions': [],
    'yandex_uid': 'd45b09ec-6e5f-4e24-9e7e-fa293965d583',
    'operations': [],
    'cashback': CASHBACK,
    'user_ip': '2a02:6b8:b010:50a3::3',
}


@pytest.mark.parametrize(
    (
        'tries',
        'transactions_cashback_status',
        'tips_cashback_status',
        'need_retry',
    ),
    [
        (1, 'init', 'in-progress', True),
        (1, 'success', 'success', False),
        (1, 'failed', 'failed', False),
        (2, 'init', 'in-progress', False),
    ],
)
@pytest.mark.config(
    EATS_TIPS_PAYMENTS_POLL_RETRY_SETTINGS={
        'max_tries': 2,
        'delay': 1,
        'factor': 1,
    },
)
@pytest.mark.pgsql('eats_tips_payments', files=['pg_eats_tips.sql'])
@pytest.mark.now(NOW.isoformat())
async def test_poll(
        stq3_context,
        pgsql,
        stq,
        mock_transactions_ng,
        tries,
        transactions_cashback_status,
        tips_cashback_status,
        need_retry,
):
    @mock_transactions_ng('/v2/invoice/retrieve')
    def _mock_retrieve_invoice(request):
        return {
            **INVOICE,
            'cashback': {**CASHBACK, 'status': transactions_cashback_status},
        }

    await poll_plus_status.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id=1,
            exec_tries=1,
            reschedule_counter=tries,
            queue='eats_tips_payments_poll_plus_status',
        ),
        order_id=ORDER_ID,
    )

    cursor = pgsql['eats_tips_payments'].cursor()
    cursor.execute(
        f"""
        SELECT cashback_status
        FROM eats_tips_payments.orders
        WHERE order_id = {ORDER_ID}
        """,
    )
    row = cursor.fetchone()
    assert row
    assert row[0] == tips_cashback_status

    if need_retry:
        eta = NOW + datetime.timedelta(seconds=1)
        conftest.check_task_rescheduled(
            stq, stq.eats_tips_payments_poll_plus_status, eta,
        )
    else:
        assert stq.is_empty
