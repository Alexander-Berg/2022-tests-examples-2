import json

import pytest


@pytest.mark.experiments3(filename='calc_surge_settings.json')
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
async def test_calc_surge(taxi_scooters_surge, mockserver, testpoint):
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

    @testpoint('calc-surge-zoned-start')
    def handle_calc_job_start(arg):
        pass

    @testpoint('calc-surge-zoned-finish')
    def handle_calc_job_finish(arg):
        pass

    await taxi_scooters_surge.invalidate_caches(
        cache_names=['scooters-zones-cache', 'scooters-positions-cache'],
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
            'value': 0.6,
            'features': [2.0],
            'extra': {
                'scooters_list': [
                    {
                        'id': 'sc-001',
                        'fuel_level': 30,
                        'number': '1',
                        'status': 'available',
                    },
                    {
                        'id': 'sc-002',
                        'fuel_level': 90,
                        'number': '2',
                        'status': 'unknown',
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
