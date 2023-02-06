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
            {'pins': 9, 'radius': 2500},
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
@pytest.mark.experiments3(filename='calc_surge_cells_settings_exp.json')
@pytest.mark.experiments3(filename='calc_surge_cells_settings.json')
@pytest.mark.config(
    CALC_SURGE_CELLS_WORKER_ENABLED=True,
    CALC_SURGE_CELLS_DRIVER_MAP_LAYERS_OVERRIDE={
        'default': ['default', 'alternative'],
    },
    HEATMAP_SAMPLES_TYPES=['taxi_surge'],
)
@pytest.mark.suspend_periodic_tasks('calc-surge-cells-worker')
async def test_calc_surge_cells(
        taxi_heatmap_sample_storage, mockserver, testpoint, redis_store,
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
        'arg': {'maps_saved': 6, 'save_map_errors': 0, 'fetch_task_errors': 0},
    }

    assert actual_saved_map.keys() == {
        'taxi_surge_full/__default__/default_exp',
        'taxi_surge_full/__default__/default',
        'taxi_surge_lightweight/__default__/default',
        'taxi_surge_lightweight/__default__/default_exp',
        'taxi_surge/__default__/default_exp',
        'taxi_surge/__default__/default',
    }
    assert mock_insert_map.times_called == 6
    driver_experimental_map = actual_saved_map[
        'taxi_surge/__default__/default_exp'
    ]

    assert common.parse_map(driver_experimental_map) == [
        {
            'hex_grid': {
                'cells_size': 1000,  # cells size from exp configs
                'legend': '1.2 - 1.3',
                'legend_measurement_units': '',
                'max_value': 1.3,
                'min_value': 1.208,
                'legend_precision': 1,
                'extra': None,
                'tl': {'lat': 50.0, 'lon': 37.0},
                'br': {'lat': 52.0, 'lon': 39.0},
            },
            'values': [
                {'value': 1.218, 'weight': 0.728, 'x': 91, 'y': 128},
                {'value': 1.3, 'weight': 1.0, 'x': 91, 'y': 129},
                {'value': 1.208, 'weight': 0.692, 'x': 91, 'y': 130},
                {'value': 1.251, 'weight': 0.835, 'x': 92, 'y': 128},
                {'value': 1.261, 'weight': 0.871, 'x': 92, 'y': 129},
            ],
        },
    ]
    # prod map is unaffected
    driver_prod_map = actual_saved_map['taxi_surge/__default__/default']
    assert (
        common.parse_map(driver_prod_map)[0]['hex_grid']['cells_size'] == 500
    )


# +5 min after samples' 'created' time
@pytest.mark.now('2019-03-08T00:05:00Z')
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
            {'pins': 1, 'radius': 2500},
            1552003200000,
        ),
    ],
    [
        'rpush',
        'taxi_surge:1552003200',
        common.build_sample(
            38.005,
            51.005,
            'taxi_surge',
            'econom/default',
            1.3,
            1,
            {'pins': 1, 'radius': 2500},
            1552003200000,
        ),
    ],
)
@pytest.mark.redis_store(['delete', 'calc-surge-cells-tasks'])
@pytest.mark.experiments3(filename='calc_surge_cells_settings.json')
@pytest.mark.experiments3(filename='calc_surge_cells_settings_pins_query.json')
@pytest.mark.config(
    CALC_SURGE_CELLS_WORKER_ENABLED=True, HEATMAP_SAMPLES_TYPES=['taxi_surge'],
)
@pytest.mark.suspend_periodic_tasks('calc-surge-cells-worker')
async def test_pins_query(
        taxi_heatmap_sample_storage, mockserver, testpoint, redis_store,
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
        'arg': {'maps_saved': 5, 'save_map_errors': 0, 'fetch_task_errors': 0},
    }

    assert actual_saved_map.keys() == {
        'taxi_surge_lightweight/__default__/default',
        'taxi_surge_full/__default__/default',
        'taxi_surge_full/__default__/default_exp',
        'taxi_surge/__default__/default_exp',
        'taxi_surge/__default__/default',
    }
    assert mock_insert_map.times_called == 5
    driver_map = actual_saved_map['taxi_surge/__default__/default']

    assert common.parse_map(driver_map) == [
        {
            'hex_grid': {
                'cells_size': 500,
                'tl': {'lat': 50.0, 'lon': 37.0},
                'br': {'lat': 52.0, 'lon': 39.0},
                'legend': '1.2 - 1.2',
                'legend_measurement_units': '',
                'max_value': 1.207,
                'min_value': 1.193,
                'legend_precision': 1,
                'extra': None,
            },
            'values': [
                # A few cells due to small query radius
                {'value': 1.193, 'weight': 1.0, 'x': 182, 'y': 257},
                {'value': 1.207, 'weight': 1.0, 'x': 183, 'y': 259},
            ],
        },
    ]


