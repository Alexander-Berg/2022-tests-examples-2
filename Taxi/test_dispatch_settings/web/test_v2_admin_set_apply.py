import random

import pytest


async def get_param_value(client, param_name, tariff, zone):
    response = await client.get(
        '/v2/admin/fetch', params={'zone_name': zone, 'tariff_name': tariff},
    )

    assert response.status == 200
    content = await response.json()

    for item in content['settings']:
        if item['name'] == param_name:
            return item.get('value', None), item['version']


@pytest.mark.config(ALL_CATEGORIES=['test_tariff_1'])
async def test_unknown_parameter(taxi_dispatch_settings_web, tariffs):
    tariffs.set_zones(['test_zone_1'])

    request = {
        'zone_name': 'test_zone_1',
        'tariff_name': 'test_tariff_1',
        'new_parameters': [
            {'name': 'UNKNOWN_PARAMETER', 'old_version': -1, 'value': 45},
        ],
    }

    response = await taxi_dispatch_settings_web.post(
        '/v2/admin/set/apply', json=request,
    )
    assert response.status == 200


async def test_invalid_schema(taxi_dispatch_settings_web):
    request = {
        'zone_name': 'test_zone_1',
        'tariff_name': 'test_tariff_1',
        'new_parameters': [
            {
                'name': 'INVALID_SCHEMA_SETTING',
                'old_version': 0,
                'value': 'any_string',
            },
        ],
    }

    response = await taxi_dispatch_settings_web.post(
        '/v2/admin/set/apply', json=request,
    )
    assert response.status == 400
    content = await response.json()
    assert content['code'] == 'bad_schema'


async def test_invalid_parameters(
        taxi_dispatch_settings_web, taxi_config, tariffs,
):
    response = await taxi_dispatch_settings_web.post(
        '/v2/admin/set/apply',
        json={
            'zone_name': 'test_zone_1',
            'tariff_name': 'test_tariff_1',
            'new_parameters': [
                {
                    'name': 'QUERY_LIMIT_LIMIT',
                    'old_version': 0,
                    'value': 'NOT_INTEGER_VALUE',
                },
            ],
        },
    )
    assert response.status == 400
    content = await response.json()
    assert content['code'] == 'bad_parameter'

    response = await taxi_dispatch_settings_web.post(
        '/v2/admin/set/apply',
        json={
            'zone_name': 'test_zone_1',
            'tariff_name': 'test_tariff_1',
            'new_parameters': [
                {'name': 'QUERY_LIMIT_LIMIT', 'old_version': 0, 'value': 33},
            ],
        },
    )
    assert response.status == 400
    content = await response.json()
    assert content['code'] == 'no_such_tariff'

    tariffs.set_zones([])
    taxi_config.set_values({'ALL_CATEGORIES': ['test_tariff_1']})
    await taxi_dispatch_settings_web.invalidate_caches()

    response = await taxi_dispatch_settings_web.post(
        '/v2/admin/set/apply',
        json={
            'zone_name': 'test_zone_1',
            'tariff_name': 'test_tariff_1',
            'new_parameters': [
                {'name': 'QUERY_LIMIT_LIMIT', 'old_version': 0, 'value': 33},
            ],
        },
    )
    assert response.status == 400
    content = await response.json()
    assert content['code'] == 'no_such_zone'


@pytest.mark.config(
    ALL_CATEGORIES=['test_tariff_1'], DISPATCH_SETTINGS_CHECK_VERSION=True,
)
async def test_version_mismatch(taxi_dispatch_settings_web, tariffs):
    tariffs.set_zones(['test_zone_1'])

    request = {
        'zone_name': 'test_zone_1',
        'tariff_name': 'test_tariff_1',
        'new_parameters': [
            {'name': 'QUERY_LIMIT_LIMIT', 'old_version': -1, 'value': 45},
            {
                'name': 'QUERY_LIMIT_MAX_LINE_DIST',
                'old_version': 0,
                'value': 44,
            },
        ],
    }

    response = await taxi_dispatch_settings_web.post(
        '/v2/admin/set/apply', json=request,
    )

    assert response.status == 409
    content = await response.json()
    assert content['code'] == 'version_mismatch'


