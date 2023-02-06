import datetime

import pytest

from taxi.stq import async_worker_ng

from eats_tips_payments.stq import charge_plus
from test_eats_tips_payments import conftest

CURRENCY = 'RUB'
WALLET_ID = 'wallet_1'
NOW = datetime.datetime(2021, 6, 15, 14, 30, 15, tzinfo=datetime.timezone.utc)
YANDEX_USER_ID = 'd45b09ec-6e5f-4e24-9e7e-fa293965d583'


@pytest.mark.config(
    EATS_TIPS_PAYMENTS_POLL_RETRY_SETTINGS={
        'max_tries': 2,
        'delay': 1,
        'factor': 1,
    },
    EATS_TIPS_PAYMENTS_PLUS_SETTINGS=conftest.ENABLED_PLUS_CONFIG,
)
@pytest.mark.pgsql('eats_tips_payments', files=['pg_eats_tips.sql'])
@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    (
        'order_id',
        'call_create',
        'base_amount',
        'profit',
        'vat',
        'plus',
        'version',
    ),
    [
        (42, True, '110.00', '6.00', '1.20', '11.00', 1),
        (44, False, '120.00', '3.00', '0.60', '0.00', 2),
        (46, True, '140.00', '0.00', '0.00', '13.00', 1),
        (47, True, '150.00', '0.00', '0.00', '13.00', 1),
    ],
)
async def test_charge(
        stq3_context,
        pgsql,
        stq,
        mock_transactions_ng,
        mock_plus_wallet,
        order_id,
        call_create,
        base_amount,
        profit,
        vat,
        plus,
        version,
):
    @mock_transactions_ng('/v2/invoice/create')
    def _mock_create_invoice(request):
        assert datetime.datetime.fromisoformat(
            request.json.pop('invoice_due'),
        ) == NOW + datetime.timedelta(days=1)
        assert request.json == {
            'id': str(order_id),
            'id_namespace': 'tips-payments',
            'currency': CURRENCY,
            'billing_service': conftest.ENABLED_PLUS_CONFIG['service_name'],
            'yandex_uid': YANDEX_USER_ID,
            'pass_params': {},
            'user_ip': '1.2.3.4',
            'payments': [],
        }
        return {}

    @mock_transactions_ng('/v2/cashback/update')
    def _mock_cashback_update(request):
        assert request.json.pop('operation_id')
        assert request.json == {
            'invoice_id': str(order_id),
            'id_namespace': 'tips-payments',
            'version': version,
            'yandex_uid': YANDEX_USER_ID,
            'user_ip': '1.2.3.4',
            'wallet_account': WALLET_ID,
            'reward': [{'amount': plus, 'source': 'service'}],
            'extra_payload': {
                'cashback_service': conftest.ENABLED_PLUS_CONFIG[
                    'service_name'
                ],
                'cashback_type': 'transaction',
                'base_amount': base_amount,
                'has_plus': 'false',
                'commission_amount': profit,
                'vat_commission_amount': vat,
                'service_id': conftest.ENABLED_PLUS_CONFIG['service_id'],
                'order_id': str(order_id),
                'issuer': conftest.ENABLED_PLUS_CONFIG['issuer'],
                'campaign_name': 'support_customers',
                'ticket': conftest.ENABLED_PLUS_CONFIG['ticket'],
            },
        }
        return {}

    @mock_plus_wallet('/v1/balances')
    def _mock_balances(request):
        assert request.query == {
            'yandex_uid': YANDEX_USER_ID,
            'currencies': 'RUB',
        }
        return {
            'balances': [
                {'balance': '0', 'wallet_id': WALLET_ID, 'currency': CURRENCY},
            ],
        }

    await charge_plus.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id=1,
            exec_tries=1,
            reschedule_counter=1,
            queue='eats_tips_payments_charge_plus',
        ),
        order_id=order_id,
        operation='1',
    )

    assert _mock_create_invoice.times_called == (1 if call_create else 0)
    assert _mock_cashback_update.times_called == 1
    assert _mock_balances.times_called == 1

    cursor = pgsql['eats_tips_payments'].cursor()
    cursor.execute(
        f"""
        SELECT cashback_status
        FROM eats_tips_payments.orders
        WHERE order_id = {order_id}
        """,
    )
    row = cursor.fetchone()
    assert row
    assert row[0] == 'in-progress'

    conftest.check_task_queued(
        stq,
        stq.eats_tips_payments_poll_plus_status,
        {'order_id': order_id},
        drop={'order_id_str'},
    )

    assert stq.is_empty
