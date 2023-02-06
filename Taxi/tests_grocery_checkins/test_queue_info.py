import datetime as dt

import dateutil.parser
import pytest


@pytest.mark.parametrize('exclude_by_shift_id', [True, False])
async def test_queue_info_basic(
        taxi_grocery_checkins, grocery_wms, taxi_config, exclude_by_shift_id,
):
    taxi_config.set(
        GROCERY_CHECKINS_QUEUE_EXCLUDE_BY_SHIFT_ID=exclude_by_shift_id,
    )

    courier_id = 'courier_id_1'
    depot_id = 'depot_id_1'
    started_at = '2021-01-24T17:19:00+00:00'
    closes_at = '2099-01-24T20:55:00+01:00'

    await _setup_shift(
        grocery_wms,
        taxi_grocery_checkins,
        [
            {
                'store_id': '12345567',
                'store_external_id': depot_id,
                'courier_id': courier_id,
                'shift_id': 'shift_id_1',
                'status': 'in_progress',
                'started_at': started_at,
                'closes_at': closes_at,
                'updated_ts': started_at,
            },
        ],
    )

    response = await taxi_grocery_checkins.post(
        '/internal/checkins/v2/queue-info', json={'depot_id': depot_id},
    )

    assert response.status_code == 200
    assert response.json() == {
        'couriers': [
            {'courier_id': courier_id, 'checkin_timestamp': started_at},
        ],
    }


@pytest.mark.parametrize('exclude_by_shift_id', [True, False])
async def test_queue_info_max_checkin_in_db(
        taxi_grocery_checkins,
        grocery_wms,
        couriers_db,
        taxi_config,
        exclude_by_shift_id,
):
    taxi_config.set(
        GROCERY_CHECKINS_QUEUE_EXCLUDE_BY_SHIFT_ID=exclude_by_shift_id,
    )

    courier_id = 'courier_id_1'
    depot_id = 'depot_id_1'
    started_at = '2021-01-24T17:19:00+00:00'
    closes_at = '2099-01-24T20:19:00+00:00'
    courier_checkin = '2021-01-24T17:20:00+00:00'
    assert dateutil.parser.isoparse(
        courier_checkin,
    ) > dateutil.parser.isoparse(started_at)

    await _setup_shift(
        grocery_wms,
        taxi_grocery_checkins,
        [
            {
                'store_id': '12345567',
                'store_external_id': depot_id,
                'courier_id': courier_id,
                'shift_id': 'shift_id_1',
                'status': 'in_progress',
                'started_at': started_at,
                'closes_at': closes_at,
                'updated_ts': started_at,
            },
        ],
    )

    couriers_db.add_entry(courier_id, None, courier_checkin, False, depot_id)

    response = await taxi_grocery_checkins.post(
        '/internal/checkins/v2/queue-info', json={'depot_id': depot_id},
    )

    assert response.status_code == 200
    assert response.json() == {
        'couriers': [
            {'courier_id': courier_id, 'checkin_timestamp': courier_checkin},
        ],
    }


@pytest.mark.parametrize('exclude_by_shift_id', [True, False])
async def test_queue_info_max_checkin_in_shift(
        taxi_grocery_checkins,
        grocery_wms,
        couriers_db,
        taxi_config,
        exclude_by_shift_id,
):
    taxi_config.set(
        GROCERY_CHECKINS_QUEUE_EXCLUDE_BY_SHIFT_ID=exclude_by_shift_id,
    )

    courier_id = 'courier_id_1'
    depot_id = 'depot_id_1'
    started_at = '2021-01-24T17:19:00+00:00'
    closes_at = '2099-01-24T20:19:00+00:00'
    courier_checkin = '2021-01-24T17:18:00+00:00'
    assert dateutil.parser.isoparse(started_at) > dateutil.parser.isoparse(
        courier_checkin,
    )

    await _setup_shift(
        grocery_wms,
        taxi_grocery_checkins,
        [
            {
                'store_id': '12345567',
                'store_external_id': depot_id,
                'courier_id': courier_id,
                'shift_id': 'shift_id_1',
                'status': 'in_progress',
                'started_at': started_at,
                'closes_at': closes_at,
                'updated_ts': started_at,
            },
        ],
    )

    couriers_db.add_entry(courier_id, None, courier_checkin, False, depot_id)

    response = await taxi_grocery_checkins.post(
        '/internal/checkins/v2/queue-info', json={'depot_id': depot_id},
    )

    assert response.status_code == 200
    assert response.json() == {
        'couriers': [
            {'courier_id': courier_id, 'checkin_timestamp': started_at},
        ],
    }


