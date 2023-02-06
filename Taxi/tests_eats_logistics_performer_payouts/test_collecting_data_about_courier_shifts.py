import psycopg2
import pytest
# pylint: disable=import-error,wildcard-import,R1714

# Common constants:

PG_DBNAME = 'eats_logistics_performer_payouts'
PG_FILES = ['eats_logistics_performer_payouts/insert_all_factors.sql']

PERIODIC_NAME = 'collecting-data-about-courier-shifts-periodic'
STQ_NAME = 'eats_logistics_performer_payouts_process_shift'


# Shift updates mock helpers:

SHIFT_UPDATES_SHIFT_6 = {
    'courier_id': '0023_A6FE',
    'shift_id': '6',
    'eats_id': '1',
    'region_id': 3,
    'status': 'not_started',
    'type': 'planned',
    'pool': 'courier',
    'travel_type': 'bicycle',
    'planned_to_start_at': '2020-06-30T10:00:00+03:00',
    'planned_to_close_at': '2020-06-30T17:00:00+03:00',
    'is_newbie': True,
}

SHIFT_UPDATES_SHIFT_7 = {
    'courier_id': '0023_A6FE',
    'shift_id': '7',
    'eats_id': '1',
    'region_id': 3,
    'status': 'closed',
    'type': 'unplanned',
    'pool': 'courier',
    'travel_type': 'bicycle',
    'started_at': '2020-06-30T11:00:00+03:00',
    'closes_at': '2020-06-30T13:00:00+03:00',
    'duration': 7200,
}

SHIFT_UPDATES_SHIFT_8 = {
    'courier_id': '0023_A6FE',
    'shift_id': '8',
    'eats_id': '1',
    'region_id': 3,
    'status': 'closed',
    'type': 'planned',
    'pool': 'courier',
    'travel_type': 'bicycle',
    'planned_to_start_at': '2020-06-30T14:00:00+03:00',
    'planned_to_close_at': '2020-06-30T18:00:00+03:00',
    'started_at': '2020-06-30T14:00:00+03:00',
    'closes_at': '2020-06-30T18:00:00+03:00',
    'offline_time': 1800,
    'duration': 14400,
    'pause_duration': 0,
    'guarantee': '1000.10',
}

SHIFT_UPDATES_SHIFT_9 = {
    'courier_id': '0025_B45C',
    'shift_id': '9',
    'eats_id': '7',
    'region_id': 3,
    'status': 'in_progress',
    'type': 'planned',
    'pool': 'courier',
    'travel_type': 'bicycle',
    'planned_to_start_at': '2020-06-30T14:00:00+03:00',
    'planned_to_close_at': '2020-06-30T18:00:00+03:00',
    'started_at': '2020-06-30T14:00:00+03:00',
}


SHIFT_UPDATES_CURSOR_END = 'abc_1'

SHIFT_UPDATES_RESPONSE_FIRST = {
    'data': {
        'cursor': SHIFT_UPDATES_CURSOR_END,
        'shifts': [
            SHIFT_UPDATES_SHIFT_6,
            SHIFT_UPDATES_SHIFT_7,
            SHIFT_UPDATES_SHIFT_8,
            SHIFT_UPDATES_SHIFT_9,
        ],
    },
}

SHIFT_UPDATES_RESPONSE_LAST = {
    'data': {'cursor': SHIFT_UPDATES_CURSOR_END, 'shifts': []},
}


def upsert_pulse(pg_cursor, pulse_name, pulse_value):
    # $1 - pulse name (aka id)
    # $2 - pulse value
    query_template = """
INSERT
INTO eats_logistics_performer_payouts.pulses ( id, timestamp_at, updated_at )
VALUES ( '{}', '{}'::TIMESTAMPTZ, NOW() )
ON CONFLICT ( id )
DO
    UPDATE
    SET timestamp_at = EXCLUDED.timestamp_at,
        updated_at = EXCLUDED.updated_at;
    """
    pg_cursor.execute(query_template.format(pulse_name, pulse_value))


def assert_pulse(pg_cursor, pulse_name, pulse_value):
    # $1 - pulse name (aka id)
    query_template = """
SELECT timestamp_at::TEXT AS value
FROM eats_logistics_performer_payouts.pulses
WHERE id = '{}';
    """
    pg_cursor.execute(query_template.format(pulse_name))
    pg_result = pg_cursor.fetchone()
    pulse_value_db = pg_result['value'] if pg_result is not None else None
    assert pulse_value_db == pulse_value


PULSE_SHIFT_NAME = 'SHIFT_FETCH'
PULSE_SHIFT_VALUE = '2022-02-20 10:30:00+03'

PULSE_PERFORMER_NAME = 'PERFORMER_FETCH'
PULSE_PERFORMER_VALUE = '2022-02-20 10:35:00+03'

CURR_TIME = '2022-02-20T10:30:00+0300'


# Tests:


@pytest.mark.pgsql(PG_DBNAME, files=PG_FILES)
@pytest.mark.now(CURR_TIME)
async def test_shift_updates_fetch(
        mockserver, pgsql, stq, taxi_eats_logistics_performer_payouts,
):
    @mockserver.json_handler('/eats-shifts/server-api/shift-data/updates')
    def mock_shift_updates(request):
        assert request.query['cursor'] is not None
        if request.query['cursor'] == SHIFT_UPDATES_CURSOR_END:
            return SHIFT_UPDATES_RESPONSE_LAST
        return SHIFT_UPDATES_RESPONSE_FIRST

    pg_cursor = pgsql[PG_DBNAME].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    upsert_pulse(pg_cursor, PULSE_PERFORMER_NAME, PULSE_PERFORMER_VALUE)

    service = taxi_eats_logistics_performer_payouts
    await service.run_periodic_task(PERIODIC_NAME)

    pg_cursor.execute('SELECT * FROM eats_logistics_performer_payouts.cursors')
    shifts_cursor = pg_cursor.fetchone()

    assert shifts_cursor is not None
    assert shifts_cursor['id'] == 'courier_shifts'
    assert shifts_cursor['cursor'] == SHIFT_UPDATES_CURSOR_END

    assert mock_shift_updates.times_called == 1
    assert_pulse(pg_cursor, PULSE_SHIFT_NAME, PULSE_SHIFT_VALUE)
