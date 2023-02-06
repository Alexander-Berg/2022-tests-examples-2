import pytest

import tests_dispatch_airport.utils as utils


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
async def test_partner_protocol_filter(
        taxi_dispatch_airport,
        taxi_config,
        testpoint,
        redis_store,
        mockserver,
        now,
        pgsql,
):
    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint('partner-protocol-filter-finished')
    def filter_finished(data):
        return data

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    @mockserver.json_handler(
        '/dispatch-airport-partner-protocol/service/v2/parked_drivers',
    )
    def _dapp_parked_drivers(request):
        assert 'parking_id' in request.json
        assert request.json['parking_id'] == '42'
        return {'drivers': [{'driver_id': 'dbid_uuid1'}]}

    config = utils.custom_config(True)
    config['DISPATCH_AIRPORT_ZONES']['ekb']['partner_parking_id'] = '42'
    taxi_config.set_values(config)

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    position = {
        'notification': [16, 6],  # notification
        'main': [21, 11],  # main notification
        'waiting': [26, 16],  # waiting main notification
    }

    # state before task run:
    # dbid_uuid1 - new, confirmed by partner
    # dbid_uuid2 - new
    # dbid_uuid3 - queued
    # dbid_uuid4 - new
    # dbid_uuid5 - new
    positions = {
        'dbid_uuid1': {'position': position['waiting'], 'timestamp': now},
        'dbid_uuid2': {'position': position['waiting'], 'timestamp': now},
        'dbid_uuid3': {'position': position['waiting'], 'timestamp': now},
        'dbid_uuid4': {'position': position['main'], 'timestamp': now},
        'dbid_uuid5': {'position': position['notification'], 'timestamp': now},
    }

    utils.publish_positions(redis_store, positions, now)
    await merge_finished.wait_call()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    response = (await filter_finished.wait_call())['data']
    updated_etalons = {
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'areas': [0, 1, 2],
            'classes': [],
        },
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kForbiddenByPartner,
            'airport': 'ekb',
            'areas': [0, 1, 2],
            'classes': [],
        },
        'dbid_uuid3': {
            'driver_id': 'dbid_uuid3',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [0, 1, 2],
            'classes': ['econom'],
        },
        'dbid_uuid4': {
            'driver_id': 'dbid_uuid4',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'areas': [0, 2],
            'classes': [],
        },
        'dbid_uuid5': {
            'driver_id': 'dbid_uuid5',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'areas': [2],
            'classes': [],
        },
    }
    assert len(response) == len(updated_etalons)
    for driver in response:
        etalon = updated_etalons[driver['driver_id']]
        utils.check_drivers(driver, etalon)
    assert not utils.get_driver_events(pgsql['dispatch_airport'])


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql(
    'dispatch_airport', files=['drivers_queue_for_timeout_test.sql'],
)
@pytest.mark.config(
    DISPATCH_AIRPORT_FORBIDDEN_BY_PARTNER_TIMEOUTS={
        '__default__': {'filter_timeout': 60},
    },
)
@pytest.mark.parametrize('old_mode_enabled', [False, True])
async def test_partner_protocol_filter_timeout(
        taxi_dispatch_airport,
        taxi_config,
        testpoint,
        redis_store,
        mockserver,
        now,
        pgsql,
        mocked_time,
        old_mode_enabled,
):
    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint('partner-protocol-filter-finished')
    def filter_finished(data):
        return data

    @testpoint('simulation-old-queue-filter-finished')
    def simulation_old_queue_finished(data):
        return data

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    @mockserver.json_handler(
        '/reposition-api/internal/reposition-api/v1/service/session/stop',
    )
    def _reposition_stop(request):
        return {}

    parked_drivers = []

    @mockserver.json_handler(
        '/dispatch-airport-partner-protocol/service/v2/parked_drivers',
    )
    def _dapp_parked_drivers(request):
        assert 'parking_id' in request.json
        assert request.json['parking_id'] == '42'
        return {
            'drivers': [
                {'driver_id': driver_id} for driver_id in parked_drivers
            ],
        }

    async def publish_positions():
        await taxi_dispatch_airport.invalidate_caches()

        positions = {
            'dbid_uuid1': {
                'position': utils.AIRPORT_POSITION,
                'timestamp': mocked_time.now(),
            },
            'dbid_uuid2': {
                'position': utils.AIRPORT_POSITION,
                'timestamp': mocked_time.now(),
            },
            'dbid_uuid3': {
                'position': utils.AIRPORT_POSITION,
                'timestamp': mocked_time.now(),
            },
            'dbid_uuid4': {
                'position': utils.AIRPORT_POSITION,
                'timestamp': mocked_time.now(),
            },
            'dbid_uuid5': {
                'position': utils.AIRPORT_POSITION,
                'timestamp': mocked_time.now(),
            },
        }

        utils.publish_positions(redis_store, positions, now)
        await merge_finished.wait_call()

    config = utils.custom_config(old_mode_enabled)
    config['DISPATCH_AIRPORT_ZONES']['ekb']['partner_parking_id'] = '42'
    taxi_config.set_values(config)

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    etalon = {
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'areas': [0, 1, 2],
            'classes': [],
            'forbidden_by_partner_started_tp': True,
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'areas': [0, 1, 2],
            'classes': [],
            'forbidden_by_partner_started_tp': True,
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid3': {
            'driver_id': 'dbid_uuid3',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnReposition,
            'airport': 'ekb',
            'areas': [0, 1, 2],
            'classes': ['econom'],
            'reposition_session_id': 'reposition_session_3',
            'forbidden_by_partner_started_tp': True,
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid4': {
            'driver_id': 'dbid_uuid4',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnAction,
            'airport': 'ekb',
            'areas': [0, 1, 2],
            'classes': ['econom'],
            'input_order_id': 'input_order_4',
            'forbidden_by_partner_started_tp': True,
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid5': {
            'driver_id': 'dbid_uuid5',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [0, 1, 2],
            'classes': ['econom'],
            'forbidden_by_partner_started_tp': True,
            'old_mode_enabled': old_mode_enabled,
        },
    }

    # iteration 1: fill forbidden by partner started tp
    await publish_positions()
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    response = (await filter_finished.wait_call())['data']
    utils.check_filter_result(response, etalon)

    simulation_old_mode_result = (
        await simulation_old_queue_finished.wait_call()
    )['data']
    utils.check_filter_result(simulation_old_mode_result, [])

    # iteration 2: 30 seconds passes - nothing changes
    mocked_time.sleep(30)
    await publish_positions()

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    response = (await filter_finished.wait_call())['data']
    utils.check_filter_result(response, etalon)

    simulation_old_mode_result = (
        await simulation_old_queue_finished.wait_call()
    )['data']
    utils.check_filter_result(simulation_old_mode_result, [])

    # iteration 3: another 30 seconds passes - driver 2 gets filtered, while
    # other drivers are parked and are queued or filtered by other filters
    mocked_time.sleep(31)
    parked_drivers = ['dbid_uuid1', 'dbid_uuid3', 'dbid_uuid4', 'dbid_uuid5']
    await publish_positions()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    response = (await filter_finished.wait_call())['data']
    for driver_id in parked_drivers:
        etalon[driver_id]['forbidden_by_partner_started_tp'] = False
    etalon['dbid_uuid2']['state'] = utils.State.kFiltered
    etalon['dbid_uuid2']['reason'] = utils.Reason.kForbiddenByPartner
    utils.check_filter_result(response, etalon)

    simulation_old_mode_result = (
        await simulation_old_queue_finished.wait_call()
    )['data']
    if old_mode_enabled:
        etalon['dbid_uuid1']['state'] = utils.State.kQueued
        etalon['dbid_uuid1']['reason'] = utils.Reason.kOldMode
    else:
        etalon['dbid_uuid1']['state'] = utils.State.kFiltered
        etalon['dbid_uuid1']['reason'] = utils.Reason.kFullQueue
    etalon['dbid_uuid3']['state'] = utils.State.kQueued
    etalon['dbid_uuid4']['state'] = utils.State.kQueued
    etalon['dbid_uuid5']['state'] = utils.State.kQueued
    etalon.pop('dbid_uuid2')
    utils.check_filter_result(simulation_old_mode_result, etalon)

    assert not utils.get_driver_events(pgsql['dispatch_airport'])
