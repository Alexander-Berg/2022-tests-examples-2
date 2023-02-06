import pytest


YT_LOGS = []


@pytest.fixture(name='testpoint_service')
def _testpoint_service(testpoint):
    @testpoint('yt_logger::messages::calculations')
    def _handler(data_json):
        YT_LOGS.append(data_json)


@pytest.mark.now('2020-07-06T00:00:00+00:00')
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
)
async def test_yt_logs(
        taxi_scooters_surge, mockserver, testpoint, testpoint_service,
):
    YT_LOGS.clear()

    @mockserver.handler('/heatmap-storage/v1/insert_map')
    def _mock_insert_map(request):
        return mockserver.make_response(
            response='{"id": 1, "saved_at": "2019-01-02T00:00:00+0000"}',
            status=200,
            content_type='application/json',
        )

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
    await handle_calc_job_finish.wait_call()
    del YT_LOGS[0]['calculation_id']
    del YT_LOGS[0]['calculation']['$pipeline_id']
    assert YT_LOGS == [
        {
            'calculation': {
                '$logs': [],
                '$meta': [
                    {
                        '$iteration': 0,
                        '$logs': [
                            {
                                '$level': 'warning',
                                '$message': 'pipeline log',
                                '$region': 'user_code',
                                '$timestamp': '2020-07-06T00:00:00+0000',
                            },
                        ],
                        '$stage': 'resource_fetch',
                    },
                    {'$iteration': 0, '$logs': [], '$stage': 'calc_surge'},
                ],
                '$pipeline_name': 'test_pipeline_name',
                'features': [{'$history': [{'$meta_idx': 1, '$value': 2}]}],
                'value': {'$history': [{'$meta_idx': 1, '$value': 0.6}]},
            },
            'timestamp': '2020-07-06T03:00:00+03:00',
            'zone_id': 'zone_id',
        },
    ]
