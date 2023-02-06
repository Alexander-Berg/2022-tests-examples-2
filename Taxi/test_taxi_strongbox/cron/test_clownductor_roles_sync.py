import pytest

from taxi.pg import pool

from taxi_strongbox.generated.cron import run_cron

DEFAULT_BODY = {
    'roles': [
        'nanny_admin_prod',
        'nanny_admin_testing',
        'strongbox_secrets_creation',
        'strongbox_secrets_prod',
        'strongbox_secrets_testing',
    ],
    'limit': 500,
}

FIRST_RESPONSE = {
    'cursor': {'greater_than': 3},
    'responsibles': [
        {
            'id': 1,
            'login': 'super',
            'role': 'nanny_admin_testing',
            'is_super': True,
        },
        {
            'id': 2,
            'login': 'some-mate',
            'role': 'nanny_admin_prod',
            'service_id': 1,
            'service_name': 'service-2',
            'project_id': 1,
            'project_name': 'taxi-infra',
            'is_super': False,
        },
        {
            'id': 3,
            'login': 'some-mate',
            'role': 'strongbox_secrets_prod',
            'service_id': 1,
            'service_name': 'service-2',
            'project_id': 2,
            'project_name': 'taxi',
            'is_super': False,
        },
        {
            'id': 4,
            'login': 'some-create-with-edit-test',
            'role': 'strongbox_secrets_creation',
            'service_id': 1,
            'service_name': 'service-2',
            'project_id': 2,
            'project_name': 'taxi',
            'is_super': False,
        },
    ],
}

SECOND_RESPONSE = {
    'responsibles': [
        {
            'id': 5,
            'login': 'super-2',
            'role': 'strongbox_secrets_prod',
            'is_super': True,
        },
        {
            'id': 6,
            'login': 'some-user-2',
            'role': 'strongbox_secrets_testing',
            'service_id': 2,
            'service_name': 'service-3',
            'project_id': 2,
            'project_name': 'taxi',
            'is_super': False,
        },
        {
            'id': 7,
            'login': 'some-user-2',
            'role': 'nanny_admin_testing',
            'service_id': 2,
            'service_name': 'service-3',
            'project_id': 2,
            'project_name': 'taxi',
            'is_super': False,
        },
        {
            'id': 8,
            'login': 'some-create-with-edit-test',
            'role': 'nanny_admin_testing',
            'service_id': 1,
            'service_name': 'service-2',
            'project_id': 2,
            'project_name': 'taxi',
            'is_super': False,
        },
    ],
}

CLOWNY_ROLES = [
    {
        'envs': ['production', 'testing', 'unstable'],
        'login': 'some-mate',
        'project_name': 'taxi',
        'role_type': 'create_secrets',
        'service_name': 'service',
        'tplatform_namespace': 'taxi',
    },
    {
        'envs': ['production', 'testing', 'unstable'],
        'login': 'some-mate',
        'project_name': 'taxi',
        'role_type': 'edit_secrets',
        'service_name': 'service',
        'tplatform_namespace': 'taxi',
    },
]

