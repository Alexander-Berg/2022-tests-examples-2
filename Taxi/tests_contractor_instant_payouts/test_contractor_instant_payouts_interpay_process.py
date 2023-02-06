import pytest

MOCK_URL = '/interpay/v1/svc/card_withdrawal/requests'
PAYOUT_ID = '00000000-0001-0001-0001-000000000000'
BAD_PAYOUT_ID = '00000001-0002-0002-0002-000000000000'
BANK_PAYOUT_ID = 123


async def test_stq_ok(stq_runner, mockserver, pgsql, mock_api):
    @mockserver.json_handler(MOCK_URL)
    def interpay_handler(request):
        assert request.headers['Authorization'] == 'Bearer token1'
        assert request.headers['Service-Key'] == '1'
        assert request.headers['Idempotency-Replay'] == 'true'

        assert request.json == {
            'contract_source_id': 1,
            'external_ref_id': PAYOUT_ID,
            'card_binding_id': 'card_id1',
            'amount': '100.01',
            'is_fee_included': False,
        }

        return {
            'id': BANK_PAYOUT_ID,
            'public_id': 'id1',
            'contract_source_id': 1,
            'external_ref_id': PAYOUT_ID,
            'card_number': '424242xxxxxx4242',
            'amount_sent': '100.01',
            'amount_fee': '100.0000',
            'amount_total': '200.0100',
            'posted_at': '2022-01-01T12:00:00+00:00',
            'state': 'processed',
            'processed_at': '2022-01-01T12:00:00+00:00',
        }

    await stq_runner.contractor_instant_payouts_interpay_process.call(
        task_id='1', kwargs={'id': PAYOUT_ID},
    )

    assert interpay_handler.times_called == 1

    cursor = pgsql['contractor_instant_payouts'].cursor()
    cursor.execute(
        f"""
        SELECT progress_status, transfer_status
        FROM contractor_instant_payouts.contractor_payout
        WHERE id = '{PAYOUT_ID}'
        """,
    )
    pg_result = cursor.fetchall()[0]
    assert pg_result[0] == 'transfer'
    assert pg_result[1] == {
        'bpid': f'{BANK_PAYOUT_ID}',
        'bpst': 'in_progress',
        'repc': 0,
    }


BAD_PARAMS = [
    ('200201', 'account_insufficient_funds'),
    ('400000', 'account_blocked'),
    ('bad_reason', 'unknown_error'),
]


@pytest.mark.parametrize('reason, error_code', BAD_PARAMS)
async def test_stq_error(
        stq_runner, mockserver, pgsql, mock_api, reason, error_code,
):
    @mockserver.json_handler(MOCK_URL)
    def interpay_handler(request):
        assert request.headers['Authorization'] == 'Bearer token1'
        assert request.headers['Service-Key'] == '1'
        assert request.headers['Idempotency-Replay'] == 'true'

        assert request.json == {
            'contract_source_id': 1,
            'external_ref_id': PAYOUT_ID,
            'card_binding_id': 'card_id1',
            'amount': '100.01',
            'is_fee_included': False,
        }

        return mockserver.make_response(
            status=400,
            json={
                'error': {
                    'code': 400,
                    'request': 'request_id1',
                    'reason': reason,
                    'message': 'Error message',
                    'details': {'amount': '100.0100', 'balance': '100.0000'},
                },
            },
        )

    await stq_runner.contractor_instant_payouts_interpay_process.call(
        task_id='1', kwargs={'id': PAYOUT_ID},
    )

    assert interpay_handler.times_called == 1

    cursor = pgsql['contractor_instant_payouts'].cursor()
    cursor.execute(
        f"""
        SELECT progress_status, error_code, transfer_status
        FROM contractor_instant_payouts.contractor_payout
        WHERE id = '{PAYOUT_ID}'
        """,
    )
    pg_result = cursor.fetchall()[0]
    assert pg_result[0] == 'rollback'
    assert pg_result[1] == error_code
    assert pg_result[2] == {'bpst': 'failed', 'repc': 0, 'bper': reason}


async def test_stq_no_payout(stq_runner, pgsql):

    await stq_runner.contractor_instant_payouts_interpay_process.call(
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