@pytest.mark.config(ALL_CATEGORIES=['test_tariff_1', 'test_tariff_4'])
@pytest.mark.parametrize(
    'group_name,response_code,etalon',
    [('base', 403, (22, 0)), (None, 200, (45, 1))],
)
async def test_group_name_set(
        taxi_dispatch_settings_web, tariffs, group_name, response_code, etalon,
):
    tariffs.set_zones(['test_zone_1'])

    request = {
        'zone_name': 'test_zone_1',
        'tariff_name': 'test_tariff_1',
        'new_parameters': [
            {'name': 'QUERY_LIMIT_LIMIT', 'old_version': -1, 'value': 45},
        ],
    }
    if group_name:
        request['group_name'] = group_name

    response = await taxi_dispatch_settings_web.post(
        '/v2/admin/set/apply', json=request,
    )

    assert response.status == response_code
    value, version = await get_param_value(
        taxi_dispatch_settings_web,
        'QUERY_LIMIT_LIMIT',
        'test_tariff_1',
        'test_zone_1',
    )
    assert (value, version) == etalon


@pytest.mark.config(ALL_CATEGORIES=['test_tariff_1'])
async def test_empty_settings(taxi_dispatch_settings_web, tariffs):
    tariffs.set_zones(['test_zone_1'])

    initial_params_check = {
        ('QUERY_LIMIT_LIMIT', 'test_tariff_1', 'test_zone_1'): (22, 0),
        ('QUERY_LIMIT_MAX_LINE_DIST', 'test_tariff_1', 'test_zone_1'): (27, 0),
        ('QUERY_LIMIT_LIMIT', 'test_tariff_1', 'test_zone_2'): (25, 0),
    }

    for params, etalons in initial_params_check.items():
        init_value, init_version = await get_param_value(
            taxi_dispatch_settings_web, params[0], params[1], params[2],
        )
        assert (init_value, init_version) == etalons

    response = await taxi_dispatch_settings_web.post(
        '/v2/admin/set/apply',
        json={
            'zone_name': 'test_zone_1',
            'tariff_name': 'test_tariff_1',
            'new_parameters': [],
        },
    )
    assert response.status == 400

    initial_params_check = {
        ('QUERY_LIMIT_LIMIT', 'test_tariff_1', 'test_zone_1'): (22, 0),
        ('QUERY_LIMIT_MAX_LINE_DIST', 'test_tariff_1', 'test_zone_1'): (27, 0),
        ('QUERY_LIMIT_LIMIT', 'test_tariff_1', 'test_zone_2'): (25, 0),
    }

    for params, etalons in initial_params_check.items():
        init_value, init_version = await get_param_value(
            taxi_dispatch_settings_web, params[0], params[1], params[2],
        )
        assert (init_value, init_version) == etalons


