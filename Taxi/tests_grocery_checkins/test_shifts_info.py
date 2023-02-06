import pytest

from tests_grocery_checkins import const

DEPOT_ID = int(const.DEPOT_ID)

NOW = '2021-01-24T17:19:00+00:00'


async def test_shifts_info_basic(taxi_grocery_checkins, grocery_wms, pgsql):

    courier_id = 'courier_id_1'
    started_at = '2021-01-24T17:19:00+00:00'
    closes_at = '2021-01-24T20:19:00+00:00'
    shift_id = 'shift_id_1'
    shift_status = 'in_progress'
    await _setup_shift(
        grocery_wms,
        taxi_grocery_checkins,
        [
            {
                'store_id': '123455657',
                'store_external_id': str(DEPOT_ID),
                'depot_id': str(DEPOT_ID),
                'courier_id': courier_id,
                'shift_id': shift_id,
                'status': shift_status,
                'started_at': started_at,
                'closes_at': closes_at,
                'updated_ts': started_at,
            },
        ],
    )

    response = await taxi_grocery_checkins.post(
        '/internal/checkins/v1/shifts/shifts-info',
        json={'depot_id': str(DEPOT_ID)},
    )

    assert response.status_code == 200
    assert response.json() == {
        'shifts': [
            {
                'closes_at': closes_at,
                'performer_id': courier_id,
                'shift_id': shift_id,
                'shift_status': shift_status,
                'started_at': started_at,
                'shift_type': 'wms',
                'updated_ts': started_at,
            },
        ],
    }


@pytest.mark.now(NOW)
@pytest.mark.experiments3(
    name='grocery_checkins_shifts_info_settings',
    consumers=['grocery-checkins/shifts-info'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={'waiting_shifts_start_period': 3600},
    is_config=True,
)
async def test_shifts_info_waiting(taxi_grocery_checkins, grocery_wms, pgsql):
    shift_id_wms = 'shift_id_2'
    courier_id_1 = 'courier_id_1'
    started_at_1 = '2021-01-24T17:20:00+00:00'
    closes_at = '2021-01-24T20:20:00+00:00'

    await _setup_shift(
        grocery_wms,
        taxi_grocery_checkins,
        [
            {
                'store_id': '123455657',
                'store_external_id': str(DEPOT_ID),
                'depot_id': str(DEPOT_ID),
                'courier_id': courier_id_1,
                'shift_id': shift_id_wms,
                'status': 'waiting',
                'started_at': started_at_1,
                'closes_at': closes_at,
                'updated_ts': started_at_1,
            },
        ],
    )

    response = await taxi_grocery_checkins.post(
        '/internal/checkins/v1/shifts/shifts-info',
        json={'depot_id': str(DEPOT_ID)},
    )

    assert response.status_code == 200
    assert response.json() == {
        'shifts': [
            {
                'closes_at': closes_at,
                'performer_id': courier_id_1,
                'shift_id': shift_id_wms,
                'shift_status': 'waiting',
                'started_at': started_at_1,
                'shift_type': 'wms',
                'updated_ts': started_at_1,
            },
        ],
    }


@pytest.mark.now(NOW)
async def test_shifts_info_closed_shifts(taxi_grocery_checkins, grocery_wms):

    courier_id_1 = 'courier_id_1'
    courier_id_2 = 'courier_id_2'
    started_at_1 = '2021-01-24T17:10:00+00:00'
    started_at_2 = '2021-01-24T17:40:00+00:00'
    closes_at = '2021-01-24T20:19:00+00:00'
    shift_id_eats = 'shift_id_1'
    shift_status = 'closed'
    await _setup_shift(
        grocery_wms,
        taxi_grocery_checkins,
        [
            {
                'store_id': '123455657',
                'store_external_id': DEPOT_ID,
                'courier_id': courier_id_1,
                'shift_id': shift_id_eats,
                'status': shift_status,
                'started_at': started_at_1,
                'closes_at': closes_at,
                'updated_ts': started_at_1,
            },
            {
                'store_id': '123455657',
                'store_external_id': DEPOT_ID,
                'courier_id': courier_id_2,
                'shift_id': shift_id_eats,
                'status': shift_status,
                'started_at': started_at_2,
                'closes_at': closes_at,
                'updated_ts': started_at_2,
            },
        ],
    )

    # closed shifts not includes in cache

    response = await taxi_grocery_checkins.post(
        '/internal/checkins/v1/shifts/shifts-info',
        json={'depot_id': str(DEPOT_ID)},
    )

    assert response.status_code == 200
    assert response.json() == {'shifts': []}


async def _setup_shift(grocery_wms, taxi_grocery_checkins, shifts):
    grocery_wms.set_couriers_shifts(shifts)
    await taxi_grocery_checkins.run_task('distlock/wms-shifts-sync')
    await taxi_grocery_checkins.invalidate_caches()
