import pytest


def get_headers(params):
    headers = {}
    if 'park_id' in params:
        headers['X-YaTaxi-Park-Id'] = params['park_id']
    if 'driver_id' in params:
        headers['X-YaTaxi-Driver-Profile-Id'] = params['driver_id']

    headers['X-Request-Application'] = 'taximeter'
    headers['X-Request-Platform'] = 'android'
    headers['X-Request-Application-Version'] = '9.30 (2345)'
    headers['Accept-Language'] = 'ru'

    return headers


@pytest.mark.parametrize(
    'params,query,code,expected,exp3_values,config',
    [
        pytest.param(
            {'driver_id': 'shadow_driver'},
            {},
            400,
            {},
            {},
            {},
            id='No park_id',
        ),
        pytest.param(
            {'park_id': 'shadow_park', 'driver_id': 'shadow_driver'},
            {},
            200,
            {
                'categories': [
                    {
                        'is_enabled': False,
                        'mask': 2,
                        'name': 'child_tariff',
                        'title': 'Категория 2',
                        'type': 'yandex',
                    },
                    {
                        'is_enabled': False,
                        'mask': 1,
                        'name': 'econom',
                        'title': 'Категория 1',
                        'type': 'yandex',
                    },
                ],
                'groups': [],
            },
            {},
            {},
            id='Good request',
        ),
        pytest.param(
            {'park_id': 'park_0', 'driver_id': 'driver_0'},
            {},
            200,
            {
                'categories': [
                    {
                        'is_enabled': False,
                        'mask': 2,
                        'name': 'child_tariff',
                        'title': 'Категория 2',
                        'type': 'yandex',
                    },
                    {
                        'is_enabled': False,
                        'mask': 1,
                        'name': 'econom',
                        'title': 'Категория 1',
                        'type': 'yandex',
                        'block_info': {
                            'block_reason': 'Many reasons',
                            'is_blocked_by_exam': False,
                            'deeplink': '/deeplink1',
                        },
                    },
                ],
                'groups': [{'category_names': ['econom'], 'id': 'default'}],
            },
            {},
            {},
            id='Driver with blocked category',
        ),
        pytest.param(
            {'park_id': 'park_1', 'driver_id': 'driver_1'},
            {},
            200,
            {
                'categories': [
                    {
                        'is_enabled': True,
                        'mask': 2,
                        'name': 'child_tariff',
                        'title': 'Категория 2',
                        'type': 'yandex',
                    },
                    {
                        'is_enabled': True,
                        'mask': 1,
                        'name': 'econom',
                        'title': 'Категория 1',
                        'type': 'yandex',
                    },
                ],
                'groups': [
                    {
                        'category_names': ['child_tariff', 'econom'],
                        'id': 'default',
                    },
                ],
            },
            {},
            {},
            id='Check whether categories in groups are sorted',
        ),
        pytest.param(
            {'park_id': 'park_2', 'driver_id': 'driver_2'},
            {},
            200,
            {
                'categories': [
                    {
                        'is_enabled': False,
                        'mask': 2,
                        'name': 'child_tariff',
                        'title': 'Категория 2',
                        'type': 'yandex',
                    },
                    {
                        'is_enabled': False,
                        'mask': 1,
                        'name': 'econom',
                        'title': 'Категория 1',
                        'type': 'yandex',
                    },
                ],
                'groups': [],
            },
            {'driver_categories_settings': {'show_in_taximeter': False}},
            {},
            id='Categories disabled by config',
        ),
        pytest.param(
            {'park_id': 'park_3', 'driver_id': 'driver_3'},
            {},
            200,
            {
                'categories': [
                    {
                        'is_enabled': True,
                        'mask': 2,
                        'name': 'child_tariff',
                        'title': 'Категория 2',
                        'type': 'yandex',
                    },
                    {
                        'is_enabled': False,
                        'mask': 1,
                        'name': 'econom',
                        'title': 'Категория 1',
                        'type': 'yandex',
                    },
                ],
                'groups': [
                    {'category_names': ['child_tariff'], 'id': 'default'},
                ],
            },
            {
                'child_tariff_visibility_settings': {
                    'always_show_in_taximeter': True,
                },
            },
            {},
            id='Check child_tariff is shown by default',
        ),
        pytest.param(
            {
                'park_id': 'park_coord_city',
                'driver_id': 'driver_with_coordinates',
            },
            {'lat': 1.0, 'lon': 1.0},
            200,
            {
                'categories': [
                    {
                        'is_enabled': False,
                        'mask': 2,
                        'name': 'child_tariff',
                        'title': 'Категория 2',
                        'type': 'yandex',
                    },
                    {
                        'is_enabled': False,
                        'mask': 1,
                        'name': 'econom',
                        'title': 'Категория 1',
                        'type': 'yandex',
                        'block_info': {
                            'block_reason': 'Position 1.0 1.0',
                            'is_blocked_by_exam': False,
                            'deeplink': '/deeplink1',
                        },
                    },
                ],
                'groups': [{'category_names': ['econom'], 'id': 'default'}],
            },
            {},
            {},
            id='Check getting position from application',
        ),
        pytest.param(
            {
                'park_id': 'park_coord_city',
                'driver_id': 'driver_without_coordinates',
            },
            {'lat': 1.0, 'lon': 1.0},
            200,
            {
                'categories': [
                    {
                        'is_enabled': False,
                        'mask': 2,
                        'name': 'child_tariff',
                        'title': 'Категория 2',
                        'type': 'yandex',
                    },
                    {
                        'is_enabled': False,
                        'mask': 1,
                        'name': 'econom',
                        'title': 'Категория 1',
                        'type': 'yandex',
                        'block_info': {
                            'block_reason': 'Position 2.0 2.0',
                            'is_blocked_by_exam': False,
                            'deeplink': '/deeplink1',
                        },
                    },
                ],
                'groups': [{'category_names': ['econom'], 'id': 'default'}],
            },
            {},
            {},
            id='Check getting position from driver-trackstory',
        ),
        pytest.param(
            {
                'park_id': 'park_coord_city',
                'driver_id': 'driver_without_coordinates_2',
            },
            {},
            200,
            {
                'categories': [
                    {
                        'is_enabled': False,
                        'mask': 2,
                        'name': 'child_tariff',
                        'title': 'Категория 2',
                        'type': 'yandex',
                    },
                    {
                        'is_enabled': False,
                        'mask': 1,
                        'name': 'econom',
                        'title': 'Категория 1',
                        'type': 'yandex',
                        'block_info': {
                            'block_reason': 'Position 0.0 0.0',
                            'is_blocked_by_exam': False,
                            'deeplink': '/deeplink1',
                        },
                    },
                ],
                'groups': [{'category_names': ['econom'], 'id': 'default'}],
            },
            {},
            {},
            id='Failed getting position',
        ),
        pytest.param(
            {'park_id': 'park_1', 'driver_id': 'driver_1'},
            {},
            200,
            {
                'categories': [
                    {
                        'is_enabled': False,
                        'mask': 2,
                        'name': 'child_tariff',
                        'title': 'Категория 2',
                        'type': 'yandex',
                    },
                    {
                        'is_enabled': True,
                        'mask': 1,
                        'name': 'econom',
                        'title': 'Категория 1',
                        'type': 'yandex',
                    },
                ],
                'groups': [{'category_names': ['econom'], 'id': 'default'}],
            },
            {},
            {
                'DRIVER_CATEGORIES_API_CHILD_TARIFF_SOURCE': {
                    '__default__': {'child_tariff_source': 'xservice'},
                    '/driver/v1/categories-api/v2/categories': {
                        'child_tariff_source': '__disabled__',
                    },
                },
            },
            id='Disable checking child_tariff',
        ),
        pytest.param(
            {'park_id': 'park_4', 'driver_id': 'driver_4'},
            {},
            200,
            {
                'categories': [
                    {
                        'is_enabled': True,
                        'mask': 2,
                        'name': 'child_tariff',
                        'title': 'Категория 2',
                        'type': 'yandex',
                    },
                    {
                        'is_enabled': False,
                        'mask': 1,
                        'name': 'econom',
                        'title': 'Категория 1',
                        'type': 'yandex',
                    },
                ],
                'groups': [
                    {'category_names': ['child_tariff'], 'id': 'default'},
                ],
            },
            {},
            {
                'DRIVER_CATEGORIES_API_CHILD_TARIFF_SOURCE': {
                    '__default__': {'child_tariff_source': 'xservice'},
                    '/driver/v1/categories-api/v2/categories': {
                        'child_tariff_source': 'fleet-vehicles',
                    },
                },
            },
            id='Checking child_tariff via fleet-vehicles',
        ),
        pytest.param(
            {'park_id': 'shadow_park', 'driver_id': 'shadow_driver'},
            {},
            200,
            {
                'categories': [
                    {
                        'is_enabled': False,
                        'mask': 2,
                        'name': 'child_tariff',
                        'title': 'Категория 4',
                        'type': 'yandex',
                    },
                    {
                        'is_enabled': False,
                        'mask': 1,
                        'name': 'econom',
                        'title': 'Категория 3',
                        'type': 'yandex',
                    },
                ],
                'groups': [],
            },
            {},
            {
                'DRIVER_CATEGORIES_API_CATEGORIES_DESCRIPTIONS': {
                    'econom': {
                        '__default__': {
                            'name_key': 'car_category_1',
                            'short_name_key': 'car_category_1_short',
                        },
                        'rus': {
                            'name_key': 'car_category_3',
                            'short_name_key': 'car_category_1_short',
                        },
                    },
                    'child_tariff': {
                        '__default__': {
                            'name_key': 'car_category_2',
                            'short_name_key': 'car_category_2_short',
                        },
                        'rus': {
                            'name_key': 'car_category_4',
                            'short_name_key': 'car_category_1_short',
                        },
                    },
                },
            },
            id='Override categories names',
        ),
    ],
)
@pytest.mark.pgsql('driver-categories-api', files=['categories.sql'])
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize('use_query_positions', [False, True])
async def test_driver_categories_get(
        taxi_driver_categories_api,
        taxi_config,
        driver_diagnostics,
        driver_profiles,
        driver_tags,
        driver_trackstory,
        experiments3,
        fleet_parks,
        fleet_vehicles,
        taximeter_xservice,
        pgsql,
        load_json,
        params,
        query,
        code,
        expected,
        exp3_values,
        config,
        use_query_positions,
        mockserver,
):
    @mockserver.json_handler('/yagr-raw/service/v2/position/store')
    def yagr_handler(request):
        # pylint: disable=unused-variable
        return ''

    exp3_json_file = load_json('experiments3_defaults.json')
    for exp3_config in exp3_json_file['configs']:
        exp3_name = exp3_config['name']
        if exp3_name in exp3_values:
            exp3_config['default_value'] = exp3_values[exp3_name]

    experiments3.add_experiments_json(exp3_json_file)

    taxi_config.set_values(config)
    taxi_config.set_values(
        {
            'DRIVER_CATEGORIES_API_USE_QUERY_POSITIONS': {
                'percent': 100 if use_query_positions else 0,
                'source': 'all',
                'max_age': 100,
                'max_retries': 3,
                'timeout': 50,
                'min_positions_required_count': 1,
            },
        },
    )

    await taxi_driver_categories_api.invalidate_caches()

    response = await taxi_driver_categories_api.get(
        '/driver/v1/categories-api/v2/categories',
        params=query,
        headers=get_headers(params),
    )
    assert response.status_code == code

    if response.status_code != 200:
        return

    got_response = response.json()
    if 'categories' in got_response:
        got_response['categories'].sort(key=lambda x: x['name'])
    assert got_response == expected


