import datetime as dt

import psycopg2
import pytest


PERIODIC = 'active-places-updater-periodic'
DEFAULT_INTERVAL = 28800
DEFAULT_YT_TABLE = '//home/eda-dwh/ods/bigfood/place/place'
DEFAULT_YT_TIMEOUT = 60000
DEFAULT_YT_BATCH_SIZE = 500
DEFAULT_UPDATE_TTL = 3
DEFAULT_BATCH_SIZE = 500
TIMEDELTA = dt.timedelta(minutes=15)

DEFAULT_CONFIG = {
    'enabled': True,
    'interval_s': DEFAULT_INTERVAL,
    'yt_table': DEFAULT_YT_TABLE,
    'yt_timeout_ms': DEFAULT_YT_TIMEOUT,
    'yt_batch_size': DEFAULT_YT_BATCH_SIZE,
    'update_ttl_h': DEFAULT_UPDATE_TTL,
    'batch_size': DEFAULT_BATCH_SIZE,
}

# Testpoints
TESTPOINT_STEP = 'eats_place_rating::active-places-updater-step'
TESTPOINT_UPDATE_PLACES = (
    'eats_place_rating::active-places-updater-update-places'
)
TESTPOINT_PROCESS_START = (
    'eats_place_rating::active-places-updater-process-start'
)
TESTPOINT_PROCESS_BATCH_GENERAL = (
    'eats_place_rating::active-places-updater-process-batch-general'
)
TESTPOINT_PROCESS_BATCH_REMAINDER = (
    'eats_place_rating::active-places-updater-process-batch-remainder'
)


@pytest.fixture(name='get_active_places')
def _get_active_places(pgsql):
    def _wrapper():
        cursor = pgsql['eats_place_rating'].cursor()
        cursor.execute('SELECT * FROM eats_place_rating.active_places')
        result = [{'place_id': row[0], 'updated_at': row[1]} for row in cursor]
        return result

    return _wrapper


@pytest.mark.config(
    EATS_PLACE_RATING_ACTIVE_PLACES_UPDATER={
        'enabled': False,
        'interval_s': DEFAULT_INTERVAL,
        'yt_table': DEFAULT_YT_TABLE,
        'yt_timeout_ms': DEFAULT_YT_TIMEOUT,
        'yt_batch_size': DEFAULT_YT_BATCH_SIZE,
        'update_ttl_h': DEFAULT_UPDATE_TTL,
        'batch_size': DEFAULT_BATCH_SIZE,
    },
)
@pytest.mark.suspend_periodic_tasks(PERIODIC)
async def test_disabled(taxi_eats_place_rating, testpoint):
    @testpoint(TESTPOINT_STEP)
    def point(arg):
        pass

    await taxi_eats_place_rating.run_periodic_task(PERIODIC)

    assert point.times_called == 0


@pytest.mark.config(
    EATS_PLACE_RATING_ACTIVE_PLACES_UPDATER={
        'enabled': True,
        'interval_s': DEFAULT_INTERVAL,
        'yt_table': 'qwerty',
        'yt_timeout_ms': DEFAULT_YT_TIMEOUT,
        'yt_batch_size': DEFAULT_YT_BATCH_SIZE,
        'update_ttl_h': DEFAULT_UPDATE_TTL,
        'batch_size': DEFAULT_BATCH_SIZE,
    },
)
@pytest.mark.suspend_periodic_tasks(PERIODIC)
async def test_incorrect_table(taxi_eats_place_rating, testpoint):
    @testpoint(TESTPOINT_STEP)
    def point_step(arg):
        pass

    @testpoint(TESTPOINT_UPDATE_PLACES)
    def point_update_places(arg):
        pass

    await taxi_eats_place_rating.run_periodic_task(PERIODIC)

    assert point_step.times_called == 1
    assert point_update_places.times_called == 0


@pytest.mark.config(EATS_PLACE_RATING_ACTIVE_PLACES_UPDATER=DEFAULT_CONFIG)
@pytest.mark.yt(
    schemas=['yt_places_schema.yaml'], dyn_table_data=['yt_places_empty.yaml'],
)
@pytest.mark.suspend_periodic_tasks(PERIODIC)
async def test_empty(
        taxi_eats_place_rating, testpoint, get_active_places, yt_apply,
):
    @testpoint(TESTPOINT_STEP)
    def point_step(arg):
        pass

    @testpoint(TESTPOINT_UPDATE_PLACES)
    def point_update_places(arg):
        pass

    @testpoint(TESTPOINT_PROCESS_START)
    def point_process_start(arg):
        pass

    await taxi_eats_place_rating.run_periodic_task(PERIODIC)

    assert point_step.times_called == 1
    assert point_update_places.times_called == 1
    assert point_process_start.times_called == 0

    assert get_active_places() == []


