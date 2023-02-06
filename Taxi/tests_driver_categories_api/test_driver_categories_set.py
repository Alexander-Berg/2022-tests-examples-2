import pytest

from tests_driver_categories_api import category_utils

ENDPOINT = '/v1/categories/set'


def get_headers(params):
    headers = {}
    if 'db' in params:
        headers['X-YaTaxi-Park-Id'] = params['db']
    if 'driver_id' in params:
        headers['X-YaTaxi-Driver-Profile-Id'] = params['driver_id']

    headers['X-Request-Application'] = 'taximeter'
    headers['X-Request-Platform'] = 'android'
    headers['X-Request-Application-Version'] = '9.30 (2345)'
    headers['Accept-Language'] = 'ru'

    return headers


def _get_data_source_config(use_pg, storage_type, use_tags_over_dms=False):
    return {
        'DRIVER_CATEGORIES_API_DATA_SOURCE': {
            '/v1/categories/set': {'use_pg': use_pg},
            '__default__': {'use_pg': False},
        },
        'DRIVER_CATEGORIES_API_DATA_SOURCE_WRITE': {
            '/v1/categories/set': {'storage_type': storage_type},
            '__default__': {'storage_type': 'old_only'},
        },
        'DRIVER_CATEGORIES_API_USE_TAGS_OVER_DMS': use_tags_over_dms,
    }


@pytest.mark.pgsql('driver-categories-api', files=['categories.sql'])
@pytest.mark.parametrize(
    'params,driver_id,data,code,output',
    [
        pytest.param(
            {'db': 'park_0', 'driver_id': 'driver_0'},
            'driver_0',
            'type=econom&value=0',
            200,
            {'success': True},
            id='Disable econom in park 0',
        ),
        pytest.param(
            {'db': 'park_0', 'driver_id': 'driver_0'},
            'driver_0',
            'type=econom&value=1',
            200,
            {'success': True},
            id='Enable econom in park 0',
        ),
        pytest.param(
            {'db': 'park_0', 'driver_id': 'driver_0'},
            'driver_0',
            'type=bussines&value=0',
            200,
            {'success': True},
            id='Disable bussines in park 0',
        ),
        pytest.param(
            {'db': 'park_0', 'driver_id': 'driver_0'},
            'driver_0',
            'type=bussines&value=1',
            200,
            {'success': True},
            id='Enable bussines in park 0',
        ),
        pytest.param(
            {'db': 'park_6', 'driver_id': 'driver_0'},
            'driver_0',
            'type=econom&value=0',
            200,
            {
                'success': False,
                'message': 'robot_setting_category_disable_forbidden',
            },
            id='Disable econom in park 1',
        ),
        pytest.param(
            {'db': 'park_6', 'driver_id': 'driver_0'},
            'driver_0',
            'type=econom&value=1',
            200,
            {'success': True},
            id='Enable econom in park 1',
        ),
        pytest.param(
            {'db': 'park_6', 'driver_id': 'driver_0'},
            'driver_0',
            'type=bussines&value=0',
            200,
            {'success': True},
            id='Disable bussines in park 1',
        ),
        pytest.param(
            {'db': 'park_6', 'driver_id': 'driver_0'},
            'driver_0',
            'type=bussines&value=1',
            200,
            {'success': True},
            id='Enable bussines in park 1',
        ),
        pytest.param(
            {'db': 'park_4', 'driver_id': 'driver_0'},
            'driver_0',
            'type=econom&value=0',
            200,
            {
                'success': False,
                'message': 'robot_setting_category_disable_forbidden',
            },
            id='Disable econom in park 2',
        ),
        pytest.param(
            {'db': 'park_4', 'driver_id': 'driver_0'},
            'driver_0',
            'type=econom&value=1',
            200,
            {'success': True},
            id='Enable econom in park 2',
        ),
        pytest.param({}, '', '', 400, {}, id='Bad request'),
    ],
)
@pytest.mark.parametrize('use_pg', [False, True])
@pytest.mark.parametrize('storage_type', ['old_only', 'old_and_pg', 'pg_only'])
async def test_driver_categories_set(
        taxi_driver_categories_api,
        taxi_config,
        candidates,
        driver_trackstory,
        driver_tags,
        fleet_parks,
        parks,
        params,
        driver_id,
        data,
        code,
        output,
        use_pg,
        storage_type,
):
    taxi_config.set_values(_get_data_source_config(use_pg, storage_type))

    await taxi_driver_categories_api.invalidate_caches()

    response = await taxi_driver_categories_api.post(
        ENDPOINT, headers=get_headers(params), params=params, data=data,
    )
    assert response.status_code == code
    if output:
        assert response.json() == output


