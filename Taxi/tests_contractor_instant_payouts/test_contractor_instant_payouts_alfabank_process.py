import decimal

import pytest

CARD_MOCK_URL = '/contractor-instant-payouts-mozen/api/public/payout/pay'
SBP_MOCK_URL = '/contractor-instant-payouts-mozen/api/public/sbp/pay'
CARD_PAYOUT_ID = '00000000-0001-0001-0001-000000000000'
SBP_PAYOUT_ID = '00000000-0001-0001-0001-000000000001'
BAD_PAYOUT_ID = '00000001-0002-0002-0002-000000000000'
BANK_PAYOUT_ID = '00000001-0002-0003-0004-000000000005'

TEST_PARAMS = [
    (
        CARD_PAYOUT_ID,
        CARD_MOCK_URL,
        {
            'card_id': 'c0000000-0000-0000-0000-000000000001',
            'id': '00000000-0001-0001-0001-000000000000',
            'value': {'amount': 10001, 'currency': 'RUB'},
            'yandex_user_id': '48b7b5d81559460fb176693800000001',
            'description': (
                'Перевод средств с баланса таксометра '
                'по договору 12345 на карту *1234'
            ),
        },
    ),
    (
        SBP_PAYOUT_ID,
        SBP_MOCK_URL,
        {
            'phone_number': '0000000000',
            'member_id': 'bank_id1',
            'id': SBP_PAYOUT_ID,
            'value': {'amount': 10001, 'currency': 'RUB'},
            'yandex_user_id': '48b7b5d81559460fb176693800000001',
            'description': (
                'Перевод средств с баланса таксометра '
                'по договору 12345 на телефон +70000000000'
            ),
        },
    ),
]


@pytest.mark.parametrize(
    ('payout_id', 'mock_url', 'expected_mozen_request'), TEST_PARAMS,
)
async def test_stq_ok(
        stq_runner,
        mockserver,
        pgsql,
        mock_api,
        payout_id,
        mock_url,
        expected_mozen_request,
):
    @mockserver.json_handler(mock_url)
    def alfabank_handler(request):
        return {
            'id': payout_id,
            'payment_id': BANK_PAYOUT_ID,
            'value': {'currency': 'RUB', 'amount': 10000},
            'comission': {'currency': 'RUB', 'amount': 1500},
            'status': 'accepted',
        }

    await stq_runner.contractor_instant_payouts_alfabank_process.call(
        task_id='1', kwargs={'id': payout_id},
    )

    assert alfabank_handler.times_called == 1
    assert (
        alfabank_handler.next_call()['request'].json == expected_mozen_request
    )

    cursor = pgsql['contractor_instant_payouts'].cursor()
    cursor.execute(
        f"""
        SELECT progress_status, transfer_status, transfer_fee
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
    assert pg_result[2] == decimal.Decimal('15.0000')


async def test_stq_no_payout(stq_runner, pgsql):

    await stq_runner.contractor_instant_payouts_alfabank_process.call(
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
    (400, 'InputValidationError', 'unknown_error'),
    (400, 'NotEnoughMoneyError', 'account_insufficient_funds'),
    (400, 'TokenDeprecated', 'account_blocked'),
    (404, 'PaymentCardNotFound', 'unknown_error'),
    (404, 'ParkNotFound', 'unknown_error'),
]


@pytest.mark.parametrize(
    'response_status, bank_error_code, error_code', BANK_ERROR_PARAMS,
)
@pytest.mark.parametrize(
    ('payout_id', 'mock_url', 'expected_mozen_request'), TEST_PARAMS,
)
async def test_stq_bank_error(
        stq_runner,
        mockserver,
        pgsql,
        mock_api,
        response_status,
        bank_error_code,
        error_code,
        payout_id,
        mock_url,
        expected_mozen_request,
):
    @mockserver.json_handler(mock_url)
    def alfabank_handler(request):
        return mockserver.make_response(
            status=response_status,
            json={'code': bank_error_code, 'message': 'Error message'},
        )

    await stq_runner.contractor_instant_payouts_alfabank_process.call(
        task_id='1', kwargs={'id': payout_id},
    )

    assert alfabank_handler.times_called == 1
    assert (
        alfabank_handler.next_call()['request'].json == expected_mozen_request
    )

    cursor = pgsql['contractor_instant_payouts'].cursor()
    cursor.execute(
        f"""
        SELECT progress_status, transfer_status, error_code
        FROM contractor_instant_payouts.contractor_payout
        WHERE id = '{payout_id}'
        """,
    )
    pg_result = cursor.fetchall()[0]
    assert pg_result[0] == 'rollback'
    assert pg_result[1] == {
        'bper': bank_error_code,
        'bpst': 'failed',
        'repc': 0,
    }
    assert pg_result[2] == error_code
