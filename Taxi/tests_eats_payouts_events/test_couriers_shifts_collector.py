import psycopg2
import pytest

SHIFT_ID = '2'
SHIFT_START = '2022-07-30T14:00:00+03:00'
SHIFT_FRAUD_TIME = '2022-07-30T13:59:59+03:00'

COURIER_PROFILE_ID = '2'
COURIER_PROFILE_REVISION = 2

DRIVER_ID = '1_2'
DRIVER_UUID = '2'

PERFORMER_PULSE_NAME = 'PERFORMER_FETCH'
PERFORMER_PULSE_TIME = '2022-07-30T14:00:01+03:00'

SHIFT_PULSE_NAME = 'SHIFT_FETCH'
SHIFT_PULSE_VALUE = '2022-07-30 14:00:00+03'

CURSOR_NAME = 'couriers_shifts'

CURR_TIME = '2022-07-30T14:00:00+03:00'

SHIFT_UPDATES_SHIFT_1 = {
    'courier_id': '0023_A6FE',
    'shift_id': '1',
    'eats_id': '1',
    'region_id': 3,
    'status': 'not_started',
    'type': 'planned',
    'pool': 'courier',
    'travel_type': 'bicycle',
    'planned_to_start_at': SHIFT_START,
    'planned_to_close_at': '2020-06-30T17:00:00+03:00',
    'is_newbie': True,
}

SHIFT_UPDATES_SHIFT_2 = {
    'courier_id': DRIVER_ID,
    'shift_id': SHIFT_ID,
    'eats_id': COURIER_PROFILE_ID,
    'region_id': 3,
    'status': 'in_progress',
    'type': 'planned',
    'pool': 'courier',
    'travel_type': 'bicycle',
    'planned_to_start_at': SHIFT_START,
    'planned_to_close_at': '2020-06-30T18:00:00+03:00',
    'started_at': SHIFT_START,
}

SHIFT_UPDATES_CURSOR_END = 'cursor_1'

SHIFT_UPDATES_RESPONSE_TWO_SHIFTS = {
    'data': {
        'cursor': SHIFT_UPDATES_CURSOR_END,
        'shifts': [SHIFT_UPDATES_SHIFT_1, SHIFT_UPDATES_SHIFT_2],
    },
}

SHIFT_UPDATES_RESPONSE_ONE_SHIFT = {
    'data': {
        'cursor': SHIFT_UPDATES_CURSOR_END,
        'shifts': [SHIFT_UPDATES_SHIFT_2],
    },
}

SHIFT_UPDATES_RESPONSE_LAST = {
    'data': {'cursor': SHIFT_UPDATES_CURSOR_END, 'shifts': []},
}


