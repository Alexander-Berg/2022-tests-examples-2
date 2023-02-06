import pytest

MOCK_CARD_INIT_URL = '/tinkoff-securepay/e2c/v2/Init'
MOCK_CARD_PAYMENT_URL = '/tinkoff-securepay/e2c/v2/Payment'
MOCK_CARD_GET_STATUS_URL = '/tinkoff-securepay/e2c/v2/GetState'

MOCK_SBP_INIT_URL = '/tinkoff-securepay/a2c/sbp/Init'
MOCK_SBP_PAYMENT_URL = '/tinkoff-securepay/a2c/sbp/Payment'
MOCK_SBP_GET_STATUS_URL = '/tinkoff-securepay/a2c/sbp/GetState'

CARD_PAYOUT_ID = '00000000-0001-0001-0001-000000000000'
SBP_PAYOUT_ID = '00000000-0001-0001-0001-000000000001'

CARD_POLL_PAYOUT_ID = '00000000-0001-0001-0001-100000000000'
SBP_POLL_PAYOUT_ID = '00000000-0001-0001-0001-100000000001'

BANK_PAYOUT_ID = '2353039'


OK_PARAMS = [
    (CARD_PAYOUT_ID, MOCK_CARD_INIT_URL, MOCK_CARD_PAYMENT_URL),
    (SBP_PAYOUT_ID, MOCK_SBP_INIT_URL, MOCK_SBP_PAYMENT_URL),
]


@pytest.mark.parametrize(
    'payout_id, mock_init_url, mock_payment_url', OK_PARAMS,
)
async def test_stq_payment_ok(
        stq_runner,
        mockserver,
        pgsql,
        mock_api,
        payout_id,
        mock_init_url,
        mock_payment_url,
):
    @mockserver.json_handler(mock_init_url)
    def init_handler(request):
        return {
            'Success': True,
            'ErrorCode': '0',
            'Status': 'CHECKED',
            'PaymentId': BANK_PAYOUT_ID,
            'OrderId': payout_id,
            'Amount': 10001,
        }

    @mockserver.json_handler(mock_payment_url)
    def payment_handler(request):
        return {
            'Success': True,
            'ErrorCode': '0',
            'Status': 'COMPLETING',
            'PaymentId': BANK_PAYOUT_ID,
            'OrderId': payout_id,
        }

    await stq_runner.contractor_instant_payouts_tinkoff_process.call(
        task_id='1', kwargs={'id': payout_id},
    )

    assert init_handler.times_called == 1
    assert payment_handler.times_called == 1

    cursor = pgsql['contractor_instant_payouts'].cursor()
    cursor.execute(
        f"""
        SELECT progress_status, transfer_status
        FROM contractor_instant_payouts.contractor_payout
        WHERE id = '{payout_id}'
        """,
    )
    pg_result = cursor.fetchall()[0]
    assert pg_result[0] == 'transfer'
    assert pg_result[1] == {'bpid': BANK_PAYOUT_ID}


POLL_PARAMS = [
    (CARD_POLL_PAYOUT_ID, MOCK_CARD_GET_STATUS_URL),
    (SBP_POLL_PAYOUT_ID, MOCK_SBP_GET_STATUS_URL),
]


@pytest.mark.parametrize('payout_id, mock_get_status_url', POLL_PARAMS)
async def test_stq_poll_ok(
        stq_runner,
        mockserver,
        pgsql,
        mock_api,
        payout_id,
        mock_get_status_url,
):
    @mockserver.json_handler(mock_get_status_url)
    def get_status_handler(request):
        return {
            'Success': True,
            'ErrorCode': '0',
            'Status': 'COMPLETED',
            'PaymentId': BANK_PAYOUT_ID,
            'OrderId': payout_id,
            'Amount': 10001,
        }

    await stq_runner.contractor_instant_payouts_tinkoff_process.call(
        task_id='1', kwargs={'id': payout_id},
    )

    assert get_status_handler.times_called == 1

    cursor = pgsql['contractor_instant_payouts'].cursor()
    cursor.execute(
        f"""
        SELECT progress_status
        FROM contractor_instant_payouts.contractor_payout
        WHERE id = '{payout_id}'
        """,
    )
    pg_result = cursor.fetchall()[0]
    assert pg_result[0] == 'succeeded'


@pytest.mark.parametrize('payout_id, mock_get_status_url', POLL_PARAMS)
async def test_stq_poll_failed(
        stq_runner,
        mockserver,
        pgsql,
        mock_api,
        payout_id,
        mock_get_status_url,
):
    @mockserver.json_handler(mock_get_status_url)
    def get_status_handler(request):
        return {
            'Success': True,
            'ErrorCode': '0',
            'Status': 'REJECTED',
            'PaymentId': BANK_PAYOUT_ID,
            'OrderId': payout_id,
            'Amount': 10001,
        }

    await stq_runner.contractor_instant_payouts_tinkoff_process.call(
        task_id='1', kwargs={'id': payout_id},
    )

    assert get_status_handler.times_called == 1

    cursor = pgsql['contractor_instant_payouts'].cursor()
    cursor.execute(
        f"""
        SELECT progress_status
        FROM contractor_instant_payouts.contractor_payout
        WHERE id = '{payout_id}'
        """,
    )
    pg_result = cursor.fetchall()[0]
    assert pg_result[0] == 'rollback'
