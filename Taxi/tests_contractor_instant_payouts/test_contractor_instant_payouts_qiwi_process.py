import decimal

import pytest

PAYOUT_ID = '00000000-0001-0001-0001-000000000000'
BAD_PAYOUT_ID = '00000001-0002-0002-0002-000000000000'
MOCK_URL = (
    '/contractor-instant-payouts-qiwi/partner/payout/'
    'v1/agents/agent/points/point/payments/' + PAYOUT_ID
)
MOCK_URL_EXECUTE = (
    '/contractor-instant-payouts-qiwi/partner/payout/'
    'v1/agents/agent/points/point/payments/' + PAYOUT_ID + '/execute'
)


async def test_stq_ok(stq_runner, mockserver, pgsql):
    @mockserver.json_handler(MOCK_URL)
    def qiwi_handler(request):
        return {'status': {'value': 'READY'}}

    @mockserver.json_handler(MOCK_URL_EXECUTE)
    def qiwi_handler_execute(request):
        return {
            'status': {'value': 'IN_PROGRESS'},
            'commission': {'currency': 'RUB', 'value': '15.00'},
        }

    await stq_runner.contractor_instant_payouts_qiwi_process.call(
        task_id='1', kwargs={'id': PAYOUT_ID},
    )

    assert qiwi_handler.times_called == 1
    assert qiwi_handler_execute.times_called == 1
    assert qiwi_handler.next_call()['request'].json == {
        'recipientDetails': {
            'providerCode': 'bank-card-token-customer',
            'fields': {'account': 'f0000000-0000-0000-0000-000000000001'},
        },
        'amount': {'value': '100.00', 'currency': 'RUB'},
        'source': {
            'paymentType': 'NO_EXTRA_CHARGE',
            'paymentToolType': 'BANK_ACCOUNT',
            'paymentTerminalType': 'INTERNET_BANKING',
        },
        'customer': {'account': 'agent'},
    }

    cursor = pgsql['contractor_instant_payouts'].cursor()
    cursor.execute(
        f"""
        SELECT progress_status, transfer_status, transfer_fee
        FROM contractor_instant_payouts.contractor_payout
        WHERE id = '{PAYOUT_ID}'
        """,
    )
    pg_result = cursor.fetchall()[0]
    assert pg_result[0] == 'transfer'
    assert pg_result[1] == {
        'bpid': PAYOUT_ID,
        'bpst': 'in_progress',
        'repc': 0,
    }
    assert pg_result[2] == decimal.Decimal('15.0000')


async def test_stq_no_payout(stq_runner, pgsql):

    await stq_runner.contractor_instant_payouts_qiwi_process.call(
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


BANK_ERROR_PARAMS = [
    (400, 'payout.bad.request', 'unknown_error'),
    (400, 'payout.insufficient_funds', 'account_insufficient_funds'),
    (404, 'payout.point.not-found', 'unknown_error'),
]


@pytest.mark.parametrize(
    'response_status, bank_error_code, error_code', BANK_ERROR_PARAMS,
)
async def test_stq_bank_error(
        stq_runner,
        mockserver,
        pgsql,
        response_status,
        bank_error_code,
        error_code,
):
    @mockserver.json_handler(MOCK_URL)
    def qiwi_handler(request):
        return mockserver.make_response(
            status=response_status, json={'errorCode': bank_error_code},
        )

    await stq_runner.contractor_instant_payouts_qiwi_process.call(
        task_id='1', kwargs={'id': PAYOUT_ID},
    )

    assert qiwi_handler.times_called == 1
    assert qiwi_handler.next_call()['request'].json == {
        'recipientDetails': {
            'providerCode': 'bank-card-token-customer',
            'fields': {'account': 'f0000000-0000-0000-0000-000000000001'},
        },
        'amount': {'value': '100.00', 'currency': 'RUB'},
        'source': {
            'paymentType': 'NO_EXTRA_CHARGE',
            'paymentToolType': 'BANK_ACCOUNT',
            'paymentTerminalType': 'INTERNET_BANKING',
        },
        'customer': {'account': 'agent'},
    }

    cursor = pgsql['contractor_instant_payouts'].cursor()
    cursor.execute(
        f"""
        SELECT progress_status, transfer_status, error_code
        FROM contractor_instant_payouts.contractor_payout
        WHERE id = '{PAYOUT_ID}'
        """,
    )
    pg_result = cursor.fetchall()[0]
    assert pg_result[0] == 'rollback'
    assert pg_result[1] == {
        'bper': '{{"errorCode":"{}"}}'.format(bank_error_code),
        'bpst': 'failed',
        'repc': 0,
    }
    assert pg_result[2] == error_code
