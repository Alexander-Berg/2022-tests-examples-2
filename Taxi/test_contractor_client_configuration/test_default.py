import pytest

from tests_contractor_state.test_contractor_client_configuration import consts


@pytest.mark.experiments3(
    name='config_name1',
    consumers=[consts.EXPERIMENTS_CONSUMER],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {
                'type': 'in_set',
                'init': {
                    'arg_name': 'park_id',
                    'set_elem_type': 'string',
                    'set': ['park_id'],
                },
            },
            'value': {'key': 'val'},
        },
    ],
    default_value={'default_key': 'default_value'},
    is_config=True,
)
@pytest.mark.experiments3(
    name='config_name2',
    consumers=[consts.EXPERIMENTS_CONSUMER],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'default_key': 'default_value'},
    is_config=True,
)
@pytest.mark.experiments3(
    name='experiment_name1',
    consumers=[consts.EXPERIMENTS_CONSUMER],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {
                'type': 'in_set',
                'init': {
                    'arg_name': 'park_id',
                    'set_elem_type': 'string',
                    'set': ['park_id'],
                },
            },
            'value': {'key': 'val'},
        },
    ],
    default_value={'default_key': 'default_value'},
    is_config=False,
)
@pytest.mark.experiments3(
    name='experiment_name2',
    consumers=[consts.EXPERIMENTS_CONSUMER],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'default_key': 'default_value'},
    is_config=False,
)
async def test_ok(
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
    assert configs['config_name1']['key'] == 'val'
    assert configs['config_name2']['default_key'] == 'default_value'

    experiments = response.json()['typed_experiments']['items']
    assert experiments['experiment_name1']['key'] == 'val'
    assert experiments['experiment_name2']['default_key'] == 'default_value'


async def test_unauthorized_401(
        taxi_contractor_state,
        mockserver,
        mock_fleet_parks_list,  # from library-client-fleet-parks
        driver_tags_mocks,  # from library-client-driver-tags
        unique_drivers_mocks,  # from conftest
        driver_ui_profile_mocks,  # from conftest
):
    headers = {**consts.DEFAULT_HEADERS}
    headers['X-YaTaxi-Driver-Profile-Id'] = ''

    response = await taxi_contractor_state.post(
        '/v1/contractor/client-configuration', headers=headers, json={},
    )
    assert response.status_code == 401
