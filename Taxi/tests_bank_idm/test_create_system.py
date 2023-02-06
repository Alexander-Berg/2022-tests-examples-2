import pytest

import tests_bank_idm.db_helpers as db_helpers


@pytest.mark.parametrize('system_path', ['test_system_path', None])
async def test_create_system_ok(taxi_bank_idm, pgsql, system_path):
    user_login = 'test_user'
    user_id = db_helpers.add_user(
        pgsql, user_login='test_user', user_email='@',
    )
    request = {
        'system_slug': 'test_system',
        'system_name': 'Test System',
        'system_description': 'test_system\'s description',
        'responsible_users': [user_login, user_login],
        'system_path': system_path,
        'creator': user_login,
    }

    response = await taxi_bank_idm.post('v1/create-system', json=request)
    assert response.status_code == 200

    cursor = pgsql['bank_idm'].cursor()
    cursor.execute(
        'select * from bank_idm.systems where system_slug != \'idm\'',
    )
    result = cursor.fetchall()
    assert len(result) == 1
    assert result[0][1] == request['system_slug']
    assert result[0][2] == request['system_name']
    assert result[0][3] == request['system_description']
    assert result[0][4] == system_path
    assert result[0][5] == user_id

    cursor.execute(
        'select * from bank_idm.actions '
        f'where system_id = {db_helpers.SELF_SYSTEM_ID}',
    )
    actions = cursor.fetchall()
    assert len(actions) >= 4

    cursor.execute(
        'select slug_path from bank_idm.roles '
        'join bank_idm.role_nodes using (rolenode_id) '
        f'where user_id = {user_id} and '
        f'system_id = {db_helpers.SELF_SYSTEM_ID} and is_leaf = true',
    )
    roles = cursor.fetchall()
    assert len(roles) == 1
    assert roles[0][0] == 'systems/test_system/responsible'


@pytest.mark.parametrize(
    'system_slug', ['', ' ', 'текст_на_русском', '!', 'a b'],
)
async def test_create_system_bad_system_slug(taxi_bank_idm, system_slug):
    request = {
        'system_slug': system_slug,
        'system_name': 'Test System',
        'system_description': 'test_system\'s description',
        'system_path': 'http://test.yandex.net/v1/idm/',
        'responsible_users': ['kalievoral', 'kalievoral'],
        'creator': 'kalievoral',
    }

    response = await taxi_bank_idm.post('v1/create-system', json=request)
    assert response.status_code == 400


async def test_create_system_no_such_responsible_user(taxi_bank_idm):
    request = {
        'system_slug': 'test_system',
        'system_name': 'Test System',
        'system_description': 'test_system\'s description',
        'system_path': 'http://test.yandex.net/v1/idm/',
        'responsible_users': ['100500'],
        'creator': 'kalievoral',
    }

    response = await taxi_bank_idm.post('v1/create-system', json=request)
    assert response.status_code == 404


async def test_create_system_no_such_creator(taxi_bank_idm):
    request = {
        'system_slug': 'test_system',
        'system_name': 'Test System',
        'system_description': 'test_system\'s description',
        'system_path': 'http://test.yandex.net/v1/idm/',
        'responsible_users': ['kalievoral'],
        'creator': '100500',
    }

    response = await taxi_bank_idm.post('v1/create-system', json=request)
    assert response.status_code == 404
