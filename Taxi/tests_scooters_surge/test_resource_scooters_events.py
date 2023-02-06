import json

import pytest


@pytest.mark.experiments3(filename='calc_surge_settings_polygon.json')
@pytest.mark.suspend_periodic_tasks('calc-surge-zoned-periodic')
@pytest.mark.usefixtures('distlocks_mockserver')
@pytest.mark.config(
    SCOOTERS_ZONES=[
        {
            'geometry': [[36, 59], [36, 58], [37, 58]],
            'id': 'zone_id',
            'name': 'zone_name',
            'region_id': 'region_id',
        },
    ],
    CALC_SCOOTERS_SURGE_ZONED_ENABLED=True,
    SCOOTERS_SURGE_STORE_IN_S3=True,
)
async def test_calc_surge_polygon(taxi_scooters_surge, mockserver, testpoint):
    actual_saved_map = {}
    saved_in_s3 = {}

    @mockserver.handler('/heatmap-storage/v1/insert_map')
    def mock_insert_map(request):
        actual_saved_map[request.query['content_key']] = request.get_data()
        return mockserver.make_response(
            response='{"id": 1, "saved_at": "2019-01-02T00:00:00+0000"}',
            status=200,
            content_type='application/json',
        )

    @mockserver.handler('/mds-s3', prefix=True)
    def mock_s3(request):
        if request.method == 'PUT':
            saved_in_s3[request.path] = request.get_data()
            return mockserver.make_response('OK', 200)
        return mockserver.make_response('Not found', 404)

    @mockserver.json_handler(
        '/scooters-ops-relocation/scooters-ops-relocation/v1/events/fetch',
    )
    def _mock_scooters_ops_relocation(request):
        assert request.json['geometry'] == {
            'outer': [
                {'lon': 36.0, 'lat': 59.0},
                {'lon': 37.0, 'lat': 58.0},
                {'lon': 36.0, 'lat': 58.0},
                {'lon': 36.0, 'lat': 59.0},
            ],
        }
        assert request.json['allowed_types'] == ['income', 'relocated-in']

        response = {
            'events': [
                {
                    'type': 'income',
                    'occured_at': '2019-01-01T00:00:00+0000',
                    'location': {'lon': 0.0, 'lat': 0.0},
                },
                {
                    'type': 'relocated-in',
                    'occured_at': '2019-01-01T00:00:00+0000',
                    'location': {'lon': 0.0, 'lat': 0.0},
                },
            ],
        }
        return mockserver.make_response(
            json=response, status=200, content_type='application/json',
        )

    @testpoint('calc-surge-zoned-start')
    def handle_calc_job_start(arg):
        pass

    @testpoint('calc-surge-zoned-finish')
    def handle_calc_job_finish(arg):
        pass

    await taxi_scooters_surge.invalidate_caches(
        cache_names=['scooters-zones-cache'],
    )

    await taxi_scooters_surge.enable_testpoints()
    await taxi_scooters_surge.run_periodic_task('calc-surge-zoned-periodic')

    await handle_calc_job_start.wait_call()
    job_stats = await handle_calc_job_finish.wait_call()

    assert job_stats == {
        'arg': {'zones_success': 1, 'zones_error': 0, 'save_map_errors': 0},
    }
    assert actual_saved_map.keys() == {'scooters_surge_zoned/default'}
    assert mock_insert_map.times_called == 1

    saved_map = {
        'zone_id': {
            'value': 2.0,
            'features': [2.0],
            'extra': {
                'scooters_events': [
                    {
                        'type': 'income',
                        'occured_at': '2019-01-01T00:00:00+00:00',
                        'location': {'lon': 0.0, 'lat': 0.0},
                    },
                    {
                        'type': 'relocated-in',
                        'occured_at': '2019-01-01T00:00:00+00:00',
                        'location': {'lon': 0.0, 'lat': 0.0},
                    },
                ],
            },
        },
    }

    assert (
        json.loads(actual_saved_map['scooters_surge_zoned/default'])
        == saved_map
    )

    # '/mds-s3/' is bucket prefix, actual key is `scooters_surge_zoned/default`
    assert saved_in_s3.keys() == {'/mds-s3/scooters_surge_zoned/default'}
    assert mock_s3.times_called == 1
    assert (
        json.loads(saved_in_s3['/mds-s3/scooters_surge_zoned/default'])
        == saved_map
    )


