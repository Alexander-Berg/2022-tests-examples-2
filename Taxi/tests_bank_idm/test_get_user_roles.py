import pytest

from tests_bank_idm import db_helpers


async def test_get_user_roles_single_role(taxi_bank_idm, pgsql):
    user_login = 'alice'
    user_id, rolenode_id = db_helpers.prepare_test_data(
        pgsql, user_login=user_login,
    )
    role_id = db_helpers.add_role(pgsql, user_id, rolenode_id)

    response = await taxi_bank_idm.post(
        'v1/get-user-roles',
        json=dict(
            user_login=user_login,
            roles=[dict(system_slug='test_slug', slug_path='test/slug_path')],
        ),
    )
    assert response.status_code == 200, f'{response.json()}'

    roles = response.json()['roles']
    assert len(roles) == 1

    role = roles[0]
    assert 'role' in role
    role = role['role']
    assert role['role_id'] == role_id
    assert role['rolenode_id'] == rolenode_id
    assert role['role_status'] == 'granted'


async def test_get_user_roles_multiple_roles(taxi_bank_idm, pgsql):
    user_login = 'test'
    system_slug = 'test_system'

    user_id = db_helpers.add_user(pgsql, user_login, 'test@yandex.ru')
    system_id = db_helpers.add_system(pgsql, system_slug, user_id)

    request_roles = list()
    roles = list()

    def create_role(status):
        idx = len(roles)
        slug_path = f'role/{idx}/responsible'
        rolenode_id = db_helpers.add_role_nodes(
            pgsql, slug_path, f'Role {idx}', system_id,
        )
        role_id = None
        if status:
            role_id = db_helpers.add_role(
                pgsql, user_id, rolenode_id, role_status=status,
            )

        request_roles.append(
            dict(system_slug=system_slug, slug_path=slug_path),
        )
        roles.append(
            dict(rolenode_id=rolenode_id, role_id=role_id, status=status),
        )

    create_role('granted')
    create_role('deprived')
    create_role(None)
    create_role('requested')

    response = await taxi_bank_idm.post(
        'v1/get-user-roles', json=dict(user_login='test', roles=request_roles),
    )
    assert response.status_code == 200

    response_roles = response.json()['roles']
    assert len(response_roles) == len(roles)

    for response_role, role in zip(response_roles, roles):
        if role.get('status', None):
            assert 'role' in response_role, str(response_role) + str(role)
            response_role = response_role['role']
            assert response_role['role_id'] == role['role_id']
            assert response_role['rolenode_id'] == role['rolenode_id']
            assert response_role['role_status'] == role['status']
        else:
            assert 'role' not in response_role


async def test_get_user_roles_disabled_system(taxi_bank_idm, pgsql):
    user_login = 'test'
    user_id = db_helpers.add_user(pgsql, user_login, 'test@yandex.ru')

    def prepare_system_rolenode_role(
            user_id,
            system_slug,
            slug_path,
            system_status='enabled',
            role_status='granted',
    ):
        system_id = db_helpers.add_system(
            pgsql, system_slug, user_id, system_status,
        )
        rolenode_id = db_helpers.add_role_nodes(
            pgsql, slug_path, f'Role {slug_path}', system_id,
        )
        role_id = db_helpers.add_role(pgsql, user_id, rolenode_id, role_status)

        return dict(rolenode_id=rolenode_id, role_id=role_id)

    first = prepare_system_rolenode_role(user_id, 'left_system', 'role/path')
    second = prepare_system_rolenode_role(
        user_id, 'right_system', 'role/path', system_status='disabled',
    )

    response = await taxi_bank_idm.post(
        'v1/get-user-roles',
        json=dict(
            user_login=user_login,
            roles=[
                dict(system_slug='left_system', slug_path='role/path'),
                dict(system_slug='right_system', slug_path='role/path'),
            ],
        ),
    )

    assert response.status_code == 200

    roles = response.json()['roles']
    assert len(roles) == 2

    role = roles[0]
    assert 'role' in role
    role = role['role']
    assert role['role_id'] == first['role_id']
    assert role['rolenode_id'] == first['rolenode_id']
    assert role['role_status'] == 'granted'

    role = roles[1]
    assert 'role' in role
    role = role['role']
    assert role['role_id'] == second['role_id']
    assert role['rolenode_id'] == second['rolenode_id']
    assert role['role_status'] == 'deprived'


async def test_get_user_roles_user_not_found(taxi_bank_idm):
    user_login = 'alice'
    response = await taxi_bank_idm.post(
        'v1/get-user-roles',
        json=dict(
            user_login=user_login,
            roles=[dict(system_slug='system_slug', slug_path='slug/path')],
        ),
    )
    assert response.status_code == 404


@pytest.mark.parametrize('system_slug', ('unknown', 'test_slug'))
async def test_get_user_roles_role_not_found(
        taxi_bank_idm, pgsql, system_slug,
):
    user_login = 'test'
    user_id, rolenode_id = db_helpers.prepare_test_data(
        pgsql, user_login=user_login,
    )
    db_helpers.add_role(pgsql, user_id, rolenode_id)
    response = await taxi_bank_idm.post(
        'v1/get-user-roles',
        json=dict(
            user_login=user_login,
            roles=[
                dict(system_slug=system_slug, slug_path='test/slug_path'),
                dict(system_slug=system_slug, slug_path='test/unknown_path'),
            ],
        ),
    )
    assert response.status_code == 404


async def test_get_user_roles_empty_rolenodes(taxi_bank_idm, pgsql):
    user_login = 'alice'
    db_helpers.prepare_test_data(pgsql, user_login=user_login)

    response = await taxi_bank_idm.post(
        'v1/get-user-roles', json=dict(user_login=user_login, roles=[]),
    )
    assert response.status_code == 400


async def test_get_user_roles_without_role(taxi_bank_idm, pgsql):
    user_login = 'bob'
    db_helpers.prepare_test_data(pgsql, user_login=user_login)

    response = await taxi_bank_idm.post(
        'v1/get-user-roles',
        json=dict(
            user_login=user_login,
            roles=[dict(system_slug='test_slug', slug_path='test/slug_path')],
        ),
    )
    assert response.status_code == 200, f'{response.json()}'

    roles = response.json()['roles']
    assert len(roles) == 1
    assert 'role' not in roles[0]