@pytest.mark.parametrize('exclude_by_shift_id', [True, False])
@pytest.mark.parametrize('shift_status', ['closed', 'paused'])
async def test_queue_info_skips_not_in_progress(
        taxi_grocery_checkins,
        grocery_wms,
        shift_status,
        taxi_config,
        exclude_by_shift_id,
):
    taxi_config.set(
        GROCERY_CHECKINS_QUEUE_EXCLUDE_BY_SHIFT_ID=exclude_by_shift_id,
    )

    courier_id = 'courier_id_1'
    depot_id = 'depot_id_1'
    started_at = '2021-01-24T17:19:00+00:00'
    closes_at = '2099-01-24T20:19:00+00:00'

    await _setup_shift(
        grocery_wms,
        taxi_grocery_checkins,
        [
            {
                'store_id': '12345567',
                'store_external_id': depot_id,
                'courier_id': courier_id,
                'shift_id': 'shift_id_1',
                'status': 'in_progress',
                'started_at': started_at,
                'closes_at': closes_at,
                'updated_ts': started_at,
            },
            {
                'store_id': '12345567',
                'store_external_id': depot_id,
                'courier_id': 'should_be_skipped',
                'shift_id': 'shift_id_2',
                'status': shift_status,
                'started_at': started_at,
                'closes_at': closes_at,
                'updated_ts': started_at,
            },
        ],
    )

    response = await taxi_grocery_checkins.post(
        '/internal/checkins/v2/queue-info', json={'depot_id': depot_id},
    )
    assert response.status_code == 200
    assert response.json() == {
        'couriers': [
            {'courier_id': courier_id, 'checkin_timestamp': started_at},
        ],
    }


@pytest.mark.parametrize('exclude_by_shift_id', [True, False])
async def test_queue_info_skips_no_started_at(
        taxi_grocery_checkins, grocery_wms, taxi_config, exclude_by_shift_id,
):
    taxi_config.set(
        GROCERY_CHECKINS_QUEUE_EXCLUDE_BY_SHIFT_ID=exclude_by_shift_id,
    )

    courier_id = 'courier_id_1'
    depot_id = 'depot_id_1'
    started_at = '2021-01-24T17:19:00+00:00'
    closes_at = '2099-01-24T20:19:00+00:00'
    await _setup_shift(
        grocery_wms,
        taxi_grocery_checkins,
        [
            {
                'store_id': '12345567',
                'store_external_id': depot_id,
                'courier_id': courier_id,
                'shift_id': 'shift_id_2',
                'status': 'in_progress',
                'started_at': started_at,
                'closes_at': closes_at,
                'updated_ts': started_at,
            },
        ],
    )

    response = await taxi_grocery_checkins.post(
        '/internal/checkins/v2/queue-info', json={'depot_id': depot_id},
    )
    assert response.status_code == 200
    assert response.json() == {
        'couriers': [
            {'courier_id': courier_id, 'checkin_timestamp': started_at},
        ],
    }


async def test_queue_info_no_depot_id(taxi_grocery_checkins):
    response = await taxi_grocery_checkins.post(
        '/internal/checkins/v2/queue-info', json={'depot_id': 'depot_id_2'},
    )
    assert response.status_code == 200
    assert response.json() == {'couriers': []}


