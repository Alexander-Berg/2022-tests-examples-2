import pytest

X_YATAXI_API_KEY = 'test_api_key'


@pytest.mark.translations(
    corp={
        'client': {'ru': 'Клиент'},
        'manager': {'ru': 'Администратор'},
        'department_manager': {'ru': 'Менеджер департамента'},
        'department_secretary': {'ru': 'Секретарь департамента'},
    },
)
async def test_get_aclroles(web_app_client):
    response = await web_app_client.get(
        '/v1/admin/acl_roles/', headers={'X-YaTaxi-Api-Key': X_YATAXI_API_KEY},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'acl_roles': [
            {'role': 'client', 'translated_role': 'Клиент'},
            {'role': 'manager', 'translated_role': 'Администратор'},
            {
                'role': 'department_manager',
                'translated_role': 'Менеджер департамента',
            },
            {
                'role': 'department_secretary',
                'translated_role': 'Секретарь департамента',
            },
        ],
    }