@pytest.mark.config(ALL_CATEGORIES=['test_tariff_1'])
async def test_existing_zone_tariff_settings(
        taxi_dispatch_settings_web, tariffs,
):
    tariffs.set_zones(['test_zone_1', 'test_zone_2'])

    initial_params_check = {
        ('QUERY_LIMIT_LIMIT', 'test_tariff_1', 'test_zone_1'): (22, 0),
        ('QUERY_LIMIT_MAX_LINE_DIST', 'test_tariff_1', 'test_zone_1'): (27, 0),
        ('QUERY_LIMIT_LIMIT', 'test_tariff_1', 'test_zone_2'): (25, 0),
    }

    for params, etalons in initial_params_check.items():
        init_value, init_version = await get_param_value(
            taxi_dispatch_settings_web, params[0], params[1], params[2],
        )
        assert (init_value, init_version) == etalons

    # Insert new params into existing zone/tariff
    response = await taxi_dispatch_settings_web.post(
        '/v2/admin/set/apply',
        json={
            'zone_name': 'test_zone_1',
            'tariff_name': 'test_tariff_1',
            'new_parameters': [
                {'name': 'QUERY_LIMIT_LIMIT', 'old_version': 0, 'value': 33},
                {
                    'name': 'QUERY_LIMIT_MAX_LINE_DIST',
                    'old_version': 0,
                    'value': 44,
                },
            ],
        },
    )
    assert response.status == 200
    response = await taxi_dispatch_settings_web.post(
        '/v2/admin/set/apply',
        json={
            'zone_name': 'test_zone_2',
            'tariff_name': 'test_tariff_1',
            'new_parameters': [
                {'name': 'QUERY_LIMIT_LIMIT', 'old_version': 0, 'value': 55},
            ],
        },
    )
    assert response.status == 200

    params_check = {
        ('QUERY_LIMIT_LIMIT', 'test_tariff_1', 'test_zone_1'): (33, 1),
        ('QUERY_LIMIT_MAX_LINE_DIST', 'test_tariff_1', 'test_zone_1'): (44, 1),
        ('QUERY_LIMIT_LIMIT', 'test_tariff_1', 'test_zone_2'): (55, 1),
    }
    for params, etalons in params_check.items():
        init_value, init_version = await get_param_value(
            taxi_dispatch_settings_web, params[0], params[1], params[2],
        )
        assert (init_value, init_version) == etalons
    # -- Insert new params into existing zone/tariff --

    # Update existing param case
    update_param_request = {
        'zone_name': 'test_zone_1',
        'tariff_name': 'test_tariff_1',
        'new_parameters': [
            {'name': 'QUERY_LIMIT_LIMIT', 'old_version': 1, 'value': 34},
        ],
    }
    response = await taxi_dispatch_settings_web.post(
        '/v2/admin/set/apply', json=update_param_request,
    )
    assert response.status == 200
    value, version = await get_param_value(
        taxi_dispatch_settings_web,
        'QUERY_LIMIT_LIMIT',
        'test_tariff_1',
        'test_zone_1',
    )
    assert (value, version) == (34, 2)
    # -- Update existing param case --

    # Insert new param case
    add_new_param_request = {
        'zone_name': 'test_zone_1',
        'tariff_name': 'test_tariff_1',
        'new_parameters': [
            {
                'name': 'QUERY_LIMIT_FREE_PREFERRED',
                'old_version': 1,
                'value': 4,
            },
        ],
    }
    response = await taxi_dispatch_settings_web.post(
        '/v2/admin/set/apply', json=add_new_param_request,
    )
    assert response.status == 200
    value, version = await get_param_value(
        taxi_dispatch_settings_web,
        'QUERY_LIMIT_FREE_PREFERRED',
        'test_tariff_1',
        'test_zone_1',
    )
    assert (value, version) == (4, 0)
    # -- Insert new param case --

    init_value, init_version = await get_param_value(
        taxi_dispatch_settings_web,
        'QUERY_LIMIT_LIMIT',
        'test_tariff_1',
        'test_zone_1',
    )
    assert (init_value, init_version) == (34, 2)


async def test_deletion_default_parameter_settings(taxi_dispatch_settings_web):
    setting = {'name': 'QUERY_LIMIT_LIMIT', 'old_version': 0}
    response = await taxi_dispatch_settings_web.post(
        '/v2/admin/set/apply',
        json={
            'zone_name': '__default__',
            'tariff_name': '__default__base__',
            'new_parameters': [setting],
        },
    )
    assert response.status == 400

    content = await response.json()
    assert content['code'] == 'default_deletion_err'


