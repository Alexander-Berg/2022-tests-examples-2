import pytest

from testsuite.utils import matching

from clownductor.internal.tasks import cubes


def task_data(name='name'):
    return {
        'id': 123,
        'job_id': 456,
        'name': name,
        'sleep_until': 0,
        'input_mapping': {},
        'output_mapping': {},
        'payload': {},
        'retries': 0,
        'status': 'in_progress',
        'error_message': None,
        'created_at': 0,
        'updated_at': 0,
    }


@pytest.fixture(name='call_cube_with_handler')
def _call_cube_with_handler(web_app_client):
    async def _wrapper(cube_name, input_data, payload=None):
        response = await web_app_client.post(
            f'/task-processor/v1/cubes/{cube_name}/',
            json={
                'input_data': input_data,
                'status': 'in_progress',
                'task_id': 1,
                'job_id': 1,
                'retries': 0,
            },
        )
        assert response.status == 200, await response.text()
        result = await response.json()
        assert result['status'] == 'success'
        if payload is not None:
            assert result['payload'] == payload

    return _wrapper


@pytest.fixture(name='call_cube_directly')
def _call_cube_directly(web_context):
    async def _wrapper(cube_name, input_data, payload=None):
        cube = cubes.CUBES[cube_name](
            web_context, task_data(), input_data, [], None,
        )
        await cube.update()
        assert cube.success
        if payload is not None:
            assert cube.payload == payload

    return _wrapper


