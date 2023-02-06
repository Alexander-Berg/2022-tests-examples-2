import datetime

import psycopg2
import pytest


@pytest.mark.suspend_periodic_tasks('matching-periodic')
@pytest.mark.suspend_periodic_tasks('wms-shifts-sync-periodic')
async def test_import_wms_shifts(
        taxi_grocery_performer_mentorship, grocery_wms, db,
):
    grocery_wms.set_couriers_shifts(None)
    await taxi_grocery_performer_mentorship.run_periodic_task(
        'wms-shifts-sync-periodic',
    )
    rows = db.select(
        [
            'performer_id',
            'shift_id',
            'depot_id',
            'legacy_depot_id',
            'started_at',
            'closes_at',
            'status',
        ],
        'shifts',
    )

    def find(performer_id):
        for row in rows:
            if row['performer_id'] == performer_id:
                return row
        return None

    def find_by_shift_id(shift_id):
        for row in rows:
            if row['shift_id'] == shift_id:
                return row
        return None

    assert find('courier_id_1') == {
        'performer_id': 'courier_id_1',
        'shift_id': '12345',
        'depot_id': '12345567',
        'legacy_depot_id': 'depot_id_1',
        'started_at': datetime.datetime(
            2021,
            1,
            24,
            20,
            19,
            tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
        ),
        'closes_at': datetime.datetime(
            2021,
            1,
            24,
            21,
            19,
            tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
        ),
        'status': 'in_progress',
    }
    assert find('courier_id_2') == {
        'performer_id': 'courier_id_2',
        'shift_id': '54321',
        'depot_id': '12345567',
        'legacy_depot_id': 'depot_id_2',
        'started_at': datetime.datetime(
            2021,
            1,
            24,
            20,
            19,
            tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
        ),
        'closes_at': datetime.datetime(
            2021,
            1,
            24,
            21,
            19,
            tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
        ),
        'status': 'closed',
    }
    assert find('courier_id_3') == {
        'performer_id': 'courier_id_3',
        'shift_id': '23545',
        'depot_id': '12345567',
        'legacy_depot_id': 'depot_id_3',
        'started_at': datetime.datetime(
            2021,
            1,
            24,
            20,
            19,
            tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
        ),
        'closes_at': datetime.datetime(
            2021,
            1,
            24,
            21,
            19,
            tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
        ),
        'status': 'waiting',
    }
    assert find('courier_id_4') == {
        'performer_id': 'courier_id_4',
        'shift_id': '25234',
        'depot_id': '12345567',
        'legacy_depot_id': 'depot_id_4',
        'started_at': datetime.datetime(
            2021,
            1,
            24,
            20,
            19,
            tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
        ),
        'closes_at': datetime.datetime(
            2021,
            1,
            24,
            21,
            19,
            tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
        ),
        'status': 'paused',
    }
    assert find_by_shift_id('54325') == {
        'performer_id': None,
        'shift_id': '54325',
        'depot_id': '12345567',
        'legacy_depot_id': 'depot_id_2',
        'started_at': datetime.datetime(
            2021,
            1,
            24,
            20,
            19,
            tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
        ),
        'closes_at': datetime.datetime(
            2021,
            1,
            24,
            21,
            19,
            tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
        ),
        'status': 'request',
    }
    assert find_by_shift_id('54329') == {
        'performer_id': 'courier_id_0',
        'shift_id': '54329',
        'depot_id': '12345567',
        'legacy_depot_id': 'depot_id_2',
        'started_at': None,
        'closes_at': None,
        'status': 'closed',
    }
