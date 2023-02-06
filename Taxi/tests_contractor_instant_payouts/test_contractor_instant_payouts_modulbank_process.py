import pytest

CARD_MOCK_URL = '/contractor-instant-payouts-modulbank/api/payouts'
SBP_MOCK_URL = '/contractor-instant-payouts-modulbank/api/sbp/payouts'
CARD_PAYOUT_ID = '00000000-0001-0001-0001-000000000000'
SBP_PAYOUT_ID = '00000000-0001-0001-0001-000000000001'
BAD_PAYOUT_ID = '00000001-0002-0002-0002-000000000000'
BANK_PAYOUT_ID = '00000001-0002-0003-0004-000000000005'

OK_PARAMS = [
    (
        CARD_PAYOUT_ID,
        CARD_MOCK_URL,
        {
            'account_id': 'a0000000-0000-0000-0000-000000000001',
            'amount': 100.01,
            'card_token': 'c0000000-0000-0000-0000-000000000001',
            'description': (
                'Перевод средств с баланса таксометра '
                'по договору 12345 на карту *1234'
            ),
            'oid': '00000000-0001-0001-0001-000000000000',
        },
    ),
    (
        SBP_PAYOUT_ID,
        SBP_MOCK_URL,
        {
            'account_id': 'a0000000-0000-0000-0000-000000000001',
            'amount': '100.01',
            'bank_id': 'bank1',
            'phone': '0000000000',
            'description': (
                'Перевод средств с баланса таксометра '
                'по договору 12345 на телефон +70000000000'
            ),
        },
    ),
]


@pytest.mark.parametrize(
    'payout_id, mock_url, expected_modulbank_request', OK_PARAMS,
)
async def test_stq_ok(
        stq_runner,
        mockserver,
        pgsql,
        mock_api,
        payout_id,
        mock_url,
        expected_modulbank_request,
):
    @mockserver.json_handler(mock_url)
    def modulbank_handler(request):
        return {'status': 'success', 'data': {'id': BANK_PAYOUT_ID}}

    await stq_runner.contractor_instant_payouts_modulbank_process.call(
        task_id='1', kwargs={'id': payout_id},
    )

    assert modulbank_handler.times_called == 1
    assert (
        modulbank_handler.next_call()['request'].json
        == expected_modulbank_request
    )

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
    assert pg_result[1] == {
        'bpid': BANK_PAYOUT_ID,
        'bpst': 'in_progress',
        'repc': 0,
    }


async def test_stq_no_payout(stq_runner, pgsql):

    await stq_runner.contractor_instant_payouts_modulbank_process.call(
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
