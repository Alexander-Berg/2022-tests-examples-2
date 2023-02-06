import math


import pytest


DATA = {
    'drivers': [
        {'park_id': 'park_0', 'car_id': 'car_0', 'driver_id': 'driver_0'},
        {'park_id': 'park_0', 'car_id': 'car_0', 'driver_id': 'driver_1'},
        {'park_id': 'park_0', 'car_id': 'car_1', 'driver_id': 'driver_1'},
        {'park_id': 'park_1', 'car_id': 'car_1', 'driver_id': 'driver_0'},
    ],
}


def _get_output(get_child_tariff):
    output = {
        'drivers': [
            {
                'park_id': 'park_0',
                'car_id': 'car_0',
                'driver_id': 'driver_0',
                'categories': [],
            },
            {
                'park_id': 'park_0',
                'car_id': 'car_0',
                'driver_id': 'driver_1',
                'categories': [],
            },
            {
                'park_id': 'park_0',
                'car_id': 'car_1',
                'driver_id': 'driver_1',
                'categories': [
                    'business',
                    'business2',
                    'cargo',
                    'comfortplus',
                    'courier',
                    'demostand',
                    'econom',
                    'eda',
                    'express',
                    'lavka',
                    'limousine',
                    'maybach',
                    'minibus',
                    'minivan',
                    'mkk',
                    'mkk_antifraud',
                    'night',
                    'park_vip',
                    'personal_driver',
                    'pool',
                    'premium_suv',
                    'premium_van',
                    'promo',
                    'scooters',
                    'selfdriving',
                    'standart',
                    'start',
                    'suv',
                    'trucking',
                    'ultimate',
                    'universal',
                    'vip',
                ],
            },
            {
                'park_id': 'park_1',
                'car_id': 'car_1',
                'driver_id': 'driver_0',
                'categories': [
                    'business',
                    'business2',
                    'comfortplus',
                    'courier',
                    'demostand',
                    'econom',
                    'express',
                    'limousine',
                    'maybach',
                    'minibus',
                ],
            },
        ],
    }
    if get_child_tariff:
        output['drivers'][2]['categories'].append('child_tariff')
        output['drivers'][2]['categories'].sort()
    return output


@pytest.mark.pgsql('driver-categories-api', files=['categories.sql'])
@pytest.mark.redis_store(
    ['hset', 'RobotSettings:park_0:Settings', 'driver_0', '0'],
    ['hset', 'RobotSettings:park_0:Settings', 'driver_1', '0'],
    ['hset', 'RobotSettings:park_1:Settings', 'driver_0', '66003072'],
)
@pytest.mark.parametrize(
    'data,child_tariff_source,code,output',
    [
        pytest.param({}, '__disabled__', 400, {}, id='Bad request'),
        pytest.param(
            {'drivers': []},
            '__disabled__',
            200,
            {'drivers': []},
            id='Empty drivers array',
        ),
        pytest.param(
            DATA,
            'xservice',
            200,
            _get_output(get_child_tariff=True),
            id='Good request (use xservice for child_tariff)',
        ),
        pytest.param(
            DATA,
            'fleet-vehicles',
            200,
            _get_output(get_child_tariff=True),
            id='Good request (use fleet-vehicles for child_tariff)',
        ),
        pytest.param(
            DATA,
            '__disabled__',
            200,
            _get_output(get_child_tariff=False),
            id='Good request (disable child_tariff check)',
        ),
    ],
)
@pytest.mark.parametrize('child_tariff_bulk_chunk_size', [1000, 2])
@pytest.mark.parametrize('use_pg', [False, True])
async def test_driver_categories_get(
        taxi_driver_categories_api,
        mockserver,
        load_json,
        taxi_config,
        driver_authorizer,
        driver_profiles,
        fleet_parks,
        fleet_vehicles,
        parks,
        taximeter_xservice,
        data,
        child_tariff_source,
        code,
        output,
        child_tariff_bulk_chunk_size,
        use_pg,
):
    @mockserver.json_handler('/taximeter-xservice/utils/qc/child_seats_bulk')
    def utils_qc_child_seats_bulk(request):
        return mockserver.make_response(
            json=load_json('taximeter_xservice.json'), status=200,
        )

    @mockserver.json_handler(
        '/fleet-vehicles/v1/vehicles/driver/has-child-tariff-bulk',
    )
    def has_child_tariff_bulk(request):
        return mockserver.make_response(
            json=load_json('fleet_vehicles.json')['has-child-tariff-bulk'],
            status=200,
        )

    taxi_config.set_values(
        {
            'DRIVER_CATEGORIES_API_DATA_SOURCE': {
                '/v2/aggregation/categories': {'use_pg': use_pg},
                '__default__': {'use_pg': False},
            },
            'DRIVER_CATEGORIES_API_CHILD_TARIFF_SOURCE': {
                '__default__': {'child_tariff_source': child_tariff_source},
            },
            'DRIVER_CATEGORIES_API_MAX_BULK_CHILD_TARIFF': (
                child_tariff_bulk_chunk_size
            ),
        },
    )

    await taxi_driver_categories_api.invalidate_caches()

    response = await taxi_driver_categories_api.post(
        'v2/aggregation/categories', json=data,
    )

    assert utils_qc_child_seats_bulk.times_called == (
        math.ceil(len(data['drivers']) / child_tariff_bulk_chunk_size)
        if child_tariff_source == 'xservice'
        else 0
    )

    assert has_child_tariff_bulk.times_called == (
        math.ceil(len(data['drivers']) / child_tariff_bulk_chunk_size)
        if child_tariff_source == 'fleet-vehicles'
        else 0
    )

    assert response.status_code == code

    if not output:
        return

    got_response = {'drivers': []}
    for item in response.json()['drivers']:
        item['categories'].sort()
        got_response['drivers'].append(item)
    assert got_response == output