# +5 min after samples' 'created' time
@pytest.mark.now('2019-03-08T00:05:00Z')
@pytest.mark.redis_store(
    [
        'rpush',
        'taxi_surge:1552003200',
        common.build_sample(
            38.005,
            51.105,
            'taxi_surge',
            'econom/default',
            1.3,
            1,
            {'pins': 10, 'radius': 2500},
            1552003200000,
        ),
    ],
    [
        'rpush',
        'taxi_surge:1552003200',
        common.build_sample(
            38.005,
            51.005,
            'taxi_surge',
            'econom/default',
            0.8,
            1,
            {'pins': 0, 'radius': 2500},
            1552003200000,
        ),
    ],
    [
        'rpush',
        'taxi_surge:1552003200',
        common.build_sample(
            38.005,
            51.005,
            'taxi_surge',
            'econom/default',
            0.8,
            1,
            {'pins': 0, 'radius': 2500},
            1552003200000,
        ),
    ],
)
@pytest.mark.redis_store(['delete', 'calc-surge-cells-tasks'])
@pytest.mark.experiments3(filename='calc_surge_cells_settings.json')
@pytest.mark.experiments3(filename='calc_surge_cells_settings_antisurge.json')
@pytest.mark.config(
    CALC_SURGE_CELLS_WORKER_ENABLED=True, HEATMAP_SAMPLES_TYPES=['taxi_surge'],
)
@pytest.mark.suspend_periodic_tasks('calc-surge-cells-worker')
async def test_antisurge(
        taxi_heatmap_sample_storage, mockserver, testpoint, redis_store,
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
        'arg': {'maps_saved': 5, 'save_map_errors': 0, 'fetch_task_errors': 0},
    }

    assert actual_saved_map.keys() == {
        'taxi_surge_full/__default__/default',
        'taxi_surge_full/__default__/default_exp',
        'taxi_surge_lightweight/__default__/default',
        'taxi_surge/__default__/default',
        'taxi_surge/__default__/default_exp',
    }
    assert mock_insert_map.times_called == 5
    full_map = actual_saved_map['taxi_surge_full/__default__/default']
    full_map_exp = actual_saved_map['taxi_surge_full/__default__/default_exp']
    # check prod override
    assert common.parse_map(full_map) == common.parse_map(full_map_exp)

    assert common.parse_map(full_map) == [
        {
            'hex_grid': {
                'cells_size': 1000,
                'legend': '0.80 - 1.30',
                'legend_measurement_units': '',
                'max_value': 1.3,
                'min_value': 0.8,
                'legend_precision': 2,
                'extra': {
                    'base_class': b'econom',
                    'free': 0.0,
                    'free_chain': 0.0,
                    'pins': 3.333,
                    'pins_driver': 0.0,
                    'pins_order': 0.0,
                    'surge': 0.967,
                    'total': 0.0,
                },
                'tl': {'lat': 50.0, 'lon': 37.0},
                'br': {'lat': 52.0, 'lon': 39.0},
            },
            'values': [
                {'value': 0.908, 'weight': 0.461, 'x': 91, 'y': 129},
                {'value': 0.908, 'weight': 0.461, 'x': 91, 'y': 130},
                {'value': 1.139, 'weight': 0.462, 'x': 91, 'y': 142},
                {'value': 1.139, 'weight': 0.462, 'x': 91, 'y': 143},
                {'value': 0.906, 'weight': 0.472, 'x': 92, 'y': 128},
                {
                    'pin_info': {
                        'avg_cost': 0,
                        'cost_count': 0,
                        'free': 0,
                        'free_chain': 0,
                        'pins': 0,
                        'total': 0,
                        'found_share': 0,
                    },
                    'value': 0.8,
                    'weight': 1.0,
                    'x': 92,
                    'y': 129,
                },
                {'value': 0.906, 'weight': 0.472, 'x': 92, 'y': 130},
                {'value': 1.142, 'weight': 0.472, 'x': 92, 'y': 141},
                {
                    'pin_info': {
                        'avg_cost': 0,
                        'cost_count': 0,
                        'free': 0,
                        'free_chain': 0,
                        'pins': 10,
                        'total': 0,
                        'found_share': 0,
                    },
                    'value': 1.3,
                    'weight': 1.0,
                    'x': 92,
                    'y': 142,
                },
                {'value': 1.142, 'weight': 0.472, 'x': 92, 'y': 143},
                {'value': 0.908, 'weight': 0.461, 'x': 93, 'y': 129},
                {'value': 0.908, 'weight': 0.461, 'x': 93, 'y': 130},
                {'value': 1.139, 'weight': 0.462, 'x': 93, 'y': 142},
                {'value': 1.139, 'weight': 0.462, 'x': 93, 'y': 143},
            ],
        },
    ]
