import decimal

import pytest

CARD_MOCK_URL = (
    '/contractor-instant-payouts-modulbank'
    + '/api/payouts/00000001-0002-0002-0002-000000000000'
)
SBP_MOCK_URL = (
    '/contractor-instant-payouts-modulbank'
    + '/api/sbp/payouts/00000001-0002-0002-0002-000000000000'
)
CARD_PAYOUT_ID = '00000000-0001-0001-0001-000000000000'
SBP_PAYOUT_ID = '00000000-0001-0001-0001-000000000001'
BAD_PAYOUT_ID = '00000001-0002-0002-0002-000000000000'
BANK_PAYOUT_ID = '00000001-0002-0003-0004-000000000005'

CARD_OK_RESPONSE = {
    'status': 'success',
    'data': {
        'id': BANK_PAYOUT_ID,
        'status': 'completed',
        'transactions': [
            {'id': BANK_PAYOUT_ID, 'amount': 100, 'commission': 1.5},
        ],
    },
}

SBP_OK_RESPONSE = {
    'status': 'success',
    'data': {'id': BANK_PAYOUT_ID, 'status': 'completed'},
}


OK_PARAMS = [
    (CARD_PAYOUT_ID, CARD_MOCK_URL, CARD_OK_RESPONSE),
    (SBP_PAYOUT_ID, SBP_MOCK_URL, SBP_OK_RESPONSE),
]


@pytest.mark.parametrize('payout_id, mock_url, mock_response', OK_PARAMS)
async def test_stq_ok(
        stq_runner, mockserver, pgsql, payout_id, mock_url, mock_response,
):
    @mockserver.json_handler(mock_url)
    def modulbank_handler(request):
        return mock_response

    await stq_runner.contractor_instant_payouts_modulbank_poll.call(
        task_id='1', kwargs={'id': payout_id},
    )

    assert modulbank_handler.times_called == 1

    cursor = pgsql['contractor_instant_payouts'].cursor()
    cursor.execute(
        f"""
        SELECT progress_status, transfer_fee
        FROM contractor_instant_payouts.contractor_payout
        WHERE id = '{payout_id}'
        """,
    )
    row = cursor.fetchall()[0]
    assert row[0] == 'succeeded'
    assert row[1] == (
        decimal.Decimal('1.5000') if payout_id == CARD_PAYOUT_ID else None
    )


CARD_BAD_RESPONSE = {
    'status': 'success',
    'data': {
        'id': BANK_PAYOUT_ID,
        'status': 'failed',
        'transactions': [
            {
                'id': BANK_PAYOUT_ID,
                'amount': 100,
                'reason_code': 'ERR_INSUFFICIENT_BALANCE',
            },
        ],
    },
}

SBP_BAD_RESPONSE = {
    'status': 'success',
    'data': {'id': BANK_PAYOUT_ID, 'status': 'failed'},
}


BAD_PARAMS = [
    (CARD_PAYOUT_ID, CARD_MOCK_URL, CARD_BAD_RESPONSE),
    (SBP_PAYOUT_ID, SBP_MOCK_URL, SBP_BAD_RESPONSE),
]


@pytest.mark.parametrize('payout_id, mock_url, mock_response', BAD_PARAMS)
async def test_stq_rollback(
        stq_runner, mockserver, pgsql, payout_id, mock_url, mock_response,
):
    @mockserver.json_handler(mock_url)
    def modulbank_handler(request):
        return mock_response

    await stq_runner.contractor_instant_payouts_modulbank_poll.call(
        task_id='1', kwargs={'id': payout_id},
    )

    assert modulbank_handler.times_called == 1

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
    if payout_id == CARD_PAYOUT_ID:
        assert row[1] == 'account_insufficient_funds'
        assert row[2] == {
            'bper': 'ERR_INSUFFICIENT_BALANCE',
            'bpid': '00000001-0002-0002-0002-000000000000',
            'bpst': 'failed',
            'repc': 0,
        }
    else:
        assert row[1] is None
        assert row[2] == {
            'bpid': '00000001-0002-0002-0002-000000000000',
            'bpst': 'failed',
            'repc': 0,
        }


async def test_stq_no_payout(stq_runner, pgsql):

    await stq_runner.contractor_instant_payouts_modulbank_poll.call(
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
