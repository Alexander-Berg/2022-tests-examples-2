# pylint: disable=import-error
import pytest
import reposition_api.fbs.v1.airport_queue.state.Request as StateRequest

import tests_dispatch_airport.utils as utils


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql(
    'dispatch_airport', files=['driver_queue.sql', 'driver_events.sql'],
)
async def test_reposition_filter_parking_relocation(
        taxi_dispatch_airport, testpoint, mockserver,
):
    @testpoint('reposition-filter-finished')
    def reposition_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    @mockserver.json_handler(
        '/reposition-api/internal/reposition-api/v1/service/session/stop',
    )
    def _reposition_stop(request):
        return {}

    @mockserver.handler('/reposition-api/v1/service/airport_queue/state')
    def reposition_mock(request):
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
            'dbid_uuid6',
            'dbid_uuid7',
            'dbid_uuid8',
        ]

        drivers = [
            {
                'dbid': 'dbid',
                'uuid': 'uuid1',
                'airport_id': 'ekb',
                'mode': 'Sintegro',
            },
            {
                'dbid': 'dbid',
                'uuid': 'uuid3',
                'airport_id': 'ekb',
                'mode': 'Airport',
            },
            {
                'dbid': 'dbid',
                'uuid': 'uuid4',
                'airport_id': 'ekb',
                'mode': 'Airport',
            },
            {
                'dbid': 'dbid',
                'uuid': 'uuid7',
                'airport_id': 'ekb',
                'mode': 'Sintegro',
            },
        ]
        return mockserver.make_response(
            response=utils.generate_reposition_api_drivers(drivers),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')
    response = (await reposition_filter_finished.wait_call())['data']

    assert reposition_mock.times_called == 1

    updated_etalons = {
        # queued driver with new parking relocation
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['econom'],
            'parking_relocation_session': 'session_dbid_uuid1',
        },
        # queued driver without relocation offer
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['econom'],
            'parking_relocation_session': None,
        },
        # entered driver driver with new repo session
        'dbid_uuid3': {
            'driver_id': 'dbid_uuid3',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnReposition,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['econom'],
            'parking_relocation_session': None,
            'reposition_session_id': 'session_dbid_uuid3',
        },
        # entered driver with existing repo in notification area
        'dbid_uuid4': {
            'driver_id': 'dbid_uuid4',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnReposition,
            'airport': 'ekb',
            'areas': [2],
            'classes': ['econom'],
            'parking_relocation_session': None,
            'reposition_session_id': 'enter_repo_session_id4',
        },
        # entered driver with existing repo in waiting area -> queued
        'dbid_uuid5': {
            'driver_id': 'dbid_uuid5',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnReposition,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['econom'],
            'parking_relocation_session': None,
            'reposition_session_id': 'enter_repo_session_id5',
        },
        # queued driver with expired relocation offer
        'dbid_uuid6': {
            'driver_id': 'dbid_uuid6',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['econom'],
            'parking_relocation_session': None,
        },
        # queued driver with existing relocation offer
        'dbid_uuid7': {
            'driver_id': 'dbid_uuid7',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['econom'],
            'parking_relocation_session': 'session_dbid_uuid7',
        },
        # entered driver with expired repo
        'dbid_uuid8': {
            'driver_id': 'dbid_uuid8',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'areas': [2],
            'classes': ['econom'],
            'parking_relocation_session': None,
            'reposition_session_id': None,
        },
    }
    utils.check_filter_result(response, updated_etalons)

    await utils.wait_certain_testpoint('ekb', queue_update_finished)
