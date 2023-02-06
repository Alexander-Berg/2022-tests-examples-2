import json

import pytest

NOW = '2021-01-24T17:19:00+00:00'


def _set_wms_shifts(grocery_wms, shifts):
    grocery_wms.set_couriers_shifts(shifts)


@pytest.mark.config(
    GROCERY_CHECKINS_WMS_SHIFTS_SYNC_SETTINGS={
        'update_freq': 100,
        'stop_elements_quantity': 100,
        'stop_last_update': 1,
        'is_cache_enabled': True,
    },
)
async def test_performer_starts_wms_shift(
        taxi_grocery_checkins, testpoint, grocery_wms, mocked_time,
):
    courier_id = 'courier_id_1'
    store_id = '12345567'
    depot_id = 'depot_id_1'
    started_at = '2021-01-24T17:19:00+00:00'

    @testpoint('logbroker_publish')
    def notify_performer_shift_started(data):
        pass

    _set_wms_shifts(
        grocery_wms,
        [
            {
                'store_id': store_id,
                'store_external_id': depot_id,
                'courier_id': courier_id,
                'shift_id': 'shift_id_1',
                'status': 'in_progress',
                'started_at': started_at,
                'updated_ts': started_at,
            },
        ],
    )

    await taxi_grocery_checkins.enable_testpoints()
    mocked_time.sleep(200)

    await taxi_grocery_checkins.run_task('distlock/wms-shifts-sync')
    await taxi_grocery_checkins.invalidate_caches()

    data = (await notify_performer_shift_started.wait_call())['data']
    name, data = data['name'], json.loads(data['data'])
    assert name == 'grocery-performer-shift-update'
    assert data == {
        'performer_id': courier_id,
        'shift_id': 'shift_id_1',
        'depot_id': depot_id,
        'shift_type': 'wms',
        'timestamp': started_at,
        'status': 'open',
    }


@pytest.mark.config(
    GROCERY_CHECKINS_WMS_SHIFTS_SYNC_SETTINGS={
        'update_freq': 100,
        'stop_elements_quantity': 100,
        'stop_last_update': 1,
        'is_cache_enabled': True,
    },
)
async def test_performer_paused_unpaused_wms_shift(
        taxi_grocery_checkins, testpoint, grocery_wms, mocked_time,
):
    courier_id = 'courier_id_1'
    store_id = '12345567'
    depot_id = 'depot_id_1'
    started_at = '2021-01-24T17:19:00+00:00'
    paused_at = '2021-01-24T17:19:00+00:00'
    unpauses_at = '2021-01-24T17:19:00+00:00'

    @testpoint('logbroker_publish')
    def notify_performer_shift_paused(data):
        pass

    _set_wms_shifts(
        grocery_wms,
        [
            {
                'store_id': store_id,
                'store_external_id': depot_id,
                'courier_id': courier_id,
                'shift_id': 'wms_shift',
                'status': 'paused',
                'started_at': started_at,
                'updated_ts': started_at,
                'paused_at': paused_at,
                'unpauses_at': unpauses_at,
            },
        ],
    )

    await taxi_grocery_checkins.enable_testpoints()
    mocked_time.sleep(200)

    await taxi_grocery_checkins.run_task('distlock/wms-shifts-sync')
    await taxi_grocery_checkins.invalidate_caches()

    data = (await notify_performer_shift_paused.wait_call())['data']
    name, data = data['name'], json.loads(data['data'])
    assert name == 'grocery-performer-shift-update'
    assert data == {
        'performer_id': courier_id,
        'shift_id': 'wms_shift',
        'depot_id': depot_id,
        'shift_type': 'wms',
        'timestamp': started_at,
        'status': 'open',
    }

    data = (await notify_performer_shift_paused.wait_call())['data']
    name, data = data['name'], json.loads(data['data'])
    assert name == 'grocery-performer-shift-update'
    assert data == {
        'performer_id': courier_id,
        'shift_id': 'wms_shift',
        'depot_id': depot_id,
        'status': 'pause',
        'shift_type': 'wms',
        'timestamp': started_at,
    }

    _set_wms_shifts(
        grocery_wms,
        [
            {
                'store_id': store_id,
                'store_external_id': depot_id,
                'courier_id': courier_id,
                'shift_id': 'wms_shift',
                'status': 'in_progress',
                'started_at': started_at,
                'updated_ts': started_at,
                'paused_at': paused_at,
                'unpauses_at': unpauses_at,
            },
        ],
    )

    mocked_time.sleep(200)
    await taxi_grocery_checkins.run_task('distlock/wms-shifts-sync')
    await taxi_grocery_checkins.invalidate_caches()

    data = (await notify_performer_shift_paused.wait_call())['data']
    name, data = data['name'], json.loads(data['data'])
    assert name == 'grocery-performer-shift-update'
    assert data == {
        'performer_id': courier_id,
        'shift_id': 'wms_shift',
        'depot_id': depot_id,
        'shift_type': 'wms',
        'timestamp': unpauses_at,
        'status': 'unpause',
    }