EXCPECTED = [
    {
        'envs': ['production', 'testing', 'unstable'],
        'login': 'some-create-with-edit-test',
        'project_name': 'taxi',
        'role_type': 'create_secrets',
        'service_name': 'service-2',
        'tplatform_namespace': 'taxi',
    },
    {
        'envs': ['testing', 'unstable'],
        'login': 'some-create-with-edit-test',
        'project_name': 'taxi',
        'role_type': 'edit_secrets',
        'service_name': 'service-2',
        'tplatform_namespace': 'taxi',
    },
    {
        'envs': ['production', 'testing', 'unstable'],
        'login': 'some-mate',
        'project_name': 'taxi',
        'role_type': 'create_secrets',
        'service_name': 'service-2',
        'tplatform_namespace': 'taxi',
    },
    {
        'envs': ['production', 'testing', 'unstable'],
        'login': 'some-mate',
        'project_name': 'taxi',
        'role_type': 'edit_secrets',
        'service_name': 'service-2',
        'tplatform_namespace': 'taxi',
    },
    {
        'envs': ['testing', 'unstable'],
        'login': 'some-user-2',
        'project_name': 'taxi',
        'role_type': 'create_secrets',
        'service_name': 'service-3',
        'tplatform_namespace': 'taxi',
    },
    {
        'envs': ['testing', 'unstable'],
        'login': 'some-user-2',
        'project_name': 'taxi',
        'role_type': 'edit_secrets',
        'service_name': 'service-3',
        'tplatform_namespace': 'taxi',
    },
    {
        'envs': ['production', 'testing', 'unstable'],
        'login': 'some-mate',
        'project_name': 'taxi-infra',
        'role_type': 'create_secrets',
        'service_name': 'service-2',
        'tplatform_namespace': 'taxi',
    },
    {
        'envs': ['production', 'testing', 'unstable'],
        'login': 'some-mate',
        'project_name': 'taxi-infra',
        'role_type': 'edit_secrets',
        'service_name': 'service-2',
        'tplatform_namespace': 'taxi',
    },
    {
        'envs': ['testing', 'unstable'],
        'login': 'super',
        'project_name': None,
        'role_type': 'create_secrets',
        'service_name': None,
        'tplatform_namespace': None,
    },
    {
        'envs': ['testing', 'unstable'],
        'login': 'super',
        'project_name': None,
        'role_type': 'edit_secrets',
        'service_name': None,
        'tplatform_namespace': None,
    },
    {
        'envs': ['production', 'testing', 'unstable'],
        'login': 'super-2',
        'project_name': None,
        'role_type': 'create_secrets',
        'service_name': None,
        'tplatform_namespace': None,
    },
    {
        'envs': ['production', 'testing', 'unstable'],
        'login': 'super-2',
        'project_name': None,
        'role_type': 'edit_secrets',
        'service_name': None,
        'tplatform_namespace': None,
    },
]


@pytest.mark.config(
    STRONGBOX_CLOWNDUCTOR_ROLES_SYNC={
        'enabled': True,
        'use_bulk_db_retrieve': False,
        'page_limit': 500,
        'sleep_time_sec': 0.1,
        'max_request_count': 20,
    },
    STRONGBOX_SCOPE_AUTHORIZE={
        'enabled': True,
        'login_required': False,
        'testing_roles': ['strongbox_secrets_testing', 'nanny_admin_testing'],
        'production_roles': ['strongbox_secrets_prod', 'nanny_admin_prod'],
        'secrets_creation_roles': ['strongbox_secrets_creation'],
    },
)
@pytest.mark.parametrize(
    'use_roles_from_clowny_roles',
    [
        pytest.param(
            True,
            marks=[pytest.mark.roles_features_on('strongbox_scopes_resolver')],
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.roles_features_off('strongbox_scopes_resolver'),
            ],
        ),
    ],
)
@pytest.mark.pgsql('strongbox', files=['test_clownductor_roles_sync.sql'])
async def test_clownductor_roles_sync(
        cron_context,
        mockserver,
        clowny_roles_grants,
        use_roles_from_clowny_roles,
):
    @mockserver.json_handler('/clownductor/permissions/v1/roles/responsibles/')
    def _mock(request):
        request_body = request.json
        if 'cursor' not in request_body:
            return FIRST_RESPONSE
        return SECOND_RESPONSE

    clowny_roles_grants.add_prod_editor(
        'some-mate', {'id': 'service-1', 'type': 'service'},
    )

    await run_cron.main(
        ['taxi_strongbox.crontasks.clownductor_roles_sync', '-t', '0'],
    )

    assert _mock.times_called == 2
    call_request = _mock.next_call()['request']
    assert call_request.json == DEFAULT_BODY
    call_request = _mock.next_call()['request']
    expected = dict(**DEFAULT_BODY)
    expected['cursor'] = {'greater_than': 3}
    assert call_request.json == expected
    records = await _get_db_records(cron_context)
    expected = EXCPECTED[:]
    if use_roles_from_clowny_roles:
        expected = CLOWNY_ROLES + expected
    assert records == expected


async def _get_db_records(context):
    master_pool: pool.Pool = context.pg.master_pool
    async with master_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT
                tplatform_namespace,
                project_name,
                service_name,
                login,
                role_type,
                array_agg(env order by env) envs
            FROM
                secrets.scope_rights
            GROUP BY
                tplatform_namespace,
                project_name,
                service_name,
                login,
                role_type
            ORDER BY
                tplatform_namespace,
                project_name,
                service_name,
                login,
                role_type
            """,
        )
    return [dict(record) for record in rows]