@pytest.mark.config(EATS_PLACE_RATING_ACTIVE_PLACES_UPDATER=DEFAULT_CONFIG)
@pytest.mark.yt(
    schemas=['yt_places_schema.yaml'],
    dyn_table_data=['yt_places_simple.yaml'],
)
@pytest.mark.suspend_periodic_tasks(PERIODIC)
async def test_simple(
        taxi_eats_place_rating, testpoint, get_active_places, yt_apply,
):
    @testpoint(TESTPOINT_STEP)
    def point_step(arg):
        pass

    @testpoint(TESTPOINT_UPDATE_PLACES)
    def point_update_places(arg):
        pass

    @testpoint(TESTPOINT_PROCESS_START)
    def point_process_start(arg):
        pass

    @testpoint(TESTPOINT_PROCESS_BATCH_GENERAL)
    def point_process_batch_general(arg):
        pass

    @testpoint(TESTPOINT_PROCESS_BATCH_REMAINDER)
    def point_process_batch_remainder(remainder):
        assert remainder > 0

    await taxi_eats_place_rating.run_periodic_task(PERIODIC)

    assert point_step.times_called == 1
    assert point_update_places.times_called == 1
    assert point_process_start.times_called == 1
    assert point_process_batch_general.times_called == 0
    assert point_process_batch_remainder.times_called == 1

    places = get_active_places()
    assert len(places) == 2

    timezone_info = psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)
    now = dt.datetime.now(timezone_info)

    assert places[0]['place_id'] == 2
    assert (now - places[0]['updated_at']).min < TIMEDELTA

    assert places[1]['place_id'] == 4
    assert (now - places[1]['updated_at']).min < TIMEDELTA


@pytest.mark.config(
    EATS_PLACE_RATING_ACTIVE_PLACES_UPDATER={
        'enabled': True,
        'interval_s': DEFAULT_INTERVAL,
        'yt_table': DEFAULT_YT_TABLE,
        'yt_timeout_ms': DEFAULT_YT_TIMEOUT,
        'yt_batch_size': 3,
        'update_ttl_h': 1,
        'batch_size': 2,
    },
)
@pytest.mark.yt(
    schemas=['yt_places_schema.yaml'],
    dyn_table_data=['yt_places_complex.yaml'],
)
@pytest.mark.pgsql(
    'eats_place_rating',
    files=('pg_eats_place_rating_active_places_complex.sql',),
)
@pytest.mark.suspend_periodic_tasks(PERIODIC)
async def test_complex(
        taxi_eats_place_rating, testpoint, get_active_places, yt_apply,
):
    @testpoint(TESTPOINT_STEP)
    def point_step(arg):
        pass

    @testpoint(TESTPOINT_UPDATE_PLACES)
    def point_update_places(arg):
        pass

    @testpoint(TESTPOINT_PROCESS_START)
    def point_process_start(arg):
        pass

    @testpoint(TESTPOINT_PROCESS_BATCH_GENERAL)
    def point_process_batch_general(arg):
        pass

    @testpoint(TESTPOINT_PROCESS_BATCH_REMAINDER)
    def point_process_batch_remainder(remainder):
        assert remainder > 0

    await taxi_eats_place_rating.run_periodic_task(PERIODIC)

    assert point_step.times_called == 1
    assert point_update_places.times_called == 1
    assert point_process_start.times_called == 2
    assert point_process_batch_general.times_called == 2
    assert point_process_batch_remainder.times_called == 1

    places = get_active_places()
    assert len(places) == 5

    timezone_info = psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)
    now = dt.datetime.now(timezone_info)

    assert places[0]['place_id'] == 1
    assert (now - places[0]['updated_at']).min < TIMEDELTA

    assert places[1]['place_id'] == 3
    assert (now - places[1]['updated_at']).min < TIMEDELTA

    assert places[2]['place_id'] == 4
    assert (now - places[2]['updated_at']).min < TIMEDELTA

    assert places[3]['place_id'] == 5
    assert (now - places[3]['updated_at']).min < TIMEDELTA

    assert places[4]['place_id'] == 6
    assert (now - places[4]['updated_at']).min < TIMEDELTA
