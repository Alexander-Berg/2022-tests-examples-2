import pytest

from tests_contractor_state.test_contractor_client_configuration import consts


@pytest.mark.translations(
    taximeter_driver_messages={'string_for_translating1': {'ru': 'Строка1'}},
    bad_keyset={'string_for_translating2': {'ru': 'Строка2'}},
)
@pytest.mark.experiments3(
    name='config_name',
    consumers=[consts.EXPERIMENTS_CONSUMER],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'l10n': [
            {
                'default': 'default_value',
                'key': 'key1',
                'tanker': {
                    'key': 'string_for_translating1',
                    'keyset': 'taximeter_driver_messages',
                },
            },
            {
                'default': 'default_value2',
                'key': 'key2',
                'tanker': {
                    'key': 'string_for_translating2',
                    'keyset': 'bad_keyset',
                },
            },
        ],
    },
    is_config=True,
)
async def test_keysets(
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
    l10n = response.json()['typed_configs']['items']['config_name']['l10n']
    assert l10n['key1'] == 'Строка1'
    assert l10n['key2'] == 'default_value2'
