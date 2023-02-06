import pytest

from tests_contractor_profession import utils
from tests_contractor_profession import utils_db


def convert_strs_to_groups(str_arr, use_stored_profession):
    groups = []
    if use_stored_profession:
        return groups
    for elem in str_arr:
        groups.append({'id': elem})
    return groups


@pytest.mark.parametrize(
    'contractor_profile_id1, is_from_dbdrivers1, use_stored_profession1',
    [
        pytest.param('uuid1', True, False, id='first:op_stored&p_calc'),
        pytest.param('uuid3', True, True, id='first:op_stored&p_stored'),
        pytest.param('exp_driver1', False, False, id='first:op_calc&p_calc'),
        pytest.param('exp_driver3', False, True, id='first:op_calc&p_stored'),
    ],
)
@pytest.mark.parametrize(
    'contractor_profile_id2, is_from_dbdrivers2, use_stored_profession2',
    [
        pytest.param('uuid2', True, False, id='second:op_stored&p_calc'),
        pytest.param('uuid4', True, True, id='second:op_stored&p_stored'),
        pytest.param('exp_driver2', False, False, id='second:op_calc&p_calc'),
        pytest.param('exp_driver4', False, True, id='second:op_calc&p_stored'),
    ],
)
@pytest.mark.parametrize(
    'orders_provider1, profession_id1, profession_module1, groups1',
    [
        pytest.param(
            'taxi', 'taxi-driver', 'taxi-driver-module', [], id='taxi-driver',
        ),
        pytest.param(
            'taxi_walking_courier',
            'walking-courier',
            'walking-courier-module',
            ['logistics-courier'],
            id='walking-courier',
        ),
    ],
)
@pytest.mark.parametrize(
    'orders_provider2, profession_id2, profession_module2, groups2',
    [
        pytest.param(
            'eda',
            'eats-courier',
            'eats-courier-module',
            [],
            id='eats-courier',
        ),
        pytest.param(
            'cargo',
            'auto-courier',
            'auto-courier-module',
            ['logistics-courier'],
            id='auto-courier',
        ),
    ],
)
@pytest.mark.experiments3(filename='profession_config.json')
@pytest.mark.experiments3(filename='profession_module_config.json')
@pytest.mark.experiments3(filename='orders_provider_configs.json')
@pytest.mark.experiments3(filename='use_stored_professions.json')
async def test_get_active_profession_bulk(
        taxi_contractor_profession,
        driver_profiles,
        mock_fleet_parks_list,
        driver_tags_mocks,
        pgsql,
        contractor_profile_id1,
        is_from_dbdrivers1,
        use_stored_profession1,
        contractor_profile_id2,
        is_from_dbdrivers2,
        use_stored_profession2,
        orders_provider1,
        profession_id1,
        profession_module1,
        groups1,
        orders_provider2,
        profession_module2,
        profession_id2,
        groups2,
):
    expected_changelog = []

    def process_contractor_params(
            park_id,
            contractor_profile_id,
            profession,
            orders_provider,
            from_dbdrivers,
            use_stored_profession,
    ):
        if from_dbdrivers:
            driver_profiles.set_orders_provider(
                park_id=park_id,
                contractor_profile_id=contractor_profile_id,
                orders_provider=orders_provider,
            )
        should_write_profession = from_dbdrivers and not use_stored_profession
        if should_write_profession:
            expected_changelog.append(
                (
                    len(expected_changelog) + 1,
                    park_id,
                    contractor_profile_id,
                    profession,
                    'by_get_active_profession_handlers',
                ),
            )
        if not from_dbdrivers or use_stored_profession:
            utils_db.insert_professions(
                pgsql,
                park_id=park_id,
                driver_profile_id=contractor_profile_id,
                profession_id=profession,
            )

    process_contractor_params(
        'db1',
        contractor_profile_id1,
        profession_id1,
        orders_provider1,
        is_from_dbdrivers1,
        use_stored_profession1,
    )
    process_contractor_params(
        'db2',
        contractor_profile_id2,
        profession_id2,
        orders_provider2,
        is_from_dbdrivers2,
        use_stored_profession2,
    )

    response = await taxi_contractor_profession.post(
        '/internal/v1/professions/get/active/bulk',
        headers=utils.get_auth_headers(),
        json={
            'contractors': [
                {
                    'contractor_profile_id': contractor_profile_id1,
                    'park_id': 'db1',
                    'contractor_app': {
                        'version_type': 'yango',
                        'version': '10.11',
                        'platform': 'ios',
                    },
                },
                {
                    'contractor_profile_id': contractor_profile_id2,
                    'park_id': 'db2',
                    'contractor_app': {
                        'version_type': 'yango',
                        'version': '10.11',
                        'platform': 'ios',
                    },
                },
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'contractors': [
            {
                'contractor': {
                    'contractor_profile_id': contractor_profile_id1,
                    'park_id': 'db1',
                },
                'profession': {
                    'id': profession_id1,
                    'groups': convert_strs_to_groups(
                        groups1, use_stored_profession1,
                    ),
                },
                'profession_module': profession_module1,
            },
            {
                'contractor': {
                    'contractor_profile_id': contractor_profile_id2,
                    'park_id': 'db2',
                },
                'profession': {
                    'id': profession_id2,
                    'groups': convert_strs_to_groups(
                        groups2, use_stored_profession2,
                    ),
                },
                'profession_module': profession_module2,
            },
        ],
    }

    assert driver_tags_mocks.v1_match_profiles.times_called == 1

    assert (
        driver_profiles.retrieve_profiles.times_called == is_from_dbdrivers1
        or is_from_dbdrivers2
    )

    pg_professions = utils_db.select_professions(
        pgsql, fields=['park_id', 'contractor_id', 'profession_id'],
    )
    pg_professions.sort(key=lambda x: x[0])
    assert pg_professions == [
        ('db1', contractor_profile_id1, profession_id1),
        ('db2', contractor_profile_id2, profession_id2),
    ]

    changelog = utils_db.select_professions_changelog(pgsql)
    assert changelog == expected_changelog


@pytest.mark.parametrize(
    'contractor_profile_id1, contractor_profile_id2',
    [
        pytest.param('uuid1', 'exp_driver1', id='not_first_is_from_exp'),
        pytest.param('exp_driver1', 'uuid1', id='first_is_from_exp'),
        pytest.param('exp_driver1', 'exp_driver2', id='both_are_from_exp'),
    ],
)
@pytest.mark.experiments3(filename='orders_provider_configs.json')
async def test_get_not_init_active_profession_bulk_from_exp(
        taxi_contractor_profession,
        driver_profiles,
        mock_fleet_parks_list,
        pgsql,
        contractor_profile_id1,
        contractor_profile_id2,
):
    driver_profiles.set_orders_provider(
        park_id='db1',
        contractor_profile_id=contractor_profile_id1,
        orders_provider='eda',
    )

    driver_profiles.set_orders_provider(
        park_id='db2',
        contractor_profile_id=contractor_profile_id2,
        orders_provider='eda',
    )

    response = await taxi_contractor_profession.post(
        '/internal/v1/professions/get/active/bulk',
        headers=utils.get_auth_headers(),
        json={
            'contractors': [
                {
                    'contractor_profile_id': contractor_profile_id1,
                    'park_id': 'db1',
                    'contractor_app': {
                        'version_type': 'yango',
                        'version': '10.11',
                        'platform': 'ios',
                    },
                },
                {
                    'contractor_profile_id': contractor_profile_id2,
                    'park_id': 'db2',
                    'contractor_app': {
                        'version_type': 'yango',
                        'version': '10.11',
                        'platform': 'ios',
                    },
                },
            ],
        },
    )

    assert response.status_code == 500
