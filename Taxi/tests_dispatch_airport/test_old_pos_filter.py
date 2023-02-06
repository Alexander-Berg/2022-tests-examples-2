import datetime

import pytest

import tests_dispatch_airport.utils as utils


OLD_POS_FILTER_NAME = 'old-pos-filter'


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
async def test_old_pos_filter(
        taxi_dispatch_airport, redis_store, testpoint, pgsql, mockserver, now,
):
    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(OLD_POS_FILTER_NAME + '-finished')
    def old_pos_filter_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        append = request.json['append'][0]
        remove = request.json['remove'][0]

        utils.check_airport_tags(
            append, ('dbid_uuid4', 'dbid_uuid6'), ('dbid_uuid2',),
        )
        utils.check_airport_tags(remove, ('dbid_uuid3', 'dbid_uuid5'))

        return {}

    @mockserver.json_handler('/driver-metrics-storage/v1/event/new/bulk')
    def _driver_metrics_storage(request):
        drivers = set()
        tokens = set()
        for event in request.json['events']:
            drivers.add(event['park_driver_profile_id'])
            tokens.add(event['idempotency_token'])

        assert drivers == set({'dbid_uuid3', 'dbid_uuid5', 'dbid_uuid6'})
        return {'events': [{'idempotency_token': token} for token in tokens]}

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - new driver: not airport areas
    # dbid_uuid2 - new driver: notification zone
    # dbid_uuid3 - stored queued driver: ttl outdated
    # dbid_uuid4 - stored queued driver
    # dbid_uuid5 - stored outdated queued driver
    # dbid_uuid6 - stored queued driver

    # avoid couple seconds diff test flaps when compare pg and geobus ts
    geobus_now = now + datetime.timedelta(minutes=2)
    geobus_drivers = {
        'dbid_uuid1': {
            'position': utils.OUT_POSITION,
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

    # old-pos-filter check
    response = (await old_pos_filter_finished.wait_call())['data']
    updated_etalon = {
        'dbid_uuid2': {
            'driver_id': 'dbid_uuid2',
            'state': utils.State.kEntered,
            'reason': '',
            'airport': 'ekb',
            'areas': [2],
            'classes': [],
        },
        'dbid_uuid3': {
            'driver_id': 'dbid_uuid3',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kQueuedGps,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['business', 'comfortplus'],
        },
        'dbid_uuid4': {
            'driver_id': 'dbid_uuid4',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['econom'],
        },
        'dbid_uuid5': {
            'driver_id': 'dbid_uuid5',
            'state': utils.State.kFiltered,
            'reason': utils.Reason.kMaxQueueTimeExceed,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['comfortplus', 'econom'],
        },
        'dbid_uuid6': {
            'driver_id': 'dbid_uuid6',
            'state': utils.State.kQueued,
            'reason': utils.Reason.kOldMode,
            'airport': 'ekb',
            'areas': [1, 2],
            'classes': ['econom'],
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
        'dbid_uuid2',
        'dbid_uuid3',
        'dbid_uuid4',
        'dbid_uuid5',
        'dbid_uuid6',
    ]

    cursor = db.cursor()
    cursor.execute(
        """
        SELECT driver_id, details
        FROM dispatch_airport.drivers_queue
        WHERE driver_id in (\'dbid_uuid3\', \'dbid_uuid5\', \'dbid_uuid6\');
    """,
    )
    for row in cursor:
        if row[0] in ('dbid_uuid3', 'dbid_uuid5'):
            assert row[1]['dms_kicked_sent']
        else:
            assert row[1]['dms_queued_sent']
    assert not utils.get_driver_events(db)
