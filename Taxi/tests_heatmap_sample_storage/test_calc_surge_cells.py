import pytest

from tests_heatmap_sample_storage import common


# +5 min after samples' 'created' time
@pytest.mark.now('2019-03-08T00:05:00Z')
# In both maps we have avg_pins = 5
@pytest.mark.redis_store(
    [
        'rpush',
        'taxi_surge:1552003200',
        common.build_sample(
            38.0,
            51.0,
            'taxi_surge',
            'econom/default',
            1.3,
            1,
            {
                'pins': 9,
                'radius': 2500,
                'free': 2,
                'total': 4,
                'free_chain': 1,
                'pins_order': 4,
                'pins_driver': 2,
            },
            1552003200000,
        ),
    ],
    [
        'rpush',
        'taxi_surge:1552003200',
        common.build_sample(
            38.0,
            51.0,
            'taxi_surge',
            'econom/default',
            1.3,
            1,
            {'pins': 3, 'radius': 2500},
            1552003200000,
        ),
    ],
    [
        'rpush',
        'taxi_surge:1552003200',
        common.build_sample(
            38.0,
            51.0,
            'taxi_surge',
            'econom/default',
            1.3,
            1,
            {'pins': 3, 'radius': 2500},
            1552003200000,
        ),
    ],
    [
        'rpush',
        'taxi_surge:1552003200',
        common.build_sample(
            38.0,
            51.0,
            'taxi_surge',
            'econom/default',
            1.3,
            1,
            {},
            1552003200000,
        ),
    ],
    [
        'rpush',
        'taxi_surge:1552003200',
        common.build_sample(
            38.0,
            51.0,
            'taxi_surge',
            'econom/default',
            1.3,
            1,
            {'cost': 99.9},
            1552003200000,
        ),
    ],
    [
        'rpush',
        'taxi_surge:1552003200',
        common.build_sample(
            38.0,
            51.0,
            'taxi_surge',
            'econom/alternative',
            1.3,
            1,
            # adjusted pins == 5
            {'pins': 20, 'radius': 5000},
            1552003200000,
        ),
    ],
    [
        'rpush',
        'taxi_surge:1552003200',
        common.build_sample(
            38.0,
            51.0,
            'taxi_surge',
            'econom/alternative',
            1.3,
            1,
            {},
            1552003200000,
        ),
    ],
    [
        'rpush',
        'taxi_surge:1552003200',
        common.build_sample(
            38.0,
            51.0,
            'taxi_surge',
            'econom/alternative',
            1.3,
            1,
            {},
            1552003200000,
        ),
    ],
    [
        'rpush',
        'taxi_surge:1552003200',
        common.build_sample(
            38.0,
            51.0,
            'taxi_surge',
            'econom/alternative',
            1.3,
            1,
            {},
            1552003200000,
        ),
    ],
    [
        'rpush',
        'taxi_surge:1552003200',
        common.build_sample(
            38.0,
            51.0,
            'taxi_surge',
            'econom/alternative',
            1.3,
            1,
            {'cost': 99.9},
            1552003200000,
        ),
    ],
)
@pytest.mark.redis_store(['delete', 'calc-surge-cells-tasks'])
@pytest.mark.experiments3(filename='calc_surge_cells_settings.json')
@pytest.mark.config(
    CALC_SURGE_CELLS_WORKER_ENABLED=True,
    CALC_SURGE_CELLS_DRIVER_MAP_LAYERS_OVERRIDE={
        'default': ['default', 'alternative'],
    },
    HEATMAP_SAMPLES_TYPES=['taxi_surge'],
    SAMPLE_STORAGE_STORE_HEATMAPS_IN_S3=True,
)
@pytest.mark.suspend_periodic_tasks('calc-surge-cells-worker')
async def test_calc_surge_cells(
        taxi_heatmap_sample_storage,
        mockserver,
        testpoint,
        redis_store,
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

    @testpoint('calc-surge-cells-worker-start')
    def handle_calc_job_start(arg):
        pass

    @testpoint('calc-surge-cells-worker-finish')
    def handle_calc_job_finish(arg):
        pass

    redis_store.rpush('calc-surge-cells-tasks', '__default__/default')
    await taxi_heatmap_sample_storage.enable_testpoints()
    await taxi_heatmap_sample_storage.run_periodic_task(
        'calc-surge-cells-worker',
    )

    start_stats = await handle_calc_job_start.wait_call()
    finish_stats = await handle_calc_job_finish.wait_call()
    common.diff_calc_surge_cells_stats(finish_stats, start_stats)
    assert finish_stats == {
        'arg': {'maps_saved': 3, 'save_map_errors': 0, 'fetch_task_errors': 0},
    }

    assert actual_saved_map.keys() == {
        'taxi_surge/__default__/default',
        'taxi_surge_full/__default__/default',
        'taxi_surge_lightweight/__default__/default',
    }
    assert mock_insert_map.times_called == 3
    assert s3_heatmap_storage.handler.times_called == 3

    assert s3_heatmap_storage.get_content_keys() == actual_saved_map.keys()

    for key in actual_saved_map:
        assert common.parse_map(
            s3_heatmap_storage.get_actual_map(key).map_data,
        ) == common.parse_map(actual_saved_map[key])

    driver_map = actual_saved_map['taxi_surge/__default__/default']
    assert common.parse_map(driver_map)[0]['hex_grid'] == {
        'cells_size': 500,
        'legend': '+90.0-180.0',
        'legend_measurement_units': 'RUR',
        'max_value': 180,
        'min_value': 90,
        'legend_precision': 0,
        'extra': None,
        'tl': {'lat': 50.0, 'lon': 37.0},
        'br': {'lat': 52.0, 'lon': 39.0},
    }
    full_map = actual_saved_map['taxi_surge_full/__default__/default']
    assert common.parse_map(full_map) == [
        {
            'hex_grid': {
                'cells_size': 500,
                'legend': '1.04 - 1.20',
                'legend_measurement_units': '',
                'max_value': 1.2,
                'min_value': 1.042,
                'legend_precision': 2,
                'extra': {
                    'base_class': b'econom',
                    'free': 0.667,
                    'free_chain': 0.333,
                    'pins': 5.0,
                    'pins_driver': 0.667,
                    'pins_order': 1.333,
                    'surge': 1.3,
                    'total': 1.333,
                },
                'tl': {'lat': 50.0, 'lon': 37.0},
                'br': {'lat': 52.0, 'lon': 39.0},
            },
            'values': [
                {'value': 1.063, 'weight': 0.163, 'x': 179, 'y': 256},
                {'value': 1.101, 'weight': 0.225, 'x': 179, 'y': 257},
                {'value': 1.101, 'weight': 0.225, 'x': 179, 'y': 258},
                {'value': 1.063, 'weight': 0.163, 'x': 179, 'y': 259},
                {'value': 1.063, 'weight': 0.163, 'x': 180, 'y': 254},
                {'value': 1.101, 'weight': 0.225, 'x': 180, 'y': 255},
                {'value': 1.139, 'weight': 0.369, 'x': 180, 'y': 256},
                {'value': 1.152, 'weight': 0.461, 'x': 180, 'y': 257},
                {'value': 1.148, 'weight': 0.432, 'x': 180, 'y': 258},
                {'value': 1.13, 'weight': 0.319, 'x': 180, 'y': 259},
                {'value': 1.084, 'weight': 0.193, 'x': 180, 'y': 260},
                {'value': 1.042, 'weight': 0.142, 'x': 181, 'y': 253},
                {'value': 1.091, 'weight': 0.205, 'x': 181, 'y': 254},
                {'value': 1.144, 'weight': 0.402, 'x': 181, 'y': 255},
                {'value': 1.166, 'weight': 0.649, 'x': 181, 'y': 256},
                {
                    'pin_info': {
                        'avg_cost': 99.9,
                        'cost_count': 1,
                        'free': 1,
                        'free_chain': 0,
                        'pins': 5,
                        'total': 1,
                        'found_share': 0.5,
                    },
                    'value': 1.2,
                    'weight': 0.647,
                    'x': 181,
                    'y': 257,
                },
                {
                    'pin_info': {
                        'avg_cost': 99.9,
                        'cost_count': 1,
                        'free': 1,
                        'free_chain': 0,
                        'pins': 5,
                        'total': 1,
                        'found_share': 0.5,
                    },
                    'value': 1.2,
                    'weight': 0.617,
                    'x': 181,
                    'y': 258,
                },
                {'value': 1.16, 'weight': 0.555, 'x': 181, 'y': 259},
                {'value': 1.127, 'weight': 0.308, 'x': 181, 'y': 260},
                {'value': 1.073, 'weight': 0.0, 'x': 181, 'y': 261},
                {'value': 1.064, 'weight': 0.165, 'x': 182, 'y': 253},
                {'value': 1.113, 'weight': 0.257, 'x': 182, 'y': 254},
                {
                    'pin_info': {
                        'avg_cost': 99.9,
                        'cost_count': 1,
                        'free': 1,
                        'free_chain': 0,
                        'pins': 5,
                        'total': 1,
                        'found_share': 0.5,
                    },
                    'value': 1.2,
                    'weight': 0.401,
                    'x': 182,
                    'y': 255,
                },
                {
                    'pin_info': {
                        'avg_cost': 99.9,
                        'cost_count': 1,
                        'free': 1,
                        'free_chain': 0,
                        'pins': 5,
                        'total': 1,
                        'found_share': 0.5,
                    },
                    'value': 1.2,
                    'weight': 0.74,
                    'x': 182,
                    'y': 256,
                },
                {
                    'pin_info': {
                        'avg_cost': 99.9,
                        'cost_count': 1,
                        'free': 1,
                        'free_chain': 0,
                        'pins': 5,
                        'total': 1,
                        'found_share': 0.5,
                    },
                    'value': 1.2,
                    'weight': 1.0,
                    'x': 182,
                    'y': 257,
                },
                {
                    'pin_info': {
                        'avg_cost': 99.9,
                        'cost_count': 1,
                        'free': 1,
                        'free_chain': 0,
                        'pins': 5,
                        'total': 1,
                        'found_share': 0.5,
                    },
                    'value': 1.2,
                    'weight': 0.897,
                    'x': 182,
                    'y': 258,
                },
                {
                    'pin_info': {
                        'avg_cost': 99.9,
                        'cost_count': 1,
                        'free': 1,
                        'free_chain': 0,
                        'pins': 5,
                        'total': 1,
                        'found_share': 0.5,
                    },
                    'value': 1.2,
                    'weight': 0.588,
                    'x': 182,
                    'y': 259,
                },
                {'value': 1.141, 'weight': 0.381, 'x': 182, 'y': 260},
                {'value': 1.085, 'weight': 0.195, 'x': 182, 'y': 261},
                {'value': 1.042, 'weight': 0.142, 'x': 183, 'y': 253},
                {'value': 1.122, 'weight': 0.288, 'x': 183, 'y': 254},
                {'value': 1.158, 'weight': 0.536, 'x': 183, 'y': 255},
                {
                    'pin_info': {
                        'avg_cost': 99.9,
                        'cost_count': 1,
                        'free': 1,
                        'free_chain': 0,
                        'pins': 5,
                        'total': 1,
                        'found_share': 0.5,
                    },
                    'value': 1.2,
                    'weight': 0.772,
                    'x': 183,
                    'y': 256,
                },
                {
                    'pin_info': {
                        'avg_cost': 99.9,
                        'cost_count': 1,
                        'free': 1,
                        'free_chain': 0,
                        'pins': 5,
                        'total': 1,
                        'found_share': 0.5,
                    },
                    'value': 1.2,
                    'weight': 0.989,
                    'x': 183,
                    'y': 257,
                },
                {
                    'pin_info': {
                        'avg_cost': 99.9,
                        'cost_count': 1,
                        'free': 1,
                        'free_chain': 0,
                        'pins': 5,
                        'total': 1,
                        'found_share': 0.5,
                    },
                    'value': 1.2,
                    'weight': 0.896,
                    'x': 183,
                    'y': 258,
                },
                {
                    'pin_info': {
                        'avg_cost': 99.9,
                        'cost_count': 1,
                        'free': 1,
                        'free_chain': 0,
                        'pins': 5,
                        'total': 1,
                        'found_share': 0.5,
                    },
                    'value': 1.2,
                    'weight': 0.585,
                    'x': 183,
                    'y': 259,
                },
                {'value': 1.136, 'weight': 0.35, 'x': 183, 'y': 260},
                {'value': 1.064, 'weight': 0.165, 'x': 183, 'y': 261},
                {'value': 1.051, 'weight': 0.0, 'x': 184, 'y': 253},
                {'value': 1.097, 'weight': 0.216, 'x': 184, 'y': 254},
                {'value': 1.152, 'weight': 0.463, 'x': 184, 'y': 255},
                {
                    'pin_info': {
                        'avg_cost': 99.9,
                        'cost_count': 1,
                        'free': 1,
                        'free_chain': 0,
                        'pins': 5,
                        'total': 1,
                        'found_share': 0.5,
                    },
                    'value': 1.2,
                    'weight': 0.607,
                    'x': 184,
                    'y': 256,
                },
                {
                    'pin_info': {
                        'avg_cost': 99.9,
                        'cost_count': 1,
                        'free': 1,
                        'free_chain': 0,
                        'pins': 5,
                        'total': 1,
                        'found_share': 0.5,
                    },
                    'value': 1.2,
                    'weight': 0.71,
                    'x': 184,
                    'y': 257,
                },
                {
                    'pin_info': {
                        'avg_cost': 99.9,
                        'cost_count': 1,
                        'free': 1,
                        'free_chain': 0,
                        'pins': 5,
                        'total': 1,
                        'found_share': 0.5,
                    },
                    'value': 1.2,
                    'weight': 0.7,
                    'x': 184,
                    'y': 258,
                },
                {'value': 1.16, 'weight': 0.556, 'x': 184, 'y': 259},
                {'value': 1.128, 'weight': 0.309, 'x': 184, 'y': 260},
                {'value': 1.042, 'weight': 0.142, 'x': 184, 'y': 261},
                {'value': 1.042, 'weight': 0.142, 'x': 185, 'y': 254},
                {'value': 1.113, 'weight': 0.257, 'x': 185, 'y': 255},
                {'value': 1.146, 'weight': 0.411, 'x': 185, 'y': 256},
                {'value': 1.157, 'weight': 0.525, 'x': 185, 'y': 257},
                {'value': 1.152, 'weight': 0.461, 'x': 185, 'y': 258},
                {'value': 1.13, 'weight': 0.318, 'x': 185, 'y': 259},
                {'value': 1.063, 'weight': 0.163, 'x': 185, 'y': 260},
                {'value': 1.063, 'weight': 0.163, 'x': 186, 'y': 255},
                {'value': 1.101, 'weight': 0.225, 'x': 186, 'y': 256},
                {'value': 1.119, 'weight': 0.277, 'x': 186, 'y': 257},
                {'value': 1.101, 'weight': 0.226, 'x': 186, 'y': 258},
                {'value': 1.063, 'weight': 0.163, 'x': 186, 'y': 259},
            ],
        },
    ]
