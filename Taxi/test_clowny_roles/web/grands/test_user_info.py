import pytest


CODE_400 = 'REQUEST_VALIDATION_ERROR'


@pytest.fixture(name='data_fill', autouse=True)
async def _data_fill(add_subsystem, add_role, add_grand):
    internal_id = await add_subsystem('internal')
    project_role_id = await add_role(
        'test_task_manager', '1', 'project', internal_id,
    )
    await add_grand('test-login-1', project_role_id)
    await add_grand('test-login-2', project_role_id)

    deploy_role_id = await add_role('test_admin', '1', 'service', internal_id)
    await add_grand('test-login-1', deploy_role_id)


@pytest.mark.parametrize(
    'login, roles',
    [
        (
            'test-login-1',
            [
                'approvals_user',
                'approvals_view',
                'test_admin',
                'test_service_responsible',
                'test_task_manager',
                'test_user',
            ],
        ),
        (
            'test-login-2',
            [
                'approvals_user',
                'approvals_view',
                'test_task_manager',
                'test_user',
            ],
        ),
        ('test-login-empty', []),
    ],
)
async def test_user_info(requests_post, login, roles):
    body = {'login': login}
    response = await requests_post('/grands/v1/user_info', body)
    data = await response.json()
    assert response.status == 200, data
    assert data == {'login': login, 'roles': roles}


async def test_user_info_login_empty(requests_post):
    body = {'login': ''}
    response = await requests_post('/grands/v1/user_info', body)
    data = await response.json()
    assert response.status == 400, data
    assert data['code'] == CODE_400


async def test_user_info_body_none(requests_post):
    body = {}
    response = await requests_post('/grands/v1/user_info', body)
    data = await response.json()
    assert response.status == 400, data
    assert data['code'] == CODE_400