@pytest.mark.config(ALL_CATEGORIES=['test_tariff_4', 'test_tariff_5'])
async def test_new_zone_tariff_many_settings(
        taxi_dispatch_settings_web, tariffs, taxi_config,
):
    tariffs.set_zones(['test_zone_4', 'test_zone_5'])

    etalon_query_limit = random.randint(1, 100)
    etalon_max_line_dist = random.randint(1, 100)
    for zone, tariff in [
            ('test_zone_4', 'test_tariff_4'),
            ('test_zone_5', 'test_tariff_5'),
    ]:
        request = {
            'zone_name': zone,
            'tariff_name': tariff,
            'new_parameters': [
                {
                    'name': 'QUERY_LIMIT_LIMIT',
                    'old_version': 2323,  # new field, any version
                    'value': etalon_query_limit,
                },
                {
                    'name': 'QUERY_LIMIT_MAX_LINE_DIST',
                    'old_version': 0,
                    'value': etalon_max_line_dist,
                },
            ],
        }
        response = await taxi_dispatch_settings_web.post(
            '/v2/admin/set/apply', json=request,
        )
        assert response.status == 200

    for zone, tariff in [
            ('test_zone_4', 'test_tariff_4'),
            ('test_zone_5', 'test_tariff_5'),
    ]:
        query_limit = await get_param_value(
            taxi_dispatch_settings_web, 'QUERY_LIMIT_LIMIT', tariff, zone,
        )
        assert (etalon_query_limit, 0) == query_limit

        max_line_dist = await get_param_value(
            taxi_dispatch_settings_web,
            'QUERY_LIMIT_MAX_LINE_DIST',
            tariff,
            zone,
        )
        assert (etalon_max_line_dist, 0) == max_line_dist

    taxi_config.set_values({'DISPATCH_SETTINGS_MAINTENANCE_MODE': True})
    await taxi_dispatch_settings_web.invalidate_caches()
    response = await taxi_dispatch_settings_web.post(
        '/v2/admin/set/apply', json=request,
    )
    assert response.status == 400
    r_json = await response.json()
    assert r_json['code'] == 'maintenance_mode'


@pytest.mark.config(ALL_CATEGORIES=['test_tariff_3'])
async def test_deletion_settings(taxi_dispatch_settings_web, tariffs):
    tariffs.set_zones(['test_zone_1', 'test_zone_3'])

    initial_params_check = {
        ('QUERY_LIMIT_LIMIT', 'test_tariff_3', 'test_zone_1'): (24, 0),
        ('QUERY_LIMIT_MAX_LINE_DIST', 'test_tariff_3', 'test_zone_3'): (28, 0),
    }

    for params, etalons in initial_params_check.items():
        init_value, init_version = await get_param_value(
            taxi_dispatch_settings_web, params[0], params[1], params[2],
        )
        assert (init_value, init_version) == etalons

    etalon = random.randint(1, 100)
    setting = {'name': 'QUERY_LIMIT_MAX_LINE_DIST', 'old_version': 0}

    response = await taxi_dispatch_settings_web.post(
        '/v2/admin/set/apply',
        json={
            'zone_name': 'test_zone_1',
            'tariff_name': 'test_tariff_3',
            'new_parameters': [
                {
                    'name': 'QUERY_LIMIT_LIMIT',
                    'old_version': 0,
                    'value': etalon,
                },
            ],
        },
    )
    assert response.status == 200

    response = await taxi_dispatch_settings_web.post(
        '/v2/admin/set/apply',
        json={
            'zone_name': 'test_zone_3',
            'tariff_name': 'test_tariff_3',
            'new_parameters': [setting],
        },
    )
    assert response.status == 200

    await taxi_dispatch_settings_web.invalidate_caches()

    etalon_params_check = {
        ('QUERY_LIMIT_LIMIT', 'test_tariff_3', 'test_zone_1'): (etalon, 1),
        ('QUERY_LIMIT_MAX_LINE_DIST', 'test_tariff_3', 'test_zone_3'): (
            None,
            1,
        ),
    }
    # Check answer from admin api (with parameter)
    for params, etalons in etalon_params_check.items():
        init_value, init_version = await get_param_value(
            taxi_dispatch_settings_web, params[0], params[1], params[2],
        )
        assert (init_value, init_version) == etalons

    # Check answer from service api (without parameter)
    response = await taxi_dispatch_settings_web.get('/v1/settings/fetch')
    assert response.status == 200
    content = await response.json()
    for setting in content['settings']:
        zone, tariff = setting['zone_name'], setting['tariff_name']
        if zone == 'test_zone_3' and tariff == 'test_tariff_3':
            for params in setting['parameters']:
                assert params['values']['QUERY_LIMIT_LIMIT'] == 29
                assert 'QUERY_LIMIT_MAX_LINE_DIST' not in params['values']