@pytest.mark.now(CURR_TIME)
async def test_couriers_shifts_collector(
        mockserver,
        pgsql,
        taxi_eats_payouts_events,
        check_last_cursor,
        check_last_pulse,
        upsert_pulse,
        insert_courier_services,
        insert_courier_profile,
):
    insert_courier_services()
    insert_courier_profile(
        courier_profile_id=COURIER_PROFILE_ID,
        revision=COURIER_PROFILE_REVISION,
    )

    upsert_pulse(PERFORMER_PULSE_NAME, PERFORMER_PULSE_TIME)

    @mockserver.json_handler('/eats-shifts/server-api/shift-data/updates')
    def mock_shift_updates(request):
        if (
                'cursor' in request.query
                and request.query['cursor'] == SHIFT_UPDATES_CURSOR_END
        ):
            return SHIFT_UPDATES_RESPONSE_LAST
        return SHIFT_UPDATES_RESPONSE_TWO_SHIFTS

    service = taxi_eats_payouts_events
    await service.run_periodic_task('couriers-shifts-collector-periodic')

    assert mock_shift_updates.times_called == 1
    check_last_cursor(CURSOR_NAME, SHIFT_UPDATES_CURSOR_END)
    check_last_pulse(SHIFT_PULSE_NAME, SHIFT_PULSE_VALUE)

    cursor = pgsql['eats_payouts_events'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    cursor.execute('SELECT * FROM eats_payouts_events.shifts')
    shift = cursor.fetchone()

    assert shift['id'] == SHIFT_ID
    assert shift['courier_profile_id'] == COURIER_PROFILE_ID
    assert shift['courier_profile_revision'] == COURIER_PROFILE_REVISION
    assert not shift['fraud_on_start']


@pytest.mark.now(CURR_TIME)
async def test_couriers_shifts_collector_pulse(
        mockserver,
        pgsql,
        testpoint,
        taxi_eats_payouts_events,
        check_last_cursor,
        check_last_pulse,
        upsert_pulse,
        insert_courier_services,
        insert_courier_profile,
):
    insert_courier_services()

    @testpoint('couriers_profiles_versions_pulse')
    def _couriers_profiles_versions_pulse(arg):
        insert_courier_profile(
            courier_profile_id=COURIER_PROFILE_ID,
            revision=COURIER_PROFILE_REVISION,
        )
        upsert_pulse(PERFORMER_PULSE_NAME, PERFORMER_PULSE_TIME)

    @mockserver.json_handler('/eats-shifts/server-api/shift-data/updates')
    def mock_shift_updates(request):
        if (
                'cursor' in request.query
                and request.query['cursor'] == SHIFT_UPDATES_CURSOR_END
        ):
            return SHIFT_UPDATES_RESPONSE_LAST
        return SHIFT_UPDATES_RESPONSE_ONE_SHIFT

    service = taxi_eats_payouts_events
    await service.run_periodic_task('couriers-shifts-collector-periodic')

    assert mock_shift_updates.times_called == 1
    check_last_cursor(CURSOR_NAME, SHIFT_UPDATES_CURSOR_END)
    check_last_pulse(SHIFT_PULSE_NAME, SHIFT_PULSE_VALUE)

    cursor = pgsql['eats_payouts_events'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    cursor.execute('SELECT * FROM eats_payouts_events.shifts')
    shift = cursor.fetchone()

    assert shift['id'] == SHIFT_ID
    assert shift['courier_profile_id'] == COURIER_PROFILE_ID
    assert shift['courier_profile_revision'] == COURIER_PROFILE_REVISION


@pytest.mark.now(CURR_TIME)
async def test_couriers_shifts_collector_fraud(
        mockserver,
        pgsql,
        taxi_eats_payouts_events,
        check_last_cursor,
        check_last_pulse,
        upsert_pulse,
        insert_courier_services,
        insert_courier_profile,
        insert_fraud_event,
):
    insert_courier_services()
    insert_courier_profile(courier_profile_id='2', revision=1)

    insert_fraud_event(driver_uuid='1', event_time=SHIFT_FRAUD_TIME)
    insert_fraud_event(driver_uuid=DRIVER_UUID, event_time=SHIFT_FRAUD_TIME)
    insert_fraud_event(driver_uuid=DRIVER_UUID, event_time=SHIFT_FRAUD_TIME)

    upsert_pulse(PERFORMER_PULSE_NAME, PERFORMER_PULSE_TIME)

    @mockserver.json_handler('/eats-shifts/server-api/shift-data/updates')
    def mock_shift_updates(request):
        if (
                'cursor' in request.query
                and request.query['cursor'] == SHIFT_UPDATES_CURSOR_END
        ):
            return SHIFT_UPDATES_RESPONSE_LAST
        return SHIFT_UPDATES_RESPONSE_TWO_SHIFTS

    service = taxi_eats_payouts_events
    await service.run_periodic_task('couriers-shifts-collector-periodic')

    assert mock_shift_updates.times_called == 1
    check_last_cursor(CURSOR_NAME, SHIFT_UPDATES_CURSOR_END)
    check_last_pulse(SHIFT_PULSE_NAME, SHIFT_PULSE_VALUE)

    cursor = pgsql['eats_payouts_events'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    cursor.execute('SELECT * FROM eats_payouts_events.shifts')
    shift = cursor.fetchone()

    assert shift['id'] == '2'
    assert shift['courier_profile_id'] == '2'
    assert shift['courier_profile_revision'] == 1
    assert shift['fraud_on_start'] == 2


@pytest.mark.now(CURR_TIME)
async def test_couriers_shifts_collector_update_driver(
        mockserver,
        pgsql,
        taxi_eats_payouts_events,
        check_last_cursor,
        check_last_pulse,
        upsert_pulse,
        insert_courier_services,
        insert_courier_profile,
        insert_driver_profile,
):
    insert_courier_services()
    insert_courier_profile(
        courier_profile_id=COURIER_PROFILE_ID,
        revision=COURIER_PROFILE_REVISION,
    )

    insert_driver_profile(driver_id=DRIVER_ID, courier_profile_id='some_id')

    upsert_pulse(PERFORMER_PULSE_NAME, PERFORMER_PULSE_TIME)

    @mockserver.json_handler('/eats-shifts/server-api/shift-data/updates')
    def mock_shift_updates(request):
        if (
                'cursor' in request.query
                and request.query['cursor'] == SHIFT_UPDATES_CURSOR_END
        ):
            return SHIFT_UPDATES_RESPONSE_LAST
        return SHIFT_UPDATES_RESPONSE_ONE_SHIFT

    service = taxi_eats_payouts_events
    await service.run_periodic_task('couriers-shifts-collector-periodic')

    assert mock_shift_updates.times_called == 1
    check_last_cursor(CURSOR_NAME, SHIFT_UPDATES_CURSOR_END)
    check_last_pulse(SHIFT_PULSE_NAME, SHIFT_PULSE_VALUE)

    cursor = pgsql['eats_payouts_events'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    cursor.execute('SELECT * FROM eats_payouts_events.driver_profiles')
    driver = cursor.fetchone()

    assert driver['id'] == DRIVER_ID
    assert driver['courier_profile_id'] == COURIER_PROFILE_ID
