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


@pytest.mark.config(
    DRIVER_CATEGORIES_API_DATA_SOURCE={'__default__': {'use_pg': True}},
    DRIVER_CATEGORIES_API_DATA_SOURCE_WRITE={
        '__default__': {'storage_type': 'old_and_pg'},
    },
    DRIVER_CATEGORIES_API_PG_CACHE_SETTINGS={
        'handlers': {
            '/driver/v1/categories-api/v2/categories': {
                'car_categories': {'cache_usage_percent': 0},
                'driver_restrictions': {'cache_usage_percent': 0},
                'park_categories': {'cache_usage_percent': 0},
            },
        },
    },
)
@pytest.mark.parametrize(
    'params,body,code,expected,config',
    [
        pytest.param(
            {'driver_id': 'shadow_driver'},
            {'category_name': 'econom', 'enable': True},
            400,
            {'message': 'No park_id'},
            {},
            id='No park_id',
        ),
        pytest.param(
            {'park_id': 'shadow_park', 'driver_id': 'shadow_driver'},
            {'enable': False},
            400,
            {'code': '400', 'message': 'Field \'category_name\' is missing'},
            {},
            id='No request body params',
        ),
        pytest.param(
            {'park_id': 'shadow_park', 'driver_id': 'shadow_driver'},
            {'category_name': 'econom', 'enable': True},
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
            id='Good request',
        ),
        pytest.param(
            {'park_id': 'park_0', 'driver_id': 'driver_0'},
            {'category_name': 'econom', 'enable': True},
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
                            'block_reason': 'Blocked by exam',
                            'is_blocked_by_exam': True,
                            'deeplink': '/deeplink2',
                        },
                    },
                ],
                'groups': [{'category_names': ['econom'], 'id': 'default'}],
            },
            {},
            id='Driver with blocked category',
        ),
        pytest.param(
            {'park_id': 'park_1', 'driver_id': 'driver_1'},
            {'category_name': 'econom', 'enable': False},
            400,
            {'message': 'robot_setting_category_disable_forbidden'},
            {},
            id='Tariff disabling is not allowed by park',
        ),
        pytest.param(
            {'park_id': 'park_2', 'driver_id': 'driver_2'},
            {'category_name': 'econom', 'enable': False},
            400,
            {'message': 'car_category_change_disabled_by_driver_fix'},
            {
                'DRIVER_ROBOT_SETTINGS': {
                    'econom_limit': {'enable': False, 'limit': 0},
                    'child_tarif_settings': {'enable': False, 'classes': []},
                    'driver_mode_subscription_enable': True,
                },
            },
            id='Tariff disabling is not allowed by driver-fix',
        ),
        pytest.param(
            {'park_id': 'park_3', 'driver_id': 'driver_3'},
            {'category_name': 'econom', 'enable': False},
            400,
            {'message': 'robot_setting_economy_limit_none'},
            {
                'DRIVER_ROBOT_SETTINGS': {
                    'econom_limit': {'enable': True, 'limit': 0},
                    'child_tarif_settings': {'enable': False, 'classes': []},
                    'driver_mode_subscription_enable': False,
                },
            },
            id='Limit of econom disables exceeded',
        ),
        pytest.param(
            {'park_id': 'park_4', 'driver_id': 'driver_4'},
            {'category_name': 'child_tariff', 'enable': False},
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
                'groups': [
                    {
                        'category_names': ['econom', 'child_tariff'],
                        'id': 'default',
                    },
                ],
            },
            {
                'DRIVER_ROBOT_SETTINGS': {
                    'econom_limit': {'enable': False, 'limit': 0},
                    'child_tarif_settings': {
                        'enable': True,
                        'classes': ['econom'],
                    },
                    'driver_mode_subscription_enable': False,
                },
            },
            id='Can disable child_tariff because of premium classes',
        ),
        pytest.param(
            {'park_id': 'park_5', 'driver_id': 'driver_5'},
            {'category_name': 'child_tariff', 'enable': False},
            400,
            {'message': 'car_category_child_tariff_disable'},
            {
                'DRIVER_ROBOT_SETTINGS': {
                    'econom_limit': {'enable': False, 'limit': 0},
                    'child_tarif_settings': {
                        'enable': True,
                        'classes': ['econom'],
                    },
                    'driver_mode_subscription_enable': False,
                },
            },
            id='Cannot disable child_tariff because driver not found',
        ),
        pytest.param(
            {'park_id': 'park_11', 'driver_id': 'driver_11'},
            {'category_name': 'child_tariff', 'enable': False},
            400,
            {'message': 'car_category_child_tariff_disable'},
            {
                'DRIVER_ROBOT_SETTINGS': {
                    'econom_limit': {'enable': False, 'limit': 0},
                    'child_tarif_settings': {
                        'enable': True,
                        'classes': ['business'],
                    },
                    'driver_mode_subscription_enable': False,
                },
            },
            id='Cannot disable child_tariff because classes not intersected',
        ),
        pytest.param(
            {'park_id': 'park_11', 'driver_id': 'driver_11'},
            {'category_name': 'child_tariff', 'enable': False},
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
                'groups': [
                    {
                        'category_names': ['econom', 'child_tariff'],
                        'id': 'default',
                    },
                ],
            },
            {
                'DRIVER_ROBOT_SETTINGS': {
                    'econom_limit': {'enable': False, 'limit': 0},
                    'child_tarif_settings': {
                        'enable': True,
                        'classes': ['econom'],
                    },
                    'driver_mode_subscription_enable': False,
                },
            },
            id='Can disable child_tariff because classes intersected',
        ),
        pytest.param(
            {'park_id': 'park_6', 'driver_id': 'driver_6'},
            {'category_name': 'econom', 'enable': False},
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
                'groups': [{'category_names': ['econom'], 'id': 'default'}],
            },
            {
                'DRIVER_CATEGORIES_API_OVERRIDE_PARK_RESTRICTIONS': {
                    'categories': ['econom'],
                },
            },
            id='Can disable tariff because of park restrictions override',
        ),
        pytest.param(
            {'park_id': 'park_7', 'driver_id': 'driver_7'},
            {'category_name': 'econom', 'enable': False},
            400,
            {'message': 'car_category_immutable_by_dependencies'},
            {
                'TAXIMETER_TARIFF_DEPENDENCIES': {
                    'dependencies': [
                        {
                            'dependency_type': 'auto_on',
                            'master_category': 'child_tariff',
                            'slave_category': 'econom',
                            'driver_tags': ['tariff_deps_tag'],
                        },
                    ],
                },
            },
            id='Cannot disable category because of tariff dependencies',
        ),
        pytest.param(
            {'park_id': 'shadow_park', 'driver_id': 'shadow_driver'},
            {'category_name': 'econom', 'enable': True},
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
@pytest.mark.experiments3(filename='experiments3_defaults.json')
async def test_driver_categories_get(
        taxi_driver_categories_api,
        taxi_config,
        candidates,
        driver_diagnostics,
        driver_profiles,
        driver_tags,
        driver_trackstory,
        fleet_parks,
        parks,
        taximeter_xservice,
        pgsql,
        params,
        body,
        code,
        expected,
        config,
):
    if config:
        taxi_config.set_values(config)

    await taxi_driver_categories_api.invalidate_caches()

    response = await taxi_driver_categories_api.post(
        '/driver/v1/categories-api/v2/categories',
        params={'lat': 55.8397594, 'lon': 37.4024391},
        headers=get_headers(params),
        json=body,
    )
    assert response.status_code == code

    got_response = response.json()
    if 'categories' in got_response:
        got_response['categories'].sort(key=lambda x: x['name'])
    if code == 400 and 'code' in expected:
        assert expected['code'] == '400'
    else:
        assert got_response == expected
