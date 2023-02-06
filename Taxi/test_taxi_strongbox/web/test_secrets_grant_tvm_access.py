import pytest

STRONGBOX_TVM_ACCESS = {
    'services': {
        'archiving': {'testing': ['archiving-testing']},
        'replication': {'testing': ['replication-testing']},
    },
}


@pytest.mark.features_on('auto_discover_scope', 'check_scope_by_clown')
@pytest.mark.config(
    STRONGBOX_SCOPE_AUTHORIZE={
        'enabled': True,
        'login_required': False,
        'testing_roles': ['strongbox_secrets_testing', 'nanny_admin_testing'],
        'production_roles': ['strongbox_secrets_prod', 'nanny_admin_prod'],
        'secrets_creation_roles': ['strongbox_secrets_creation'],
    },
    STRONGBOX_TVM_ACCESS=STRONGBOX_TVM_ACCESS,
)
@pytest.mark.pgsql('strongbox', files=['test_secrets.sql'])
@pytest.mark.parametrize(
    'secret_key, service_name, expected_tvm_access',
    [
        ('SEARCH_ABLE_SECRET_2', 'replication', ['replication']),
        ('TVM_ACCESS_SECRET', 'archiving', ['archiving', 'replication']),
    ],
)
async def test_secrets_grant_tvm_access(
        web_context,
        web_app_client,
        clown_roles_mock,
        secret_key,
        service_name,
        expected_tvm_access,
):
    clown_roles_mock()
    headers = {
        'X-YaTaxi-Api-Key': 'strongbox_api_token',
        'X-Yandex-Login': 'some-mate',
    }
    response = await web_app_client.post(
        '/v1/secrets/grant_tvm_access/',
        json={'service_name': service_name, 'secret_key': secret_key},
        headers=headers,
    )
    data = await response.json()
    assert response.status == 200, data
    tvm_access = await _get_tvm_access(web_context, secret_key)
    assert tvm_access == expected_tvm_access


@pytest.mark.config(STRONGBOX_TVM_ACCESS=STRONGBOX_TVM_ACCESS)
async def test_secrets_grant_tvm_access_403(web_context, web_app_client):
    response = await web_app_client.post(
        '/v1/secrets/grant_tvm_access/',
        json={'service_name': 'archiving', 'secret_key': 'TVM_ACCESS_SECRET'},
    )
    data = await response.json()
    assert response.status == 403, data


async def _get_tvm_access(context, secret_key):
    query, args = context.sqlt.tvm_access_get_tvm_services(
        secret_keys=[secret_key],
    )
    async with context.pg.master_pool.acquire() as conn:
        results = await conn.fetch(query, *args)
    assert len(results) == 1
    return results[0]['service_names']
