async def test_handler(web_app_client):
    response = await web_app_client.get(
        '/permissions/v1/idm/get-roles/',
        headers={'X-IDM-Request-Id': 'abc'},
        params={'limit': 3},
    )
    assert response.status == 200, await response.text()
    result = await response.json()
    assert result == {
        'code': 0,
        'roles': [
            {
                'login': 'd1mbas',
                'path': '/project/taxi/project_role/deploy_approve_manager/',
            },
            {
                'path': (
                    '/project/taxi/project_role/services_roles/service'
                    '/clownductor/service_role/deploy_approve_programmer/'
                ),
                'login': 'd1mbas',
            },
            {
                'path': '/project/__supers__/super_role/nanny_admin_prod/',
                'login': 'd1mbas',
            },
        ],
        'next-url': (
            '/permissions/v1/idm/get-roles/?limit=3&greater_than=3&stop_on=6'
        ),
    }

    response = await web_app_client.get(
        result['next-url'], headers={'X-IDM-Request-Id': 'abc'},
    )
    assert response.status == 200, await response.text()
    assert await response.json() == {
        'code': 0,
        'roles': [
            {
                'path': '/project/eda/project_role/deploy_approve_manager/',
                'login': 'd1mbas',
            },
            {
                'path': (
                    '/project/taxi/project_role/services_roles/service'
                    '/clownductor/service_role/deploy_approve_programmer/'
                ),
                'login': 'd1mbas',
            },
            {
                'path': (
                    '/project/eda/project_role/services_roles/service'
                    '/clownductor/service_role/deploy_approve_programmer/'
                ),
                'login': 'd1mbas',
            },
        ],
    }
