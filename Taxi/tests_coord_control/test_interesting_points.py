# pylint: disable=import-error

import datetime

import pytest

from geobus_tools import geobus  # noqa: F401 C5521

PERFORMER_FROM_PUBSUB_NAME = 'performer-from-pubsub-received'
CHANNEL_NAME = 'channel:yagr:signal_v2'
STORE_INTERESTING_POINTS_NAME = 'stored-interesting-points'
BAD_AREA_DETECTION_NAME = 'bad-area-detection'
INTERESTING_POINTS_REMOVED_NAME = 'interesting-points-removed'
SAVED_STRATEGIES_NAME = 'saved-strategies'
PERFORMERS_TO_CALCULATE_NAME = 'performers-to-calculate'


async def _publish_message(
        message, redis_store, performer_from_pubsub_received,
):
    fbs_message = geobus.serialize_signal_v2(message, datetime.datetime.now())
    redis_store.publish(CHANNEL_NAME, fbs_message)
    if performer_from_pubsub_received:
        assert (await performer_from_pubsub_received.wait_call())[
            'data'
        ] == message[0]['driver_id']


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.now('2020-04-21T12:16:50.123456+0000')
@pytest.mark.suspend_periodic_tasks('bad_areas_detector')
@pytest.mark.config(
    COORD_CONTROL_INTERESTING_POINTS_SETTINGS={
        'radius': 200,
        'points_ttl': 120,
        'detector_batch_size': 1,
        'cleanup_batch_size': 2,
        'minimum_points_for_detection': 1,
        'points_weight_threshold_log': 0,
        'points_weight_threshold_applied': 2,
    },
)
async def test_interesting_points_base(
        taxi_coord_control, redis_store, load_json, testpoint,
):
    @testpoint(PERFORMER_FROM_PUBSUB_NAME)
    def performer_from_pubsub_received(data):
        return data

    @testpoint(STORE_INTERESTING_POINTS_NAME)
    def store_interesting_points(data):
        return data

    @testpoint(BAD_AREA_DETECTION_NAME)
    def bad_zones_detector(data):
        return data

    await taxi_coord_control.enable_testpoints()

    messages = load_json('geobus_messages.json')

    await _publish_message(
        messages[:4], redis_store, performer_from_pubsub_received,
    )

    await _publish_message(
        messages[4:], redis_store, performer_from_pubsub_received,
    )

    assert (await store_interesting_points.wait_call())['data'] == 2

    await taxi_coord_control.run_periodic_task('bad_areas_detector')

    detected_bad_zones = (await bad_zones_detector.wait_call())['data']
    assert detected_bad_zones == {
        'performer_id': 'dbid_uuid',
        'weight': 2.0,
        'fetched_points': 2,
        'detected_bad_area_log': True,
        'detected_bad_area_applied': False,
    }


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.now('2020-04-21T12:16:50.123456+0000')
@pytest.mark.suspend_periodic_tasks('bad_areas_detector')
@pytest.mark.config(
    COORD_CONTROL_INTERESTING_POINTS_SETTINGS={
        'radius': 200,
        'points_ttl': 120,
        'detector_batch_size': 1,
        'cleanup_batch_size': 2,
        'minimum_points_for_detection': 1,
        'minimum_performers_for_detection': 2,
        'points_weight_threshold_log': 0,
        'points_weight_threshold_applied': 2,
    },
)
async def test_interesting_points_min_performers(
        taxi_coord_control, redis_store, load_json, testpoint,
):
    @testpoint(PERFORMER_FROM_PUBSUB_NAME)
    def performer_from_pubsub_received(data):
        return data

    @testpoint(STORE_INTERESTING_POINTS_NAME)
    def store_interesting_points(data):
        return data

    @testpoint(BAD_AREA_DETECTION_NAME)
    def bad_zones_detector(data):
        return data

    await taxi_coord_control.enable_testpoints()

    messages = load_json('geobus_messages.json')

    await _publish_message(
        messages[:4], redis_store, performer_from_pubsub_received,
    )

    await _publish_message(
        messages[4:], redis_store, performer_from_pubsub_received,
    )

    assert (await store_interesting_points.wait_call())['data'] == 2

    await taxi_coord_control.run_periodic_task('bad_areas_detector')

    detected_bad_zones = (await bad_zones_detector.wait_call())['data']
    assert detected_bad_zones == {
        'performer_id': 'dbid_uuid',
        'weight': 2.0,
        'fetched_points': 2,
        'detected_bad_area_log': False,
        'detected_bad_area_applied': False,
    }