@pytest.mark.config(
    DRIVER_ROBOT_SETTINGS={
        'econom_limit': {'enable': True, 'limit': 2},
        'child_tarif_settings': {'enable': False, 'classes': []},
        'driver_mode_subscription_enable': False,
    },
)
@pytest.mark.pgsql('driver-categories-api', files=['categories.sql'])
@pytest.mark.parametrize('use_pg', [False, True])
@pytest.mark.parametrize('storage_type', ['old_only', 'old_and_pg', 'pg_only'])
async def test_driver_categories_set_econom_limit(
        taxi_driver_categories_api,
        taxi_config,
        candidates,
        driver_trackstory,
        driver_profiles,
        driver_tags,
        fleet_parks,
        parks,
        redis_store,
        use_pg,
        storage_type,
):
    taxi_config.set_values(_get_data_source_config(use_pg, storage_type))

    params = {'db': 'park_0', 'driver_id': 'driver_0'}
    driver_id = 'driver_0'
    data = 'type=econom&value=0'

    await taxi_driver_categories_api.invalidate_caches()

    response = await taxi_driver_categories_api.post(
        ENDPOINT, headers=get_headers(params), params=params, data=data,
    )
    assert response.status_code == 200
    assert response.json() == {
        'success': True,
        'message': 'robot_setting_economy_limit_1',
    }

    await taxi_driver_categories_api.invalidate_caches()

    response = await taxi_driver_categories_api.post(
        ENDPOINT, headers=get_headers(params), params=params, data=data,
    )
    assert response.status_code == 200
    assert response.json() == {
        'success': True,
        'message': 'robot_setting_economy_limit_zero',
    }

    await taxi_driver_categories_api.invalidate_caches()

    response = await taxi_driver_categories_api.post(
        ENDPOINT, headers=get_headers(params), params=params, data=data,
    )
    assert response.status_code == 200
    assert response.json() == {
        'success': False,
        'message': 'robot_setting_economy_limit_none',
    }


@pytest.mark.config(
    DRIVER_ROBOT_SETTINGS={
        'econom_limit': {'enable': False, 'limit': 0},
        'child_tarif_settings': {'enable': False, 'classes': []},
        'driver_mode_subscription_enable': True,
    },
)
@pytest.mark.pgsql('driver-categories-api', files=['categories.sql'])
@pytest.mark.parametrize('use_pg', [False, True])
@pytest.mark.parametrize('storage_type', ['old_only', 'old_and_pg', 'pg_only'])
@pytest.mark.parametrize('use_tags_over_dms', [True, False])
async def test_driver_categories_set_driver_fix(
        taxi_driver_categories_api,
        taxi_config,
        candidates,
        driver_trackstory,
        driver_mode_subscription,
        driver_tags,
        fleet_parks,
        parks,
        use_pg,
        storage_type,
        use_tags_over_dms,
):
    taxi_config.set_values(
        _get_data_source_config(use_pg, storage_type, use_tags_over_dms),
    )

    await taxi_driver_categories_api.invalidate_caches()

    params = {'db': 'park_0', 'driver_id': 'driver_0'}
    driver_id = 'driver_0'
    data = 'type=econom&value=0'

    response = await taxi_driver_categories_api.post(
        ENDPOINT, headers=get_headers(params), params=params, data=data,
    )
    assert response.status_code == 200
    assert response.json() == {
        'success': False,
        'message': 'car_category_change_disabled_by_driver_fix',
    }


@pytest.mark.pgsql('driver-categories-api', files=['categories.sql'])
@pytest.mark.parametrize(
    'classes,output',
    [
        pytest.param(['business'], {'success': True}, id=f'Success one class'),
        pytest.param(
            ['ultima'],
            {'success': False, 'message': 'car_category_child_tariff_disable'},
            id=f'Fail one class',
        ),
        pytest.param(
            ['econom', 'business', 'ultima'],
            {'success': True},
            id=f'Success multiclass',
        ),
        pytest.param(
            [],
            {'success': False, 'message': 'car_category_child_tariff_disable'},
            id=f'Fail empty classes',
        ),
    ],
)
@pytest.mark.parametrize('use_pg', [False, True])
@pytest.mark.parametrize('storage_type', ['old_only', 'old_and_pg', 'pg_only'])
async def test_driver_categories_set_child_tariff(
        taxi_driver_categories_api,
        candidates,
        driver_trackstory,
        driver_tags,
        fleet_parks,
        parks,
        classes,
        output,
        use_pg,
        storage_type,
        taxi_config,
):
    config = _get_data_source_config(use_pg, storage_type)
    config['DRIVER_ROBOT_SETTINGS'] = {
        'econom_limit': {'enable': False, 'limit': 0},
        'child_tarif_settings': {'enable': True, 'classes': classes},
        'driver_mode_subscription_enable': False,
    }
    taxi_config.set_values(config)
    params = {'db': 'park_0', 'driver_id': 'driver_0'}
    driver_id = 'driver_0'
    data = 'type=child_tariff&value=0'

    await taxi_driver_categories_api.invalidate_caches()

    response = await taxi_driver_categories_api.post(
        ENDPOINT, headers=get_headers(params), params=params, data=data,
    )
    assert response.status_code == 200
    assert response.json() == output


