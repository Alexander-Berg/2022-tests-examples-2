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
                    'arg_name': 'metrica_id',
                    'set': ['metrica_id'],
                    'set_elem_type': 'string',
                },
            },
            'value': {'key': 'val'},
        },
    ],
    default_value={'default_key': 'default_value'},
    is_config=True,
)
async def test_metrica_id_in_request(
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
        json={'metrica_id': 'metrica_id'},
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
                    'arg_name': 'metrica_id',
                    'set': ['metrica_id'],
                    'set_elem_type': 'string',
                },
            },
            'value': {'key': 'val'},
        },
    ],
    default_value={'default_key': 'default_value'},
    is_config=True,
)
async def test_no_metrica_id_in_request(
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
    assert configs['config_name']['default_key'] == 'default_value'