@pytest.mark.experiments3(filename='calc_surge_settings_circle.json')
@pytest.mark.suspend_periodic_tasks('calc-surge-zoned-periodic')
@pytest.mark.usefixtures('distlocks_mockserver')
@pytest.mark.config(
    SCOOTERS_ZONES=[
        {
            'geometry': [[36, 58], [36, 60], [38, 60], [38, 58]],
            'id': 'zone_id',
            'name': 'zone_name',
            'region_id': 'region_id',
        },
    ],
    CALC_SCOOTERS_SURGE_ZONED_ENABLED=True,
    SCOOTERS_SURGE_STORE_IN_S3=True,
)
async def test_calc_surge_circle(taxi_scooters_surge, mockserver, testpoint):
    actual_saved_map = {}
    saved_in_s3 = {}

    @mockserver.handler('/heatmap-storage/v1/insert_map')
    def mock_insert_map(request):
        actual_saved_map[request.query['content_key']] = request.get_data()
        return mockserver.make_response(
            response='{"id": 1, "saved_at": "2019-01-02T00:00:00+0000"}',
            status=200,
            content_type='application/json',
        )

    @mockserver.handler('/mds-s3', prefix=True)
    def mock_s3(request):
        if request.method == 'PUT':
            saved_in_s3[request.path] = request.get_data()
            return mockserver.make_response('OK', 200)
        return mockserver.make_response('Not found', 404)

    @mockserver.json_handler(
        '/scooters-ops-relocation/scooters-ops-relocation/v1/events/fetch',
    )
    def _mock_scooters_ops_relocation(request):
        assert request.json['geometry']['center'] == {'lon': 37, 'lat': 59}
        assert request.json['geometry']['radius_m'] == 81332
        assert request.json['allowed_types'] == ['income', 'relocated-in']

        response = {
            'events': [
                {
                    'type': 'income',
                    'occured_at': '2019-01-01T00:00:00+0000',
                    'location': {'lon': 0.0, 'lat': 0.0},
                },
                {
                    'type': 'relocated-in',
                    'occured_at': '2019-01-01T00:00:00+0000',
                    'location': {'lon': 0.0, 'lat': 0.0},
                },
            ],
        }
        return mockserver.make_response(
            json=response, status=200, content_type='application/json',
        )

    @testpoint('calc-surge-zoned-start')
    def handle_calc_job_start(arg):
        pass

    @testpoint('calc-surge-zoned-finish')
    def handle_calc_job_finish(arg):
        pass

    await taxi_scooters_surge.invalidate_caches(
        cache_names=['scooters-zones-cache'],
    )

    await taxi_scooters_surge.enable_testpoints()
    await taxi_scooters_surge.run_periodic_task('calc-surge-zoned-periodic')

    await handle_calc_job_start.wait_call()
    job_stats = await handle_calc_job_finish.wait_call()

    assert job_stats == {
        'arg': {'zones_success': 1, 'zones_error': 0, 'save_map_errors': 0},
    }
    assert actual_saved_map.keys() == {'scooters_surge_zoned/default'}
    assert mock_insert_map.times_called == 1

    saved_map = {
        'zone_id': {
            'value': 2.0,
            'features': [2.0],
            'extra': {
                'scooters_events': [
                    {
                        'type': 'income',
                        'occured_at': '2019-01-01T00:00:00+00:00',
                        'location': {'lon': 0.0, 'lat': 0.0},
                    },
                    {
                        'type': 'relocated-in',
                        'occured_at': '2019-01-01T00:00:00+00:00',
                        'location': {'lon': 0.0, 'lat': 0.0},
                    },
                ],
            },
        },
    }

    assert (
        json.loads(actual_saved_map['scooters_surge_zoned/default'])
        == saved_map
    )

    # '/mds-s3/' is bucket prefix, actual key is `scooters_surge_zoned/default`
    assert saved_in_s3.keys() == {'/mds-s3/scooters_surge_zoned/default'}
    assert mock_s3.times_called == 1
    assert (
        json.loads(saved_in_s3['/mds-s3/scooters_surge_zoned/default'])
        == saved_map
    )


