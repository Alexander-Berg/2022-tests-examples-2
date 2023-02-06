import dateutil.parser
import pytest

PREVIOUS_CHECKIN = '2021-01-24T17:18:00+01:00'
PREVIOUS_CHECKIN_DT = dateutil.parser.isoparse(PREVIOUS_CHECKIN)
NOW = '2021-01-24T17:19:00+01:00'
NOW_DT = dateutil.parser.isoparse(NOW)

PARK_ID = 'parkid'
TAXI_PERFORMER_ID = 'courierid'

WMS_COURIER_ID = f'{PARK_ID}_{TAXI_PERFORMER_ID}'


@pytest.mark.now(NOW)
async def test_courier_checkin_creates_entry(
        taxi_grocery_checkins, couriers_db, grocery_wms, stq_runner,
):
    _setup_shift(grocery_wms)

    await taxi_grocery_checkins.run_task('distlock/wms-shifts-sync')
    await taxi_grocery_checkins.invalidate_caches()

    await _checkin_courier(stq_runner)

    db_entries = couriers_db.load_all_couriers()
    assert len(db_entries) == 1
    _assert_entry(db_entries[0], WMS_COURIER_ID, NOW_DT)


@pytest.mark.now(NOW)
async def test_courier_checkin_updates_entry(
        taxi_grocery_checkins, couriers_db, grocery_wms, stq_runner,
):
    assert PREVIOUS_CHECKIN_DT < NOW_DT

    _setup_shift(grocery_wms)

    await taxi_grocery_checkins.run_task('distlock/wms-shifts-sync')
    await taxi_grocery_checkins.invalidate_caches()

    couriers_db.add_entry(WMS_COURIER_ID, None, PREVIOUS_CHECKIN, True)

    db_entries = couriers_db.load_all_couriers()
    assert len(db_entries) == 1
    _assert_entry(db_entries[0], WMS_COURIER_ID, PREVIOUS_CHECKIN_DT, True)

    await _checkin_courier(stq_runner)

    db_entries = couriers_db.load_all_couriers()
    assert len(db_entries) == 1
    _assert_entry(db_entries[0], WMS_COURIER_ID, NOW_DT, False)


def _assert_entry(
        db_entry, courier_id, checkin_timestamp, excluded_from_queue=False,
):
    assert db_entry.courier_id == courier_id
    assert db_entry.checkin_timestamp == checkin_timestamp
    assert db_entry.excluded_from_queue == excluded_from_queue


def _setup_shift(grocery_wms):
    grocery_wms.set_couriers_shifts(
        [
            {
                'store_id': '12345567',
                'store_external_id': 'depot_id_1',
                'courier_id': WMS_COURIER_ID,
                'shift_id': 'shift_id_1',
                'status': 'in_progress',
                'started_at': '2020-07-28T08:47:00Z',
                'updated_ts': '2020-07-28T09:07:12Z',
            },
        ],
    )


async def _checkin_courier(stq_runner):
    await stq_runner.grocery_couriers_checkins.call(
        task_id='task_id',
        kwargs={'park_id': PARK_ID, 'performer_id': TAXI_PERFORMER_ID},
    )