@pytest.mark.parametrize('use_handler', [True, False])
@pytest.mark.parametrize(
    'cube_name, input_data, payload, batch_paths, batch_bodies',
    [
        (
            'PermissionsAddNodesForService',
            {'service_id': 2},
            None,
            [
                '/rolenodes/',
                '/rolenodes/',
                '/rolenodes/',
                '/rolenodes/',
                '/rolenodes/',
                '/rolenodes/',
                '/rolenodes/',
                '/rolenodes/',
                '/rolenodes/',
                '/rolenodes/',
                '/rolenodes/',
                '/rolenodes/',
                '/rolenodes/',
            ],
            [
                {
                    'parent': (
                        '/project/taxi/project_role/services_roles/service/'
                    ),
                    'slug': 'service-2',
                    'system': 'clownductor',
                    'unique_id': 'srv-2',
                    'name': {'en': 'service-2', 'ru': 'service-2'},
                },
                {
                    'parent': (
                        '/project/taxi/project_role/services_roles'
                        '/service/service-2/'
                    ),
                    'slug': 'service_role',
                    'system': 'clownductor',
                    'name': {'en': 'service role', 'ru': 'сервисная роль'},
                },
                {
                    'help': {
                        'en': 'Allows to approve release by developer',
                        'ru': 'Даёт право на аппрув релиза разработчиком',
                    },
                    'name': {
                        'en': 'deploy approve by developer',
                        'ru': 'ок выкатки разработчика',
                    },
                    'parent': (
                        '/project/taxi/project_role/services_roles'
                        '/service/service-2/service_role/'
                    ),
                    'set': 'deploy_approve_programmer',
                    'slug': 'deploy_approve_programmer',
                    'system': 'clownductor',
                    'unique_id': 'srv-2-deploy_approve_programmer',
                },
                {
                    'help': {
                        'en': 'Allows to approve release by manager',
                        'ru': 'Даёт право на аппрув релиза менеджером',
                    },
                    'name': {
                        'en': 'deploy approve by manager',
                        'ru': 'ок выкатки менеджера',
                    },
                    'parent': (
                        '/project/taxi/project_role/services_roles'
                        '/service/service-2/service_role/'
                    ),
                    'set': 'deploy_approve_manager',
                    'slug': 'deploy_approve_manager',
                    'system': 'clownductor',
                    'unique_id': 'srv-2-deploy_approve_manager',
                },
                {
                    'help': {
                        'en': (
                            'Allows to approve sandbox '
                            'resource release by developer'
                        ),
                        'ru': (
                            'Даёт право на аппрув '
                            'sandbox-ресурса разработчиком'
                        ),
                    },
                    'name': {
                        'en': (
                            'deploy approve for sandbox resource by developer'
                        ),
                        'ru': 'ок выкатки sandbox ресурса разработчиком',
                    },
                    'parent': (
                        '/project/taxi/project_role/services_roles'
                        '/service/service-2/service_role/'
                    ),
                    'set': 'deploy_approve_sandbox_programmer',
                    'slug': 'deploy_approve_sandbox_programmer',
                    'system': 'clownductor',
                    'unique_id': 'srv-2-deploy_approve_sandbox_programmer',
                },
                {
                    'help': {
                        'en': 'Gives admin role in nanny service (in stable)',
                        'ru': (
                            'Выдаёт в няня сервисе админские права '
                            '(в продакшене)'
                        ),
                    },
                    'name': {
                        'en': 'admin rights to nanny service (stable)',
                        'ru': 'админский доступ в няня сервис (продакшен)',
                    },
                    'parent': (
                        '/project/taxi/project_role/services_roles'
                        '/service/service-2/service_role/'
                    ),
                    'set': 'nanny_admin_prod',
                    'slug': 'nanny_admin_prod',
                    'system': 'clownductor',
                    'unique_id': 'srv-2-nanny_admin_prod',
                },
                {
                    'help': {
                        'en': 'Gives admin role in nanny service (in testing)',
                        'ru': (
                            'Выдаёт в няня сервисе админские права '
                            '(в тестинге)'
                        ),
                    },
                    'name': {
                        'en': 'admin rights to nanny service (testing)',
                        'ru': 'админский доступ в няня сервис (тестинг)',
                    },
                    'parent': (
                        '/project/taxi/project_role/services_roles'
                        '/service/service-2/service_role/'
                    ),
                    'set': 'nanny_admin_testing',
                    'slug': 'nanny_admin_testing',
                    'system': 'clownductor',
                    'unique_id': 'srv-2-nanny_admin_testing',
                },
                {
                    'help': {
                        'en': 'Gives rights to change secrets (in stable)',
                        'ru': (
                            'Выдаёт права для создания и '
                            'редактирования секретов (в продакшене)'
                        ),
                    },
                    'name': {
                        'en': 'access to change secrets (stable)',
                        'ru': 'доступ на редактирование секретов (продакшен)',
                    },
                    'parent': (
                        '/project/taxi/project_role/services_roles/service'
                        '/service-2/service_role/'
                    ),
                    'set': 'strongbox_secrets_prod',
                    'slug': 'strongbox_secrets_prod',
                    'system': 'clownductor',
                    'unique_id': 'srv-2-strongbox_secrets_prod',
                },
                {
                    'help': {
                        'en': 'Gives rights to change secrets (in testing)',
                        'ru': (
                            'Выдаёт права для создания и'
                            ' редактирования секретов (в тестинге)'
                        ),
                    },
                    'name': {
                        'en': 'access to change secrets (testing)',
                        'ru': 'доступ на редактирование секретов (тестинг)',
                    },
                    'parent': (
                        '/project/taxi/project_role/services_roles/service'
                        '/service-2/service_role/'
                    ),
                    'set': 'strongbox_secrets_testing',
                    'slug': 'strongbox_secrets_testing',
                    'system': 'clownductor',
                    'unique_id': 'srv-2-strongbox_secrets_testing',
                },
                {
                    'help': {
                        'en': (
                            'Gives rights to create secrets '
                            'in all environments'
                        ),
                        'ru': (
                            'Выдаёт права для создания секретов '
                            'во всех окружениях'
                        ),
                    },
                    'name': {
                        'en': 'access to create secrets',
                        'ru': 'доступ на создание секретов',
                    },
                    'parent': (
                        '/project/taxi/project_role/services_roles'
                        '/service/service-2/service_role/'
                    ),
                    'set': 'strongbox_secrets_creation',
                    'slug': 'strongbox_secrets_creation',
                    'system': 'clownductor',
                    'unique_id': 'srv-2-strongbox_secrets_creation',
                },
                {
                    'help': {
                        'en': (
                            'Grants ro access to mdb cluster, '
                            'it allows you to view base cluster info, '
                            'monitoring in YC interface'
                        ),
                        'ru': (
                            'Выдаёт доступ на кластер mdb, '
                            'который позволяет просматривать базовую '
                            'информацию о кластере, '
                            'а также его мониторинги в интерфейсе yc'
                        ),
                    },
                    'name': {
                        'en': 'ro accesses for mdb cluster',
                        'ru': 'доступ на чтение до mdb кластера баз',
                    },
                    'parent': (
                        '/project/taxi/project_role/services_roles'
                        '/service/service-2/service_role/'
                    ),
                    'set': 'mdb_cluster_ro_access',
                    'slug': 'mdb_cluster_ro_access',
                    'system': 'clownductor',
                    'unique_id': 'srv-2-mdb_cluster_ro_access',
                },
                {
                    'help': {
                        'en': (
                            'Grants developer role to nanny service. '
                            'This role allows to use non-root ssh.'
                        ),
                        'ru': (
                            'Выдаёт роль developer в няня сервисе. '
                            'Роль даёт не рутовый ssh доступ к сервису.'
                        ),
                    },
                    'name': {
                        'en': 'developer access to nanny service',
                        'ru': 'разработческий доступ к няня сервису',
                    },
                    'parent': (
                        '/project/taxi/project_role/services_roles'
                        '/service/service-2/service_role/'
                    ),
                    'set': 'nanny_developer',
                    'slug': 'nanny_developer',
                    'system': 'clownductor',
                    'unique_id': 'srv-2-nanny_developer',
                },
                {
                    'help': {
                        'en': (
                            'Grants evicter role to nanny service. '
                            'This role allows to use pods eviction.'
                        ),
                        'ru': (
                            'Выдаёт роль evicter в няня сервисе. '
                            'Роль даёт доступ к эвакуации подов.'
                        ),
                    },
                    'name': {
                        'en': 'access to nanny service pods eviction',
                        'ru': 'доступ к эвакуации подов няня сервиса',
                    },
                    'parent': (
                        '/project/taxi/project_role/services_roles'
                        '/service/service-2/service_role/'
                    ),
                    'set': 'nanny_evicter',
                    'slug': 'nanny_evicter',
                    'system': 'clownductor',
                    'unique_id': 'srv-2-nanny_evicter',
                },
            ],
        ),
        (
            'PermissionsDeleteNodesForDeletingService',
            {'service_id': 2},
            None,
            [
                (
                    '/rolenodes/clownductor'
                    '/project/taxi/project_role'
                    '/services_roles/service/service-2/'
                ),
            ],
            None,
        ),
        (
            'PermissionsRequestRolesForNewService',
            {'service_id': 2},
            {'roles_to_approve': [1, 2, 3, 4]},
            [
                '/rolerequests/',
                '/rolerequests/',
                '/rolerequests/',
                '/rolerequests/',
            ],
            [
                {
                    'group': 50889,
                    'path': (
                        '/taxi/services_roles/service-2/nanny_admin_testing/'
                    ),
                    'system': 'clownductor',
                },
                {
                    'group': 50889,
                    'path': (
                        '/taxi/services_roles/service-2'
                        '/strongbox_secrets_creation/'
                    ),
                    'system': 'clownductor',
                },
                {
                    'group': 50889,
                    'path': (
                        '/taxi/services_roles/service-2/mdb_cluster_ro_access/'
                    ),
                    'system': 'clownductor',
                },
                {
                    'path': (
                        '/taxi/services_roles'
                        '/service-2/deploy_approve_programmer/'
                    ),
                    'system': 'clownductor',
                    'user': 'ilyasov',
                },
            ],
        ),
        pytest.param(
            'PermissionsRequestRolesForNewService',
            {'service_id': 2},
            {'roles_to_approve': [1, 2, 3]},
            ['/rolerequests/', '/rolerequests/', '/rolerequests/'],
            [
                {
                    'group': 50889,
                    'path': (
                        '/taxi/services_roles/service-2/nanny_admin_testing/'
                    ),
                    'system': 'clownductor',
                },
                {
                    'group': 50889,
                    'path': (
                        '/taxi/services_roles/service-2'
                        '/strongbox_secrets_creation/'
                    ),
                    'system': 'clownductor',
                },
                {
                    'path': (
                        '/taxi/services_roles'
                        '/service-2/deploy_approve_programmer/'
                    ),
                    'system': 'clownductor',
                    'user': 'ilyasov',
                },
            ],
            marks=pytest.mark.config(
                CLOWNDUCTOR_RESTRICT_RO_FOR_MDB={'__default__': True},
            ),
        ),
        pytest.param(
            'PermissionsRequestRoleForDuty',
            {'service_id': 1, 'branch_id': 1, 'need_updates': True},
            {'actual_role_ids': [1]},
            ['/rolerequests/'],
            [
                {
                    'group': 50889,
                    'path': '/taxi/services_roles/service-1/nanny_admin_prod/',
                    'system': 'clownductor',
                    'without_hold': True,
                    'comment': (
                        matching.RegexString(
                            r'automatic request role for duty group '
                            r'\(job_id: \d+, task_id: \d+\)',
                        )
                    ),
                },
            ],
        ),
        pytest.param(
            'PermissionsRevokeRoleForDuty',
            {
                'service_id': 1,
                'branch_id': 1,
                'need_updates': True,
                'actual_role_ids': [1],
            },
            {'revoked_role_ids': []},
            [],
            [],
        ),
        pytest.param(
            'PermissionsRequestRoleForDuty',
            {'service_id': 1, 'need_updates': True},
            {'actual_role_ids': [1]},
            ['/rolerequests/'],
            [
                {
                    'group': 50889,
                    'path': '/taxi/services_roles/service-1/nanny_admin_prod/',
                    'system': 'clownductor',
                    'without_hold': True,
                    'comment': (
                        matching.RegexString(
                            r'automatic request role for duty group '
                            r'\(job_id: \d+, task_id: \d+\)',
                        )
                    ),
                },
            ],
        ),
    ],
)
@pytest.mark.features_on(
    'permissions_cube_add_node_for_service',
    'permissions_cube_delete_node_for_service',
    'permissions_cube_give_role_for_service',
)
async def test_cubes(
        mock_idm,
        abc_mockserver,
        login_mockserver,
        staff_mockserver,
        add_service,
        add_nanny_branch,
        set_remote_params,
        make_empty_config,
        call_cube_directly,
        call_cube_with_handler,
        cube_name,
        input_data,
        payload,
        batch_paths,
        batch_bodies,
        use_handler,
):
    abc_mockserver(services=['some-slug'])
    login_mockserver()
    staff_mockserver()

    service = await add_service('taxi', 'service-1')
    branch_id = await add_nanny_branch(
        service['id'], 'stable', direct_link='taxi_branch-1_stable',
    )

    cfg = make_empty_config()
    cfg.service_info.stable.set('duty', {'abc_slug': 'some-slug'})
    await set_remote_params(service['id'], branch_id, cfg)

    await add_service('taxi', 'service-2')

    @mock_idm('/api/v1/batch/')
    def _batch_handler(request):
        def _body(id_):
            method = requests[0]['method']
            path = requests[0]['path']
            if method == 'DELETE':
                return ''
            if method == 'POST':
                if path == '/rolenodes/':
                    return None
                return {'id': id_ + 1}
            raise RuntimeError(f'unknown method {method} for mock')

        requests = request.json
        assert len({x['method'] for x in requests}) == 1
        assert [x['path'] for x in requests] == batch_paths
        if batch_bodies:
            assert [x['body'] for x in requests] == batch_bodies
        else:
            assert not any(x.get('body') for x in requests)
        assert len({x['id'] for x in requests}) == len(requests)
        return {
            'responses': [
                {'id': x['id'], 'status_code': 200, 'body': _body(i)}
                for i, x in enumerate(requests)
            ],
        }

    if use_handler:
        await call_cube_with_handler(cube_name, input_data, payload)
    else:
        await call_cube_directly(cube_name, input_data, payload)

    if cube_name == 'PermissionsRequestRoleForDuty':
        assert _batch_handler.times_called == 1
        call = _batch_handler.next_call()
        assert call['request'].json == [
            {
                'body': {
                    'group': 50889,
                    'path': '/taxi/services_roles/service-1/nanny_admin_prod/',
                    'system': 'clownductor',
                    'without_hold': True,
                    'comment': matching.RegexString(
                        r'automatic request role for duty group '
                        r'\(job_id: \d+, task_id: \d+\)',
                    ),
                },
                'id': 'taxi+services_roles+service=1+nanny_admin_prod-50889',
                'method': 'POST',
                'path': '/rolerequests/',
                'rollback_on_4xx': False,
            },
        ]