@pytest.mark.experiments3(filename='calc_surge_settings_bbox.json')
@pytest.mark.suspend_periodic_tasks('calc-surge-zoned-periodic')
@pytest.mark.usefixtures('distlocks_mockserver')
@pytest.mark.config(
    SCOOTERS_ZONES=[
        {
            'geometry': [[36, 58], [36, 60], [38, 60], [38, 58]],
            'id': 'zone_id',
            'name': 'zone_name',
            'region_id': 'region_id',
        },
    ],
    CALC_SCOOTERS_SURGE_ZONED_ENABLED=True,
    SCOOTERS_SURGE_STORE_IN_S3=True,
)
async def test_calc_surge_bbox(taxi_scooters_surge, mockserver, testpoint):
    actual_saved_map = {}
    saved_in_s3 = {}

    @mockserver.handler('/heatmap-storage/v1/insert_map')
    def mock_insert_map(request):
        actual_saved_map[request.query['content_key']] = request.get_data()
        return mockserver.make_response(
            response='{"id": 1, "saved_at": "2019-01-02T00:00:00+0000"}',
            status=200,
            content_type='application/json',
        )

    @mockserver.handler('/mds-s3', prefix=True)
    def mock_s3(request):
        if request.method == 'PUT':
            saved_in_s3[request.path] = request.get_data()
            return mockserver.make_response('OK', 200)
        return mockserver.make_response('Not found', 404)

    @mockserver.json_handler(
        '/scooters-ops-relocation/scooters-ops-relocation/v1/events/fetch',
    )
    def _mock_scooters_ops_relocation(request):
        assert request.json['geometry']['tl'] == {
            'lon': 35.99103942677581,
            'lat': 60.00448783533135,
        }
        assert request.json['geometry']['br'] == {
            'lon': 38.008455535261405,
            'lat': 57.995510768939575,
        }
        assert request.json['allowed_types'] == ['income', 'relocated-in']

        response = {
            'events': [
                {
                    'type': 'income',
                    'occured_at': '2019-01-01T00:00:00+0000',
                    'location': {'lon': 0.0, 'lat': 0.0},
                },
                {
                    'type': 'relocated-in',
                    'occured_at': '2019-01-01T00:00:00+0000',
                    'location': {'lon': 0.0, 'lat': 0.0},
                },
            ],
        }
        return mockserver.make_response(
            json=response, status=200, content_type='application/json',
        )

    @testpoint('calc-surge-zoned-start')
    def handle_calc_job_start(arg):
        pass

    @testpoint('calc-surge-zoned-finish')
    def handle_calc_job_finish(arg):
        pass

    await taxi_scooters_surge.invalidate_caches(
        cache_names=['scooters-zones-cache'],
    )

    await taxi_scooters_surge.enable_testpoints()
    await taxi_scooters_surge.run_periodic_task('calc-surge-zoned-periodic')

    await handle_calc_job_start.wait_call()
    job_stats = await handle_calc_job_finish.wait_call()

    assert job_stats == {
        'arg': {'zones_success': 1, 'zones_error': 0, 'save_map_errors': 0},
    }
    assert actual_saved_map.keys() == {'scooters_surge_zoned/default'}
    assert mock_insert_map.times_called == 1

    saved_map = {
        'zone_id': {
            'value': 2.0,
            'features': [2.0],
            'extra': {
                'scooters_events': [
                    {
                        'type': 'income',
                        'occured_at': '2019-01-01T00:00:00+00:00',
                        'location': {'lon': 0.0, 'lat': 0.0},
                    },
                    {
                        'type': 'relocated-in',
                        'occured_at': '2019-01-01T00:00:00+00:00',
                        'location': {'lon': 0.0, 'lat': 0.0},
                    },
                ],
            },
        },
    }

    assert (
        json.loads(actual_saved_map['scooters_surge_zoned/default'])
        == saved_map
    )

    # '/mds-s3/' is bucket prefix, actual key is `scooters_surge_zoned/default`
    assert saved_in_s3.keys() == {'/mds-s3/scooters_surge_zoned/default'}
    assert mock_s3.times_called == 1
    assert (
        json.loads(saved_in_s3['/mds-s3/scooters_surge_zoned/default'])
        == saved_map
    )