# Distance between performers ~ 1.25 km
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.now('2020-04-21T12:16:50.123456+0000')
@pytest.mark.suspend_periodic_tasks('bad_areas_detector')
@pytest.mark.parametrize(
    'radius,'
    'minimum_points_for_detection,'
    'points_weight_threshold_log,'
    'points_weight_threshold_applied,'
    'target_weight,'
    'fetched_points,'
    'is_logged_by_loggable_weight,'
    'is_logged_by_applied_weight',
    [
        (2000, 1, 0, 2, 2.0, 4, True, False),
        (120, 1, 0, 2, 2.0, 2, True, False),
        (120, 10, 0, 2, 2.0, 2, False, False),
        (120, 1, 0, 0, 2.0, 2, True, True),
    ],
)
async def test_interesting_points_bad_areas(
        taxi_coord_control,
        taxi_config,
        redis_store,
        load_json,
        testpoint,
        radius,
        minimum_points_for_detection,
        points_weight_threshold_log,
        points_weight_threshold_applied,
        target_weight,
        fetched_points,
        is_logged_by_loggable_weight,
        is_logged_by_applied_weight,
):
    @testpoint(PERFORMER_FROM_PUBSUB_NAME)
    def performer_from_pubsub_received(data):
        return data

    @testpoint(STORE_INTERESTING_POINTS_NAME)
    def store_interesting_points(data):
        return data

    @testpoint(BAD_AREA_DETECTION_NAME)
    def bad_zones_detector(data):
        return data

    taxi_config.set_values(
        dict(
            COORD_CONTROL_INTERESTING_POINTS_SETTINGS={
                'radius': radius,
                'points_ttl': 120,
                'detector_batch_size': 1,
                'cleanup_batch_size': 2,
                'minimum_points_for_detection': minimum_points_for_detection,
                'points_weight_threshold_log': points_weight_threshold_log,
                'points_weight_threshold_applied': (
                    points_weight_threshold_applied
                ),
            },
        ),
    )
    await taxi_coord_control.invalidate_caches()

    await taxi_coord_control.enable_testpoints()

    messages = load_json('geobus_messages_bad_areas.json')

    await _publish_message(
        messages[:4], redis_store, performer_from_pubsub_received,
    )
    await _publish_message(
        messages[4:8], redis_store, performer_from_pubsub_received,
    )

    await _publish_message(
        messages[8:10], redis_store, performer_from_pubsub_received,
    )
    await _publish_message(
        messages[10:], redis_store, performer_from_pubsub_received,
    )

    assert (await store_interesting_points.wait_call())['data'] == 2

    await taxi_coord_control.run_periodic_task('bad_areas_detector')

    detected_bad_zones = (await bad_zones_detector.wait_call())['data']
    assert detected_bad_zones['weight'] == target_weight
    assert detected_bad_zones['fetched_points'] == fetched_points
    assert (
        detected_bad_zones['detected_bad_area_log']
        == is_logged_by_loggable_weight
    )
    assert (
        detected_bad_zones['detected_bad_area_applied']
        == is_logged_by_applied_weight
    )


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.now('2020-04-21T12:16:50.123456+0000')
@pytest.mark.suspend_periodic_tasks('bad_areas_detector', 'Cleaner')
@pytest.mark.config(
    COORD_CONTROL_INTERESTING_POINTS_SETTINGS={
        'radius': 200,
        'points_ttl': 120,
        'detector_batch_size': 1,
        'cleanup_batch_size': 2,
        'minimum_points_for_detection': 1,
        'points_weight_threshold_log': 0,
        'points_weight_threshold_applied': 2,
    },
)
async def test_interesting_points_cleanup(
        taxi_coord_control, redis_store, load_json, testpoint, mocked_time,
):
    await taxi_coord_control.tests_control(invalidate_caches=False)

    @testpoint(PERFORMER_FROM_PUBSUB_NAME)
    def performer_from_pubsub_received(data):
        return data

    @testpoint(STORE_INTERESTING_POINTS_NAME)
    def store_interesting_points(data):
        return data

    @testpoint(INTERESTING_POINTS_REMOVED_NAME)
    def interesting_points_removed(data):
        return data

    await taxi_coord_control.enable_testpoints()

    messages = load_json('geobus_messages.json')

    await _publish_message(
        messages[:4], redis_store, performer_from_pubsub_received,
    )

    await _publish_message(
        messages[4:], redis_store, performer_from_pubsub_received,
    )

    assert (await store_interesting_points.wait_call())['data'] == 2

    mocked_time.set(mocked_time.now() + datetime.timedelta(minutes=10))
    await taxi_coord_control.tests_control(invalidate_caches=False)
    await taxi_coord_control.run_periodic_task('Cleaner')

    assert (await interesting_points_removed.wait_call())['data'] == 2


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.now('2020-04-21T12:16:50.123456+0000')
@pytest.mark.suspend_periodic_tasks('bad_areas_detector')
@pytest.mark.config(
    COORD_CONTROL_INTERESTING_POINTS_SETTINGS={
        'radius': 200,
        'points_ttl': 120,
        'cleanup_batch_size': 2,
        'detector_batch_size': 1,
        'minimum_points_for_detection': 1,
        'points_weight_threshold_log': 0,
        'points_weight_threshold_applied': 1,
    },
)
async def test_interesting_points_empty_strategy(
        taxi_coord_control, redis_store, load_json, testpoint,
):
    @testpoint(PERFORMER_FROM_PUBSUB_NAME)
    def performer_from_pubsub_received(data):
        return data

    @testpoint(STORE_INTERESTING_POINTS_NAME)
    def store_interesting_points(data):
        return data

    @testpoint(BAD_AREA_DETECTION_NAME)
    def bad_zones_detector(data):
        return data

    await taxi_coord_control.enable_testpoints()

    messages = load_json('geobus_messages_empty_strategy.json')

    await _publish_message(
        messages[:4], redis_store, performer_from_pubsub_received,
    )

    response = await taxi_coord_control.get(
        'location_settings',
        params={
            'driver_profile_id': 'uuid',
            'park_db_id': 'dbid',
            'taximeter_agent_info': 'Taximeter-BETA 9.33 (1234)',
        },
    )
    assert response.status_code == 404
    await performer_from_pubsub_received.wait_call()

    await _publish_message(
        messages[4:6], redis_store, performer_from_pubsub_received,
    )

    assert (await store_interesting_points.wait_call())['data'] == 2

    await taxi_coord_control.run_periodic_task('bad_areas_detector')

    detected_bad_zones = (await bad_zones_detector.wait_call())['data']
    assert detected_bad_zones == {
        'performer_id': 'dbid_uuid',
        'weight': 2.0,
        'fetched_points': 2,
        'detected_bad_area_log': True,
        'detected_bad_area_applied': True,
    }

    await _publish_message(
        messages[6:], redis_store, performer_from_pubsub_received,
    )

    response = await taxi_coord_control.get(
        'location_settings',
        params={
            'driver_profile_id': 'uuid',
            'park_db_id': 'dbid',
            'taximeter_agent_info': 'Taximeter-BETA 9.33 (1234)',
        },
    )

    strategy = response.json()['location_settings']
    for strategy_type in ('realtime_strategy', 'verified_strategy'):
        assert not strategy[strategy_type]['primaryGroup']
        assert not strategy[strategy_type]['alternativeGroups']
        assert not strategy[strategy_type]['referenceGroups']


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.now('2020-04-21T12:16:50.123456+0000')
@pytest.mark.suspend_periodic_tasks('bad_areas_detector')
@pytest.mark.config(
    COORD_CONTROL_HEATMAP_SETTINGS={'sending_samples_enabled': True},
    COORD_CONTROL_INTERESTING_POINTS_SETTINGS={
        'radius': 2500,
        'points_ttl': 120,
        'detector_batch_size': 1,
        'cleanup_batch_size': 2,
        'minimum_points_for_detection': 1,
        'points_weight_threshold_log': 0,
        'points_weight_threshold_applied': 0,
    },
)
async def test_interesting_points_heatmap_samples(
        taxi_coord_control, mockserver, redis_store, load_json, testpoint,
):
    @testpoint(PERFORMER_FROM_PUBSUB_NAME)
    def performer_from_pubsub_received(data):
        return data

    @mockserver.json_handler('/heatmap-sample-storage/v1/add_samples')
    def _mock_heatmap(request):
        req_points = [
            (sample['point']['lon'], sample['point']['lat'])
            for sample in request.json['samples']
        ]
        check_points = [
            (signal['position'][0], signal['position'][1])
            for signal in [messages[7], messages[11]]
        ]
        assert sorted(req_points) == sorted(check_points)
        return {'timestamp': '2020-04-21T12:16:50.123456+0000'}

    @testpoint(STORE_INTERESTING_POINTS_NAME)
    def store_interesting_points(data):
        return data

    @testpoint(BAD_AREA_DETECTION_NAME)
    def bad_zones_detector(data):
        return data

    await taxi_coord_control.invalidate_caches()

    await taxi_coord_control.enable_testpoints()

    messages = load_json('geobus_messages_bad_areas.json')

    await _publish_message(
        messages[:4], redis_store, performer_from_pubsub_received,
    )
    await _publish_message(
        messages[4:8], redis_store, performer_from_pubsub_received,
    )

    await _publish_message(
        messages[8:10], redis_store, performer_from_pubsub_received,
    )

    assert (await store_interesting_points.wait_call())['data'] == 2

    await taxi_coord_control.run_periodic_task('bad_areas_detector')

    await bad_zones_detector.wait_call()

    await _publish_message(
        messages[10:], redis_store, performer_from_pubsub_received,
    )

    await _mock_heatmap.wait_call()


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.now('2020-04-21T12:16:50.123456+0000')
@pytest.mark.suspend_periodic_tasks(
    'bad_areas_detector', 'bad_areas_detector_for_duplicated',
)
@pytest.mark.config(
    COORD_CONTROL_INTERESTING_POINTS_SETTINGS={
        'radius': 200,
        'points_ttl': 120,
        'detector_batch_size': 1,
        'cleanup_batch_size': 2,
        'minimum_points_for_detection': 1,
        'points_weight_threshold_log': 0,
        'points_weight_threshold_applied': 2,
    },
    COORD_CONTROL_TELEPORT_PERFORMERS_SETTINGS_V2={
        'duplication_area': {
            'center': {'lon': 37.629870, 'lat': 55.833998},
            'radius': 2500,
        },
        'percent_of_performers': 100,
        'teleports': [
            {
                'source': 'android_gps',
                'teleport_area': {
                    'center': {'lon': 37.629870, 'lat': 55.833998},
                    'radius': 25,
                },
                'destination_area': {
                    'center': {'lon': 37.031911, 'lat': 55.933935},
                    'radius': 10,
                },
            },
        ],
    },
)
async def test_interesting_points_duplication(
        taxi_coord_control, redis_store, load_json, testpoint,
):
    @testpoint(PERFORMER_FROM_PUBSUB_NAME)
    def performer_from_pubsub_received(data):
        return data

    @testpoint(STORE_INTERESTING_POINTS_NAME)
    def store_interesting_points(data):
        return data

    @testpoint(BAD_AREA_DETECTION_NAME)
    def bad_zones_detector(data):
        return data

    await taxi_coord_control.enable_testpoints()

    messages = load_json('geobus_messages_duplication.json')

    await _publish_message(messages[:4], redis_store, None)
    for _ in range(2):
        await performer_from_pubsub_received.wait_call()

    await _publish_message(messages[4:], redis_store, None)
    await performer_from_pubsub_received.wait_call()

    assert (await store_interesting_points.wait_call())['data'] == 2

    await taxi_coord_control.run_periodic_task(
        'bad_areas_detector_for_duplicated',
    )

    detected_bad_zones = (await bad_zones_detector.wait_call())['data']
    assert detected_bad_zones == {
        'performer_id': 'dbid_uuid' + '#',
        'weight': 2.0,
        'fetched_points': 2,
        'detected_bad_area_log': True,
        'detected_bad_area_applied': False,
    }

    response = await taxi_coord_control.post(
        'atlas/track', json={'dbid_uuid': 'dbid_uuid'},
    )

    assert response.status_code == 200
    for source in response.json()['track']:
        if source['source'] == 'android_gps':
            assert source['points'][0]['lon'] == messages[4]['position'][0]
            assert source['points'][0]['lat'] == messages[4]['position'][1]

    response = await taxi_coord_control.post(
        'atlas/track', json={'dbid_uuid': 'dbid_uuid#'},
    )
    assert response.status_code == 200
    assert response.json()['track']


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.now('2020-04-21T12:16:50.123456+0000')
@pytest.mark.suspend_periodic_tasks(
    'bad_areas_detector', 'bad_areas_detector_for_duplicated',
)
@pytest.mark.config(
    COORD_CONTROL_INTERESTING_POINTS_SETTINGS={
        'radius': 200,
        'points_ttl': 120,
        'detector_batch_size': 1,
        'cleanup_batch_size': 2,
        'minimum_points_for_detection': 1,
        'points_weight_threshold_log': 0,
        'points_weight_threshold_applied': 2,
    },
    COORD_CONTROL_TELEPORT_PERFORMERS_SETTINGS_V2={
        'duplication_area': {
            'center': {'lon': 37.629870, 'lat': 55.833998},
            'radius': 2500,
        },
        'percent_of_performers': 100,
        'teleports': [
            {
                'source': 'android_gps',
                'teleport_area': {
                    'center': {'lon': 37.629870, 'lat': 55.833998},
                    'radius': 25,
                },
                'destination_area': {
                    'center': {'lon': 37.031911, 'lat': 55.933935},
                    'radius': 10,
                },
            },
            {
                'source': 'yandex_lbs_gsm',
                'duplication_area': {
                    'center': {'lon': 37.629870, 'lat': 55.833998},
                    'radius': 2500,
                },
                'teleport_area': {
                    'center': {'lon': 37.629870, 'lat': 55.833998},
                    'radius': 25,
                },
                'destination_area': {
                    'center': {'lon': 37.031911, 'lat': 55.933935},
                    'radius': 10,
                },
                'percent_of_performers': 100,
            },
        ],
    },
)
async def test_interesting_points_double_duplication(
        taxi_coord_control, redis_store, load_json, testpoint,
):
    @testpoint(PERFORMER_FROM_PUBSUB_NAME)
    def performer_from_pubsub_received(data):
        return data

    @testpoint(PERFORMERS_TO_CALCULATE_NAME)
    def performers_to_calculate(data):
        return data

    await taxi_coord_control.enable_testpoints()

    messages = load_json('geobus_messages_duplication.json')

    await _publish_message(messages[:4], redis_store, None)
    for _ in range(2):
        await performer_from_pubsub_received.wait_call()

    assert set((await performers_to_calculate.wait_call())['data']) == {
        'dbid_uuid',
        'dbid_uuid#',
    }


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.now('2020-04-21T12:16:50.123456+0000')
@pytest.mark.suspend_periodic_tasks('bad_areas_detector')
@pytest.mark.config(
    COORD_CONTROL_TELEPORT_PERFORMERS_SETTINGS_V2={
        'duplication_area': {
            'center': {'lon': 37.631911, 'lat': 55.833935},
            'radius': 1,
        },
        'percent_of_performers': 100,
        'teleports': [],
    },
)
async def test_interesting_points_duplication_area(
        taxi_coord_control, redis_store, load_json, testpoint,
):
    @testpoint(PERFORMERS_TO_CALCULATE_NAME)
    def performers_to_calculate(data):
        return data

    await taxi_coord_control.enable_testpoints()

    messages = load_json('geobus_messages.json')

    await _publish_message([messages[2]], redis_store, None)

    assert set((await performers_to_calculate.wait_call())['data']) == {
        'dbid_uuid',
        'dbid_uuid#',
    }

    await _publish_message([messages[4]], redis_store, None)
    assert set((await performers_to_calculate.wait_call())['data']) == {
        'dbid_uuid',
    }
