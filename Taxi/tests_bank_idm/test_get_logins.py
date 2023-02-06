import pytest

from tests_bank_idm import db_helpers


async def test_get_logins(taxi_bank_idm, pgsql):
    response = await taxi_bank_idm.post(
        'v1/get-logins',
        json=dict(system_slug='idm', slug_path='systems/idm/responsible'),
    )
    assert response.status_code == 200, f'{response.json()}'

    logins = response.json()['logins']
    assert len(logins) == 1
    assert logins[0] == 'kalievoral'


def create_rolenode_id(pgsql):
    slug_path = 'test/slug_path'
    system_slug = 'test_slug'

    responsible_user_id = db_helpers.add_user(pgsql, 'pam', 'test@gmail.com')
    system_id = db_helpers.add_system(pgsql, system_slug, responsible_user_id)
    return db_helpers.add_role_nodes(pgsql, slug_path, 'Slug Path', system_id)


def create_role(pgsql, login, role_status, rolenode_id):
    user_id = db_helpers.add_user(pgsql, login, 'test@gmail.com')
    db_helpers.add_role(pgsql, user_id, rolenode_id, role_status)


@pytest.mark.parametrize('no_role', ['deprived', 'requested', 'rerequested'])
async def test_get_multiply_logins(taxi_bank_idm, pgsql, no_role):
    rolenode_id = create_rolenode_id(pgsql)

    user_granted_first = 'user_granted_first'
    user_granted_second = 'user_granted_second'
    user_no_role = 'user_no_role'

    create_role(pgsql, user_no_role, no_role, rolenode_id)
    create_role(pgsql, user_granted_first, 'granted', rolenode_id)
    create_role(pgsql, user_granted_second, 'granted', rolenode_id)

    response = await taxi_bank_idm.post(
        'v1/get-logins',
        json=dict(system_slug='test_slug', slug_path='test/slug_path'),
    )
    assert response.status_code == 200, f'{response.json()}'

    logins = response.json()['logins']
    assert len(logins) == 2
    assert (
        logins[0] == 'user_granted_first'
        and logins[1] == 'user_granted_second'
    )


@pytest.mark.parametrize('unknown', ['system_slug', 'slug_path'])
async def test_get_user_roles_empty_rolenodes(taxi_bank_idm, pgsql, unknown):
    body_json = dict(system_slug='idm', slug_path='systems/idm/responsible')
    body_json[unknown] = 'unknown'
    response = await taxi_bank_idm.post('v1/get-logins', json=body_json)
    assert response.status_code == 404


async def test_disable_system(taxi_bank_idm, pgsql):
    user_login = 'test'
    db_helpers.prepare_test_data(pgsql, user_login, system_status='disabled')
    body_json = dict(system_slug='test_slug', slug_path='test/slug_path')
    response = await taxi_bank_idm.post('v1/get-logins', json=body_json)
    assert response.status_code == 400


async def test_empty_logins_list(taxi_bank_idm, pgsql):
    rolenode_id = create_rolenode_id(pgsql)
    create_role(pgsql, 'user', 'requested', rolenode_id)

    response = await taxi_bank_idm.post(
        'v1/get-logins',
        json=dict(system_slug='test_slug', slug_path='test/slug_path'),
    )
    assert response.status_code == 200, f'{response.json()}'

    logins = response.json()['logins']
    assert not logins
