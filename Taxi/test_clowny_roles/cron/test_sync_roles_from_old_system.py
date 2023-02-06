import pytest

from testsuite.utils import matching

from clowny_roles.internal.helpers.idm_roles_fetcher import models

LITTLE_EARLY_DT = '2019-12-11T09:23:54.427840+00:00'
DT_STR = '2020-12-11T09:23:54.427840+00:00'
ROLES = [
    {
        'id': 1,
        'type': 'active',
        'ownership': 'personal',
        'data': {'project': 'prj-1', 'project_role': 'deploy_approve_manager'},
        'user': {'username': 'user', 'is_active': True},
        'added': DT_STR,
        'updated': DT_STR,
        'state': 'granted',
        'system': {'slug': 'clownductor'},
        'node': {'slug': 'deploy_approve_manager'},
    },
    {
        'id': 2,
        'type': 'active',
        'ownership': 'group',
        'data': {
            'project': 'prj-1',
            'project_role': 'services_roles',
            'service': 'srv-1',
            'service_role': 'deploy_approve_programmer',
        },
        'group': {'slug': 'group', 'id': 1},
        'added': DT_STR,
        'updated': DT_STR,
        'state': 'granted',
        'system': {'slug': 'clownductor'},
        'node': {'slug': 'deploy_approve_programmer'},
    },
    {
        'id': 3,
        'type': 'active',
        'ownership': 'personal',
        'data': {'project': 'prj-2', 'project_role': 'deploy_approve_manager'},
        'user': {'username': 'user', 'is_active': True},
        'added': LITTLE_EARLY_DT,
        'updated': LITTLE_EARLY_DT,
        'state': 'declined',
        'system': {'slug': 'clownductor'},
        'node': {'slug': 'deploy_approve_manager'},
    },
    {
        'id': 4,
        'type': 'active',
        'ownership': 'personal',
        'data': {'project': 'prj-2', 'project_role': 'deploy_approve_manager'},
        'user': {'username': 'user', 'is_active': True},
        'added': DT_STR,
        'updated': DT_STR,
        'state': 'declined',
        'system': {'slug': 'clownductor'},
        'node': {'slug': 'deploy_approve_manager'},
    },
    {
        'id': 5,
        'type': 'active',
        'ownership': 'personal',
        'data': {'project': '__supers__', 'super_role': 'nanny_admin_testing'},
        'user': {'username': 'user', 'is_active': True},
        'added': DT_STR,
        'updated': DT_STR,
        'state': 'granted',
        'system': {'slug': 'clownductor'},
        'node': {'slug': 'nanny_admin_testing'},
    },
    {
        'id': 10006,
        'type': 'active',
        'ownership': 'personal',
        'data': {
            'project': 'deleted-project',
            'project_role': 'deploy_approve_manager',
        },
        'user': {'username': 'user', 'is_active': True},
        'added': DT_STR,
        'updated': DT_STR,
        'state': 'granted',
        'system': {'slug': 'clownductor'},
        'node': {'slug': 'deploy_approve_manager'},
    },
    {
        'id': 10007,
        'type': 'active',
        'ownership': 'personal',
        'data': {
            'project': 'prj-1',
            'project_role': 'services_roles',
            'service': 'deleted-service',
            'service_role': 'deploy_approve_programmer',
        },
        'user': {'username': 'user', 'is_active': True},
        'added': DT_STR,
        'updated': DT_STR,
        'state': 'granted',
        'system': {'slug': 'clownductor'},
        'node': {'slug': 'deploy_approve_manager'},
    },
    {
        'id': 200001,
        'type': 'active',
        'ownership': 'personal',
        'data': {
            'namespace': 'taxi',
            'namespace_role': 'project_roles',
            'project': 'prj-2',
            'project_role': 'subsystem_internal',
            'project_subsystem_internal': 'deploy_approve_manager',
        },
        'user': {'username': 'user', 'is_active': True},
        'added': LITTLE_EARLY_DT,
        'updated': LITTLE_EARLY_DT,
        'state': 'declined',
        'system': {'slug': 'clowny-platform'},
        'node': {'slug': 'deploy_approve_manager'},
    },
    {
        'id': 200002,
        'type': 'active',
        'ownership': 'personal',
        'data': {
            'namespace': 'taxi',
            'namespace_role': 'project_roles',
            'project': 'prj-2',
            'project_role': 'subsystem_internal',
            'project_subsystem_internal': 'deploy_approve_manager',
        },
        'user': {'username': 'user', 'is_active': True},
        'added': DT_STR,
        'updated': DT_STR,
        'state': 'granted',
        'system': {'slug': 'clowny-platform'},
        'node': {'slug': 'deploy_approve_manager'},
    },
]


