import pytest

BANK_PAYOUT_ID = '00000001-0002-0003-0004-000000000005'
BAD_PAYOUT_ID = '00000001-0002-0002-0002-000000000000'

CARD_PAYOUT_ID = '00000000-0001-0001-0001-000000000000'
SBP_PAYOUT_ID = '00000000-0001-0001-0001-000000000001'

CARD_MOCK_URL = (
    '/contractor-instant-payouts-mozen/api/public/payout/pay/status/'
)
SBP_MOCK_URL = '/contractor-instant-payouts-mozen/api/public/sbp/pay/status/'

TEST_PARAMS = [
    (CARD_PAYOUT_ID, CARD_MOCK_URL, BANK_PAYOUT_ID),
    (SBP_PAYOUT_ID, SBP_MOCK_URL, SBP_PAYOUT_ID),
]


@pytest.mark.parametrize(('payout_id', 'mock_url', 'payment_id'), TEST_PARAMS)
async def test_stq_ok(
        stq_runner, mockserver, pgsql, payout_id, mock_url, payment_id,
):
    @mockserver.json_handler(mock_url + payment_id)
    def alfabank_handler(request):
        return {'payment_id': payment_id, 'status': 'succeed'}

    await stq_runner.contractor_instant_payouts_alfabank_poll.call(
        task_id='1', kwargs={'id': payout_id},
    )

    assert alfabank_handler.times_called == 1

    cursor = pgsql['contractor_instant_payouts'].cursor()
    cursor.execute(
        f"""
        SELECT progress_status
        FROM contractor_instant_payouts.contractor_payout
        WHERE id = '{payout_id}'
        """,
    )
    row = cursor.fetchall()[0]
    assert row[0] == 'succeeded'


@pytest.mark.parametrize(('payout_id', 'mock_url', 'payment_id'), TEST_PARAMS)
async def test_stq_rollback(
        stq_runner, mockserver, pgsql, payout_id, mock_url, payment_id,
):
    @mockserver.json_handler(mock_url + payment_id)
    def alfabank_handler(request):
        return {'payment_id': payment_id, 'status': 'error'}

    await stq_runner.contractor_instant_payouts_alfabank_poll.call(
        task_id='1', kwargs={'id': payout_id},
    )

    assert alfabank_handler.times_called == 1

    cursor = pgsql['contractor_instant_payouts'].cursor()
    cursor.execute(
        f"""
        SELECT progress_status, error_code, transfer_status
        FROM contractor_instant_payouts.contractor_payout
        WHERE id = '{payout_id}'
        """,
    )
    row = cursor.fetchall()[0]
    assert row[0] == 'rollback'
    assert row[1] is None
    assert row[2] == {'bpid': BANK_PAYOUT_ID, 'bpst': 'failed', 'repc': 0}


async def test_stq_no_payout(stq_runner, pgsql):

    await stq_runner.contractor_instant_payouts_alfabank_poll.call(
        task_id='1', kwargs={'id': BAD_PAYOUT_ID},
    )

    cursor = pgsql['contractor_instant_payouts'].cursor()
    cursor.execute(
        f"""
        SELECT count(*)
        FROM contractor_instant_payouts.contractor_payout
        WHERE id = '{BAD_PAYOUT_ID}'
        """,
    )
    count = cursor.fetchall()[0][0]
    assert count == 0
