import decimal

import dateutil
import pytest

ENDPOINT = '/driver/v1/instant-payouts/v1/sbp/payouts/withdrawal'

PAYOUT_ID = '10e665a1-8ef7-5315-924d-3329f406597f'
PARK_ID = '48b7b5d81559460fb1766938f94009c1'
CONTRACTOR_ID = '48b7b5d81559460fb176693800000001'
IDEMPOTENCY_TOKEN = 'TESTSUITE'
BANK_ID = '100000000001'
PHONE_PD_ID = 'pd_id1'


def build_taximeter_headers(park_id, contractor_id):
    return {
        'User-Agent': 'Taximeter 8.90 (228)',
        'Accept-Language': 'ru',
        'X-Request-Application-Version': '8.90',
        'X-YaTaxi-Park-Id': park_id,
        'X-YaTaxi-Driver-Profile-Id': contractor_id,
    }


def build_headers(
        park_id=PARK_ID,
        contractor_id=CONTRACTOR_ID,
        idempotency_token=IDEMPOTENCY_TOKEN,
):
    return {
        **build_taximeter_headers(
            park_id=park_id, contractor_id=contractor_id,
        ),
        'X-Idempotency-Token': idempotency_token,
    }


def build_payload(amount, phone, bank_id=BANK_ID):
    return {'amount': amount, 'bank_id': bank_id, 'phone': phone}


@pytest.mark.now('2020-01-01T18:00:00+03:00')
async def test_success(
        taxi_contractor_instant_payouts, mock_api, stock, stq, pgsql,
):
    response = await taxi_contractor_instant_payouts.post(
        ENDPOINT,
        headers=build_headers(),
        json=build_payload(amount='40', bank_id=BANK_ID, phone='+70000000000'),
    )

    assert response.status_code == 204, response.text

    with pgsql['contractor_instant_payouts'].cursor() as cursor:
        cursor.execute(
            """
            SELECT
                id,
                park_id,
                contractor_id,
                bank_id,
                phone_pd_id,
                created_at,
                updated_at,
                withdrawal_amount,
                debit_amount,
                debit_fee,
                min_balance,
                transfer_amount,
                progress_status,
                transfer_status,
                method
            FROM
                contractor_instant_payouts.contractor_payout
        """,
        )
        assert cursor.fetchall() == [
            (
                PAYOUT_ID,
                PARK_ID,
                CONTRACTOR_ID,
                BANK_ID,
                PHONE_PD_ID,
                dateutil.parser.parse('2020-01-01T18:00:00+03:00'),
                dateutil.parser.parse('2020-01-01T18:00:00+03:00'),
                decimal.Decimal('40.0000'),
                decimal.Decimal('40.0000'),
                decimal.Decimal('4.1320'),
                decimal.Decimal('95.0101'),
                decimal.Decimal('40.0000'),
                'debit',
                {},
                'sbp',
            ),
        ]
        cursor.execute(
            """
            SELECT
                id,
                updated_at,
                progress_status,
                transfer_status
            FROM
                contractor_instant_payouts.contractor_payout_log
        """,
        )
        assert cursor.fetchall() == [
            (
                PAYOUT_ID,
                dateutil.parser.parse('2020-01-01T18:00:00+03:00'),
                'debit',
                {},
            ),
        ]

    assert stq.contractor_instant_payouts_debit.times_called == 1
    task = stq.contractor_instant_payouts_debit.next_call()
    assert task['id'] == str(PAYOUT_ID)
    assert task['kwargs']['id'] == str(PAYOUT_ID)


TEST_CONFLICT_PARAMS = [
    (
        '76b7b5d81559460fb1766938f94009c2',
        {'code': 'wrong_state', 'message': 'Withdrawal not available.'},
        {},
    ),
    (
        '48b7b5d81559460fb1766938f94009c1',
        {'code': 'wrong_state', 'message': 'Withdrawal not available.'},
        {'CONTRACTOR_INSTANT_PAYOUTS_SBP_ACCOUNT_KINDS': []},
    ),
]


@pytest.mark.parametrize(
    ('park_id', 'expected_response', 'config'), TEST_CONFLICT_PARAMS,
)
async def test_conflict(
        taxi_config,
        taxi_contractor_instant_payouts,
        mock_api,
        stock,
        park_id,
        expected_response,
        config,
):
    taxi_config.set_values(config)

    response = await taxi_contractor_instant_payouts.post(
        ENDPOINT,
        headers=build_headers(park_id=park_id),
        json=build_payload(amount='40', bank_id=BANK_ID, phone='+70000000000'),
    )

    assert response.status_code == 409, response.text
    assert response.json() == expected_response
