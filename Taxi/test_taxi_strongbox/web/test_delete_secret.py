import pytest

SECRET_KEY = 'TVM_ACCESS_SECRET'


@pytest.mark.pgsql('strongbox', files=['test_secrets.sql'])
async def test_delete_secret(web_context):
    count = await web_context.pg.master_pool.fetchval(
        'SELECT COUNT(*) FROM secrets.tvm_access WHERE secret_key = $1',
        SECRET_KEY,
    )
    assert count == 1
    await web_context.pg.master_pool.execute(
        'DELETE FROM secrets.secrets WHERE key = $1', SECRET_KEY,
    )
    count = await web_context.pg.master_pool.fetchval(
        'SELECT COUNT(*) FROM secrets.tvm_access WHERE secret_key = $1',
        SECRET_KEY,
    )
    assert count == 0


@pytest.mark.parametrize(
    ['body', 'expected_status', 'expected_content'],
    [
        pytest.param(
            {'key': 'SEARCH_ABLE_SECRET_2'},
            200,
            {'key': 'SEARCH_ABLE_SECRET_2'},
        ),
        pytest.param(
            {'key': 'SEARCH_ABLE_SECRET_2', 'env': 'production'},
            200,
            {'env': 'production', 'key': 'SEARCH_ABLE_SECRET_2'},
        ),
        pytest.param(
            {'key': 'TEST_1', 'env': 'unstable'},
            400,
            {
                'message': (
                    'Secret scope is empty, cant remove in admin. use script'
                ),
                'code': 'REQUEST_ERROR',
            },
        ),
        pytest.param(
            {'key': 'not_found_key'},
            404,
            {
                'code': 'SECRET_NOT_FOUND',
                'message': 'Secret: not_found_key is not found',
            },
        ),
    ],
)
@pytest.mark.pgsql('strongbox', files=['test_secrets.sql'])
async def test_apply_remove_secret(
        taxi_strongbox_web, body, expected_status, expected_content,
):
    response = await taxi_strongbox_web.post(
        '/v1/secrets/remove/',
        json=body,
        headers={
            'X-Yandex-Login': 'login',
            'X-YaTaxi-Api-Key': 'strongbox_api_token',
        },
    )
    assert response.status == expected_status
    data = await response.json()
    assert data == expected_content
