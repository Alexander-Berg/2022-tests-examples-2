# pylint: disable=import-error
import datetime

import pytest
import reposition_api.fbs.v1.airport_queue.state.Request as StateRequest

import tests_dispatch_airport.utils as utils


REPOSITION_FILTER_NAME = 'reposition-filter'
NON_AIRPORT_MODE = 'NonAirportMode'


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize(
    'svo_group_id', [None, 'another_group_id', 'test_group_id'],
)
async def test_group_id_with_non_airport_mode(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        mockserver,
        now,
        taxi_config,
        svo_group_id,
        pgsql,
):
    zones_config = taxi_config.get('DISPATCH_AIRPORT_ZONES')
    zones_config['ekb']['old_mode_enabled'] = False
    zones_config['svo']['old_mode_enabled'] = False
    zones_config['ekb']['group_id'] = 'test_group_id'
    if svo_group_id is not None:
        zones_config['svo']['group_id'] = svo_group_id
    relocation_config = taxi_config.get(
        'DISPATCH_AIRPORT_RELOCATION_REPOSITION_SETTINGS',
    )
    relocation_config['by_point']['__default__']['mode'] = NON_AIRPORT_MODE
    taxi_config.set_values(
        {
            'DISPATCH_AIRPORT_ZONES': zones_config,
            'DISPATCH_AIRPORT_RELOCATION_REPOSITION_SETTINGS': (
                relocation_config
            ),
        },
    )

    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(REPOSITION_FILTER_NAME + '-finished')
    def reposition_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        return utils.generate_candidates_response(
            request.json['driver_ids'], ['econom'],
        )

    @mockserver.handler('/reposition-api/v1/service/airport_queue/state')
    def _reposition(request):
        request = StateRequest.Request.GetRootAsRequest(request.get_data(), 0)
        assert request.AirportQueueId() is None
        request_drivers = []
        for i in range(request.DriversLength()):
            driver = request.Drivers(i)
            dbid = driver.ParkDbId().decode()
            uuid = driver.DriverProfileId().decode()
            request_drivers.append(f'{dbid}_{uuid}')
        assert sorted(request_drivers) == ['dbid_uuid1', 'dbid_uuid2']

        drivers = [
            {'dbid': 'dbid', 'uuid': 'uuid1', 'airport_id': 'svo'},
            {
                'dbid': 'dbid',
                'uuid': 'uuid2',
                'airport_id': '',
                'mode': NON_AIRPORT_MODE,
            },
        ]
        return mockserver.make_response(
            response=utils.generate_reposition_api_drivers(drivers),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    @mockserver.json_handler(
        '/reposition-api/internal/reposition-api/v1/service/session/stop',
    )
    def _reposition_stop(request):
        return {}

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - new driver: notification zone (with reposition)
    # dbid_uuid2 - new driver: notification zone (Sintegro mode)

    # avoid couple seconds diff test flaps when compare pg and geobus ts
    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid1': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid2': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now)
    await merge_finished.wait_call()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    response = (await reposition_filter_finished.wait_call())['data']
    updated_etalons = {
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kNonAirportReposition,
            'airport': 'ekb',
            'areas': [2],
            'classes': ['econom'],
            'old_mode_enabled': False,
        },
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnReposition,
            'airport': 'ekb',
            'areas': [2],
            'classes': ['econom'],
            'reposition_session_id': 'session_dbid_uuid2',
            'old_mode_enabled': False,
        },
    }
    events = [('udid2', 'entered_on_repo')]
    if svo_group_id == 'test_group_id':
        driver_1 = updated_etalons['dbid_uuid1']
        driver_1['state'] = utils.State.kEntered
        driver_1['reason'] = utils.Reason.kOnReposition
        driver_1['reposition_session_id'] = 'session_dbid_uuid1'
        events.insert(0, ('udid1', 'entered_on_repo'))

    utils.check_filter_result(response, updated_etalons)

    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    db = pgsql['dispatch_airport']
    assert utils.get_drivers_queue(db) == ['dbid_uuid1', 'dbid_uuid2']
    assert (
        sorted(
            utils.get_driver_events(db, no_event_id=True), key=lambda x: x[0],
        )
        == events
    )


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.busy_drivers(
    busy_drivers=[
        {
            'driver_id': 'dbid_uuid1',
            'order_id': 'order_id_1',
            'taxi_status': 3,
            'final_destination': {'lat': 11.0, 'lon': 21.0},
        },
        {
            'driver_id': 'dbid_uuid2',
            'order_id': 'order_id_2',
            'taxi_status': 3,
            'final_destination': {'lat': 11.0, 'lon': 21.0},
        },
    ],
)
async def test_non_airport_reposition_with_airport_order(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        pgsql,
        mockserver,
        now,
        taxi_config,
        mode,
):
    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint('orders-filter-finished')
    def orders_filter_finished(data):
        return data

    @testpoint('reposition-filter-finished')
    def reposition_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        append = request.json['append'][0]
        assert 'remove' not in request.json
        if mode == 'new':
            utils.check_airport_tags(append, (), ('dbid_uuid1',))
        else:
            utils.check_airport_tags(append, ('dbid_uuid2',), ('dbid_uuid1',))
        return {}

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        return utils.generate_candidates_response(
            request.json['driver_ids'], ['econom', 'comfortplus'],
        )

    @mockserver.json_handler(
        '/driver-categories-api/v2/aggregation/categories',
    )
    def _driver_categories(request):
        assert len(request.json['drivers']) == 2
        return utils.generate_categories_response(
            [driver['driver_id'] for driver in request.json['drivers']],
            ['comfortplus', 'econom'],
        )

    @mockserver.handler('/reposition-api/v1/service/airport_queue/state')
    def _reposition(request):
        request = StateRequest.Request.GetRootAsRequest(request.get_data(), 0)
        assert request.AirportQueueId() is None
        request_drivers = []
        for i in range(request.DriversLength()):
            driver = request.Drivers(i)
            dbid = driver.ParkDbId().decode()
            uuid = driver.DriverProfileId().decode()
            request_drivers.append(f'{dbid}_{uuid}')
        assert sorted(request_drivers) == ['dbid_uuid1', 'dbid_uuid2']

        drivers = [{'dbid': 'dbid', 'uuid': 'uuid2', 'airport_id': ''}]
        return mockserver.make_response(
            response=utils.generate_reposition_api_drivers(drivers),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    old_mode_enabled = utils.get_old_mode_enabled(mode)
    custom_config = utils.custom_config(old_mode_enabled=old_mode_enabled)
    taxi_config.set_values(custom_config)
    utils.set_mode_in_config(taxi_config, mode)

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - driver with order -> entered on_action
    # dbid_uuid2 - driver with order, but filtered by non airport reposition

    # avoid couple seconds diff test flaps when compare pg and geobus ts
    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid1': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid2': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now)
    await merge_finished.wait_call()
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    reposition_response = (await reposition_filter_finished.wait_call())[
        'data'
    ]
    reposition_etalons = {
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['econom', 'comfortplus'],
            'input_order_id': 'order_id_1',
        },
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'state': (
                utils.State.kEntered
                if mode != 'new'
                else utils.State.kFiltered
            ),
            'reason': (
                '' if mode != 'new' else utils.Reason.kNonAirportReposition
            ),
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['econom', 'comfortplus'],
            'input_order_id': 'order_id_2',
        },
    }
    utils.check_filter_result(reposition_response, reposition_etalons)
    orders_response = (await orders_filter_finished.wait_call())['data']
    orders_etalons = {
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnAction,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['econom', 'comfortplus'],
            'input_order_id': 'order_id_1',
        },
    }
    if mode != 'new':
        orders_etalons['dbid_uuid2'] = {
            'driver_id': 'dbid_uuid2',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['econom', 'comfortplus'],
            'input_order_id': 'order_id_2',
        }
    utils.check_filter_result(orders_response, orders_etalons)

    await utils.wait_certain_testpoint('ekb', queue_update_finished)
    db = pgsql['dispatch_airport']
    drivers = utils.get_drivers_queue(db)
    assert drivers == ['dbid_uuid1', 'dbid_uuid2']

    if mode != 'new':
        orders_etalons['dbid_uuid2']['state'] = utils.State.kQueued
    else:
        orders_etalons['dbid_uuid2'] = reposition_etalons['dbid_uuid2']

    utils.update_etalons_by_simulation_old_queue_filter_processing(
        orders_etalons, mode,
    )
    utils.check_drivers_queue(db, orders_etalons.values())

    if mode != 'old':
        assert sorted(
            utils.get_driver_events(db, no_event_id=True), key=lambda x: x[0],
        ) == [('udid1', 'entered_on_order')]
    else:
        assert not utils.get_driver_events(db)
