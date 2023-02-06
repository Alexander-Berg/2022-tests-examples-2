import datetime

import pytest

import tests_dispatch_airport.utils as utils


@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.parametrize(
    'enabled_without_active_label,working_hours,allowed_by_schedule',
    [
        (
            False,
            {'start_local_time': '10:30', 'end_local_time': '19:30'},
            False,
        ),
        (
            True,
            {'start_local_time': '10:30', 'end_local_time': '19:30'},
            False,
        ),
        (True, {'start_local_time': '10:30', 'end_local_time': '19:30'}, True),
    ],
)
async def test_rfid_label_filter(
        taxi_dispatch_airport,
        taxi_config,
        testpoint,
        mockserver,
        mocked_time,
        enabled_without_active_label,
        working_hours,
        allowed_by_schedule,
):
    @testpoint('rfid-label-filter-finished')
    def filter_finished(data):
        return data

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    @mockserver.handler('/reposition-api/v1/service/airport_queue/state')
    def _reposition(request):
        drivers = [{'dbid': 'dbid', 'uuid': 'uuid3', 'airport_id': 'ekb'}]
        return mockserver.make_response(
            response=utils.generate_reposition_api_drivers(drivers),
            headers={'Content-Type': 'application/x-flatbuffers'},
        )

    date = datetime.datetime(2021, 10, 4, 8, 00, 00)
    if not allowed_by_schedule:
        date = datetime.datetime(2021, 10, 4, 7, 00, 00)

    mocked_time.set(date)

    settings = {
        'ekb': {
            'enabled_without_active_label': enabled_without_active_label,
            'enter_check_enabled': True,
        },
    }
    if working_hours:
        settings['ekb'].update(working_hours)
    taxi_config.set_values(
        {'DISPATCH_AIRPORT_WITHOUT_RFID_LABEL_AVAILABILITY': settings},
    )

    config = utils.custom_config(True)
    taxi_config.set_values(config)

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    response = (await filter_finished.wait_call())['data']
    updated_etalons = {
        'dbid_uuid1': {  # driver with active label
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnAction,
            'airport': 'ekb',
            'areas': [0, 1, 2],
            'classes': ['econom'],
        },
        'dbid_uuid2': {  # driver without label
            'driver_id': 'dbid_uuid2',
            'state': (
                utils.State.kFiltered
                if not enabled_without_active_label or not allowed_by_schedule
                else utils.State.kEntered
            ),
            'reason': (
                utils.Reason.kWithoutActiveRfidLabel
                if not enabled_without_active_label or not allowed_by_schedule
                else utils.Reason.kOnAction
            ),
            'airport': 'ekb',
            'areas': [0, 1, 2],
            'classes': ['econom'],
        },
        'dbid_uuid3': {  # driver without label, but entered not on action
            'driver_id': 'dbid_uuid3',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnReposition,
            'airport': 'ekb',
            'areas': [0, 2],
            'classes': ['econom'],
            'reposition_session_id': 'dbid_uuid3_session',
        },
        'dbid_uuid4': {  # driver without label, but already queued
            'driver_id': 'dbid_uuid4',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnAction,
            'airport': 'ekb',
            'areas': [0, 1, 2],
            'classes': ['econom'],
        },
    }
    assert len(response) == len(updated_etalons)
    for driver in response:
        etalon = updated_etalons[driver['driver_id']]
        utils.check_drivers(driver, etalon)
