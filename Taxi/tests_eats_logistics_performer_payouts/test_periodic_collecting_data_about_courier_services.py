import psycopg2
import pytest


@pytest.mark.pgsql(
    'eats_logistics_performer_payouts',
    files=['eats_logistics_performer_payouts/insert_all_factors.sql'],
)
async def test_periodic_task(
        taxi_eats_logistics_performer_payouts, local_service, pgsql,
):
    await taxi_eats_logistics_performer_payouts.run_periodic_task(
        'collecting-data-about-courier-services-periodic',
    )

    cursor = pgsql['eats_logistics_performer_payouts'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    cursor.execute('SELECT * FROM eats_logistics_performer_payouts.cursors')
    receipt_request = cursor.fetchone()

    assert receipt_request['id'] == 'courier_services'
    assert receipt_request['cursor'] == 'abc_1'


@pytest.mark.pgsql(
    'eats_logistics_performer_payouts',
    files=['eats_logistics_performer_payouts/insert_all_factors.sql'],
)
async def test_periodic_task_with_double_call(
        taxi_eats_logistics_performer_payouts,
        local_service_with_double_call,
        pgsql,
):
    await taxi_eats_logistics_performer_payouts.run_periodic_task(
        'collecting-data-about-courier-services-periodic',
    )

    cursor = pgsql['eats_logistics_performer_payouts'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    cursor.execute('SELECT * FROM eats_logistics_performer_payouts.cursors')
    receipt_request = cursor.fetchone()

    assert receipt_request['id'] == 'courier_services'
    assert receipt_request['cursor'] == 'abc_2'
