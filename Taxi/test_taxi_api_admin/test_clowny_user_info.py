LOGIN_ROLES = {'superuser': ['super_role', 'super_duper']}


async def test_platform_user_info(taxi_api_admin_client, mock_clowny_roles):
    @mock_clowny_roles('/grands/v1/user_info/')
    async def _request(*args, **kwargs):
        request = args[0].json
        login = request['login']
        return {'login': login, 'roles': LOGIN_ROLES.get(login, [])}

    response = await taxi_api_admin_client.get('/platform/user_info/')
    assert response.status == 200
    data = await response.json()
    assert data == {
        'login': 'superuser',
        'roles': LOGIN_ROLES.get('superuser', []),
    }
    assert _request.times_called == 1


async def test_platform_user_info_400(taxi_api_admin_client):
    response = await taxi_api_admin_client.get('/platform/user_info/')
    assert response.status == 400
    data = await response.json()
    assert data == {
        'status': 'error',
        'message': 'Error occurred while requesting clowny_roles service',
        'code': 'CLOWNY_ROLES_HANDLER_ERROR',
    }
