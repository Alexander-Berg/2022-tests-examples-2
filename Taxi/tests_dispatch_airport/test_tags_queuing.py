# pylint: disable=import-error
import datetime

import pytest
import reposition_api.fbs.v1.airport_queue.state.Request as StateRequest

import tests_dispatch_airport.utils as utils


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid_uuid1', 'airport_queue_test_allow_tag'),
        ('dbid_uuid', 'dbid_uuid2', 'airport_queue_test_allow_tag'),
        ('dbid_uuid', 'dbid_uuid3', 'airport_queue_test_allow_tag'),
        ('dbid_uuid', 'dbid_uuid3', 'airport_queue_test_deny_tag'),
    ],
    topic_relations=[
        ('airport_queue', 'airport_queue_test_allow_tag'),
        ('airport_queue', 'airport_queue_test_deny_tag'),
    ],
)
@pytest.mark.parametrize(
    'airport_tags_key', ['ekb', '__default__', 'other_airport'],
)
async def test_tags_queuing(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        pgsql,
        mockserver,
        now,
        taxi_config,
        mode,
        airport_tags_key,
):
    old_mode_enabled = utils.get_old_mode_enabled(mode)

    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint('tags-queuing-finished')
    def tags_queuing_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        assert len(request.json['driver_ids']) == 7
        assert request.json['zone_id'] == 'ekb_home_zone'
        return utils.generate_candidates_response(
            request.json['driver_ids'], ['comfortplus', 'econom'],
        )

    @mockserver.json_handler(
        '/driver-categories-api/v2/aggregation/categories',
    )
    def _driver_categories(request):
        assert len(request.json['drivers']) == 7
        return utils.generate_categories_response(
            [driver['driver_id'] for driver in request.json['drivers']],
            ['comfortplus', 'econom'],
        )

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        if mode == 'new':
            if airport_tags_key == 'other_airport':
                append = request.json['append'][0]
                assert 'remove' not in request.json
                utils.check_airport_tags(
                    append,
                    expected_queued=(),
                    expected_entered=('dbid_uuid6', 'dbid_uuid7'),
                )
            else:
                append = request.json['append'][0]
                remove = request.json['remove'][0]
                utils.check_airport_tags(
                    remove,
                    expected_queued=(),
                    expected_entered=('dbid_uuid6',),
                )
                utils.check_airport_tags(
                    append,
                    expected_queued=('dbid_uuid1', 'dbid_uuid6'),
                    expected_entered=('dbid_uuid2', 'dbid_uuid7'),
                )

        return {}

    tags_queuing_config_value = {'__default__': {'allow': []}}
    tags_queuing_config_value.update(
        {
            airport_tags_key: {
                'allow': ['airport_queue_test_allow_tag'],
                'deny': ['airport_queue_test_deny_tag'],
            },
        },
    )

    custom_config = utils.custom_config(old_mode_enabled=old_mode_enabled)
    custom_config.update(
        {'DISPATCH_AIRPORT_TAGS_QUEUING': tags_queuing_config_value},
    )
    taxi_config.set_values(custom_config)
    utils.set_mode_in_config(taxi_config, mode)

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - driver with allow tag in waiting area
    # dbid_uuid2 - driver with allow tag in notification area
    # dbid_uuid3 - driver with allow and deny tags in waiting area
    # dbid_uuid4 - driver w/o allow tags in waiting area
    # dbid_uuid5 - driver w/o allow tags, but with deny tags in waiting area
    # dbid_uuid6 - stored entered driver with tag reason
    # dbid_uuid7 - stored entered driver with on_action reason

    # avoid couple seconds diff test flaps when compare pg and geobus ts
    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid1': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid2': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid3': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid4': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid5': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid6': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
        },
        'dbid_uuid7': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now)
    await merge_finished.wait_call()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    response = (await tags_queuing_finished.wait_call())['data']
    can_be_queued_by_tag = airport_tags_key != 'other_airport'
    updated_etalons = {
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': (
                utils.State.kQueued
                if can_be_queued_by_tag
                else utils.State.kEntered
            ),
            'reason': utils.Reason.kOnTag if can_be_queued_by_tag else '',
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
        },
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnTag if can_be_queued_by_tag else '',
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [2],
            'classes': ['comfortplus', 'econom'],
        },
        'dbid_uuid3': {
            'driver_id': 'dbid_uuid3',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
        },
        'dbid_uuid4': {
            'driver_id': 'dbid_uuid4',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
        },
        'dbid_uuid5': {
            'driver_id': 'dbid_uuid5',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
        },
        'dbid_uuid6': {
            'driver_id': 'dbid_uuid6',
            'state': (
                utils.State.kQueued
                if can_be_queued_by_tag
                else utils.State.kEntered
            ),
            'reason': utils.Reason.kOnTag,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
        },
        'dbid_uuid7': {
            'driver_id': 'dbid_uuid7',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOnAction,
            'airport': 'ekb',
            'old_mode_enabled': old_mode_enabled,
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
        },
    }
    assert len(response) == len(updated_etalons)
    for driver in response:
        etalon = updated_etalons[driver['driver_id']]
        utils.check_drivers(driver, etalon)

    if can_be_queued_by_tag:
        await _tags.wait_call()
    elif airport_tags_key == 'other_airport':
        await _tags.wait_call()
    else:
        assert _tags.times_called == 0
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    db = pgsql['dispatch_airport']
    drivers = utils.get_drivers_queue(db)
    assert drivers == [
        'dbid_uuid1',
        'dbid_uuid2',
        'dbid_uuid3',
        'dbid_uuid4',
        'dbid_uuid5',
        'dbid_uuid6',
        'dbid_uuid7',
    ]
    if mode == 'old':
        assert not utils.get_driver_events(db)
    else:
        assert utils.get_driver_events(db) == {
            ('udid7', 'session_id_7', 'entered_on_order'): {
                'airport_id': 'ekb',
                'driver_id': 'dbid_uuid7',
            },
        }
    # queue on old_mode drivers in waiting area
    for driver_id in ['dbid_uuid1', 'dbid_uuid3', 'dbid_uuid4', 'dbid_uuid5']:
        updated_etalons[driver_id]['state'] = utils.State.kQueued
    utils.update_etalons_by_simulation_old_queue_filter_processing(
        updated_etalons, mode,
    )
    utils.check_drivers_queue(db, updated_etalons.values())


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tags_v2_index(
    tags_list=[('dbid_uuid', 'dbid_uuid1', 'airport_queue_test_allow_tag')],
    topic_relations=[('airport_queue', 'airport_queue_test_allow_tag')],
)
@pytest.mark.config(
    DISPATCH_AIRPORT_TAGS_QUEUING={
        'ekb': {'allow': ['airport_queue_test_allow_tag']},
    },
)
async def test_tags_queuing_with_non_airport_reposition(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        pgsql,
        mockserver,
        now,
        taxi_config,
):
    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
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
        utils.check_airport_tags(append, ('dbid_uuid1',))

        return {}

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

    custom_config = utils.custom_config(old_mode_enabled=False)
    taxi_config.set_values(custom_config)

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - driver with allow tag in waiting area
    # dbid_uuid2 - driver without allowed tag, is filtered by reposition

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

    response = (await reposition_filter_finished.wait_call())['data']
    updated_etalons = {
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnTag,
            'airport': 'ekb',
            'old_mode_enabled': False,
            'areas': [1, 2],
            'classes': [],
        },
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kNonAirportReposition,
            'airport': 'ekb',
            'old_mode_enabled': False,
            'areas': [1, 2],
            'classes': [],
        },
    }
    utils.check_filter_result(response, updated_etalons)

    await _tags.wait_call()
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    db = pgsql['dispatch_airport']
    drivers = utils.get_drivers_queue(db)
    assert drivers == ['dbid_uuid1', 'dbid_uuid2']
    assert not utils.get_driver_events(db)


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid_uuid1', 'airport_queue_test_allow_tag'),
        ('dbid_uuid', 'dbid_uuid2', 'airport_queue_test_allow_tag'),
    ],
    topic_relations=[('airport_queue', 'airport_queue_test_allow_tag')],
)
@pytest.mark.config(
    DISPATCH_AIRPORT_TAGS_QUEUING={
        'ekb': {'allow': ['airport_queue_test_allow_tag']},
    },
)
@pytest.mark.busy_drivers(
    busy_drivers=[
        {
            'driver_id': 'dbid_uuid1',
            'order_id': 'order_id_1',
            'taxi_status': 3,
            'final_destination': {'lat': 1.0, 'lon': 1.0},
        },
        {
            'driver_id': 'dbid_uuid2',
            'order_id': 'order_id_2',
            'taxi_status': 3,
            'final_destination': {'lat': 11.0, 'lon': 21.0},
        },
        {
            'driver_id': 'dbid_uuid3',
            'order_id': 'order_id_3',
            'taxi_status': 3,
            'final_destination': {'lat': 1.0, 'lon': 1.0},
        },
    ],
)
async def test_tags_queuing_with_non_airport_order(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        pgsql,
        mockserver,
        now,
        taxi_config,
        order_archive_mock,
):
    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint('orders-filter-finished')
    def orders_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        append = request.json['append'][0]
        assert 'remove' not in request.json
        utils.check_airport_tags(append, ('dbid_uuid1', 'dbid_uuid2'))

        return {}

    # retrieve setup
    order_archive_mock.set_order_proc([])

    custom_config = utils.custom_config(old_mode_enabled=False)
    taxi_config.set_values(custom_config)

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - driver with allow tag and non airport order in waiting area
    # dbid_uuid2 - driver with allow tag and airport order in waiting area
    # dbid_uuid3 - driver without allowed tag, filtered by non airport order

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
        'dbid_uuid3': {
            'position': utils.WAITING_POSITION,
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now)
    await merge_finished.wait_call()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    response = (await orders_filter_finished.wait_call())['data']
    updated_etalons = {
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnTag,
            'airport': 'ekb',
            'old_mode_enabled': False,
            'areas': [1, 2],
            'classes': [],
            'input_order_id': 'order_id_1',
        },
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOnTag,
            'airport': 'ekb',
            'old_mode_enabled': False,
            'areas': [1, 2],
            'classes': [],
            'input_order_id': 'order_id_2',
        },
        'dbid_uuid3': {
            'driver_id': 'dbid_uuid3',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kNotAirportInputOrder,
            'airport': 'ekb',
            'old_mode_enabled': False,
            'areas': [1, 2],
            'classes': [],
            'input_order_id': 'order_id_3',
        },
    }
    utils.check_filter_result(response, updated_etalons)

    await _tags.wait_call()
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    db = pgsql['dispatch_airport']
    drivers = utils.get_drivers_queue(db)
    assert drivers == ['dbid_uuid1', 'dbid_uuid2', 'dbid_uuid3']
    assert not utils.get_driver_events(db)