@pytest.mark.parametrize(
    'categories,params,driver_id,data,output',
    [
        pytest.param(
            [],
            {'db': 'park_4', 'driver_id': 'driver_0'},
            'driver_0',
            'type=econom&value=0',
            {
                'success': False,
                'message': 'robot_setting_category_disable_forbidden',
            },
            id=f'Without override',
        ),
        pytest.param(
            ['econom'],
            {'db': 'park_4', 'driver_id': 'driver_0'},
            'driver_0',
            'type=econom&value=0',
            {'success': True},
            id=f'With override',
        ),
    ],
)
@pytest.mark.parametrize('use_pg', [False, True])
@pytest.mark.parametrize('storage_type', ['old_only', 'old_and_pg', 'pg_only'])
async def test_driver_categories_set_park_categories_override(
        taxi_driver_categories_api,
        candidates,
        driver_trackstory,
        driver_tags,
        fleet_parks,
        parks,
        categories,
        params,
        driver_id,
        data,
        output,
        use_pg,
        storage_type,
        taxi_config,
):
    config = _get_data_source_config(use_pg, storage_type)
    config['DRIVER_CATEGORIES_API_OVERRIDE_PARK_RESTRICTIONS'] = {
        'categories': categories,
    }
    taxi_config.set_values(config)

    await taxi_driver_categories_api.invalidate_caches()

    response = await taxi_driver_categories_api.post(
        ENDPOINT, headers=get_headers(params), params=params, data=data,
    )
    assert response.status_code == 200
    assert response.json() == output


