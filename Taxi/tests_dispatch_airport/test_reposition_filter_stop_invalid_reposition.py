# pylint: disable=import-error
import pytest
import reposition_api.fbs.v1.airport_queue.state.Request as StateRequest

import tests_dispatch_airport.utils as utils

REPOSITION_FILTER_NAME = 'reposition-filter'


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
async def test_reposition_filter_stop_invalid_reposition(
        taxi_dispatch_airport, testpoint, pgsql, mockserver, mode,
):
    number_of_drivers = 5
    old_mode_enabled = utils.get_old_mode_enabled(mode)

    @testpoint(REPOSITION_FILTER_NAME + '-finished')
    def reposition_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        assert len(request.json['driver_ids']) == number_of_drivers
        assert request.json['zone_id'] == 'ekb_home_zone'
        return utils.generate_candidates_response(
            request.json['driver_ids'], ['comfortplus', 'econom'],
        )

    @mockserver.json_handler(
        '/driver-categories-api/v2/aggregation/categories',
    )
    def _driver_categories(request):
        assert len(request.json['drivers']) == number_of_drivers
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
        assert sorted(request_drivers) == [
            'dbid_uuid1',
            'dbid_uuid2',
            'dbid_uuid3',
            'dbid_uuid4',
            'dbid_uuid5',
        ]

        drivers = [
            {
                'dbid': 'dbid',
                'uuid': 'uuid1',
                'airport_id': 'ekb',
                'session_id': 'invalid_session_1',
            },
            {
                'dbid': 'dbid',
                'uuid': 'uuid2',
                'airport_id': 'ekb',
                'session_id': 'invalid_session_2',
            },
            {'dbid': 'dbid', 'uuid': 'uuid3', 'airport_id': 'ekb'},
            {'dbid': 'dbid', 'uuid': 'uuid4', 'airport_id': 'ekb'},
            {'dbid': 'dbid', 'uuid': 'uuid5', 'airport_id': 'svo'},
        ]
        return mockserver.make_response(
            response=utils.generate_reposition_api_drivers(drivers),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    stopped_sessions = set()

    @mockserver.json_handler(
        '/reposition-api/internal/reposition-api/v1/service/session/stop',
    )
    def reposition_stop(request):
        stopped_sessions.add(request.json['session_id'])
        return {}

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - queued, on_reposition and has invalid reposition
    # dbid_uuid2 - queued, old_mode and has invalid reposition
    # dbid_uuid3 - entered, old_mode and has new reposition
    # dbid_uuid4 - entered, on_reposition and still has it
    # dbid_uuid5 - queued, old_mode and has reposition to another airport

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    # reposition-filter check
    response = (await reposition_filter_finished.wait_call())['data']
    updated_etalons = {
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnReposition,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
            'reposition_session_id': 'session_dbid_uuid1',
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid3': {
            'driver_id': 'dbid_uuid3',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnReposition,
            'airport': 'ekb',
            'areas': [2],
            'classes': ['comfortplus', 'econom'],
            'old_mode_enabled': old_mode_enabled,
            'reposition_session_id': 'session_dbid_uuid3',
        },
        'dbid_uuid4': {
            'driver_id': 'dbid_uuid4',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnReposition,
            'airport': 'ekb',
            'areas': [2],
            'classes': ['comfortplus', 'econom'],
            'reposition_session_id': 'session_dbid_uuid4',
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid5': {
            'driver_id': 'dbid_uuid5',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [2],
            'classes': ['comfortplus', 'econom'],
            'old_mode_enabled': old_mode_enabled,
        },
    }

    utils.check_filter_result(response, updated_etalons)

    assert reposition_stop.times_called == 2
    assert stopped_sessions == {'invalid_session_1', 'invalid_session_2'}

    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    db = pgsql['dispatch_airport']
    drivers = utils.get_drivers_queue(db)
    assert drivers == [
        'dbid_uuid1',
        'dbid_uuid2',
        'dbid_uuid3',
        'dbid_uuid4',
        'dbid_uuid5',
    ]