@pytest.mark.parametrize('use_handler', [True, False])
@pytest.mark.parametrize(
    'cube_name, input_data, mock_called_times',
    [
        ('PermissionsAddNodesForService', {'service_id': 1}, 2),
        ('PermissionsDeleteNodesForDeletingService', {'service_id': 1}, 2),
        ('PermissionsRequestRolesForNewService', {'service_id': 1}, 2),
    ],
)
@pytest.mark.features_on(
    'permissions_cube_add_node_for_service',
    'permissions_cube_delete_node_for_service',
    'permissions_cube_give_role_for_service',
)
async def test_cubes_for_retries(
        mockserver,
        mock_idm,
        login_mockserver,
        staff_mockserver,
        add_service,
        call_cube_with_handler,
        call_cube_directly,
        cube_name,
        input_data,
        mock_called_times,
        use_handler,
):
    login_mockserver()
    staff_mockserver()

    await add_service('taxi', 'cool-service-1')

    idm_responses = {
        'PermissionsAddNodesForService': iter(
            [
                {'status_code': 200},
                {'status_code': 200},
                {'status_code': 200},
                {'status_code': 200},
                {'status_code': 200},
                {'status_code': 200},
                {'status_code': 200},
                {'status_code': 200},
                {'status_code': 200},
                {'status_code': 200},
                {
                    'status_code': 400,
                    'body': {'message': 'уже есть на этом уровне дерева'},
                },
                {'status_code': 500},
                {'status_code': 200},
                {'status_code': 200},
                {'status_code': 200},
                {'status_code': 200},
                {'status_code': 200},
                {'status_code': 200},
                {'status_code': 200},
                {'status_code': 200},
                {
                    'status_code': 400,
                    'body': {'message': 'уже есть на этом уровне дерева'},
                },
                {'status_code': 200},
                {'status_code': 200},
                {'status_code': 200},
                {'status_code': 200},
                {'status_code': 200},
            ],
        ),
        'PermissionsDeleteNodesForDeletingService': iter(
            [{'status_code': 500}, {'status_code': 200}],
        ),
        'PermissionsRequestRolesForNewService': iter(
            [
                {'status_code': 200},
                {'status_code': 500},
                {
                    'status_code': 400,
                    'body': {
                        'error_code': 'BAD_REQUEST',
                        'errors': {'group': ['Группа с id=116722 не найдена']},
                        'message': (
                            '... '
                            'в системе "Клоундуктор" в состоянии "Выдана"'
                            '...'
                        ),
                    },
                },
                {
                    'status_code': 400,
                    'body': {
                        'error_code': 'BAD_REQUEST',
                        'errors': {'group': ['Группа с id=116722 не найдена']},
                        'message': (
                            '... '
                            'в системе "Клоундуктор" в состоянии '
                            '"Подтверждена"'
                            '...'
                        ),
                    },
                },
                {'status_code': 200},
                {'status_code': 200},
            ],
        ),
    }

    @mock_idm('/api/v1/batch/')
    def _batch_handler(request):
        def _body(id_):
            method = requests[0]['method']
            path = requests[0]['path']
            if method == 'DELETE':
                return ''
            if method == 'POST':
                if path == '/rolenodes/':
                    return None
                return {'id': id_ + 1}
            raise RuntimeError(f'unknown method {method} for mock')

        requests = request.json
        responses = []
        status = 200
        for i, req in enumerate(requests):
            resp = next(idm_responses[cube_name])
            responses.append(
                {
                    'id': req['id'],
                    'status_code': resp['status_code'],
                    'body': resp.get('body') or _body(i),
                },
            )
            if resp['status_code'] != 200:
                status = resp['status_code']
        return mockserver.make_response(
            status=status, json={'responses': responses},
        )

    if use_handler:
        await call_cube_with_handler(cube_name, input_data)
    else:
        await call_cube_directly(cube_name, input_data)

    assert _batch_handler.times_called == mock_called_times
