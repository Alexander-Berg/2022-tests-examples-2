from typing import List

import pytest

from clowny_roles.crontasks import add_roles_to_idm


@pytest.fixture(name='init_mocks')
def _init_mocks(
        mock_clownductor, mock_idm_batch, add_subsystem, add_role, add_grand,
):
    async def _wrapper(idm_mock_responses_by_id=None):
        duty_ids = (i for i in range(1, 11))

        @mock_clownductor('/v1/services/duty_info/')
        def duty_info_handler(request):
            service_id = request.json['service_id']
            if service_id == 4:
                return {
                    'duty_group_id': 'abc_slug:primary_schedule',
                    'duty_person_logins': ['login-1', 'login-2'],
                }
            return {
                'duty_group_id': f'group-{service_id}',
                'duty_person_logins': [
                    f'duty-{next(duty_ids)}',
                    f'duty-{next(duty_ids)}',
                ],
            }

        duty_roles = [
            'nanny_admin_prod',
            'nanny_admin_testing',
            'mdb_cluster_ro_access',
        ]
        admin_roles = ['nanny_admin_prod']
        services = ['srv-1-slug', 'srv-3-slug', 'srv-4-slug', 'srv-5-slug']
        projects = ['prj-1', 'prj-2', 'prj-3']

        internal_subsystem_id = await add_subsystem('internal')
        for service in services:
            for duty_role in duty_roles:
                await add_role(
                    duty_role, service, 'service', internal_subsystem_id,
                )
        for project in projects:
            for admin_role in admin_roles:
                await add_role(
                    admin_role, project, 'project', internal_subsystem_id,
                )
        await add_grand('duty-1', 1)
        await add_grand('duty-4', 5)
        await add_grand('admin-2', 4)

        return {
            'duty_info_handler': duty_info_handler,
            'batch_handler': mock_idm_batch(
                responses_by_id=idm_mock_responses_by_id,
            ),
        }

    return _wrapper


@pytest.fixture(name='get_requested_roles')
def _get_requested_roles(cron_context, get_roles, get_subsystem):
    async def _wrapper() -> List[add_roles_to_idm.RequestedRole]:
        roles = await get_roles()
        roles_by_scope = {x.scope: x for x in roles}
        subsystem = await get_subsystem('internal')

        query, _ = cron_context.sqlt.meta_requested_roles_fetch_all()
        async with cron_context.pg_manager.secondary_connect() as conn:
            rows = await conn.fetch(query)
        return [
            add_roles_to_idm.RequestedRole.from_db(
                x, roles_by_scope, subsystem,
            )
            for x in rows
        ]

    return _wrapper


@pytest.fixture(name='add_requested_roles')
def _add_requested_roles(cron_context):
    async def _wrapper(*requests: add_roles_to_idm.RequestedRole):
        query, args = cron_context.sqlt.meta_requested_roles_upsert_many(
            [x.to_db() for x in requests],
        )
        async with cron_context.pg_manager.primary_connect() as conn:
            await conn.fetch(query, *args)

    return _wrapper


CONFIG_MARK = pytest.mark.config(
    CLOWNDUCTOR_NEW_IDM_SYSTEM_USAGE={
        '__default__': {
            '__default__': {
                '__default__': {'idm_request_roles_for_sync_cron': False},
            },
        },
        'taxi': {
            'prj-1': {
                '__default__': {'idm_request_roles_for_sync_cron': True},
            },
            'prj-2': {
                '__default__': {'idm_request_roles_for_sync_cron': True},
            },
            'prj-3': {
                '__default__': {'idm_request_roles_for_sync_cron': False},
            },
        },
    },
    CLOWNDUCTOR_SYNC_DUTY_ADMINS={
        'no_duty_in_stable_owners': [
            {'project_name': 'prj-2', 'service_name': 'srv-3'},
        ],
    },
)


@CONFIG_MARK
async def test_add_roles_to_idm(
        load_yaml, cron_runner, init_mocks, get_requested_roles,
):
    mocks = await init_mocks()

    await cron_runner.add_roles_to_idm()

    assert mocks['duty_info_handler'].times_called == 5

    requests = []
    while mocks['batch_handler'].has_calls:
        requests.append(mocks['batch_handler'].next_call())

    # cause srv-4 has abc duty, we do not call idm
    assert len(requests) == 4
    for i, request_ in enumerate(requests):
        assert request_['request'].json == load_yaml(
            f'idm_request_{i}.yaml',
        ), i

    roles = await get_requested_roles()
    assert {x.idm_role_id for x in roles} == set(range(1, 15))
    assert len(roles) == 14


@CONFIG_MARK
async def test_add_roles_with_retries(
        cron_runner,
        get_role,
        init_mocks,
        add_requested_roles,
        get_requested_roles,
):
    mocks = await init_mocks(
        idm_mock_responses_by_id={
            (
                'taxi+project_roles+'
                'prj=1+service_roles+'
                'srv=1+subsystem_internal+'
                'mdb_cluster_ro_access-None-duty=1'
            ): {
                'body': {
                    'message': (
                        '...'
                        'в системе "Платформа Клоундуктор" '
                        'в состоянии "Выдана"'
                        '...'
                    ),
                },
                'status_code': 400,
                'reason': 'already_requested',
            },
        },
    )
    await add_requested_roles(
        add_roles_to_idm.RequestedRole(
            idm_role_id=1,
            role_meta=add_roles_to_idm.RoleMeta(
                login='duty-1',
                group_id=None,
                role=await get_role(
                    'mdb_cluster_ro_access', 'service', 'srv-1-slug',
                ),
            ),
        ),
    )

    await cron_runner.add_roles_to_idm()

    assert mocks['duty_info_handler'].times_called == 5

    requests = []
    while mocks['batch_handler'].has_calls:
        requests.append(mocks['batch_handler'].next_call())

    assert len(requests) == 4

    roles = await get_requested_roles()
    assert {x.idm_role_id for x in roles} == set(range(1, 15))
    assert len(roles) == 14


@CONFIG_MARK
async def test_task_for_removing_roles(
        load_yaml,
        cron_runner,
        get_role,
        init_mocks,
        add_requested_roles,
        get_requested_roles,
):
    mocks = await init_mocks()

    # this role will be deleted
    await add_requested_roles(
        add_roles_to_idm.RequestedRole(
            idm_role_id=100500,
            role_meta=add_roles_to_idm.RoleMeta(
                login=None,
                group_id=123,
                role=await get_role(
                    'mdb_cluster_ro_access', 'service', 'srv-1-slug',
                ),
            ),
        ),
    )

    await cron_runner.add_roles_to_idm()

    assert mocks['duty_info_handler'].times_called == 5

    requests = []
    while mocks['batch_handler'].has_calls:
        requests.append(mocks['batch_handler'].next_call())

    assert len(requests) == 5

    # we only interested in deprive request
    # other (role request) checked before
    assert requests[-1]['request'].json == load_yaml(
        'idm_deprive_request.yaml',
    )

    roles = await get_requested_roles()
    assert {x.idm_role_id for x in roles} == set(range(1, 15))
    assert len(roles) == 14
