import psycopg2
import pytest


@pytest.mark.pgsql(
    'eats_logistics_performer_payouts',
    files=['eats_logistics_performer_payouts/insert_all_factors.sql'],
)
async def test_distlock_task(
        taxi_eats_logistics_performer_payouts,
        pgsql,
        handlers_for_journal_salary,
):
    await taxi_eats_logistics_performer_payouts.run_periodic_task(
        'collecting-journal-salary-adjustments-periodic',
    )

    cursor = pgsql['eats_logistics_performer_payouts'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    cursor.execute('SELECT * FROM eats_logistics_performer_payouts.cursors')
    receipt_request = cursor.fetchone()

    assert receipt_request['id'] == 'courier_adjustments'
    assert receipt_request['cursor'] == 'abc_1'