@pytest.mark.config(
    GROCERY_CHECKINS_WMS_SHIFTS_SYNC_SETTINGS={
        'update_freq': 100,
        'stop_elements_quantity': 100,
        'stop_last_update': 1,
        'is_cache_enabled': True,
    },
)
async def test_performer_closed_wms_shift(
        taxi_grocery_checkins, testpoint, grocery_wms, mocked_time,
):
    courier_id = 'courier_id_1'
    store_id = '12345567'
    depot_id = 'depot_id_1'
    started_at = '2021-01-24T17:19:00+00:00'
    closes_at = '2021-01-24T17:19:05+00:00'

    @testpoint('logbroker_publish')
    def notify_performer_shift(data):
        pass

    _set_wms_shifts(
        grocery_wms,
        [
            {
                'store_id': store_id,
                'store_external_id': depot_id,
                'courier_id': courier_id,
                'shift_id': 'wms_shift',
                'status': 'in_progress',
                'started_at': started_at,
                'updated_ts': started_at,
            },
        ],
    )

    await taxi_grocery_checkins.enable_testpoints()
    mocked_time.sleep(200)
    await taxi_grocery_checkins.run_task('distlock/wms-shifts-sync')
    await taxi_grocery_checkins.invalidate_caches()

    data = (await notify_performer_shift.wait_call())['data']
    name, data = data['name'], json.loads(data['data'])
    assert name == 'grocery-performer-shift-update'
    assert data == {
        'performer_id': courier_id,
        'shift_id': 'wms_shift',
        'depot_id': depot_id,
        'shift_type': 'wms',
        'timestamp': started_at,
        'status': 'open',
    }

    await taxi_grocery_checkins.invalidate_caches()

    _set_wms_shifts(
        grocery_wms,
        [
            {
                'store_id': store_id,
                'store_external_id': depot_id,
                'courier_id': courier_id,
                'shift_id': 'wms_shift',
                'status': 'closed',
                'started_at': started_at,
                'updated_ts': started_at,
                'closes_at': closes_at,
            },
        ],
    )

    mocked_time.sleep(200)
    await taxi_grocery_checkins.run_task('distlock/wms-shifts-sync')
    await taxi_grocery_checkins.invalidate_caches()

    data = (await notify_performer_shift.wait_call())['data']
    name, data = data['name'], json.loads(data['data'])
    assert name == 'grocery-performer-shift-update'
    assert data == {
        'performer_id': courier_id,
        'shift_id': 'wms_shift',
        'depot_id': depot_id,
        'shift_type': 'wms',
        'timestamp': closes_at,
        'status': 'close',
    }


