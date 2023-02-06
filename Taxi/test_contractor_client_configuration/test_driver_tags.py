import pytest

from tests_contractor_state.test_contractor_client_configuration import consts


@pytest.mark.experiments3(
    name='config_name',
    consumers=[consts.EXPERIMENTS_CONSUMER],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={'default_key': 'default_value'},
    is_config=True,
    clauses=[
        {
            'predicate': {
                'type': 'contains',
                'init': {
                    'arg_name': 'driver_tags',
                    'set_elem_type': 'string',
                    'value': 'tag1',
                },
            },
            'value': {'key': 'val'},
        },
    ],
)
async def test_driver_tags_kwarg(
        taxi_contractor_state,
        mockserver,
        mock_fleet_parks_list,  # from library-client-fleet-parks
        driver_tags_mocks,  # from library-client-driver-tags
        unique_drivers_mocks,  # from conftest
        driver_ui_profile_mocks,  # from conftest
):
    driver_tags_mocks.set_tags_info(
        'park_id', 'driver_profile_id', ['tag1', 'tag2'],
    )

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
    default_value={'default_key': 'default_value'},
    is_config=True,
    clauses=[
        {
            'predicate': {
                'type': 'in_set',
                'init': {
                    'arg_name': 'unique_driver_id',
                    'set_elem_type': 'string',
                    'set': ['unique_driver_id'],
                },
            },
            'value': {'key': 'val'},
        },
    ],
)
async def test_driver_tags_with_unique_driver_id(
        taxi_contractor_state,
        mockserver,
        mock_fleet_parks_list,  # from library-client-fleet-parks
        driver_tags_mocks,  # from library-client-driver-tags
        driver_ui_profile_mocks,  # from conftest
):
    driver_tags_mocks.set_tags_info(
        dbid='park_id',
        uuid='driver_profile_id',
        tags=['tag1', 'tag2'],
        udid='unique_driver_id',
    )
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
    default_value={'default_key': 'default_value'},
    is_config=True,
    clauses=[
        {
            'predicate': {
                'type': 'in_set',
                'init': {
                    'arg_name': 'unique_driver_id',
                    'set_elem_type': 'string',
                    'set': ['unique_driver_id'],
                },
            },
            'value': {'key': 'val'},
        },
    ],
)
async def test_driver_tags_without_unique_driver_id(
        taxi_contractor_state,
        mockserver,
        mock_fleet_parks_list,  # from library-client-fleet-parks
        driver_tags_mocks,  # from library-client-driver-tags
        driver_ui_profile_mocks,  # from conftest
        unique_drivers_mocks,  # from conftest
):
    driver_tags_mocks.set_tags_info(
        dbid='park_id', uuid='driver_profile_id', tags=['tag1', 'tag2'],
    )
    response = await taxi_contractor_state.post(
        '/v1/contractor/client-configuration',
        headers=consts.DEFAULT_HEADERS,
        json={},
    )
    assert response.status_code == 200
    configs = response.json()['typed_configs']['items']
    assert configs['config_name']['default_key'] == 'default_value'


async def test_driver_tags_error(
        taxi_contractor_state,
        mockserver,
        mock_fleet_parks_list,  # from library-client-fleet-parks
        driver_tags_mocks,  # from library-client-driver-tags
        driver_ui_profile_mocks,  # from conftest
):
    driver_tags_mocks.set_error(
        handler='/v2/drivers/match/profile', error_code=500,
    )
    response = await taxi_contractor_state.post(
        '/v1/contractor/client-configuration',
        headers=consts.DEFAULT_HEADERS,
        json={},
    )
    assert response.status_code == 200  # driver_tags is optional kwarg
