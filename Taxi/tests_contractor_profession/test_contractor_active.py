import pytest

from tests_contractor_profession import utils
from tests_contractor_profession import utils_db


def convert_strs_to_groups(str_arr):
    groups = []
    for elem in str_arr:
        groups.append({'id': elem})
    return groups


@pytest.mark.parametrize(
    'contractor_profile_id, is_from_dbdrivers',
    [
        pytest.param('uuid1', True, id='orders_provider_from_dbdrivers'),
        pytest.param('exp_driver1', False, id='orders_provider_from_exp'),
    ],
)
@pytest.mark.parametrize(
    'orders_provider, profession_id, groups',
    [
        ('eda', 'eats-courier', []),
        ('taxi', 'taxi-driver', []),
        ('cargo', 'auto-courier', ['logistics-courier']),
        ('taxi_walking_courier', 'walking-courier', ['logistics-courier']),
    ],
)
@pytest.mark.experiments3(filename='profession_config.json')
@pytest.mark.experiments3(filename='orders_provider_configs.json')
async def test_get_active_profession(
        taxi_contractor_profession,
        mockserver,
        driver_profiles,
        pgsql,
        contractor_profile_id,
        is_from_dbdrivers,
        orders_provider,
        profession_id,
        groups,
):
    if is_from_dbdrivers:
        driver_profiles.set_orders_provider(
            park_id='db1',
            contractor_profile_id=contractor_profile_id,
            orders_provider=orders_provider,
        )
    else:
        utils_db.insert_professions(
            pgsql,
            driver_profile_id=contractor_profile_id,
            profession_id=profession_id,
        )

    response = await taxi_contractor_profession.get(
        'driver/v1/contractor-profession/v1/professions/active',
        headers=utils.get_auth_headers(
            driver_profile_id=contractor_profile_id,
        ),
    )

    assert response.status_code == 200
    assert response.json() == {
        'profession': {
            'id': profession_id,
            'groups': convert_strs_to_groups(groups),
        },
    }

    result = utils_db.select_professions(
        pgsql, driver_profile_id=contractor_profile_id,
    )
    assert result == [(1, 'db1', contractor_profile_id, profession_id)]

    result = utils_db.select_professions_changelog(pgsql)
    if is_from_dbdrivers:
        assert result == [
            (
                1,
                'db1',
                contractor_profile_id,
                profession_id,
                'by_get_active_profession_handlers',
            ),
        ]
    else:
        assert result == []

    assert driver_profiles.retrieve_profiles.times_called == is_from_dbdrivers


@pytest.mark.experiments3(filename='orders_provider_configs.json')
async def test_get_not_init_profession_from_exp(taxi_contractor_profession):
    response = await taxi_contractor_profession.get(
        'driver/v1/contractor-profession/v1/professions/active',
        headers=utils.get_auth_headers(driver_profile_id='exp_driver1'),
    )

    assert response.status_code == 500