@pytest.mark.config(
    TAXIMETER_TARIFF_DEPENDENCIES={
        'dependencies': [
            {
                'dependency_type': 'auto_on',
                'master_category': 'express',
                'slave_category': 'courier',
                'driver_tags': ['sometag'],
            },
        ],
    },
)
@pytest.mark.pgsql('driver-categories-api', files=['categories.sql'])
@pytest.mark.parametrize(
    'current_restrictions,expected_restrictions,params,driver_id,data,output,',
    [
        pytest.param(
            ['express', 'courier'],
            [],
            {'db': 'park_0', 'driver_id': 'driver_0'},
            'driver_0',
            'type=express&value=1',
            {'success': True},
            id='Enable express (express and courier disabled)',
        ),
        pytest.param(
            ['express', 'courier'],
            ['express'],
            {'db': 'park_0', 'driver_id': 'driver_0'},
            'driver_0',
            'type=courier&value=1',
            {'success': True},
            id='Enable courier (express and courier disabled)',
        ),
        pytest.param(
            ['express'],
            [],
            {'db': 'park_0', 'driver_id': 'driver_0'},
            'driver_0',
            'type=express&value=1',
            {'success': True},
            id='Enable express (express disabled, courier enabled)',
        ),
        pytest.param(
            ['express'],
            ['express', 'courier'],
            {'db': 'park_0', 'driver_id': 'driver_0'},
            'driver_0',
            'type=courier&value=0',
            {'success': True},
            id='Disable courier (express disabled, courier enabled)',
        ),
        pytest.param(
            ['courier'],
            ['express', 'courier'],
            {'db': 'park_0', 'driver_id': 'driver_0'},
            'driver_0',
            'type=express&value=0',
            {'success': True},
            id='Disable express (express enabled, courier disabled)',
        ),
        pytest.param(
            ['courier'],
            [],
            {'db': 'park_0', 'driver_id': 'driver_0'},
            'driver_0',
            'type=courier&value=1',
            {'success': True},
            id='Enable courier (express enabled, courier disabled)',
        ),
        pytest.param(
            [],
            ['express'],
            {'db': 'park_0', 'driver_id': 'driver_0'},
            'driver_0',
            'type=express&value=0',
            {'success': True},
            id='Disable express (express and courier enabled)',
        ),
        pytest.param(
            [],
            [],
            {'db': 'park_0', 'driver_id': 'driver_0'},
            'driver_0',
            'type=courier&value=0',
            {
                'success': False,
                'message': 'car_category_immutable_by_dependencies',
            },
            id='Disable courier (express and courier enabled)',
        ),
        pytest.param(
            ['business2', 'comfortplus'],
            [],
            {'db': 'park_0', 'driver_id': 'driver_0'},
            'driver_0',
            'type=comfortplus&value=1',
            {'success': True},
            id='Enable comfortplus',
        ),
        pytest.param(
            [],
            ['business2', 'comfortplus'],
            {'db': 'park_0', 'driver_id': 'driver_0'},
            'driver_0',
            'type=comfortplus&value=0',
            {'success': True},
            id='Disable comfortplus',
        ),
    ],
)
@pytest.mark.parametrize('use_pg', [False, True])
@pytest.mark.parametrize('storage_type', ['old_only', 'old_and_pg', 'pg_only'])
async def test_driver_categories_set_complex_cases(
        taxi_driver_categories_api,
        taxi_config,
        candidates,
        driver_trackstory,
        driver_tags,
        fleet_parks,
        parks,
        redis_store,
        current_restrictions,
        expected_restrictions,
        params,
        driver_id,
        data,
        output,
        use_pg,
        storage_type,
        pgsql,
):
    taxi_config.set_values(_get_data_source_config(use_pg, storage_type))

    category_utils.upsert_driver_restrictions(
        pgsql, params['db'], driver_id, current_restrictions,
    )

    category_utils.set_redis_restrictions(
        redis_store, params['db'], driver_id, current_restrictions,
    )

    await taxi_driver_categories_api.invalidate_caches()

    response = await taxi_driver_categories_api.post(
        ENDPOINT, headers=get_headers(params), params=params, data=data,
    )

    assert response.status_code == 200
    assert response.json() == output

    driver_restrictions = category_utils.select_driver_restrictions(
        pgsql, params['db'], driver_id,
    )

    expected_pg_restrictions = (
        current_restrictions
        if storage_type == 'old_only'
        else expected_restrictions
    )

    category_utils.check_unordered_collections(
        driver_restrictions, expected_pg_restrictions,
    )

    expected_redis_restrictions = (
        current_restrictions
        if storage_type == 'pg_only'
        else expected_restrictions
    )

    redis_general_category = redis_store.hgetall(
        f'RobotSettings:{params["db"]}:Settings',
    )[driver_id.encode()].decode()
    general_restrictions = category_utils.convert_flag_to_restrictions(
        int(redis_general_category),
    )

    category_utils.check_unordered_collections(
        general_restrictions, expected_redis_restrictions,
    )

    for category in expected_redis_restrictions:
        category_code = category_utils.get_category_code(category)
        assert redis_store.smembers(
            f'RobotSettings:{params["db"]}:Settings_{category_code}',
        ) == {driver_id.encode()}


@pytest.mark.pgsql('driver-categories-api', files=['categories.sql'])
@pytest.mark.parametrize(
    'enabled',
    [
        pytest.param(False, id='Tag maker disabled'),
        pytest.param(True, id='Tag maker enabled'),
    ],
)
@pytest.mark.parametrize('use_pg', [False, True])
@pytest.mark.parametrize('storage_type', ['old_only', 'old_and_pg', 'pg_only'])
async def test_tag_maker_call(
        taxi_driver_categories_api,
        taxi_config,
        candidates,
        driver_trackstory,
        driver_tags,
        fleet_parks,
        parks,
        stq,
        enabled,
        use_pg,
        storage_type,
):
    taxi_config.set_values(_get_data_source_config(use_pg, storage_type))
    taxi_config.set_values(
        {'DRIVER_CATEGORIES_API_TAG_MAKER_ENABLED': {'enabled': enabled}},
    )
    await taxi_driver_categories_api.invalidate_caches()

    params = {'db': 'park_0', 'driver_id': 'driver_0'}

    response = await taxi_driver_categories_api.post(
        ENDPOINT,
        headers=get_headers(params),
        params=params,
        data='type=econom&value=0',
    )
    assert response.status_code == 200
    assert response.json() == {'success': True}
    assert stq.driver_categories_tag_maker.times_called == enabled
    if enabled:
        next_call = stq.driver_categories_tag_maker.next_call()
        assert next_call['kwargs']['type'] == 'driver_category'
