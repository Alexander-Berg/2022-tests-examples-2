import pytest

import tests_bank_idm.db_helpers as db_helpers


async def test_front_systems(taxi_bank_idm):
    response = await taxi_bank_idm.post('v1/front/v1/systems', json={})
    assert response.status_code == 200
    roles = response.json()['systems_info']
    assert len(roles) == 1
    assert roles == [
        {
            'system_description': 'Bank IDM system',
            'system_id': 1,
            'system_name': 'IDM',
            'system_slug': 'idm',
            'system_status': 'enabled',
        },
    ]


async def test_front_systems_few_systems(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    db_helpers.prepare_test_data(pgsql, user_login)
    response = await taxi_bank_idm.post('v1/front/v1/systems', json={})
    assert response.status_code == 200
    roles = response.json()['systems_info']
    assert len(roles) == 2


@pytest.mark.parametrize('system_slug', [' ', 'текст_на_русском', '!', 'a b'])
async def test_front_systems_bad_system_slug(
        taxi_bank_idm, pgsql, system_slug,
):
    response = await taxi_bank_idm.post(
        f'v1/front/v1/systems/{system_slug}', json={},
    )
    assert response.status_code == 400


async def test_front_systems_system_slug(taxi_bank_idm, pgsql):
    user_login = 'test_user'
    db_helpers.prepare_test_data(pgsql, user_login)
    system_slug = 'test_slug'
    response = await taxi_bank_idm.post(
        f'v1/front/v1/systems/{system_slug}', json={},
    )
    assert response.status_code == 200
    system = response.json()
    assert system == {
        'system_info': {
            'system_description': 'TEST SYSTEM DESCRIPTION',
            'system_id': 2,
            'system_name': 'TEST SYSTEM',
            'system_slug': 'test_slug',
            'system_status': 'enabled',
        },
        'responsible_users': ['responsible'],
    }


async def test_front_systems_system_slug_not_found(taxi_bank_idm, pgsql):
    system_slug = 'not_existed_system'
    response = await taxi_bank_idm.post(
        f'v1/front/v1/systems/{system_slug}', json={},
    )
    assert response.status_code == 404
