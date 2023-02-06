import pytest


@pytest.mark.parametrize('handler', ['/user_info', '/user_info/'])
async def test_user_info(taxi_api_admin_client, handler):
    response = await taxi_api_admin_client.request(
        'GET', handler, cookies={'yandexuid': '24248601603782976'},
    )
    assert response.status == 200
    data = await response.json()
    data['permissions'] = sorted(data['permissions'])
    assert data == {
        'login': 'superuser',
        'permissions': [
            'send_sms',
            'send_sms_new',
            'test_perm',
            'view_drafts',
        ],
        'filters': {},
        'api_switch': {},
    }
