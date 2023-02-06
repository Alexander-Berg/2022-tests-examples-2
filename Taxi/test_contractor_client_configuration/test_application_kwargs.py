import pytest

from tests_contractor_state.test_contractor_client_configuration import consts


@pytest.mark.experiments3(
    name='config_name',
    consumers=[consts.EXPERIMENTS_CONSUMER],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {
                'type': 'in_set',
                'init': {
                    'arg_name': 'application.brand',
                    'set': ['yandex'],
                    'set_elem_type': 'string',
                },
            },
            'value': {'key': 'val'},
        },
    ],
    default_value={'default_key': 'default_value'},
    is_config=True,
)
async def test_app_kwargs(
        taxi_contractor_state,
        mockserver,
        mock_fleet_parks_list,  # from library-client-fleet-parks
        driver_tags_mocks,  # from library-client-driver-tags
        unique_drivers_mocks,  # from conftest
        driver_ui_profile_mocks,  # from conftest
):
    response = await taxi_contractor_state.post(
        '/v1/contractor/client-configuration',
        headers=consts.DEFAULT_HEADERS,
        json={},
    )
    assert response.status_code == 200
    configs = response.json()['typed_configs']['items']
    assert configs['config_name']['key'] == 'val'


@pytest.mark.experiments3(
    name='config_name',
    consumers=[consts.EXPERIMENTS_CONSUMER],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {
                'type': 'in_set',
                'init': {
                    'arg_name': 'build_type',
                    'set': ['beta'],
                    'set_elem_type': 'string',
                },
            },
            'value': {'key': 'val'},
        },
    ],
    default_value={'default_key': 'default_value'},
    is_config=True,
)
async def test_build_type_kwarg(
        taxi_contractor_state,
        mockserver,
        mock_fleet_parks_list,  # from library-client-fleet-parks
        driver_tags_mocks,  # from library-client-driver-tags
        unique_drivers_mocks,  # from conftest
        driver_ui_profile_mocks,  # from conftest
):
    headers = {**consts.DEFAULT_HEADERS}
    headers['X-Request-Application-Build-Type'] = 'beta'

    response = await taxi_contractor_state.post(
        '/v1/contractor/client-configuration', headers=headers, json={},
    )
    assert response.status_code == 200
    configs = response.json()['typed_configs']['items']
    assert configs['config_name']['key'] == 'val'


@pytest.mark.experiments3(
    name='config_name',
    consumers=[consts.EXPERIMENTS_CONSUMER],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {
                'type': 'in_set',
                'init': {
                    'arg_name': 'build_type',
                    'set': [''],
                    'set_elem_type': 'string',
                },
            },
            'value': {'key': 'val'},
        },
    ],
    default_value={'default_key': 'default_value'},
    is_config=True,
)
async def test_build_type_kwarg_default1(
        taxi_contractor_state,
        mockserver,
        mock_fleet_parks_list,  # from library-client-fleet-parks
        driver_tags_mocks,  # from library-client-driver-tags
        unique_drivers_mocks,  # from conftest
        driver_ui_profile_mocks,  # from conftest
):
    headers = {**consts.DEFAULT_HEADERS}
    del headers['X-Request-Application-Build-Type']
    # equals headers['X-Request-Application-Build-Type'] = ''

    response = await taxi_contractor_state.post(
        '/v1/contractor/client-configuration', headers=headers, json={},
    )
    assert response.status_code == 200
    configs = response.json()['typed_configs']['items']
    assert configs['config_name']['key'] == 'val'


@pytest.mark.experiments3(
    name='config_name',
    consumers=[consts.EXPERIMENTS_CONSUMER],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {
                'type': 'in_set',
                'init': {
                    'arg_name': 'build_type',
                    'set': [''],
                    'set_elem_type': 'string',
                },
            },
            'value': {'key': 'val'},
        },
    ],
    default_value={'default_key': 'default_value'},
    is_config=True,
)
async def test_build_type_kwarg_default2(
        taxi_contractor_state,
        mockserver,
        mock_fleet_parks_list,  # from library-client-fleet-parks
        driver_tags_mocks,  # from library-client-driver-tags
        unique_drivers_mocks,  # from conftest
        driver_ui_profile_mocks,  # from conftest
):
    headers = {**consts.DEFAULT_HEADERS}
    headers['X-Request-Application-Build-Type'] = ''
    # equals del headers['X-Request-Application-Build-Type']

    response = await taxi_contractor_state.post(
        '/v1/contractor/client-configuration', headers=headers, json={},
    )
    assert response.status_code == 200
    configs = response.json()['typed_configs']['items']
    assert configs['config_name']['key'] == 'val'
