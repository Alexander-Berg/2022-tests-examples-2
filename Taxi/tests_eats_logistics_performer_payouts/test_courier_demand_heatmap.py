import pytest


CATALOG_PLACES_JSON = [
    {
        'id': 0,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [47.525496503606774, 55.75568074159372]},
        'region': {'id': 2, 'geobase_ids': [1, 2, 3], 'time_zone': 'UTC+3'},
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
        'type': 'native',
        'enabled': True,
    },
    {
        'id': 1,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [47.525496503606774, 55.75568074159372]},
        'region': {'id': 2, 'geobase_ids': [1, 2, 3], 'time_zone': 'UTC+3'},
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
        'type': 'native',
        'enabled': True,
    },
    {
        'id': 2,
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'location': {'geo_point': [47.526396503606774, 55.75898074159372]},
        'region': {'id': 3, 'geobase_ids': [1, 2, 3], 'time_zone': 'UTC+3'},
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
        'type': 'native',
        'enabled': True,
    },
]

SURGE_PLACES_JSON = [
    # 0
    {'load_level': 31},
    # 1
    {'load_level': 71},
    # 2
    {'load_level': 105},
]


HANDLER_ADD_SAMPLES = '/heatmap-sample-storage/v1/add_samples'


def mk_json_add_samples(request):
    sample = request.json['samples'][0]
    assert sample['type'] == 'eda_surge'
    assert sample['map_name'] == 'courier_demand/default'
    return {'timestamp': '2021-05-11T00:00:00+00:00'}


HANDLER_SURGE_LEVEL = '/eats-surge-resolver/api/v1/surge-level'


def mk_json_surge_level(request):
    json = {'jsonrpc': '2.0', 'id': 1, 'result': []}
    for place_id in request.json['params']['placeIds']:
        place_json = {
            'placeId': place_id,
            'nativeInfo': {
                'surgeLevel': 0,
                'loadLevel': SURGE_PLACES_JSON[place_id]['load_level'],
                'deliveryFee': 228.0,
            },
            'taxiInfo': {'surgeLevel': 8, 'show_radius': 3000.0},
            'calculatorName': 'calc_surge_eats_dummy_dummy',
        }
        json['result'].append(place_json)

    return json


TASK_NAME = 'courier-demand-heatmap'


@pytest.mark.experiments3(
    name='eats_pauouts_courier_demand_pipeline_arguments',
    consumers=['eats-logistics-performer-payouts/courier-demand-calculator'],
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={
        'pipeline_name': 'courier_demand_pclinear',
        'coeff_basic': 1.1,
        'coeff_low_density': 1.4,
        'coeff_ll_min': 50,
        'coeff_ll_max': 75,
        'coeff_surge_slope': 14.0,
    },
    clauses=[],
)
@pytest.mark.experiments3(
    name='eats_payouts_courier_demand_show',
    consumers=['eats-logistics-performer-payouts/courier-demand-heatmap'],
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={'enabled': True},
    clauses=[],
)
@pytest.mark.eats_catalog_storage_cache(CATALOG_PLACES_JSON)
@pytest.mark.now('2021-05-11T01:00:30+00:00')
@pytest.mark.parametrize(
    'call_cnt_map',
    [
        pytest.param(
            {HANDLER_SURGE_LEVEL: 1, HANDLER_ADD_SAMPLES: 1}, id='happy path',
        ),
    ],
)
async def test_handle_order_created(
        call_cnt_map, mockserver, taxi_eats_logistics_performer_payouts,
):
    @mockserver.json_handler(HANDLER_SURGE_LEVEL)
    def surge_level_handler(request):
        return mk_json_surge_level(request)

    @mockserver.json_handler(HANDLER_ADD_SAMPLES)
    def add_samples_handler(request):
        return mk_json_add_samples(request)

    await taxi_eats_logistics_performer_payouts.run_periodic_task(
        f'{TASK_NAME}-periodic',
    )

    assert (
        surge_level_handler.times_called == call_cnt_map[HANDLER_SURGE_LEVEL]
    )
    assert (
        add_samples_handler.times_called == call_cnt_map[HANDLER_ADD_SAMPLES]
    )