@pytest.mark.experiments3(
    name='child_tariff_visibility_settings',
    consumers=['driver-categories-api'],
    clauses=[
        {
            'title': 'ios',
            'predicate': {
                'init': {
                    'arg_name': 'application',
                    'arg_type': 'string',
                    'value': 'taximeter-ios',
                },
                'type': 'eq',
            },
            'value': {'always_show_in_taximeter': False},
        },
        {
            'title': 'all the other',
            'predicate': {'type': 'true'},
            'value': {'always_show_in_taximeter': True},
        },
    ],
    is_config=True,
)
@pytest.mark.config(
    DRIVER_CATEGORIES_API_CHILD_TARIFF_SOURCE={
        '__default__': {'child_tariff_source': 'fleet-vehicles'},
    },
)
@pytest.mark.parametrize('is_ios', [True, False])
@pytest.mark.pgsql('driver-categories-api', files=['categories.sql'])
async def test_driver_categories_get_ios(
        taxi_driver_categories_api,
        driver_diagnostics,
        driver_profiles,
        driver_tags,
        driver_trackstory,
        fleet_parks,
        fleet_vehicles,
        taximeter_xservice,
        experiments3,
        load_json,
        is_ios,
):
    exp3_json = load_json('experiments3_defaults.json')
    configs_to_add = list(
        filter(
            lambda x: x['name'] != 'child_tariff_visibility_settings',
            exp3_json['configs'],
        ),
    )
    experiments3.add_experiments_json({'configs': configs_to_add})

    headers = get_headers({'park_id': 'park_0', 'driver_id': 'driver_0'})
    if is_ios:
        headers['X-Request-Platform'] = 'ios'

    response = await taxi_driver_categories_api.get(
        '/driver/v1/categories-api/v2/categories', headers=headers,
    )
    assert response.status_code == 200

    response_json = response.json()
    child_tariff = [
        item
        for item in response_json['categories']
        if item['name'] == 'child_tariff'
    ]

    assert len(child_tariff) == 1
    assert child_tariff[0]['is_enabled'] is not is_ios


