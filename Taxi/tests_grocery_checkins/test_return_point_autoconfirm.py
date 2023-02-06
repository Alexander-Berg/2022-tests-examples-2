import pytest

from tests_grocery_checkins import const

PARK_ID = 'parkid'
DRIVER_ID = 'courierid'
WMS_COURIER_ID = f'{PARK_ID}_{DRIVER_ID}'
DEPOT_ID = '123456'

REGION_ID = const.REGION_ID

PREVIOUS_CHECKIN = '2021-01-24T17:18:00+00:00'
CLOSES_AT = '2021-01-24T20:18:00+00:00'
HOUR_BEFORE_CLOSE = '2021-01-24T19:20:00+00:00'
FOUR_MINUTES_BEFORE_CLOSE = '2021-01-24T20:14:00+00:00'


@pytest.mark.now(FOUR_MINUTES_BEFORE_CLOSE)
@pytest.mark.experiments3(
    name='grocery_checkins_return_autoconfirm_settings',
    consumers=['grocery-checkins/return-autoconfirm'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={
        'enable_autoconfirm': True,
        'allowed_autoconfirm_period': 300,
        'allowed_shifts_gap': 500,
    },
    is_config=True,
)
async def test_return_point_autoconfirm_basic(
        taxi_grocery_checkins,
        couriers_db,
        cargo_dispatch,
        stq_runner,
        grocery_wms,
        pgsql,
):
    """
    db = pgsql['grocery_checkins']
    cursor = db.cursor()
    cursor.execute(
        \"""INSERT INTO grocery_checkins.shifts
        (
        courier_id,
        shift_id,
        depot_id,
        status,
        started_at,
        updated_ts,
        closes_at
        )
        VALUES ('parkid_courierid', 'shift_id', '123456',
        'in_progress', '2021-01-24T08:47:00Z',
        '2021-01-24T09:07:12Z', '2021-01-24T20:18:00Z');
        \""",
    )
    cursor.close()
    """

    await _setup_shift(
        grocery_wms,
        taxi_grocery_checkins,
        [
            {
                'store_id': '12345567',
                'store_external_id': DEPOT_ID,
                'courier_id': WMS_COURIER_ID,
                'shift_id': 'shift_id',
                'status': 'in_progress',
                'closes_at': '2021-01-24T20:18:00Z',
                'started_at': '2021-01-24T20:18:00Z',
                'updated_ts': '2021-01-24T09:07:12Z',
            },
        ],
    )

    couriers_db.add_entry(
        WMS_COURIER_ID, None, PREVIOUS_CHECKIN, False, DEPOT_ID,
    )

    # await taxi_grocery_checkins.run_task('distlock/wms-shifts-sync')
    await taxi_grocery_checkins.invalidate_caches()

    await stq_runner.grocery_courier_last_order_delivered.call(
        task_id='task_id',
        kwargs={
            'park_id': PARK_ID,
            'driver_id': DRIVER_ID,
            'waybill_external_ref': 'waybill_ref',
            'return_claim_point_id': 4,
        },
    )

    courier = couriers_db.load_all_couriers()[0]
    assert courier.excluded_from_queue is True

    response = await taxi_grocery_checkins.post(
        '/internal/checkins/v2/queue-info', json={'depot_id': DEPOT_ID},
    )

    assert response.status_code == 200
    assert cargo_dispatch.confirm_times_called == 1
    assert response.json() == {'couriers': []}


async def _test_no_autoconfirm(
        taxi_grocery_checkins,
        couriers_db,
        cargo_dispatch,
        stq_runner,
        grocery_wms,
):
    await _setup_shift(
        grocery_wms,
        taxi_grocery_checkins,
        [
            {
                'store_id': '12345567',
                'store_external_id': DEPOT_ID,
                'courier_id': WMS_COURIER_ID,
                'shift_id': 'shift_id',
                'status': 'in_progress',
                'closes_at': CLOSES_AT,
                'started_at': PREVIOUS_CHECKIN,
                'updated_ts': '2020-07-28T09:07:12Z',
            },
        ],
    )

    couriers_db.add_entry(
        WMS_COURIER_ID, None, PREVIOUS_CHECKIN, False, DEPOT_ID,
    )

    await taxi_grocery_checkins.invalidate_caches()

    await stq_runner.grocery_courier_last_order_delivered.call(
        task_id='task_id',
        kwargs={
            'park_id': PARK_ID,
            'driver_id': DRIVER_ID,
            'waybill_external_ref': 'waybill_ref',
            'return_claim_point_id': 4,
        },
    )

    courier = couriers_db.load_all_couriers()[0]
    assert courier.excluded_from_queue is False

    response = await taxi_grocery_checkins.post(
        '/internal/checkins/v2/queue-info', json={'depot_id': DEPOT_ID},
    )

    assert response.status_code == 200
    assert cargo_dispatch.confirm_times_called == 0
    assert response.json() == {
        'couriers': [
            {
                'checkin_timestamp': PREVIOUS_CHECKIN,
                'courier_id': WMS_COURIER_ID,
            },
        ],
    }


@pytest.mark.now(HOUR_BEFORE_CLOSE)
@pytest.mark.experiments3(
    name='grocery_checkins_return_autoconfirm_settings',
    consumers=['grocery-checkins/return-autoconfirm'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={
        'enable_autoconfirm': True,
        'allowed_autoconfirm_period': 300,
        'allowed_shifts_gap': 300,
    },
    is_config=True,
)
async def test_return_point_autoconfirm_no_confirm(
        taxi_grocery_checkins,
        couriers_db,
        cargo_dispatch,
        stq_runner,
        grocery_wms,
):
    await _test_no_autoconfirm(**locals())


@pytest.mark.now(FOUR_MINUTES_BEFORE_CLOSE)
@pytest.mark.experiments3(
    name='grocery_checkins_return_autoconfirm_settings',
    consumers=['grocery-checkins/return-autoconfirm'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={
        'enable_autoconfirm': True,
        'allowed_autoconfirm_period': 300,
        'allowed_shifts_gap': 300,
    },
    clauses=[
        {
            'title': 'Disable for depot',
            'value': {
                'enable_autoconfirm': False,
                'allowed_autoconfirm_period': 300,
            },
            'enabled': True,
            'is_signal': False,
            'predicate': {
                'init': {
                    'value': DEPOT_ID,
                    'arg_name': 'depot_id',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
        },
    ],
    is_config=True,
)
async def test_return_point_autoconfirm_disabled_for_depot(
        taxi_grocery_checkins,
        couriers_db,
        cargo_dispatch,
        stq_runner,
        grocery_wms,
):
    await _test_no_autoconfirm(**locals())


@pytest.mark.now(FOUR_MINUTES_BEFORE_CLOSE)
@pytest.mark.experiments3(
    name='grocery_checkins_return_autoconfirm_settings',
    consumers=['grocery-checkins/return-autoconfirm'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={
        'enable_autoconfirm': True,
        'allowed_autoconfirm_period': 300,
        'allowed_shifts_gap': 300,
    },
    clauses=[
        {
            'title': 'Disable for depot',
            'value': {
                'enable_autoconfirm': False,
                'allowed_autoconfirm_period': 300,
            },
            'enabled': True,
            'is_signal': False,
            'predicate': {
                'init': {
                    'value': WMS_COURIER_ID,
                    'arg_name': 'courier_dbid_uuid',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
        },
    ],
    is_config=True,
)
async def test_return_point_autoconfirm_disabled_for_courier(
        taxi_grocery_checkins,
        couriers_db,
        cargo_dispatch,
        stq_runner,
        grocery_wms,
):
    await _test_no_autoconfirm(**locals())


@pytest.mark.now(HOUR_BEFORE_CLOSE)
@pytest.mark.experiments3(
    name='grocery_checkins_return_autoconfirm_settings',
    consumers=['grocery-checkins/return-autoconfirm'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={
        'enable_autoconfirm': True,
        'allowed_autoconfirm_period': 300,
        'allowed_shifts_gap': 300,
    },
    clauses=[
        {
            'title': 'Disable for one country',
            'value': {
                'enable_autoconfirm': False,
                'allowed_autoconfirm_period': 300,
            },
            'enabled': True,
            'is_signal': False,
            'predicate': {
                'init': {
                    'value': 'RUS',
                    'arg_name': 'country_iso3',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
        },
    ],
    is_config=True,
)
async def test_return_point_autoconfirm_disabled_for_country_iso3(
        taxi_grocery_checkins,
        couriers_db,
        cargo_dispatch,
        stq_runner,
        grocery_wms,
):
    await _test_no_autoconfirm(**locals())


@pytest.mark.now(HOUR_BEFORE_CLOSE)
@pytest.mark.experiments3(
    name='grocery_checkins_return_autoconfirm_settings',
    consumers=['grocery-checkins/return-autoconfirm'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={
        'enable_autoconfirm': True,
        'allowed_autoconfirm_period': 300,
        'allowed_shifts_gap': 300,
    },
    clauses=[
        {
            'title': 'Disable for one region',
            'value': {
                'enable_autoconfirm': False,
                'allowed_autoconfirm_period': 300,
            },
            'enabled': True,
            'is_signal': False,
            'predicate': {
                'init': {
                    'value': REGION_ID,
                    'arg_name': 'region_id',
                    'arg_type': 'string',
                },
                'type': 'eq',
            },
        },
    ],
    is_config=True,
)
async def test_return_point_autoconfirm_disabled_for_region_id(
        taxi_grocery_checkins,
        couriers_db,
        cargo_dispatch,
        stq_runner,
        grocery_wms,
):
    await _test_no_autoconfirm(**locals())


@pytest.mark.now(FOUR_MINUTES_BEFORE_CLOSE)
@pytest.mark.experiments3(
    name='grocery_checkins_return_autoconfirm_settings',
    consumers=['grocery-checkins/return-autoconfirm'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={
        'enable_autoconfirm': True,
        'allowed_autoconfirm_period': 300,
        'allowed_shifts_gap': 300,
    },
    is_config=True,
)
async def test_return_point_autoconfirm_wms_shifts(
        taxi_grocery_checkins, couriers_db, cargo_dispatch, stq_runner, pgsql,
):
    db = pgsql['grocery_checkins']
    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO grocery_checkins.shifts
        (
        courier_id,
        shift_id,
        depot_id,
        status,
        started_at,
        updated_ts,
        closes_at
        )
        VALUES ('wmsparkid_courierid', 'shift_id', '123456',
        'in_progress', '2021-01-24T08:47:00Z',
        '2021-01-24T09:07:12Z', '2021-01-24T20:18:00Z');
        """,
    )
    cursor.close()

    couriers_db.add_entry(
        'wmsparkid_courierid', None, PREVIOUS_CHECKIN, False, '123456',
    )

    await taxi_grocery_checkins.invalidate_caches()

    await stq_runner.grocery_courier_last_order_delivered.call(
        task_id='task_id',
        kwargs={
            'park_id': 'wmsparkid',
            'driver_id': DRIVER_ID,
            'waybill_external_ref': 'waybill_ref',
            'return_claim_point_id': 4,
        },
    )

    courier = couriers_db.load_all_couriers()[0]
    assert courier.excluded_from_queue is True

    response = await taxi_grocery_checkins.post(
        '/internal/checkins/v2/queue-info', json={'depot_id': DEPOT_ID},
    )

    assert response.status_code == 200
    assert cargo_dispatch.confirm_times_called == 1
    assert response.json() == {'couriers': []}


@pytest.mark.now(FOUR_MINUTES_BEFORE_CLOSE)
@pytest.mark.experiments3(
    name='grocery_checkins_return_autoconfirm_settings',
    consumers=['grocery-checkins/return-autoconfirm'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={
        'enable_autoconfirm': True,
        'allowed_autoconfirm_period': 3000,
        'allowed_shifts_gap': 300,
    },
    is_config=True,
)
@pytest.mark.parametrize(
    'current_shift_started, current_shift_closes,'
    'waiting_shift_started, waiting_shift_closes',
    [
        (
            '2021-01-24T08:47:00Z',
            '2021-01-24T20:18:00Z',
            '2021-01-24T20:19:00Z',
            None,
        ),
        (
            '2021-01-24T08:47:00Z',
            '2021-01-24T20:18:00Z',
            '2021-01-24T20:19:00Z',
            '2021-01-24T20:20:00Z',
        ),
    ],
)
async def test_no_autoconfirm_wms_cause_waiting(
        taxi_grocery_checkins,
        couriers_db,
        cargo_dispatch,
        stq_runner,
        grocery_wms,
        current_shift_started,
        current_shift_closes,
        waiting_shift_started,
        waiting_shift_closes,
):
    grocery_wms.set_couriers_shifts(
        [
            {
                'store_id': '123455657',
                'store_external_id': DEPOT_ID,
                'courier_id': WMS_COURIER_ID,
                'shift_id': 'shift_id',
                'depot_id': DEPOT_ID,
                'status': 'in_progress',
                'started_at': current_shift_started,
                'updated_ts': current_shift_started,
                'closes_at': current_shift_closes,
            },
            {
                'store_id': '123455657',
                'store_external_id': DEPOT_ID,
                'courier_id': WMS_COURIER_ID,
                'shift_id': 'shift_id',
                'depot_id': DEPOT_ID,
                'status': 'waiting',
                'started_at': waiting_shift_started,
                'closes_at': waiting_shift_closes,
            },
        ],
    )

    couriers_db.add_entry(
        WMS_COURIER_ID, None, PREVIOUS_CHECKIN, False, DEPOT_ID,
    )

    await taxi_grocery_checkins.invalidate_caches()

    await stq_runner.grocery_courier_last_order_delivered.call(
        task_id='task_id',
        kwargs={
            'park_id': PARK_ID,
            'driver_id': DRIVER_ID,
            'waybill_external_ref': 'waybill_ref',
            'return_claim_point_id': 4,
        },
    )

    courier = couriers_db.load_all_couriers()[0]
    assert courier.excluded_from_queue is False

    response = await taxi_grocery_checkins.post(
        '/internal/checkins/v2/queue-info', json={'depot_id': DEPOT_ID},
    )

    assert response.status_code == 200
    assert cargo_dispatch.confirm_times_called == 0
    assert response.json() == {'couriers': []}


@pytest.mark.now(HOUR_BEFORE_CLOSE)
@pytest.mark.experiments3(
    name='grocery_checkins_return_autoconfirm_settings',
    consumers=['grocery-checkins/return-autoconfirm'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Disable for one country',
            'value': {
                'enable_autoconfirm': False,
                'allowed_autoconfirm_period': 300,
            },
            'enabled': True,
            'is_signal': False,
            'predicate': {
                'init': {
                    'value': 'rover',
                    'arg_name': 'driver_tags',
                    'set_elem_type': 'string',
                },
                'type': 'contains',
            },
        },
    ],
    is_config=True,
)
async def test_check_driver_tags(
        taxi_grocery_checkins,
        couriers_db,
        eats_core,
        cargo_dispatch,
        stq_runner,
        grocery_wms,
        mockserver,
        experiments3,
        eats_shifts,
):
    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def mock_driver_tags(request):
        return mockserver.make_response(status=200, json={'tags': ['rover']})

    exp3_recorder = experiments3.record_match_tries(
        'grocery_checkins_return_autoconfirm_settings',
    )

    await _setup_shift(
        grocery_wms,
        taxi_grocery_checkins,
        [
            {
                'store_id': '12345567',
                'store_external_id': DEPOT_ID,
                'courier_id': WMS_COURIER_ID,
                'shift_id': 'shift_id',
                'status': 'in_progress',
                'closes_at': CLOSES_AT,
                'started_at': PREVIOUS_CHECKIN,
                'updated_ts': '2020-07-28T09:07:12Z',
            },
        ],
    )

    couriers_db.add_entry(WMS_COURIER_ID, None, PREVIOUS_CHECKIN, False)

    await taxi_grocery_checkins.invalidate_caches()

    await stq_runner.grocery_courier_last_order_delivered.call(
        task_id='task_id',
        kwargs={
            'park_id': PARK_ID,
            'driver_id': DRIVER_ID,
            'waybill_external_ref': 'waybill_ref',
            'return_claim_point_id': 4,
        },
    )

    assert mock_driver_tags.times_called == 1

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    assert match_tries[0].kwargs['driver_tags'] == ['rover']


async def _setup_shift(grocery_wms, taxi_grocery_checkins, shifts):
    grocery_wms.set_couriers_shifts(shifts)
    await taxi_grocery_checkins.run_task('distlock/wms-shifts-sync')
    await taxi_grocery_checkins.invalidate_caches()
