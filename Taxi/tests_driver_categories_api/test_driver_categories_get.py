import pytest


@pytest.mark.config(
    TAXIMETER_COURIER_CATEGORY_SETTINGS={
        'dbs': ['park_0', 'park_1'],
        'enable': True,
    },
    TAXIMETER_DEMOSTAND_CATEGORY_SETTINGS={
        'dbs': ['park_0', 'park_1'],
        'enable': True,
    },
    TAXIMETER_EDA_CATEGORY_SETTINGS={
        'dbs': ['park_0', 'park_1'],
        'enable': True,
    },
    TAXIMETER_LAVKA_CATEGORY_SETTINGS={
        'dbs': ['park_0', 'park_1'],
        'enable': True,
    },
    TAXIMETER_SELFDRIVING_CATEGORY_SETTINGS={
        'dbs': ['park_0'],
        'enable': True,
    },
    TAXIMETER_CARGO_CATEGORY_SETTINGS={
        'cities': [],
        'cities_disable': [],
        'countries': [],
        'countries_disable': [],
        'dbs': ['park_0'],
        'dbs_disable': [],
        'enable': True,
    },
    TAXIMETER_EXPRESS_CATEGORY_SETTINGS={
        'cities': [],
        'cities_disable': [],
        'countries': [],
        'countries_disable': [],
        'dbs': ['park_0', 'park_1'],
        'dbs_disable': [],
        'enable': True,
    },
    TAXIMETER_LIMOUSINE_CATEGORY_SETTINGS={
        'cities': [],
        'cities_disable': [],
        'countries': [],
        'countries_disable': [],
        'dbs': ['park_0', 'park_1'],
        'dbs_disable': [],
        'enable': True,
    },
    TAXIMETER_MKK_ANTIFRAUD_CATEGORY_SETTINGS={
        'cities': [],
        'cities_disable': [],
        'countries': [],
        'countries_disable': [],
        'dbs': ['park_0'],
        'dbs_disable': [],
        'enable': True,
    },
    TAXIMETER_NIGHT_CATEGORY_SETTINGS={
        'cities': [],
        'cities_disable': [],
        'countries': [],
        'countries_disable': [],
        'dbs': ['park_0'],
        'dbs_disable': [],
        'enable': True,
    },
    TAXIMETER_PERSONAL_DRIVER_CATEGORY_SETTINGS={
        'cities': [],
        'cities_disable': [],
        'countries': [],
        'countries_disable': [],
        'dbs': ['park_0'],
        'dbs_disable': [],
        'enable': True,
    },
    TAXIMETER_POOL_CATEGORY_SETTINGS={
        'cities': [],
        'cities_disable': [],
        'countries': [],
        'countries_disable': [],
        'dbs': ['park_0'],
        'dbs_disable': [],
        'enable': True,
    },
    TAXIMETER_PREMIUM_SUV_CATEGORY_SETTINGS={
        'cities': [],
        'cities_disable': [],
        'countries': [],
        'countries_disable': [],
        'dbs': ['park_0'],
        'dbs_disable': [],
        'enable': True,
    },
    TAXIMETER_PREMIUM_VAN_CATEGORY_SETTINGS={
        'cities': [],
        'cities_disable': [],
        'countries': [],
        'countries_disable': [],
        'dbs': ['park_0'],
        'dbs_disable': [],
        'enable': True,
    },
    TAXIMETER_PROMO_CATEGORY_SETTINGS={
        'cities': [],
        'cities_disable': [],
        'countries': [],
        'countries_disable': [],
        'dbs': ['park_0'],
        'dbs_disable': [],
        'enable': True,
    },
    TAXIMETER_SCOOTERS_CATEGORY_SETTINGS={
        'dbs': ['park_0', 'park_1'],
        'enable': True,
    },
    TAXIMETER_SUV_CATEGORY_SETTINGS={
        'cities': [],
        'cities_disable': [],
        'countries': [],
        'countries_disable': [],
        'dbs': ['park_0', 'park_1'],
        'dbs_disable': [],
        'enable': True,
    },
)
@pytest.mark.pgsql('driver-categories-api', files=['categories.sql'])
@pytest.mark.redis_store(
    ['hset', 'RobotSettings:park_0:Settings', 'driver_2', '-35616'],
    ['hset', 'RobotSettings:park_1:Settings', 'driver_0', '66003072'],
    ['hset', 'RobotSettings:park_3:Settings', 'driver_0', '139456'],
    ['hset', 'RobotSettings:park_5:Settings', 'driver_0', '4096'],
)
@pytest.mark.parametrize(
    'params,driver_id,code,output,config,is_uberdriver',
    [
        pytest.param({}, '', 401, {}, {}, False, id='Bad request'),
        pytest.param(
            {'db': 'park_0'},
            'driver_0',
            200,
            {'CarCategory': 0, 'Settings': 0},
            {},
            False,
            id='No caregories nor driver restrictions',
        ),
        pytest.param(
            {'db': 'park_0'},
            'driver_1',
            200,
            {'CarCategory': -201392129, 'Settings': 0},
            {},
            False,
            id='All available car categories',
        ),
        pytest.param(
            {'db': 'park_0'},
            'driver_2',
            200,
            {'CarCategory': 0, 'Settings': -35616},
            {},
            False,
            id='All available driver restrictions',
        ),
        pytest.param(
            {'db': 'park_1'},
            'driver_0',
            200,
            {'CarCategory': 277661463, 'Settings': 17571968},
            {},
            False,
            id='Some park & driver restrictions',
        ),
        pytest.param(
            {'db': 'park_1'},
            'driver_0',
            200,
            {'CarCategory': 277661463, 'Settings': 17571968},
            {'DRIVER_CATEGORIES_API_UBERDRIVER_DONT_SHOW': False},
            True,
            id='uberdriver with disabled no_show',
        ),
        pytest.param(
            {'db': 'park_1'},
            'driver_0',
            200,
            {'CarCategory': 0, 'Settings': 17571968},
            {'DRIVER_CATEGORIES_API_UBERDRIVER_DONT_SHOW': True},
            True,
            id='uberdriver dont show tariffs',
        ),
        pytest.param(
            {'db': 'park_2'},
            'driver_0',
            200,
            {'CarCategory': 291823, 'Settings': 0},
            {'TAXIMETER_ULTIMATE_CATEGORY_ENABLED': False},
            False,
            id='Car categories disabled by configs',
        ),
        pytest.param(
            {'db': 'park_3'},
            'driver_0',
            200,
            {'CarCategory': 678, 'Settings': 139456},
            {},
            False,
            id='Categories with fuzzy names',
            # wagon -> universal, comfort -> business and etc.)
        ),
        pytest.param(
            {'db': 'park_5'},
            'driver_0',
            200,
            {'CarCategory': 0, 'Settings': 4096},
            {
                'DRIVER_CATEGORIES_API_OVERRIDE_PARK_RESTRICTIONS': {
                    'categories': ['comfortplus'],
                },
            },
            False,
            id='Park restrictions overrides',
        ),
    ],
)
@pytest.mark.parametrize('use_pg', [False, True])
@pytest.mark.parametrize('cache_usage_percent', [0, 100])
async def test_driver_categories_get(
        taxi_driver_categories_api,
        mockserver,
        taxi_config,
        driver_profiles,
        fleet_parks,
        parks,
        taximeter_xservice,
        params,
        driver_id,
        code,
        output,
        config,
        is_uberdriver,
        use_pg,
        cache_usage_percent,
):
    config['DRIVER_CATEGORIES_API_DATA_SOURCE'] = {
        '/v1/categories/get': {'use_pg': use_pg},
        '__default__': {'use_pg': False},
    }
    cache_settings_index = cache_usage_percent < 100
    config['DRIVER_CATEGORIES_API_PG_CACHE_SETTINGS'] = {
        'handlers': (
            (
                {},
                {
                    '/v1/categories/get': {
                        'car_categories': {
                            'cache_usage_percent': cache_usage_percent,
                        },
                        'driver_restrictions': {
                            'cache_usage_percent': cache_usage_percent,
                        },
                        'park_categories': {
                            'cache_usage_percent': cache_usage_percent,
                        },
                    },
                },
            )[cache_settings_index]
        ),
    }
    taxi_config.set_values(config)

    if is_uberdriver:

        @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
        def _tags(request):
            return {'tags': ['uberdriver_block']}

    await taxi_driver_categories_api.invalidate_caches()

    headers = {
        'X-Request-Application': 'taximeter',
        'X-Request-Platform': 'android',
        'X-Request-Application-Brand': 'yandex',
        'X-Request-Application-Version': '9.49 (2345)',
        'User-Agent': 'Taximeter 9.49',  # required in yaml
        'Accept-Language': 'ru',
    }
    if 'db' in params:
        headers['X-YaTaxi-Park-Id'] = params['db']
    if driver_id:
        headers['X-YaTaxi-Driver-Profile-Id'] = driver_id

    if is_uberdriver:
        headers['X-Request-Application'] = 'uberdriver'
        headers['X-Request-Application-Brand'] = 'uber'
        headers['User-Agent'] = 'Taximeter-Uber 9.49'

    response = await taxi_driver_categories_api.post(
        'v1/categories/get', headers=headers,
    )
    assert response.status_code == code
    if output:
        assert response.json() == output
