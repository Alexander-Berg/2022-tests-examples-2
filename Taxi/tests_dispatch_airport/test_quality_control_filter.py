import datetime

import pytest

import tests_dispatch_airport.utils as utils


QUALITY_CONTROL_FILTER_NAME = 'quality-control-filter'


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
async def test_quality_control_filter(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        pgsql,
        mockserver,
        now,
        taxi_config,
):
    zones_config = taxi_config.get('DISPATCH_AIRPORT_ZONES')
    zones_config['ekb']['qc_check_allowed'] = True
    taxi_config.set_values(zones_config)

    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(QUALITY_CONTROL_FILTER_NAME + '-finished')
    def quality_control_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    @mockserver.json_handler('/candidates/satisfy')
    def _satisfy(request):
        assert request.json['zone_id'] == 'ekb_home_zone'
        return {
            'drivers': [
                {
                    'dbid': 'dbid',
                    'uuid': 'uuid3',
                    'details': {'some_filter': ['some_value']},
                },
                {
                    'dbid': 'dbid',
                    'uuid': 'uuid4',
                    'details': {'partners/qc_block': ['any blocking reason']},
                },
                {
                    'dbid': 'dbid',
                    'uuid': 'uuid5',
                    'details': {'partners/qc_block': []},
                },
                {
                    'dbid': 'dbid',
                    'uuid': 'uuid6',
                    'details': {'partners/qc_block': ['any blocking reason']},
                },
                {
                    'dbid': 'dbid',
                    'uuid': 'uuid7',
                    'details': {'partners/qc_block': ['any blocking reason']},
                },
            ],
        }

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - new driver:           notification zone
    # dbid_uuid2 - new driver:           waiting zone
    # dbid_uuid3 - stored queued driver: unblocked -> unblocked (qc missed)
    # dbid_uuid4 - stored queued driver: unblocked -> blocked
    # dbid_uuid5 - stored queued driver: blocked -> unblocked (qc empty)
    # dbid_uuid6 - stored queued driver: blocked -> blocked (not filtered)
    # dbid_uuid7 - stored queued driver: blocked -> blocked (filtered)

    # avoid couple seconds diff test flaps when compare pg and geobus ts
    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid1': {
            'position': utils.NOTIFICATION_POSITION,
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

    response = (await quality_control_filter_finished.wait_call())['data']
    updated_etalons = {
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'areas': [2],
            'classes': [],
            'last_freeze_started_tp': False,
        },
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': [],
            'last_freeze_started_tp': False,
        },
        'dbid_uuid3': {
            'driver_id': 'dbid_uuid3',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['econom'],
            'last_freeze_started_tp': False,
        },
        'dbid_uuid4': {
            'driver_id': 'dbid_uuid4',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['econom'],
            'last_freeze_started_tp': True,
        },
        'dbid_uuid5': {
            'driver_id': 'dbid_uuid5',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['econom'],
            'last_freeze_started_tp': False,
        },
        'dbid_uuid6': {
            'driver_id': 'dbid_uuid6',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['econom'],
            'last_freeze_started_tp': True,
        },
        'dbid_uuid7': {
            'driver_id': 'dbid_uuid7',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kFreezeExpired,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['econom'],
            'last_freeze_started_tp': True,
        },
    }
    assert len(response) == len(updated_etalons)
    for driver in response:
        etalon = updated_etalons[driver['driver_id']]
        utils.check_drivers(driver, etalon)

    await _tags.wait_call()
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
    assert not utils.get_driver_events(db)


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue_two_classes.sql'])
@pytest.mark.parametrize(
    'freezed_uuid1_classes',
    [None, {'econom'}, {'comfortplus'}, {'comfortplus', 'econom'}],
)
async def test_quality_control_several_classes(
        taxi_dispatch_airport,
        testpoint,
        pgsql,
        mockserver,
        taxi_config,
        freezed_uuid1_classes,
):
    zones_config = taxi_config.get('DISPATCH_AIRPORT_ZONES')
    zones_config['ekb']['qc_check_allowed'] = True
    taxi_config.set_values(zones_config)

    @testpoint(QUALITY_CONTROL_FILTER_NAME + '-finished')
    def quality_control_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    @mockserver.json_handler('/candidates/satisfy')
    def _satisfy(request):
        assert request.json['zone_id'] == 'ekb_home_zone'
        block_detail = {'partners/qc_block': ['any blocking reason']}
        econom_resp = {
            'drivers': [
                {'dbid': 'dbid', 'uuid': 'uuid1', 'details': {}},
                {
                    'dbid': 'dbid',
                    'uuid': 'uuid2',
                    'details': {'some_filter': ['some_value']},
                },
            ],
        }
        comfortplus_resp = {
            'drivers': [{'dbid': 'dbid', 'uuid': 'uuid1', 'details': {}}],
        }

        if freezed_uuid1_classes == {'econom'}:
            econom_resp['drivers'][0]['details'] = block_detail
        if freezed_uuid1_classes == {'comfortplus'}:
            comfortplus_resp['drivers'][0]['details'] = block_detail
        if freezed_uuid1_classes == {'comfortplus', 'econom'}:
            econom_resp['drivers'][0]['details'] = block_detail
            comfortplus_resp['drivers'][0]['details'] = block_detail

        if 'econom' in request.json['allowed_classes']:
            return econom_resp
        return comfortplus_resp

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow drivers:
    # dbid_uuid1 - stored queued driver:
    # unblocked -> if freezed_uuid1_classes is not None blocked else unblocked
    # dbid_uuid2 - stored queued driver: unblocked -> unblocked
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    response = (await quality_control_filter_finished.wait_call())['data']
    updated_etalons = {
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [0, 1],
            'classes': ['comfortplus', 'econom'],
            'last_freeze_started_tp': bool(freezed_uuid1_classes),
        },
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [0, 1],
            'classes': ['econom'],
            'last_freeze_started_tp': False,
        },
    }
    assert len(response) == len(updated_etalons)
    for driver in response:
        etalon = updated_etalons[driver['driver_id']]
        utils.check_drivers(driver, etalon)

    await _tags.wait_call()
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    db = pgsql['dispatch_airport']
    drivers = utils.get_drivers_queue(db)
    assert drivers == ['dbid_uuid1', 'dbid_uuid2']
    assert not utils.get_driver_events(db)


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue_timeout.sql'])
async def test_quality_control_timeout(
        taxi_dispatch_airport, testpoint, pgsql, mockserver, taxi_config,
):
    zones_config = taxi_config.get('DISPATCH_AIRPORT_ZONES')
    zones_config['ekb']['qc_check_allowed'] = True
    taxi_config.set_values(zones_config)

    @testpoint(QUALITY_CONTROL_FILTER_NAME + '-finished')
    def quality_control_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        return {}

    @mockserver.json_handler('/candidates/satisfy')
    def _satisfy(request):
        assert request.json['zone_id'] == 'ekb_home_zone'
        if 'comfortplus' in request.json['allowed_classes']:
            raise mockserver.TimeoutError()
        return {
            'drivers': [
                {
                    'dbid': 'dbid',
                    'uuid': 'uuid1',
                    'details': {'some_filter': ['some_value']},
                },
            ],
        }

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow drivers:
    # dbid_uuid1 - stored queued driver blocked -> blocked because of timeout
    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    response = (await quality_control_filter_finished.wait_call())['data']
    updated_etalons = {
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [0, 1],
            'classes': ['comfortplus', 'econom'],
            'last_freeze_started_tp': True,
        },
    }
    assert len(response) == len(updated_etalons)
    for driver in response:
        etalon = updated_etalons[driver['driver_id']]
        utils.check_drivers(driver, etalon)

    await _tags.wait_call()
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    db = pgsql['dispatch_airport']
    drivers = utils.get_drivers_queue(db)
    assert drivers == ['dbid_uuid1']
    assert not utils.get_driver_events(db)
