import pytest

import tests_bank_idm.db_helpers as db_helpers


IDM_SYSTEM_INFO = {
    'system_description': 'Bank IDM system',
    'system_id': 1,
    'system_name': 'IDM',
    'system_slug': 'idm',
    'system_status': 'enabled',
}


async def test_front_suggest_systems_without_text(taxi_bank_idm):
    response = await taxi_bank_idm.post(
        'v1/front/v1/suggest/systems', json={'text': ''},
    )
    assert response.status_code == 200
    roles = response.json()['systems_info']
    assert len(roles) == 1
    assert roles == [IDM_SYSTEM_INFO]


@pytest.mark.parametrize('text', ['', 'I', 'ID', 'IDM', 'i', 'id', 'idm'])
async def test_front_suggest_systems_success(taxi_bank_idm, text):
    response = await taxi_bank_idm.post(
        'v1/front/v1/suggest/systems', json={'text': text},
    )
    assert response.status_code == 200
    assert response.json()['systems_info'] == [IDM_SYSTEM_INFO]


@pytest.mark.parametrize('text', ['D', 'DM', 'IDMM', ' '])
async def test_front_suggest_systems_empty_response(taxi_bank_idm, text):
    response = await taxi_bank_idm.post(
        'v1/front/v1/suggest/systems', json={'text': text},
    )
    assert response.status_code == 200
    assert response.json()['systems_info'] == []


@pytest.mark.parametrize('text', ['s', 'system'])
async def test_front_suggest_systems_few_systems(taxi_bank_idm, pgsql, text):
    user_id = db_helpers.add_user(
        pgsql, user_login='test_user', user_email='@',
    )
    db_helpers.add_system(
        pgsql,
        system_slug='test/system/slug1',
        user_id=user_id,
        system_name='system1',
    )
    db_helpers.add_system(
        pgsql,
        system_slug='test/system/slug2',
        user_id=user_id,
        system_name='system2',
    )
    response = await taxi_bank_idm.post(
        'v1/front/v1/suggest/systems', json={'text': text},
    )
    assert response.status_code == 200
    roles = response.json()['systems_info']
    assert len(roles) == 2
