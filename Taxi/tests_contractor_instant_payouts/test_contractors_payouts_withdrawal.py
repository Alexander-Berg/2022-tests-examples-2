import decimal

import dateutil
import pytest


@pytest.mark.now('2020-01-01T18:00:00+03:00')
async def test_success(
        contractors_payouts_withdrawal, mock_api, stock, stq, pgsql,
):
    payout_id = '10e665a1-8ef7-5315-924d-3329f406597f'

    response = await contractors_payouts_withdrawal(json={'amount': '40'})
    assert response.status_code == 204, response.text

    with pgsql['contractor_instant_payouts'].cursor() as cursor:
        cursor.execute(
            """
            SELECT
                id,
                park_id,
                contractor_id,
                card_id,
                created_at,
                updated_at,
                withdrawal_amount,
                debit_amount,
                debit_fee,
                min_balance,
                transfer_amount,
                progress_status,
                transfer_status
            FROM
                contractor_instant_payouts.contractor_payout
        """,
        )
        assert cursor.fetchall() == [
            (
                payout_id,
                '48b7b5d81559460fb1766938f94009c1',
                '48b7b5d81559460fb176693800000001',
                '00000000-0001-0001-0000-000000000000',
                dateutil.parser.parse('2020-01-01T18:00:00+03:00'),
                dateutil.parser.parse('2020-01-01T18:00:00+03:00'),
                decimal.Decimal('40.0000'),
                decimal.Decimal('40.0000'),
                decimal.Decimal('4.1320'),
                decimal.Decimal('95.0101'),
                decimal.Decimal('40.0000'),
                'debit',
                {},
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
                payout_id,
                dateutil.parser.parse('2020-01-01T18:00:00+03:00'),
                'debit',
                {},
            ),
        ]

    assert stq.contractor_instant_payouts_debit.times_called == 1
    task = stq.contractor_instant_payouts_debit.next_call()
    assert task['id'] == str(payout_id)
    assert task['kwargs']['id'] == str(payout_id)


@pytest.mark.now('2020-01-01T18:00:00+03:00')
async def test_blocked(
        contractors_payouts_withdrawal, mock_api, stock, stq, pgsql,
):
    payout_id = '10e665a1-8ef7-5315-924d-3329f406597f'

    response = await contractors_payouts_withdrawal(json={'amount': '40'})
    assert response.status_code == 204, response.text

    with pgsql['contractor_instant_payouts'].cursor() as cursor:
        cursor.execute(
            """
            SELECT
                id,
                park_id,
                contractor_id,
                card_id,
                created_at,
                updated_at,
                withdrawal_amount,
                debit_amount,
                debit_fee,
                min_balance,
                transfer_amount,
                progress_status,
                transfer_status
            FROM
                contractor_instant_payouts.contractor_payout
        """,
        )
        assert cursor.fetchall() == [
            (
                payout_id,
                '48b7b5d81559460fb1766938f94009c1',
                '48b7b5d81559460fb176693800000001',
                '00000000-0001-0001-0000-000000000000',
                dateutil.parser.parse('2020-01-01T18:00:00+03:00'),
                dateutil.parser.parse('2020-01-01T18:00:00+03:00'),
                decimal.Decimal('40.0000'),
                decimal.Decimal('40.0000'),
                decimal.Decimal('4.1320'),
                decimal.Decimal('95.0101'),
                decimal.Decimal('40.0000'),
                'debit',
                {},
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
                payout_id,
                dateutil.parser.parse('2020-01-01T18:00:00+03:00'),
                'debit',
                {},
            ),
        ]

    assert stq.contractor_instant_payouts_debit.times_called == 1
    task = stq.contractor_instant_payouts_debit.next_call()
    assert task['id'] == str(payout_id)
    assert task['kwargs']['id'] == str(payout_id)
