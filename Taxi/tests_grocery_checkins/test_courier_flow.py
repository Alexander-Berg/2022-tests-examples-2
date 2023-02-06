import dateutil.parser

PARK_ID = 'parkid'
TAXI_PERFORMER_ID = 'courierid'
WMS_COURIER_ID = f'{PARK_ID}_{TAXI_PERFORMER_ID}'
DEPOT_ID = 'depot_id_1'

STARTED_AT = '2021-01-24T16:55:00+01:00'
STARTED_AT_DT = dateutil.parser.isoparse(STARTED_AT)
CLOSES_AT = '2021-01-24T20:55:00+01:00'
FAR_FAR_AWAY = '2099-01-24T20:55:00+01:00'
FIRST_CHECKIN = '2021-01-24T17:18:00+01:00'
FIRST_CHECKIN_DT = dateutil.parser.isoparse(FIRST_CHECKIN)
SECOND_CHECKIN = '2021-01-24T17:25:00+01:00'
SECOND_CHECKIN_DT = dateutil.parser.isoparse(SECOND_CHECKIN)

SHIFTS = [
    {
        'store_id': '12345567',
        'store_external_id': DEPOT_ID,
        'courier_id': WMS_COURIER_ID,
        'shift_id': 'shift_id_1',
        'status': 'in_progress',
        'started_at': STARTED_AT,
        'updated_ts': STARTED_AT,
        'closes_at': FAR_FAR_AWAY,
    },
]


# 1. We dont have an active shift for courier
# 2. We get an active shift for courier
# 3. We checkin courier and ensure the queue is updated
# 4. We checkin courier again and ensure the queue is updated
# 5. We dont have an active shift for courier anymore
async def test_courier_flow(
        taxi_grocery_checkins, grocery_wms, mocked_time, stq_runner,
):
    assert STARTED_AT_DT < FIRST_CHECKIN_DT < SECOND_CHECKIN_DT

    # 1. We dont have an active shift for courier
    couriers = await _retrieve_queue_info(taxi_grocery_checkins)
    assert not couriers

    # 2. We get an active shift for courier
    await _setup_shift(grocery_wms, taxi_grocery_checkins, SHIFTS)

    couriers = await _retrieve_queue_info(taxi_grocery_checkins)
    assert len(couriers) == 1
    _assert_courier(couriers[0], STARTED_AT_DT)

    # 3. We checkin courier and ensure the queue is updated
    mocked_time.set(FIRST_CHECKIN_DT)
    await _checkin_courier(stq_runner)
    couriers = await _retrieve_queue_info(taxi_grocery_checkins)
    assert len(couriers) == 1
    _assert_courier(couriers[0], FIRST_CHECKIN_DT)

    # 4. We checkin courier again and ensure the queue is updated
    mocked_time.set(SECOND_CHECKIN_DT)
    await _checkin_courier(stq_runner)
    couriers = await _retrieve_queue_info(taxi_grocery_checkins)
    assert len(couriers) == 1
    _assert_courier(couriers[0], SECOND_CHECKIN_DT)

    # 5. We dont have an active shift for courier anymore
    new_shift = SHIFTS[:]
    # new_shift[0]['closed_at'] = CLOSES_AT
    new_shift[0]['status'] = 'closed'
    await _setup_shift(grocery_wms, taxi_grocery_checkins, new_shift)
    couriers = await _retrieve_queue_info(taxi_grocery_checkins)
    assert not couriers


async def _retrieve_queue_info(taxi_grocery_checkins):
    response = await taxi_grocery_checkins.post(
        '/internal/checkins/v2/queue-info', json={'depot_id': DEPOT_ID},
    )
    assert response.status_code == 200

    return response.json()['couriers']


async def _setup_shift(grocery_wms, taxi_grocery_checkins, shifts):
    grocery_wms.set_couriers_shifts(shifts)
    await taxi_grocery_checkins.run_task('distlock/wms-shifts-sync')
    await taxi_grocery_checkins.invalidate_caches()


def _assert_courier(courier_json, checkin_timestamp):
    assert courier_json['courier_id'] == WMS_COURIER_ID
    assert (
        dateutil.parser.isoparse(courier_json['checkin_timestamp'])
        == checkin_timestamp
    )


async def _checkin_courier(stq_runner):
    await stq_runner.grocery_couriers_checkins.call(
        task_id='task_id',
        kwargs={'park_id': PARK_ID, 'performer_id': TAXI_PERFORMER_ID},
    )
