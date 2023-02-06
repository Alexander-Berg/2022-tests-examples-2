import psycopg2
import pytest

CURSOR_VALUE = 'cursor_1'

PERFORMER_ID = 1

ADJUSTMENT_FROM_CORE = {
    'id': 1,
    'courier_id': PERFORMER_ID,
    'reason': 'because',
    'amount': 10.1,
    'comment': 'comment',
    'date': '2001-04-01',
    'related_id': 123,
    'order_nr': 'order_nr',
}

NOW = '2022-01-01T01:00:00+0300'
PULSE_NAME = 'PERFORMER_FETCH'
PULSE_TIME = '2022-01-01T01:00:02+0300'


async def test_salary_adjustments_collector(
        taxi_eats_payouts_events,
        pgsql,
        core_salary_adjustments,
        insert_courier_services,
        insert_courier_profile,
        check_last_cursor,
):
    insert_courier_services()

    performer_last_revision = 2
    insert_courier_profile(courier_profile_id=str(PERFORMER_ID), revision=1)
    insert_courier_profile(
        courier_profile_id=str(PERFORMER_ID), revision=performer_last_revision,
    )
    insert_courier_profile(courier_profile_id='2', revision=1)

    core_salary_adjustments.add_adjustments(
        CURSOR_VALUE, [ADJUSTMENT_FROM_CORE],
    )

    await taxi_eats_payouts_events.run_periodic_task(
        'salary-adjustments-collector-periodic',
    )

    check_last_cursor('salary_adjustments', CURSOR_VALUE)

    cursor = pgsql['eats_payouts_events'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    cursor.execute('SELECT * FROM eats_payouts_events.salary_adjustments')
    salary_adjustments = cursor.fetchone()

    assert salary_adjustments['id'] == ADJUSTMENT_FROM_CORE['id']
    assert salary_adjustments['courier_profile_id'] == str(
        ADJUSTMENT_FROM_CORE['courier_id'],
    )
    assert (
        salary_adjustments['courier_profile_revision']
        == performer_last_revision
    )


@pytest.mark.now(NOW)
async def test_salary_adjustments_collector_pulse(
        taxi_eats_payouts_events,
        pgsql,
        testpoint,
        core_salary_adjustments,
        insert_courier_services,
        insert_courier_profile,
        upsert_pulse,
        check_last_cursor,
):
    insert_courier_services()

    core_salary_adjustments.add_adjustments(
        CURSOR_VALUE, [ADJUSTMENT_FROM_CORE],
    )

    @testpoint('couriers_profiles_versions_pulse')
    def _couriers_profiles_versions_pulse(arg):
        insert_courier_profile(
            courier_profile_id=str(PERFORMER_ID), revision=1,
        )
        upsert_pulse(PULSE_NAME, PULSE_TIME)

    await taxi_eats_payouts_events.run_periodic_task(
        'salary-adjustments-collector-periodic',
    )

    check_last_cursor('salary_adjustments', CURSOR_VALUE)

    cursor = pgsql['eats_payouts_events'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    cursor.execute('SELECT * FROM eats_payouts_events.salary_adjustments')
    salary_adjustments = cursor.fetchone()

    assert salary_adjustments['id'] == ADJUSTMENT_FROM_CORE['id']
    assert salary_adjustments['courier_profile_id'] == str(
        ADJUSTMENT_FROM_CORE['courier_id'],
    )
    assert salary_adjustments['courier_profile_revision'] == 1
