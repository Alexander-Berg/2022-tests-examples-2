import pytest


@pytest.mark.pgsql('driver-categories-api', files=['categories.sql'])
@pytest.mark.parametrize(
    'params,headers,exp3_values,config,code,output',
    [
        pytest.param(
            {'driver_profile_id': 'shadow_driver'},
            {},
            {},
            {},
            400,
            {},
            id='No park_id',
        ),
        pytest.param(
            {'park_id': 'shadow_park'},
            {},
            {},
            {},
            400,
            {},
            id='No driver_profile_id',
        ),
        pytest.param(
            {'park_id': 'shadow_park', 'driver_profile_id': 'shadow_driver'},
            {},
            {},
            {},
            200,
            {'categories': []},
            id='Driver has no vehicle',
        ),
        pytest.param(
            {
                'park_id': 'park_1',
                'vehicle_id': 'car_1',
                'driver_profile_id': 'shadow_driver',
            },
            {},
            {},
            {},
            200,
            {'categories': []},
            id='Driver has vehicle with no categories',
        ),
        pytest.param(
            {
                'park_id': 'park_2',
                'vehicle_id': 'car_2',
                'driver_profile_id': 'shadow_driver',
            },
            {},
            {},
            {},
            200,
            {'categories': ['class1', 'class2']},
            id='Driver has vehicle with some categories',
        ),
        pytest.param(
            {
                'park_id': 'park_2',
                'vehicle_id': 'car_2',
                'driver_profile_id': 'shadow_driver',
            },
            {},
            {},
            {
                'DRIVER_CATEGORIES_API_CHILD_TARIFF_SOURCE': {
                    '__default__': {'child_tariff_source': 'xservice'},
                },
            },
            200,
            {'categories': ['class1', 'class2']},
            id='Check child tariff (not available)',
        ),
        pytest.param(
            {
                'park_id': 'park_1',
                'vehicle_id': 'car_1',
                'driver_profile_id': 'driver_1',
            },
            {},
            {},
            {
                'DRIVER_CATEGORIES_API_CHILD_TARIFF_SOURCE': {
                    '__default__': {'child_tariff_source': 'xservice'},
                },
            },
            200,
            {'categories': ['child_tariff']},
            id='Check child tariff via xservice',
        ),
        pytest.param(
            {
                'park_id': 'park_1',
                'vehicle_id': 'car_1',
                'driver_profile_id': 'driver_1',
            },
            {},
            {},
            {
                'DRIVER_CATEGORIES_API_CHILD_TARIFF_SOURCE': {
                    '__default__': {'child_tariff_source': 'xservice'},
                    '/internal/v2/allowed_driver_categories': {
                        'child_tariff_source': '__disabled__',
                    },
                },
            },
            200,
            {'categories': []},
            id='Check child tariff (available, but disabled by config)',
        ),
        pytest.param(
            {
                'park_id': 'park_2',
                'vehicle_id': 'car_2',
                'driver_profile_id': 'shadow_driver',
            },
            {},
            {'driver_categories_settings': {'show_in_taximeter': False}},
            {},
            200,
            {'categories': []},
            id='Categories disabled by config3.0 driver_categories_settings',
        ),
        pytest.param(
            {
                'park_id': 'park_2',
                'vehicle_id': 'car_2',
                'driver_profile_id': 'shadow_driver',
            },
            {},
            {
                'child_tariff_visibility_settings': {
                    'always_show_in_taximeter': True,
                },
            },
            {},
            200,
            {'categories': ['child_tariff', 'class1', 'class2']},
            id='Child tariff is shown by config3.0 '
            'child_tariff_visibility_settings',
        ),
        pytest.param(
            {
                'park_id': 'park_2',
                'vehicle_id': 'car_2',
                'driver_profile_id': 'shadow_driver',
            },
            {'user-agent': 'taximeter 1.12 (129) ios'},
            {
                'clauses': [
                    {
                        'title': 'Title',
                        'value': {'always_show_in_taximeter': True},
                        'enabled': True,
                        'is_signal': False,
                        'predicate': {
                            'init': {
                                'predicates': [
                                    {
                                        'init': {
                                            'predicate': {
                                                'init': {
                                                    'value': 'taximeter-ios',
                                                    'arg_name': 'application',
                                                    'arg_type': 'string',
                                                },
                                                'type': 'eq',
                                            },
                                        },
                                        'type': 'not',
                                    },
                                ],
                            },
                            'type': 'all_of',
                        },
                        'is_tech_group': False,
                        'extension_method': 'replace',
                        'is_paired_signal': False,
                    },
                ],
            },
            {},
            200,
            {'categories': ['class1', 'class2']},
            id='Child tariff is not shown by config3.0 '
            'child_tariff_visibility_settings because of ios',
        ),
        pytest.param(
            {
                'park_id': 'park_3',
                'vehicle_id': 'car_3',
                'driver_profile_id': 'driver_3',
            },
            {'user-agent': 'diver-categories / 0.450'},
            {},
            {
                'DRIVER_CATEGORIES_API_CHILD_TARIFF_SOURCE': {
                    '__default__': {'child_tariff_source': 'xservice'},
                    '/internal/v2/allowed_driver_categories': {
                        'child_tariff_source': 'fleet-vehicles',
                    },
                },
            },
            200,
            {'categories': ['child_tariff']},
            id='Check child tariff via fleet-vehicles',
        ),
    ],
)
async def test_driver_categories_get(
        mockserver,
        taxi_driver_categories_api,
        load_json,
        taxi_config,
        experiments3,
        taximeter_xservice,
        driver_tags,
        fleet_parks,
        fleet_vehicles,
        driver_trackstory,
        exp3_values,
        config,
        params,
        headers,
        code,
        output,
):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_driver_profiles_retrive(request):
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'driver_3',
                    'data': {
                        'taximeter_version_type': '',
                        'taximeter_version': '10.12(123)',
                        'taximeter_platform': 'android',
                    },
                },
            ],
        }

    exp3_json_file = load_json('experiments3_defaults.json')
    for exp3_config in exp3_json_file['configs']:
        exp3_name = exp3_config['name']
        if exp3_name in exp3_values:
            exp3_config['default_value'] = exp3_values[exp3_name]
        if 'clauses' in exp3_values:
            exp3_config['clauses'] = exp3_values['clauses']

    experiments3.add_experiments_json(exp3_json_file)

    taxi_config.set_values(config)

    await taxi_driver_categories_api.invalidate_caches()

    response = await taxi_driver_categories_api.get(
        'internal/v2/allowed_driver_categories',
        params=params,
        headers=headers,
    )
    assert response.status_code == code

    if not output:
        return
    categories = response.json()['categories']
    categories.sort()
    assert categories == output['categories']
