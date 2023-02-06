import time

import pytest

DISTLOCK_NAME = 'scooters-misc-scooters-watcher'

MOSCOW_LOCATION = {'lon': 37.4, 'lat': 55.7}


@pytest.mark.config(
    SCOOTERS_MISC_SCOOTERS_WATCHER_SETTINGS={
        'sleep-time-ms': 10000,
        'enabled': True,
        'scooter_tag_to_cable_lock_availability_mapping': {
            'scooter_moscow': True,
            'scooter_krasnodar': False,
        },
    },
)
async def test_cable_locks(
        taxi_scooters_misc, mockserver, generate_uuid, testpoint,
):
    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def _mock_car_details(_):
        cars = [
            {
                'number': '0001',
                'model_id': 'ninebot',
                'telematics': {'has_cable_lock': 1},
                'tags': [{'tag': 'scooter_moscow', 'tag_id': generate_uuid}],
            },
            {  # no has_cable_lock -> unchecked scooter
                'number': '0002',
                'model_id': 'ninebot',
                'telematics': {},
                'tags': [{'tag': 'scooter_moscow', 'tag_id': generate_uuid}],
            },
            {  # bad telematics -> bad scooter
                'number': '0003',
                'model_id': 'ninebot',
                'telematics': {'has_cable_lock': 0},
                'tags': [{'tag': 'scooter_moscow', 'tag_id': generate_uuid}],
            },
        ]
        return {'cars': cars, 'timestamp': int(time.time())}

    @testpoint('check-cable-locks')
    def _testpoint(data):
        assert data == {'unchecked_scooters': '0002', 'bad_scooters': '0003'}

    await taxi_scooters_misc.run_distlock_task(DISTLOCK_NAME)
    assert _mock_car_details.times_called == 2
    assert _testpoint.times_called == 1


MAX_HEARTBEAT_AGE = 10
STALE_LAG = MAX_HEARTBEAT_AGE + 1


@pytest.mark.now('2022-07-01T19:10:34+03:00')
@pytest.mark.config(
    SCOOTERS_MISC_SCOOTERS_WATCHER_SETTINGS={
        'sleep-time-ms': 10000,
        'enabled': True,
        'tag_stale_scooters': {
            'limit_overall_scooters': 1,
            'max_heartbeat_age': MAX_HEARTBEAT_AGE,
            'tag_name': 'no_heartbeat',
        },
    },
)
async def test_tag_stale(
        taxi_scooters_misc,
        taxi_scooters_misc_monitor,
        mockserver,
        mocked_time,
        generate_uuid,
):
    await taxi_scooters_misc.tests_control(reset_metrics=True)

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def _mock_car_details(_):
        now = 1656691834
        cars = [
            {
                'id': '00000000-0000-0000-0000-000000000001',
                'number': '0001',
                'model_id': 'ninebot',
                'tags': [
                    {'tag': 'scooter_moscow', 'tag_id': generate_uuid},
                    {'tag': 'no_heartbeat', 'tag_id': generate_uuid},
                ],
            },
            {
                'id': '00000000-0000-0000-0000-000000000002',
                'number': '0002',
                'model_id': 'ninebot',
                'tags': [
                    {'tag': 'scooter_moscow', 'tag_id': generate_uuid},
                    {'tag': 'no_heartbeat', 'tag_id': generate_uuid},
                ],
                'lag': {'heartbeat': now - MAX_HEARTBEAT_AGE},
            },
            {
                'id': '00000000-0000-0000-0000-000000000003',
                'number': '0003',
                'model_id': 'ninebot',
                'tags': [{'tag': 'scooter_moscow', 'tag_id': generate_uuid}],
                'lag': {'heartbeat': now - STALE_LAG},
            },
            {
                'id': '00000000-0000-0000-0000-000000000004',
                'number': '0004',
                'model_id': 'ninebot',
                'tags': [{'tag': 'scooter_moscow', 'tag_id': generate_uuid}],
                'lag': {'heartbeat': now - STALE_LAG},
            },
        ]
        return {'cars': cars, 'timestamp': int(time.time())}

    @mockserver.json_handler('/scooter-backend/api/taxi/car/tag_add')
    def _mock_tag_add(request):
        assert request.json == {
            'object_ids': [
                '00000000-0000-0000-0000-000000000003',
            ],  # limited by `limit_overall_scooters`
            'tag_name': 'no_heartbeat',
        }
        return {
            'tagged_objects': [
                {
                    'tag_id': [],
                    'object_id': '00000000-0000-0000-0000-000000000003',
                },
            ],
        }

    @mockserver.json_handler('/scooter-backend/api/taxi/car/tag_remove')
    def _mock_tag_remove(request):
        assert request.json == {
            'object_ids': ['00000000-0000-0000-0000-000000000002'],
            'tag_names': ['no_heartbeat'],
        }
        return {}

    await taxi_scooters_misc.run_distlock_task(DISTLOCK_NAME)
    assert _mock_tag_add.times_called == 1
    assert _mock_tag_remove.times_called == 1

    mocked_time.sleep(10)  # idea copied from userver-sample/*/test_metrix.py
    await taxi_scooters_misc.tests_control(invalidate_caches=False)
    metrics = await taxi_scooters_misc_monitor.get_metric(
        'scooters_misc_metrics',
    )
    assert metrics == {
        'no_heartbeat_seconds': {
            '$meta': {'solomon_children_labels': 'percentile'},
            'p75': STALE_LAG,
            'p95': STALE_LAG,
            'p99': STALE_LAG,
        },
        'stale_count': {
            '$meta': {'solomon_children_labels': 'kind'},
            'skip': 1,
            'stale': 2,
        },
    }