@pytest.mark.pgsql('driver-categories-api', files=['categories_group.sql'])
@pytest.mark.config(
    DRIVER_CATEGORIES_API_CATEGORIES_DESCRIPTIONS={
        'econom': {
            '__default__': {
                'name_key': 'car_category_econom',
                'short_name_key': 'car_category_econom',
            },
        },
        'comfortplus': {
            '__default__': {
                'name_key': 'car_category_comfortplus',
                'short_name_key': 'car_category_comfortplus',
            },
        },
        'express': {
            '__default__': {
                'name_key': 'car_category_express',
                'short_name_key': 'car_category_express',
            },
        },
        'scooters': {
            '__default__': {
                'name_key': 'car_category_scooters',
                'short_name_key': 'car_category_scooters',
            },
        },
    },
)
@pytest.mark.parametrize(
    'config_value,params,expected_groups_response',
    [
        pytest.param(
            'empty_group',
            {'park_id': 'park_group_0', 'driver_id': 'driver_group_0'},
            [{'category_names': ['econom'], 'id': 'default'}],
            id='empty_group',
        ),
        pytest.param(
            'empty_car_categories',
            {'park_id': 'park_group_0', 'driver_id': 'driver_group_1'},
            [],
            id='empty_car_categories',
        ),
        pytest.param(
            'one_group',
            {'park_id': 'park_group_1', 'driver_id': 'driver_group_1'},
            [
                {
                    'category_names': ['econom', 'comfortplus'],
                    'id': 'id_1',
                    'display_name': 'Группа 1',
                },
            ],
            id='one_group',
        ),
        pytest.param(
            'two_groups',
            {'park_id': 'park_group_2', 'driver_id': 'driver_group_2'},
            [
                {
                    'category_names': ['econom', 'comfortplus'],
                    'id': 'id_1',
                    'display_name': 'Группа 1',
                },
                {
                    'category_names': ['scooters', 'express'],
                    'id': 'id_2',
                    'display_name': 'Группа 2',
                },
            ],
            id='two_groups',
        ),
        pytest.param(
            'two_groups_category_override',
            {'park_id': 'park_group_2', 'driver_id': 'driver_group_2'},
            [
                {'category_names': ['scooters'], 'id': 'default'},
                {
                    'category_names': ['econom', 'comfortplus'],
                    'id': 'id_1',
                    'display_name': 'Группа 1',
                },
                {
                    'category_names': ['express'],
                    'id': 'id_2',
                    'display_name': 'Группа 2',
                },
            ],
            id='two_groups_category_override',
        ),
        pytest.param(
            'two_groups_group_id_override',
            {'park_id': 'park_group_2', 'driver_id': 'driver_group_2'},
            [
                {
                    'category_names': [
                        'econom',
                        'scooters',
                        'express',
                        'comfortplus',
                    ],
                    'id': 'id_1',
                    'display_name': 'Группа 1',
                },
            ],
            id='two_groups_group_id_override',
        ),
        pytest.param(
            'insufficient_categories',
            {'park_id': 'park_group_2', 'driver_id': 'driver_group_2'},
            [
                {
                    'category_names': ['scooters', 'comfortplus'],
                    'id': 'default',
                },
                {
                    'category_names': ['econom'],
                    'id': 'id_1',
                    'display_name': 'Группа 1',
                },
                {
                    'category_names': ['express'],
                    'id': 'id_2',
                    'display_name': 'Группа 2',
                },
            ],
            id='insufficient_categories',
        ),
    ],
)
async def test_driver_categories_grouping(
        taxi_driver_categories_api,
        driver_diagnostics,
        driver_profiles,
        driver_tags,
        driver_trackstory,
        fleet_parks,
        fleet_vehicles,
        taximeter_xservice,
        load_json,
        experiments3,
        config_value,
        params,
        expected_groups_response,
):
    config_values = load_json('grouping_config_values.json')
    exp3_json_file = load_json('experiments3_defaults.json')
    configs = exp3_json_file['configs']
    for config in configs:
        if config['name'] == 'driver_categories_api_categories_grouping':
            config['default_value'] = config_values[config_value]

    experiments3.add_experiments_json(exp3_json_file)

    response = await taxi_driver_categories_api.get(
        '/driver/v1/categories-api/v2/categories',
        params={'lat': 52, 'lon': 39},
        headers=get_headers(params),
    )

    got_response = response.json()
    assert got_response['groups'] == expected_groups_response
