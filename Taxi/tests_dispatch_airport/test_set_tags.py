import pytest

import tests_dispatch_airport.utils as utils


@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.pgsql('dispatch_airport', files=['drivers_queue.sql'])
@pytest.mark.config(
    DISPATCH_AIRPORT_DRIVER_TAG_TIMINGS={
        'airport_tag_ttl': 240,
        'time_remaining_to_update': 10,
    },
)
async def test_tags_set(
        taxi_dispatch_airport,
        redis_store,
        testpoint,
        mocked_time,
        mockserver,
        taxi_config,
):
    @testpoint(utils.POS_PROCESSOR_NAME + '-merge-finished')
    def merge_finished(data):
        return data

    @testpoint(utils.QUEUE_UPDATER_NAME + '-finished')
    def queue_update_finished(_):
        pass

    custom_config = utils.custom_config(old_mode_enabled=True)
    taxi_config.set_values(custom_config)

    await taxi_dispatch_airport.invalidate_caches()
    await taxi_dispatch_airport.enable_testpoints()

    # check follow driver categories:
    # dbid_uuid1 - new driver in waiting area
    # dbid_uuid2 - new driver in notification area
    # dbid_uuid3 - existing entered driver in waiting area
    # dbid_uuid4 - existing entered driver in notification area
    # dbid_uuid5 - existing queued driver in waiting area
    # dbid_uuid6 - existing queued driver in outside area
    # dbid_uuid7 - existing entered driver in outside area

    async def publish_positions():
        geobus_now = mocked_time.now()
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
                'position': utils.NOTIFICATION_POSITION,
                'timestamp': geobus_now,
            },
            'dbid_uuid5': {
                'position': utils.WAITING_POSITION,
                'timestamp': geobus_now,
            },
            'dbid_uuid6': {
                'position': utils.OUT_POSITION,
                'timestamp': geobus_now,
            },
            'dbid_uuid7': {
                'position': utils.OUT_POSITION,
                'timestamp': geobus_now,
            },
        }
        utils.publish_positions(redis_store, geobus_drivers, geobus_now)
        await merge_finished.wait_call()

    # iteration 1
    # avoid couple seconds diff test flaps when compare pg and geobus ts
    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        append = request.json['append'][0]
        remove = request.json['remove'][0]
        utils.check_airport_tags(
            append,
            expected_queued=(
                'dbid_uuid1',
                'dbid_uuid3',
                'dbid_uuid5',
                'dbid_uuid6',
            ),
            expected_entered=('dbid_uuid2', 'dbid_uuid4'),
        )

        utils.check_airport_tags(
            remove,
            expected_queued=(),
            expected_entered=('dbid_uuid3', 'dbid_uuid7'),
        )

        return {}

    mocked_time.sleep(120)
    await publish_positions()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    await _tags.wait_call()
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    # iteration 2 - airport_tag_ttl didn't pass
    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        assert 'append' not in request.json
        remove = request.json['remove'][0]
        utils.check_airport_tags(
            remove,
            # dbid_uuid6 filtered by leave queue timeout
            expected_queued=('dbid_uuid6',),
            expected_entered=(),
        )

        return {}

    await taxi_dispatch_airport.invalidate_caches()
    mocked_time.sleep(120)
    await publish_positions()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    await _tags.wait_call()
    await utils.wait_certain_testpoint('ekb', queue_update_finished)

    # iteration 3 - airport_tag_ttl passed
    @mockserver.json_handler('/tags/v2/upload')
    def _tags(request):
        append = request.json['append'][0]
        assert 'remove' not in request.json
        utils.check_airport_tags(
            append,
            expected_queued=('dbid_uuid1', 'dbid_uuid3', 'dbid_uuid5'),
            expected_entered=('dbid_uuid2', 'dbid_uuid4'),
        )

        return {}

    await taxi_dispatch_airport.invalidate_caches()
    mocked_time.sleep(120)
    await publish_positions()

    await taxi_dispatch_airport.run_task('distlock/queue-update-scheduler-ekb')

    await _tags.wait_call()
    await utils.wait_certain_testpoint('ekb', queue_update_finished)
