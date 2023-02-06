import pytest

import tests_bank_idm.db_helpers as db_helpers


async def test_front_suggest_roles_without_text(taxi_bank_idm):
    response = await taxi_bank_idm.post(
        'v1/front/v1/suggest/roles',
        json={'system_slug': 'idm', 'parent_slug_path': 'systems'},
    )
    assert response.status_code == 200
    roles = response.json()['roles_info']
    assert len(roles) == 1


async def test_front_suggest_roles_all_roles_by_system(taxi_bank_idm):
    response = await taxi_bank_idm.post(
        'v1/front/v1/suggest/roles', json={'system_slug': 'idm'},
    )
    assert response.status_code == 200
    roles = response.json()['roles_info']
    assert len(roles) == 1


@pytest.mark.parametrize('text', [' ', '/', 'a/', 'a/b'])
async def test_front_suggest_roles_bad_text_pattern(taxi_bank_idm, text):
    response = await taxi_bank_idm.post(
        'v1/front/v1/suggest/roles', json={'system_slug': 'idm', 'text': text},
    )
    assert response.status_code == 400


async def test_front_suggest_roles_empty_response(taxi_bank_idm):
    response = await taxi_bank_idm.post(
        'v1/front/v1/suggest/roles',
        json={'system_slug': 'idm', 'text': 'ystem'},
    )
    assert response.status_code == 200
    assert response.json() == {'roles_info': []}


@pytest.mark.parametrize('parent_slug_path', ['a/b', 'a/bc/de'])
async def test_front_suggest_roles_bad_parent_slug_path(
        taxi_bank_idm, pgsql, parent_slug_path,
):
    user_id = db_helpers.add_user(
        pgsql, user_login='test_user', user_email='@',
    )
    system_id = db_helpers.add_system(
        pgsql, system_slug='system_slug1', user_id=user_id,
    )
    db_helpers.add_role_nodes(pgsql, 'a/bc/d', 'Slug Path', system_id)
    db_helpers.add_role_nodes(pgsql, 'a/bc/e', 'Slug Path', system_id)
    response = await taxi_bank_idm.post(
        'v1/front/v1/suggest/roles',
        json={
            'system_slug': 'system_slug1',
            'text': '',
            'parent_slug_path': parent_slug_path,
        },
    )
    assert response.status_code == 200
    assert response.json() == {'roles_info': []}


async def test_front_suggest_roles_few_roles(taxi_bank_idm, pgsql):
    user_id = db_helpers.add_user(
        pgsql, user_login='test_user', user_email='@',
    )
    system_id = db_helpers.add_system(
        pgsql, system_slug='system_slug1', user_id=user_id,
    )

    rolenode_id = db_helpers.add_role_nodes(
        pgsql, 'a/bc', 'Slug Path', system_id,
    )
    db_helpers.add_role_nodes(
        pgsql,
        'a/bc/d',
        'Slug Path',
        system_id,
        parent_rolenode_id=rolenode_id,
    )
    db_helpers.add_role_nodes(
        pgsql,
        'a/bc/e',
        'Slug Path',
        system_id,
        parent_rolenode_id=rolenode_id,
    )
    response = await taxi_bank_idm.post(
        'v1/front/v1/suggest/roles',
        json={
            'system_slug': 'system_slug1',
            'text': '',
            'parent_slug_path': 'a/bc',
        },
    )
    assert response.status_code == 200
    roles = response.json()['roles_info']
    assert len(roles) == 2


async def test_front_suggest_roles_with_create_rolenode(taxi_bank_idm, pgsql):
    system_slug = 'system_slug1'
    user_login = 'test_user'
    user_id = db_helpers.add_user(pgsql, user_login=user_login, user_email='@')
    db_helpers.add_system(pgsql, system_slug=system_slug, user_id=user_id)
    request = {
        'system_slug': system_slug,
        'user_login': user_login,
        'role_name': 'Test Role',
        'slug_path': 'a/bc/d',
        'hide': False,
    }
    response = await taxi_bank_idm.post('v1/create-role', json=request)
    assert response.status_code == 200
    response = await taxi_bank_idm.post(
        'v1/front/v1/suggest/roles',
        json={
            'system_slug': system_slug,
            'text': '',
            'parent_slug_path': 'a/bc',
        },
    )
    assert response.status_code == 200
    roles = response.json()['roles_info']
    assert len(roles) == 1
