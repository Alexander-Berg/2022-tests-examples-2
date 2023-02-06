import datetime

import pytest

import tests_dispatch_airport.utils as utils

CLIENTS_FILTER_NAME = 'clients-filter'


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql(
    'dispatch_airport', files=['drivers_queue.sql', 'driver_events.sql'],
)
@pytest.mark.experiments3(
    filename='experiments3_dispatch_airport_allowed_clients.json',
)
@pytest.mark.parametrize('old_mode_enabled', [True, False])
@pytest.mark.busy_drivers(
    busy_drivers=[
        {
            'driver_id': 'dbid_uuid14',
            'order_id': 'order_id_14',
            'taxi_status': 3,
            'final_destination': {'lat': 1.0, 'lon': 1.0},
        },
        {
            'driver_id': 'dbid_uuid15',
            'order_id': 'order_id_15',
            'taxi_status': 3,
            'final_destination': {'lat': 11.0, 'lon': 21.0},
        },
        {
            'driver_id': 'dbid_uuid16',
            'order_id': 'order_id_16',
            'taxi_status': 3,
            'final_destination': {'lat': 11.0, 'lon': 21.0},
        },
    ],
)
async def test_clients_filter(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        pgsql,
        mockserver,
        taxi_config,
        load_json,
        now,
        old_mode_enabled,
):
    config = utils.custom_config(old_mode_enabled)
    taxi_config.set_values(config)

    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(CLIENTS_FILTER_NAME + '-finished')
    def clients_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        assert request.json['zone_id'] == 'ekb_home_zone'
        return load_json('candidates.json')

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _driver_app_profiles(request):
        assert len(request.json['id_in_set']) == 14
        assert set(request.json['projection']) == set(
            {
                'data.taximeter_version_type',
                'data.taximeter_platform',
                'data.taximeter_version',
                'data.taximeter_brand',
                'data.taximeter_build_type',
                'data.taximeter_platform_version',
                'data.locale',
            },
        )
        return load_json('profiles.json')

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        append = request.json['append'][0]
        remove = request.json['remove'][0]
        if old_mode_enabled:
            utils.check_airport_tags(
                append,
                expected_queued=('dbid_uuid7',),
                expected_entered=(
                    'dbid_uuid1',
                    'dbid_uuid2',
                    'dbid_uuid6',
                    'dbid_uuid8',
                    'dbid_uuid9',
                    'dbid_uuid10',
                    'dbid_uuid11',
                ),
            )
            utils.check_airport_tags(
                remove, expected_queued=(), expected_entered=('dbid_uuid7',),
            )
        else:
            utils.check_airport_tags(
                append,
                expected_queued=('dbid_uuid7',),
                expected_entered=('dbid_uuid6',),
            )
            utils.check_airport_tags(
                remove, expected_queued=(), expected_entered=('dbid_uuid7',),
            )

        return {}

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - new driver: taximeter-production (android)
    # dbid_uuid2 - new driver: taximeter-beta (android)
    # dbid_uuid3 - new driver: taximeter-production (ios)
    # dbid_uuid4 - new driver: uber (android)
    # dbid_uuid5 - new driver: uber (ios)
    # dbid_uuid6 - stored driver: taximeter (android)
    # dbid_uuid7 - stored driver: taximeter (android)
    # dbid_uuid8 - new driver: taximeter-az (android)
    # dbid_uuid9 - new driver: taximeter-yango (android)
    # dbid_uuid10 - new driver: taximeter-yango-sdc (android)
    # dbid_uuid11 - new driver: taximeter-yango-dev (android)
    # dbid_uuid12 - new driver: vezet (android)
    # dbid_uuid13 - new driver: vezet (ios)
    # dbid_uuid14 - new driver: vezet (ios), busy, not allowed order
    # dbid_uuid15 - new driver: vezet (ios), busy, allowed order
    # dbid_uuid16 - new driver: vezet (ios), busy, allowed order, event exists

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
        'dbid_uuid3': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid4': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid5': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid8': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid9': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid10': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid11': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid12': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid13': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid14': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid15': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid16': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now)
    await merge_finished.wait_call()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    response = (await clients_filter_finished.wait_call())['data']
    updated_etalon = {
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'areas': [2],
            'classes': [],
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'areas': [2],
            'classes': [],
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid3': {
            'driver_id': 'dbid_uuid3',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kWrongClient,
            'airport': 'ekb',
            'areas': [2],
            'classes': [],
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid4': {
            'driver_id': 'dbid_uuid4',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kWrongClient,
            'airport': 'ekb',
            'areas': [2],
            'classes': [],
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid5': {
            'driver_id': 'dbid_uuid5',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kWrongClient,
            'airport': 'ekb',
            'areas': [2],
            'classes': [],
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid6': {
            'driver_id': 'dbid_uuid6',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [2],
            'classes': ['econom'],
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid7': {
            'driver_id': 'dbid_uuid7',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid8': {
            'driver_id': 'dbid_uuid8',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'areas': [2],
            'classes': [],
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid9': {
            'driver_id': 'dbid_uuid9',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'areas': [2],
            'classes': [],
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid10': {
            'driver_id': 'dbid_uuid10',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'areas': [2],
            'classes': [],
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid11': {
            'driver_id': 'dbid_uuid11',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'areas': [2],
            'classes': [],
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid12': {
            'driver_id': 'dbid_uuid12',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kWrongClient,
            'airport': 'ekb',
            'areas': [2],
            'classes': [],
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid13': {
            'driver_id': 'dbid_uuid13',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kWrongClient,
            'airport': 'ekb',
            'areas': [2],
            'classes': [],
            'old_mode_enabled': old_mode_enabled,
        },
        'dbid_uuid14': {
            'driver_id': 'dbid_uuid14',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kWrongClient,
            'airport': 'ekb',
            'areas': [2],
            'classes': ['econom'],
            'old_mode_enabled': old_mode_enabled,
            'input_order_id': 'order_id_14',
        },
        'dbid_uuid15': {
            'driver_id': 'dbid_uuid15',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kWrongClient,
            'airport': 'ekb',
            'areas': [2],
            'classes': ['econom'],
            'old_mode_enabled': old_mode_enabled,
            'input_order_id': 'order_id_15',
        },
        'dbid_uuid16': {
            'driver_id': 'dbid_uuid16',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kWrongClient,
            'airport': 'ekb',
            'areas': [2],
            'classes': ['econom'],
            'old_mode_enabled': old_mode_enabled,
            'input_order_id': 'order_id_16',
        },
    }
    assert len(response) == len(updated_etalon)
    for driver in response:
        etalon = updated_etalon[driver['driver_id']]
        utils.check_drivers(driver, etalon)

    await _tags.wait_call()
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    db = pgsql['dispatch_airport']
    drivers = utils.get_drivers_queue(db)
    assert drivers == [
        'dbid_uuid1',
        'dbid_uuid10',
        'dbid_uuid11',
        'dbid_uuid12',
        'dbid_uuid13',
        'dbid_uuid14',
        'dbid_uuid15',
        'dbid_uuid16',
        'dbid_uuid2',
        'dbid_uuid3',
        'dbid_uuid4',
        'dbid_uuid5',
        'dbid_uuid6',
        'dbid_uuid7',
        'dbid_uuid8',
        'dbid_uuid9',
    ]
    driver_events_keys = list(utils.get_driver_events(db).keys())
    etalon_driver_event_keys = [
        ('udid16', 'old_session_id16', 'entered_on_order_wrong_client'),
    ]
    if old_mode_enabled:
        assert driver_events_keys == etalon_driver_event_keys
    else:
        first_event = driver_events_keys.pop(0)
        assert ('udid15', 'entered_on_order_wrong_client') == (
            first_event[0],
            first_event[2],
        )
        assert driver_events_keys == etalon_driver_event_keys
