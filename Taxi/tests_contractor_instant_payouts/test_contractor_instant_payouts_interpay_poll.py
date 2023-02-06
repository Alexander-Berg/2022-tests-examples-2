PAYOUT_ID = '00000000-0001-0001-0001-000000000000'
BAD_PAYOUT_ID = '00000001-0002-0002-0002-000000000000'

BANK_PAYOUT_ID = '123'
MOCK_URL = f'/interpay/v1/svc/card_withdrawal/requests/' + BANK_PAYOUT_ID


async def test_stq_ok(stq_runner, mockserver, pgsql):
    @mockserver.json_handler(MOCK_URL)
    def interpay_handler(request):
        assert request.headers['Authorization'] == 'Bearer token1'
        assert request.headers['Service-Key'] == '1'

        return {
            'id': int(BANK_PAYOUT_ID),
            'contract_source_id': 1,
            'card_number': '424242xxxxxx4242',
            'amount_sent': '100.01',
            'amount_fee': '100.0000',
            'amount_total': '200.0100',
            'posted_at': '2022-01-01T12:00:00+00:00',
            'state': 'processed',
        }

    await stq_runner.contractor_instant_payouts_interpay_poll.call(
        task_id='1', kwargs={'id': PAYOUT_ID},
    )

    assert interpay_handler.times_called == 1

    cursor = pgsql['contractor_instant_payouts'].cursor()
    cursor.execute(
        f"""
        SELECT progress_status
        FROM contractor_instant_payouts.contractor_payout
        WHERE id = '{PAYOUT_ID}'
        """,
    )
    row = cursor.fetchall()[0]
    assert row[0] == 'succeeded'


async def test_stq_rollback(stq_runner, mockserver, pgsql):
    @mockserver.json_handler(MOCK_URL)
    def interpay_handler(request):
        assert request.headers['Authorization'] == 'Bearer token1'
        assert request.headers['Service-Key'] == '1'

        return {
            'id': int(BANK_PAYOUT_ID),
            'public_id': 'id1',
            'contract_source_id': 1,
            'external_ref_id': PAYOUT_ID,
            'card_number': '424242xxxxxx4242',
            'amount_sent': '100.01',
            'amount_fee': '100.0000',
            'amount_total': '200.0100',
            'posted_at': '2022-01-01T12:00:00+00:00',
            'state': 'cancelled',
            'processed_at': '2022-01-01T12:00:00+00:00',
        }

    await stq_runner.contractor_instant_payouts_interpay_poll.call(
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
    row = cursor.fetchall()[0]
    assert row[0] == 'rollback'
    assert row[1] is None
    assert row[2] == {'bpid': BANK_PAYOUT_ID, 'bpst': 'failed', 'repc': 0}


async def test_stq_no_payout(stq_runner, pgsql):

    await stq_runner.contractor_instant_payouts_interpay_poll.call(
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
