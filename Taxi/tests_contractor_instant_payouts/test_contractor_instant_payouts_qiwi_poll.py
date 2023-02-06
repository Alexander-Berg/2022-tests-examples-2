PAYOUT_ID = '00000000-0001-0001-0001-000000000000'
BAD_PAYOUT_ID = '00000001-0002-0002-0002-000000000000'
MOCK_URL = (
    '/contractor-instant-payouts-qiwi/partner/'
    'payout/v1/agents/agent/points/point/payments/' + PAYOUT_ID
)


async def test_stq_ok(stq_runner, mockserver, pgsql):
    @mockserver.json_handler(MOCK_URL)
    def qiwi_handler(request):
        return {'status': {'value': 'COMPLETED'}}

    await stq_runner.contractor_instant_payouts_qiwi_poll.call(
        task_id='1', kwargs={'id': PAYOUT_ID},
    )

    assert qiwi_handler.times_called == 1

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
    def qiwi_handler(request):
        return {'status': {'value': 'FAILED', 'errorCode': 'code'}}

    await stq_runner.contractor_instant_payouts_qiwi_poll.call(
        task_id='1', kwargs={'id': PAYOUT_ID},
    )

    assert qiwi_handler.times_called == 1

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
    assert row[1] == 'unknown_error'
    assert row[2] == {
        'bpid': PAYOUT_ID,
        'bpst': 'failed',
        'repc': 0,
        'bper': 'code',
    }


async def test_stq_no_payout(stq_runner, pgsql):

    await stq_runner.contractor_instant_payouts_qiwi_poll.call(
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
