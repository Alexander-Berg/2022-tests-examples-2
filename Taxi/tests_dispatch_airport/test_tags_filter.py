import datetime

import pytest

import tests_dispatch_airport.utils as utils


TAGS_FILTER_NAME = 'tags-filter'


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid_uuid1', 'airport_queue_blacklist_driver'),
        ('dbid_uuid', 'dbid_uuid2', 'airport_queue_kick_driver_cancel'),
        ('dbid_uuid', 'dbid_uuid4', 'airport_queue_kick_user_cancel'),
        ('dbid_uuid', 'dbid_uuid5', 'airport_queue_fraud_detected'),
        ('dbid_uuid', 'dbid_uuid6', 'airport_queue_fraud_detected_short'),
        ('dbid_uuid', 'dbid_uuid7', 'airport_queue_fraud_detected_long'),
        ('dbid_uuid', 'dbid_uuid8', 'airport_queue_fraud_detected_wrong'),
    ],
    topic_relations=[
        ('airport_queue', 'airport_queue_blacklist_driver'),
        ('airport_queue', 'airport_queue_kick_driver_cancel'),
        ('airport_queue', 'airport_queue_kick_user_cancel'),
        ('airport_queue', 'airport_queue_fraud_detected'),
        ('airport_queue', 'airport_queue_fraud_detected_short'),
        ('airport_queue', 'airport_queue_fraud_detected_long'),
        ('airport_queue', 'airport_queue_fraud_detected_wrong'),
    ],
)
async def test_tags_filter(
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

    @testpoint(TAGS_FILTER_NAME + '-finished')
    def tags_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        append = request.json['append'][0]
        remove = request.json['remove'][0]
        utils.check_airport_tags(append, ('dbid_uuid3',), ('dbid_uuid8',))
        utils.check_airport_tags(
            remove,
            ('dbid_uuid2', 'dbid_uuid4', 'dbid_uuid7'),
            ('dbid_uuid6',),
        )
        return {}

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - new driver:            blacklisted
    # dbid_uuid2 - stored queued driver:  kick driver cancel
    # dbid_uuid3 - stored queued driver
    # dbid_uuid4 - stored queued driver:  kick user cancel
    # dbid_uuid5 - new driver:            anti fraud tag
    # dbid_uuid6 - entered driver:        anti fraud tag short
    # dbid_uuid7 - queued driver:         anti fraud tag long
    # dbid_uuid8 - entered driver:        wrong anti fraud tag (not in config)

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
        'dbid_uuid5': {
            'position': utils.NOTIFICATION_POSITION,
            'timestamp': geobus_now,
        },
    }
    utils.publish_positions(redis_store, geobus_drivers, now)
    await merge_finished.wait_call()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    # tags-filter check
    response = (await tags_filter_finished.wait_call())['data']
    updated_etalons = {
        'dbid_uuid1': {
            'driver_id': 'dbid_uuid1',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kBlacklist,
            'airport': 'ekb',
            'areas': [2],
            'classes': [],
        },
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kDriverCancel,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['econom'],
        },
        'dbid_uuid3': {
            'driver_id': 'dbid_uuid3',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['econom'],
        },
        'dbid_uuid4': {
            'driver_id': 'dbid_uuid4',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kUserCancel,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['econom'],
        },
        'dbid_uuid5': {
            'driver_id': 'dbid_uuid5',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kAntiFraudTag,
            'airport': 'ekb',
            'areas': [2],
            'classes': [],
        },
        'dbid_uuid6': {
            'driver_id': 'dbid_uuid6',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kAntiFraudTag,
            'airport': 'ekb',
            'areas': [2],
            'classes': ['econom'],
        },
        'dbid_uuid7': {
            'driver_id': 'dbid_uuid7',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kAntiFraudTag,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['econom'],
        },
        'dbid_uuid8': {
            'driver_id': 'dbid_uuid8',
            'state': utils.State.kEntered,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [2],
            'classes': ['econom'],
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
        'dbid_uuid8',
    ]
    assert not utils.get_driver_events(db)