@pytest.mark.config(
    SCOOTERS_MISC_SCOOTERS_WATCHER_SETTINGS={
        'sleep-time-ms': 10000,
        'enabled': True,
        'car_details_tags_filter': '-dead',
    },
)
async def test_location_events(
        taxi_scooters_misc, mockserver, testpoint, load_json, experiments3,
):
    config = load_json('exp3_scooters_events_handler_settings.json')[
        'configs'
    ][0]
    config['match']['consumers'] = [{'name': 'scooters-misc/scooters_watcher'}]
    experiments3.add_config(**config)

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def _mock_car_details(request):
        if 'tags_filter' in request.query.keys():
            assert request.query['tags_filter'] == '-dead'
            cars = [
                {  # scooter with acceleration in bad area -> generate event
                    'id': 'id_0001',
                    'number': '0001',
                    'model_id': 'ninebot',
                    'location': {**MOSCOW_LOCATION, 'tags': ['area_for_bad']},
                    'telematics': {'accelerator_pedal': 1},
                },
                {  # scooter without acceleration out of bad area -> generate event
                    'id': 'id_0002',
                    'number': '0002',
                    'model_id': 'ninebot',
                    'location': {**MOSCOW_LOCATION, 'tags': ['moscow_area']},
                    'telematics': {'accelerator_pedal': 0},
                },
                {  # scooter with acceleration out of bad area -> no event
                    'id': 'id_0003',
                    'number': '0003',
                    'model_id': 'ninebot',
                    'location': {**MOSCOW_LOCATION, 'tags': ['moscow_area']},
                    'telematics': {'accelerator_pedal': 1},
                },
                {  # scooter without acceleration in bad area -> no event
                    'id': 'id_0004',
                    'number': '0004',
                    'model_id': 'ninebot',
                    'location': {**MOSCOW_LOCATION, 'tags': ['area_for_bad']},
                    'telematics': {'accelerator_pedal': 0},
                },
                {  # scooter without location and telematics -> no event
                    'id': 'id_0005',
                    'number': '0005',
                    'model_id': 'ninebot',
                },
            ]
            return {'cars': cars, 'timestamp': int(time.time())}
        else:
            return {'cars': [], 'timestamp': 1655447659}

    @testpoint('check-location-events')
    def _testpoint(data):
        assert data == [
            {'scooter_id': 'id_0001', 'type': 'scooter_in_forbidden_zone'},
            {'scooter_id': 'id_0002', 'type': 'scooter_out_of_forbidden_zone'},
        ]

    await taxi_scooters_misc.run_distlock_task(DISTLOCK_NAME)
    assert _mock_car_details.times_called == 2
    assert _testpoint.times_called == 1


@pytest.mark.config(
    SCOOTERS_MISC_SCOOTERS_WATCHER_SETTINGS={
        'sleep-time-ms': 10000,
        'enabled': True,
        'car_details_tags_filter': '-dead',
    },
)
async def test_battery_level_events(
        taxi_scooters_misc, mockserver, testpoint, load_json, experiments3,
):
    config = load_json('exp3_scooters_events_handler_settings.json')[
        'configs'
    ][0]
    config['match']['consumers'] = [{'name': 'scooters-misc/scooters_watcher'}]
    experiments3.add_config(**config)

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def _mock_car_details(request):
        if 'tags_filter' in request.query.keys():
            assert request.query['tags_filter'] == '-dead'
            cars = [
                {  # scooter with acceleration with low battery level -> event
                    'id': 'id_0001',
                    'number': '0001',
                    'model_id': 'ninebot',
                    'telematics': {'accelerator_pedal': 1, 'fuel_level': 5},
                },
                {  # scooter without acceleration with sufficient battery level -> event # noqa: E501 (line too long)
                    'id': 'id_0002',
                    'number': '0002',
                    'model_id': 'ninebot',
                    'telematics': {'accelerator_pedal': 0, 'fuel_level': 30},
                },
                {  # scooter with acceleration with sufficient battery level -> no event # noqa: E501 (line too long)
                    'id': 'id_0003',
                    'number': '0003',
                    'model_id': 'ninebot',
                    'telematics': {'accelerator_pedal': 1, 'fuel_level': 30},
                },
                {  # scooter without acceleration with low battery level -> no event # noqa: E501 (line too long)
                    'id': 'id_0004',
                    'number': '0004',
                    'model_id': 'ninebot',
                    'telematics': {'accelerator_pedal': 0, 'fuel_level': 5},
                },
                {  # scooter without telematics -> no event
                    'id': 'id_0005',
                    'number': '0005',
                    'model_id': 'ninebot',
                },
            ]
            return {'cars': cars, 'timestamp': int(time.time())}
        else:
            return {'cars': [], 'timestamp': 1655447659}

    @testpoint('check-battery-level-events')
    def _testpoint(data):
        assert data == [
            {'scooter_id': 'id_0001', 'type': 'low_battery_level'},
            {'scooter_id': 'id_0002', 'type': 'sufficient_battery_level'},
        ]

    await taxi_scooters_misc.run_distlock_task(DISTLOCK_NAME)
    assert _mock_car_details.times_called == 2
    assert _testpoint.times_called == 1