@pytest.mark.config(
    CLOWNY_ROLES_OLD_TREE_SYNCER_SETTINGS={
        'system': 'clownductor',
        'new_system': 'clowny-platform',
        'fetch_limit': 50,
        'active_features': {},
        'inactive_features': {},
    },
)
@pytest.mark.parametrize(
    'db_checked_roles, batch_calls, deprive_calls',
    [
        pytest.param(
            [
                {
                    'role_id': 1,
                    'last_state': models.RoleState.requested.value,
                    'ownership': models.RoleOwnership.personal.value,
                    'checked_at': matching.datetime_string,
                },
                {
                    'role_id': 4,
                    'last_state': models.RoleState.deprived.value,
                    'ownership': models.RoleOwnership.personal.value,
                    'checked_at': matching.datetime_string,
                },
                {
                    'role_id': 2,
                    'last_state': models.RoleState.requested.value,
                    'ownership': models.RoleOwnership.group.value,
                    'checked_at': matching.datetime_string,
                },
            ],
            2,
            1,
            marks=[pytest.mark.roles_features_on('sync_old_system_to_new')],
            id='feature on',
        ),
        pytest.param(
            [],
            0,
            0,
            marks=[pytest.mark.roles_features_off('sync_old_system_to_new')],
            id='feature off',
        ),
    ],
)
async def test_sync_roles(
        mockserver,
        mock_idm,
        cron_context,
        cron_runner,
        mock_idm_batch,
        add_subsystem,
        add_role,
        db_checked_roles,
        batch_calls,
        deprive_calls,
):
    subsystem_id = await add_subsystem('internal')
    await add_role('deploy_approve_manager', 'prj-1', 'project', subsystem_id)
    await add_role(
        'deploy_approve_programmer', 'srv-1-slug', 'service', subsystem_id,
    )

    _batch_handler = mock_idm_batch()

    @mockserver.handler(r'/idm/api/v1/roles/(?P<role_id>\d+)/', regex=True)
    def _deprive_handler(request, role_id):
        if int(role_id) == 200002 and request.method == 'DELETE':
            return mockserver.make_response(status=204)
        return mockserver.make_response(status=404)

    @mock_idm('/api/v1/roles/')
    def _handler(request):
        role_ownership = request.query['ownership']
        system_slug = request.query['system']

        roles = [
            x
            for x in ROLES
            if x['ownership'] == role_ownership
            and x['system']['slug'] == system_slug
        ]

        return {
            'meta': {
                'limit': int(request.query['limit']),
                'offset': 0,
                'total_count': len(roles),
                'next': None,
                'previous': None,
            },
            'objects': roles,
        }

    await cron_runner.sync_roles_from_old_system()

    calls = []
    while _handler.has_calls:
        calls.append(_handler.next_call())

    assert len(calls) == 4
    assert [x['request'].query for x in calls] == [
        {
            'limit': '50',
            'parent_type': 'absent',
            'system': 'clownductor',
            'ownership': 'personal',
        },
        {
            'limit': '50',
            'parent_type': 'absent',
            'system': 'clowny-platform',
            'ownership': 'personal',
        },
        {
            'limit': '50',
            'parent_type': 'absent',
            'system': 'clownductor',
            'ownership': 'group',
        },
        {
            'limit': '50',
            'parent_type': 'absent',
            'system': 'clowny-platform',
            'ownership': 'group',
        },
    ]

    repo = models.Repository(cron_context)
    checked_roles = await repo.fetch_all(cron_context.pg.primary)
    assert [x.as_dict() for x in checked_roles] == db_checked_roles
    assert _batch_handler.times_called == batch_calls
    assert _deprive_handler.times_called == deprive_calls
