import pytest

from tests_heatmap_sample_storage import common


# +5 min after samples' 'created' time
@pytest.mark.now('2019-03-08T00:05:00Z')
@pytest.mark.redis_store(
    [
        'rpush',
        'coord_control:1552003200',
        common.build_sample(
            37.0, 55.0, 'coord_control', 'default', 1, 1, {}, 1552003200000,
        ),
    ],
    [
        'rpush',
        'coord_control:1552003200',
        common.build_sample(
            37.0, 55.0, 'coord_control', 'default', 0.5, 1, {}, 1552003200000,
        ),
    ],
    [
        'rpush',
        'coord_control:1552003200',
        common.build_sample(
            37.05,
            55.05,
            'coord_control',
            'default',
            0.3,
            1,
            {},
            1552003200000,
        ),
    ],
)
@pytest.mark.experiments3(filename='heatmaps_config.json')
@pytest.mark.config(
    HEATMAP_SAMPLE_STORAGE_ENABLED_JOBS={'calc-heatmap': True},
    HEATMAP_SAMPLES_TYPES=['coord_control'],
    SAMPLE_STORAGE_STORE_HEATMAPS_IN_S3=True,
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.suspend_periodic_tasks('calc-heatmap-periodic')
@pytest.mark.usefixtures('distlocks_mockserver')
async def test_calc_heatmap(
        taxi_heatmap_sample_storage,
        mockserver,
        testpoint,
        load_binary,
        s3_heatmap_storage,
):
    actual_saved_map = {}

    @mockserver.handler('/heatmap-storage/v1/insert_map')
    def mock_insert_map(request):
        actual_saved_map[request.query['content_key']] = request.get_data()
        return mockserver.make_response(
            response='{"id": 1, "saved_at": "2019-01-02T00:00:00+0000"}',
            status=200,
            content_type='application/json',
        )

    @testpoint('calc-heatmap-start')
    def handle_calc_job_start(arg):
        pass

    @testpoint('calc-heatmap-finish')
    def handle_calc_job_finish(arg):
        pass

    await taxi_heatmap_sample_storage.enable_testpoints()
    await taxi_heatmap_sample_storage.run_periodic_task(
        'calc-heatmap-periodic',
    )
    await handle_calc_job_start.wait_call()
    cells_calc_stats = await handle_calc_job_finish.wait_call()

    assert cells_calc_stats == {
        'arg': {
            'cells_calculated': {'coord_control/default': 11},
            'maps_saved': 1,
            'samples_processed': {'coord_control/default': 0},
            'save_maps_error': 0,
        },
    }
    assert actual_saved_map.keys() == {'coord_control/default'}
    assert mock_insert_map.times_called == 1
    assert s3_heatmap_storage.handler.times_called == 1

    heatmap = actual_saved_map['coord_control/default']

    actual_map = s3_heatmap_storage.get_actual_map('coord_control/default')
    assert common.parse_map(heatmap) == common.parse_map(actual_map.map_data)

    assert common.parse_map(heatmap) == [
        {
            'hex_grid': {
                'br': {'lat': 56.0, 'lon': 38.0},
                'cells_size': 500.0,
                'legend': '0.12 - 0.61',
                'legend_precision': 2,
                'legend_measurement_units': '',
                'max_value': 0.611,
                'min_value': 0.122,
                'tl': {'lat': 54.0, 'lon': 36.0},
                'extra': None,
            },
            'values': [
                {'value': 0.611, 'weight': 2.0, 'x': 165, 'y': 257},
                {'value': 0.611, 'weight': 2.0, 'x': 165, 'y': 258},
                {'value': 0.611, 'weight': 2.0, 'x': 166, 'y': 256},
                {'value': 0.611, 'weight': 2.0, 'x': 166, 'y': 257},
                {'value': 0.611, 'weight': 2.0, 'x': 166, 'y': 258},
                {'value': 0.611, 'weight': 2.0, 'x': 167, 'y': 257},
                {'value': 0.611, 'weight': 2.0, 'x': 167, 'y': 258},
                {'value': 0.122, 'weight': 1.0, 'x': 174, 'y': 269},
                {'value': 0.122, 'weight': 1.0, 'x': 174, 'y': 270},
                {'value': 0.122, 'weight': 1.0, 'x': 175, 'y': 270},
                {'value': 0.122, 'weight': 1.0, 'x': 175, 'y': 271},
            ],
        },
    ]


# +5 min after samples' 'created' time
@pytest.mark.now('2019-03-08T00:05:00Z')
@pytest.mark.redis_store(
    [
        'rpush',
        'coord_control:1552003200',
        common.build_sample(
            37.0,
            55.0,
            'coord_control',
            'default',
            1,
            1,
            {'f_legend': 1},
            1552003200000,
        ),
    ],
    [
        'rpush',
        'coord_control:1552003200',
        common.build_sample(
            37.0,
            55.0,
            'coord_control',
            'default',
            0.5,
            1,
            {'f_legend': 2},
            1552003200000,
        ),
    ],
    [
        'rpush',
        'coord_control:1552003200',
        common.build_sample(
            37.05,
            55.05,
            'coord_control',
            'default',
            0.3,
            1,
            {'f_legend': 3},
            1552003200000,
        ),
    ],
)
@pytest.mark.experiments3(filename='heatmaps_config_legend.json')
@pytest.mark.config(
    HEATMAP_SAMPLE_STORAGE_ENABLED_JOBS={'calc-heatmap': True},
    HEATMAP_SAMPLES_TYPES=['coord_control'],
    SAMPLE_STORAGE_STORE_HEATMAPS_IN_S3=True,
)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.suspend_periodic_tasks('calc-heatmap-periodic')
@pytest.mark.usefixtures('distlocks_mockserver')
async def test_custom_legend(
        taxi_heatmap_sample_storage,
        mockserver,
        testpoint,
        load_binary,
        s3_heatmap_storage,
):
    actual_saved_map = {}

    @mockserver.handler('/heatmap-storage/v1/insert_map')
    def mock_insert_map(request):
        actual_saved_map[request.query['content_key']] = request.get_data()
        return mockserver.make_response(
            response='{"id": 1, "saved_at": "2019-01-02T00:00:00+0000"}',
            status=200,
            content_type='application/json',
        )

    @testpoint('calc-heatmap-start')
    def handle_calc_job_start(arg):
        pass

    @testpoint('calc-heatmap-finish')
    def handle_calc_job_finish(arg):
        pass

    await taxi_heatmap_sample_storage.enable_testpoints()
    await taxi_heatmap_sample_storage.run_periodic_task(
        'calc-heatmap-periodic',
    )
    await handle_calc_job_start.wait_call()
    cells_calc_stats = await handle_calc_job_finish.wait_call()

    assert cells_calc_stats == {
        'arg': {
            'cells_calculated': {'coord_control/default': 11},
            'maps_saved': 1,
            'samples_processed': {'coord_control/default': 0},
            'save_maps_error': 0,
        },
    }
    assert actual_saved_map.keys() == {'coord_control/default'}
    assert mock_insert_map.times_called == 1
    assert s3_heatmap_storage.handler.times_called == 1

    heatmap = actual_saved_map['coord_control/default']

    actual_map = s3_heatmap_storage.get_actual_map('coord_control/default')
    assert common.parse_map(heatmap) == common.parse_map(actual_map.map_data)

    assert common.parse_map(heatmap) == [
        {
            'hex_grid': {
                'br': {'lat': 56.0, 'lon': 38.0},
                'cells_size': 500.0,
                'legend': '1.00 - 3.00',
                'legend_measurement_units': '',
                'legend_precision': 2,
                'max_value': 3,
                'min_value': 1,
                'tl': {'lat': 54.0, 'lon': 36.0},
                'extra': None,
            },
            'values': [
                {'value': 0.611, 'weight': 2.0, 'x': 165, 'y': 257},
                {'value': 0.611, 'weight': 2.0, 'x': 165, 'y': 258},
                {'value': 0.611, 'weight': 2.0, 'x': 166, 'y': 256},
                {'value': 0.611, 'weight': 2.0, 'x': 166, 'y': 257},
                {'value': 0.611, 'weight': 2.0, 'x': 166, 'y': 258},
                {'value': 0.611, 'weight': 2.0, 'x': 167, 'y': 257},
                {'value': 0.611, 'weight': 2.0, 'x': 167, 'y': 258},
                {'value': 0.122, 'weight': 1.0, 'x': 174, 'y': 269},
                {'value': 0.122, 'weight': 1.0, 'x': 174, 'y': 270},
                {'value': 0.122, 'weight': 1.0, 'x': 175, 'y': 270},
                {'value': 0.122, 'weight': 1.0, 'x': 175, 'y': 271},
            ],
        },
    ]