@pytest.mark.config(
    GROCERY_CHECKINS_WMS_SHIFTS_SYNC_SETTINGS={
        'update_freq': 100,
        'stop_elements_quantity': 100,
        'stop_last_update': 1,
        'is_cache_enabled': True,
    },
)
async def test_closed_event_when_change_shift_id_in_wms_cache(
        taxi_grocery_checkins, testpoint, grocery_wms, mocked_time,
):
    courier_id = 'courier_id_1'
    store_id = '12345567'
    depot_id = 'depot_id_1'
    started_at = '2021-01-24T17:19:00+00:00'

    @testpoint('logbroker_publish')
    def notify_performer_shift(data):
        pass

    _set_wms_shifts(
        grocery_wms,
        [
            {
                'store_id': store_id,
                'store_external_id': depot_id,
                'courier_id': courier_id,
                'shift_id': 'wms_shift_1',
                'status': 'in_progress',
                'started_at': started_at,
                'updated_ts': started_at,
            },
        ],
    )

    await taxi_grocery_checkins.enable_testpoints()
    mocked_time.sleep(200)
    await taxi_grocery_checkins.run_task('distlock/wms-shifts-sync')
    await taxi_grocery_checkins.invalidate_caches()

    data = (await notify_performer_shift.wait_call())['data']
    name, data = data['name'], json.loads(data['data'])
    assert name == 'grocery-performer-shift-update'
    assert data == {
        'performer_id': courier_id,
        'shift_id': 'wms_shift_1',
        'depot_id': depot_id,
        'timestamp': started_at,
        'shift_type': 'wms',
        'status': 'open',
    }

    await taxi_grocery_checkins.invalidate_caches()

    _set_wms_shifts(
        grocery_wms,
        [
            {
                'store_id': store_id,
                'store_external_id': depot_id,
                'courier_id': courier_id,
                'shift_id': 'wms_shift_2',
                'status': 'in_progress',
                'started_at': started_at,
                'updated_ts': started_at,
            },
            {
                'store_id': store_id,
                'store_external_id': depot_id,
                'courier_id': courier_id,
                'shift_id': 'wms_shift_1',
                'status': 'closed',
                'closed_at': started_at,
                'updated_ts': started_at,
            },
        ],
    )

    mocked_time.sleep(200)
    await taxi_grocery_checkins.run_task('distlock/wms-shifts-sync')
    await taxi_grocery_checkins.invalidate_caches()

    data = (await notify_performer_shift.wait_call())['data']
    name, data = data['name'], json.loads(data['data'])
    assert name == 'grocery-performer-shift-update'
    assert data == {
        'performer_id': courier_id,
        'shift_id': 'wms_shift_1',
        'depot_id': depot_id,
        'shift_type': 'wms',
        'status': 'close',
        'timestamp': started_at,
    }

    data = (await notify_performer_shift.wait_call())['data']
    name, data = data['name'], json.loads(data['data'])
    assert name == 'grocery-performer-shift-update'
    assert data == {
        'performer_id': courier_id,
        'shift_id': 'wms_shift_2',
        'depot_id': depot_id,
        'shift_type': 'wms',
        'status': 'open',
        'timestamp': started_at,
    }


@pytest.mark.config(
    GROCERY_CHECKINS_WMS_SHIFTS_SYNC_SETTINGS={
        'update_freq': 100,
        'stop_elements_quantity': 100,
        'stop_last_update': 1,
        'is_cache_enabled': True,
    },
)
async def test_performer_closed_wms_shift_after_open_new(
        taxi_grocery_checkins, testpoint, grocery_wms, mocked_time,
):
    courier_id = 'courier_id_1'
    store_id = '12345567'
    depot_id = 'depot_id_1'
    started_at = '2021-01-24T17:19:00+00:00'

    @testpoint('logbroker_publish')
    def notify_performer_shift(data):
        pass

    _set_wms_shifts(
        grocery_wms,
        [
            {
                'store_id': store_id,
                'store_external_id': depot_id,
                'courier_id': courier_id,
                'shift_id': 'wms_shift_1',
                'status': 'in_progress',
                'started_at': started_at,
                'updated_ts': started_at,
            },
        ],
    )

    await taxi_grocery_checkins.enable_testpoints()
    mocked_time.sleep(200)
    await taxi_grocery_checkins.run_task('distlock/wms-shifts-sync')
    await taxi_grocery_checkins.invalidate_caches()

    data = (await notify_performer_shift.wait_call())['data']
    name, data = data['name'], json.loads(data['data'])
    assert name == 'grocery-performer-shift-update'
    assert data == {
        'performer_id': courier_id,
        'shift_id': 'wms_shift_1',
        'depot_id': depot_id,
        'shift_type': 'wms',
        'timestamp': started_at,
        'status': 'open',
    }

    await taxi_grocery_checkins.invalidate_caches()

    _set_wms_shifts(
        grocery_wms,
        [
            {
                'store_id': store_id,
                'store_external_id': depot_id,
                'courier_id': courier_id,
                'shift_id': 'wms_shift_2',
                'status': 'in_progress',
                'started_at': started_at,
                'updated_ts': started_at,
            },
        ],
    )

    mocked_time.sleep(200)
    await taxi_grocery_checkins.run_task('distlock/wms-shifts-sync')
    await taxi_grocery_checkins.invalidate_caches()

    data = (await notify_performer_shift.wait_call())['data']
    name, data = data['name'], json.loads(data['data'])
    assert name == 'grocery-performer-shift-update'
    assert data == {
        'performer_id': courier_id,
        'shift_id': 'wms_shift_1',
        'depot_id': depot_id,
        'shift_type': 'wms',
        'status': 'close',
        'timestamp': started_at,
    }

    data = (await notify_performer_shift.wait_call())['data']
    name, data = data['name'], json.loads(data['data'])
    assert name == 'grocery-performer-shift-update'
    assert data == {
        'performer_id': courier_id,
        'shift_id': 'wms_shift_2',
        'depot_id': depot_id,
        'shift_type': 'wms',
        'timestamp': started_at,
        'status': 'open',
    }