@pytest.mark.parametrize('same_shift_id_at_db', [True, False])
@pytest.mark.parametrize('exclude_by_shift_id', [True, False])
async def test_queue_info_excluded_from_queue(
        taxi_grocery_checkins,
        grocery_wms,
        couriers_db,
        taxi_config,
        exclude_by_shift_id,
        same_shift_id_at_db,
):
    taxi_config.set(
        GROCERY_CHECKINS_QUEUE_EXCLUDE_BY_SHIFT_ID=exclude_by_shift_id,
    )

    courier_id = 'courier_id_1'
    depot_id = 'depot_id_1'
    started_at = '2021-01-24T17:19:00+00:00'
    shift_id = 'shift_id_1'

    couriers_db.add_entry(
        courier_id,
        None,
        started_at,
        True,
        depot_id,
        shift_id if same_shift_id_at_db else (shift_id + '123'),
    )

    await _setup_shift(
        grocery_wms,
        taxi_grocery_checkins,
        [
            {
                'store_id': '12345567',
                'store_external_id': depot_id,
                'courier_id': courier_id,
                'shift_id': shift_id,
                'status': 'in_progress',
                'started_at': started_at,
                'closes_at': '2099-07-28T09:07:12Z',
                'updated_ts': '2020-07-28T09:07:12Z',
            },
        ],
    )

    response = await taxi_grocery_checkins.post(
        '/internal/checkins/v2/queue-info', json={'depot_id': depot_id},
    )

    assert response.status_code == 200
    if exclude_by_shift_id and not same_shift_id_at_db:
        assert response.json() == {
            'couriers': [
                {'courier_id': courier_id, 'checkin_timestamp': started_at},
            ],
        }
    else:
        assert response.json() == {'couriers': []}


async def test_shift_pause_view_update_db(taxi_grocery_checkins, couriers_db):
    courier_id = 'courier_id_1'
    depot_id = 'depot_id_1'
    started_at = '2021-01-24T17:19:00+00:00'
    paused_at = '2021-01-24T17:24:00+00:00'
    shift_id = 'shift_id_1'

    couriers_db.add_entry(
        courier_id, None, started_at, False, depot_id, None, None, None,
    )

    response = await taxi_grocery_checkins.post(
        '/internal/checkins/v1/shifts/pause',
        json={
            'performer_id': courier_id,
            'shift_id': shift_id,
            'paused_at': paused_at,
        },
    )

    assert response.status_code == 200

    assert len(couriers_db.load_all_couriers()) == 1
    courier = couriers_db.load_all_couriers()[0]
    assert courier.last_pause_timestamp == dt.datetime.fromisoformat(paused_at)
    assert courier.paused_shift_id == shift_id


@pytest.mark.parametrize('is_excluded_by_pause', [True, False])
@pytest.mark.parametrize(
    'paused_at, updated_at, is_excluded',
    [
        ('2021-01-24T17:25:00+00:00', '2021-01-24T17:24:00+00:00', True),
        ('2021-01-24T17:25:00+00:00', '2021-01-24T17:26:00+00:00', False),
    ],
)
async def test_queue_info_excluded_from_queue_by_pause(
        taxi_grocery_checkins,
        grocery_wms,
        couriers_db,
        taxi_config,
        is_excluded_by_pause,
        paused_at,
        updated_at,
        is_excluded,
):
    taxi_config.set(
        GROCERY_CHECKINS_QUEUE_EXCLUDE_BY_PAUSE=is_excluded_by_pause,
    )

    courier_id = 'courier_id_1'
    depot_id = 'depot_id_1'
    started_at = '2021-01-24T17:19:00+00:00'
    shift_id = 'shift_id_1'

    couriers_db.add_entry(
        courier_id,
        None,
        started_at,
        False,
        depot_id,
        None,
        paused_at,
        shift_id,
    )

    await _setup_shift(
        grocery_wms,
        taxi_grocery_checkins,
        [
            {
                'store_id': '12345567',
                'store_external_id': depot_id,
                'courier_id': courier_id,
                'shift_id': shift_id,
                'status': 'in_progress',
                'started_at': started_at,
                'closes_at': '2099-01-24T18:00:00+00:00',
                'updated_ts': updated_at,
            },
        ],
    )

    response = await taxi_grocery_checkins.post(
        '/internal/checkins/v2/queue-info', json={'depot_id': depot_id},
    )

    assert response.status_code == 200
    if is_excluded_by_pause:
        assert len(response.json()['couriers']) == (0 if is_excluded else 1)
    else:
        assert len(response.json()['couriers']) == 1


async def _setup_shift(grocery_wms, taxi_grocery_checkins, shifts):
    grocery_wms.set_couriers_shifts(shifts)
    await taxi_grocery_checkins.run_task('distlock/wms-shifts-sync')
    await taxi_grocery_checkins.invalidate_caches()
