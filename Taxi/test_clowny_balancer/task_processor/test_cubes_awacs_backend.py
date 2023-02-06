import pytest

from clowny_balancer.lib import models
from clowny_balancer.lib.helpers import awacs


def _case(
        cube_name,
        input_data,
        payload=None,
        result_extras=None,
        mocks_extras=None,
):
    return cube_name, input_data, payload, result_extras, mocks_extras or {}


@pytest.mark.config(
    CLOWNDUCTOR_AVAILABLE_DATACENTERS={
        'all_datacenters': ['vla', 'man', 'sas', 'iva', 'myt'],
        'projects': [
            {'datacenters': ['sas', 'vla', 'myt'], 'name': 'taxi-devops'},
            {'datacenters': ['sas', 'vla', 'myt'], 'name': '__default__'},
        ],
    },
    CLOWNY_BALANCER_FEATURES={
        '__default__': {},
        'taxi-devops': {
            'service-31': {
                'exclude_man_from_creating_dc_local_backends': True,
            },
        },
    },
)
@pytest.mark.parametrize(
    'cube_name, input_data, payload, result_extras, mocks_extras',
    [
        _case(
            'AwacsBackendCreate',
            {
                'namespace_id': 'ns_1',
                'endpoint_set_id': 'endpoint_set_1',
                'branch_id': 1,
            },
            {'upstream_id': 1},
        ),
        _case(
            'AwacsBackendCreate',
            {
                'namespace_id': 'ns_1',
                'endpoint_set_id': 'endpoint_set_1',
                'branch_id': 3,
                'backend_id': 'backend_1',
            },
            {'upstream_id': 12},
        ),
        _case(
            'AwacsBackendWaitFor',
            {'namespace_id': 'ns_1', 'backend_id': 'backend_1'},
        ),
        _case(
            'AwacsBackendsDelete',
            {'namespace_id': 'ns_1', 'backend_ids': ['backend_1']},
            {'backend_ids': ['backend_1']},
        ),
        _case(
            'AwacsBackendFindSystem',
            {'namespace_id': 'ns_1'},
            {'backend_ids': []},
        ),
        _case(
            'AwacsWaitSyncBackends',
            {
                'namespace_ids': ['ns_1'],
                'man_pod_ids': ['k67cwweyrsc56f5e'],
                'sas_pod_ids': ['o5xprzwtm5ir5ab2'],
                'vla_pod_ids': [],
            },
            {'success_after_sleep': False},
        ),
        _case(
            'AwacsWaitSyncBackends',
            {
                'namespace_ids': ['ns_1'],
                'man_pod_ids': ['k67cwweyrsc56f5e'],
                'sas_pod_ids': ['o5xprzwtm5ir5ab2'],
                'vla_pod_ids': [],
            },
            {'success_after_sleep': True},
            {'sleep_duration': 300, 'status': 'in_progress'},
            {'backends_only_sd_fast': True},
        ),
        _case(
            'AwacsWaitSyncBackends',
            {
                'namespace_ids': ['ns_1'],
                'pod_ids_by_region': {
                    'man': ['k67cwweyrsc56f5e'],
                    'sas': ['o5xprzwtm5ir5ab2'],
                },
            },
            {'success_after_sleep': False},
        ),
        _case(
            'AwacsBackendsCreateByDc',
            {'entry_point_id': 41},
            {
                'upstream_ids': [1, 2, 3, 4],
                'backend_ids_by_env': {
                    'stable': {
                        'vla': 'backend_vla',
                        'sas': 'backend_sas',
                        'myt': 'backend_myt',
                    },
                    'prestable': {'myt': 'backend_myt_pre'},
                },
                'namespace_id': 'taxi-service-31',
            },
        ),
        _case(
            'AwacsAddDcToSlowBackends',
            {
                'namespace_ids': ['ns_1'],
                'man_pod_ids': ['k67cwweyrsc56f5e'],
                'sas_pod_ids': ['o5xprzwtm5ir5ab2'],
                'vla_pod_ids': [],
            },
        ),
        _case(
            'AwacsAddDcToSlowBackends',
            {
                'namespace_ids': ['ns_1'],
                'pod_ids_by_region': {
                    'man': ['k67cwweyrsc56f5e'],
                    'sas': ['o5xprzwtm5ir5ab2'],
                },
            },
        ),
        _case(
            'AwacsUpdateEntrypointSet',
            {
                'regions': ['SAS'],
                'awacs_namespace_id': 'ns_1',
                'awacs_backend_id': 'backend_1',
            },
            mocks_extras={'backends_only_sd_fast': True},
        ),
        _case(
            'AwacsCreateDcLocalBackends',
            {
                'branch_id': 1,
                'namespace_id': 'taxi-service-31',
                'endpoint_set_id': 'backend_1',
            },
            {'upstream_ids': [1, 2, 3, 4]},
        ),
        _case(
            'AwacsCreateDcLocalBackends',
            {
                'branch_id': 2,
                'namespace_id': 'taxi-service-31',
                'endpoint_set_id': 'backend_1',
            },
            {'upstream_ids': [1, 2, 3, 4]},
        ),
    ],
)
async def test_cubes(
        mockserver,
        mock_clownductor,
        web_context,
        call_cube,
        cube_name,
        input_data,
        payload,
        result_extras,
        mocks_extras,
):
    @mock_clownductor('/v1/services/')
    def _services_handler(request):
        services = [
            {
                'id': 31,
                'project_id': 150,
                'name': 'service-31',
                'cluster_type': 'nanny',
                'project_name': 'taxi-devops',
            },
        ]
        if request.query.get('service_id'):
            return [
                service
                for service in services
                if str(service['id']) == request.query['service_id']
            ]
        return []

    @mockserver.json_handler('/client-nanny-yp/api/yplite/pod-sets/ListPods/')
    def _get_pods(request):
        def _add_ratemask_and_state(pod):
            pod.update(
                {
                    'spec': {
                        'sysctlProperties': [
                            {
                                'name': 'net.ipv6.icmp.ratemask',
                                'value': '0,3-127',
                            },
                        ],
                    },
                    'status': {
                        'agent': {
                            'iss': {
                                'currentStates': [{'currentState': 'ACTIVE'}],
                            },
                        },
                    },
                },
            )
            return pod

        if request.json['serviceId'] == 'taxi_service-31_stable':
            if request.json['cluster'] == 'SAS':
                return {
                    'pods': [
                        _add_ratemask_and_state({}),
                        _add_ratemask_and_state({}),
                    ],
                }
            if request.json['cluster'] == 'VLA':
                return {
                    'pods': [
                        _add_ratemask_and_state({}),
                        _add_ratemask_and_state({}),
                    ],
                }
            if request.json['cluster'] == 'MYT':
                return {'pods': [_add_ratemask_and_state({})]}
        if request.json['serviceId'] == 'taxi_service-31_pre_stable':
            if request.json['cluster'] == 'MYT':
                return {'pods': [_add_ratemask_and_state({})]}
        return {'pods': []}

    @mockserver.json_handler('/client-awacs/api/GetNamespace/')
    def _get_namespace(_):
        return {'namespace': {'meta': {'auth': {}}}}

    def _backend(ns_id):
        balancer_id = f'{ns_id}:balancer'
        return {
            'meta': {'namespaceId': 'ns_1', 'id': 'backend_1', 'version': '1'},
            'statuses': [
                {
                    'active': {balancer_id: {'status': awacs.TRUE_VAL}},
                    'inProgress': {balancer_id: {'status': awacs.FALSE_VAL}},
                    'validated': {balancer_id: {'status': awacs.TRUE_VAL}},
                },
            ],
            'spec': {
                'selector': {
                    'type': (
                        'YP_ENDPOINT_SETS_SD'
                        if mocks_extras.get('backends_only_sd_fast')
                        else 'YP_ENDPOINT_SETS'
                    ),
                    'yp_endpoint_sets': [
                        {'endpoint_set_id': 'endpoint_set_1'},
                    ],
                },
            },
        }

    @mockserver.json_handler('/client-awacs/api/GetBackend/')
    def _get_handler(request):
        if (
                request.json['namespaceId'] in ('ns_1', 'taxi-service-31')
                and request.json['id']
                in ('backend_1', 'backend_vla', 'backend_vla_pre')
        ):
            return {'backend': _backend(request.json['namespaceId'])}
        return mockserver.make_response(status=404)

    @mockserver.json_handler('/client-awacs/api/ListBackends/')
    def _list_handler(request):
        return {
            'backends': [_backend(request.json['namespaceId'])],
            'annotatedBackends': [
                {
                    'backend': _backend(request.json['namespaceId']),
                    'endpointSet': {
                        'spec': {
                            'instances': [
                                {
                                    'host': (
                                        'k67cwweyrsc56f5e.man.yp-c.yandex.net'
                                    ),
                                },
                                {
                                    'host': (
                                        'o5xprzwtm5ir5ab2.sas.yp-c.yandex.net'
                                    ),
                                },
                            ],
                        },
                        'meta': {
                            'version': '8406fe62-ea4e-4b0b-9dfe-a63fbfbda565',
                        },
                        'statuses': [
                            {
                                'active': {
                                    'service:net_man': {'status': 'True'},
                                    'service:net_sas': {'status': 'True'},
                                },
                                'id': '8406fe62-ea4e-4b0b-9dfe-a63fbfbda565',
                                'inProgress': {
                                    'service:net_man': {'status': 'False'},
                                    'service:net_sas': {'status': 'False'},
                                },
                                'validated': {},
                            },
                        ],
                    },
                },
            ],
        }

    @mockserver.json_handler('/client-awacs/api/CreateBackend/')
    def _create_handler(_):
        return {}

    @mockserver.json_handler('/client-awacs/api/RemoveBackend/')
    def _remove_handler(request):
        assert request.json == {
            'namespaceId': 'ns_1',
            'id': 'backend_1',
            'version': '1',
        }
        return {}

    @mock_clownductor('/v1/branches/')
    def _branches_handler(request):
        branches = [
            {
                'id': 1,
                'env': 'stable',
                'direct_link': 'taxi_service-31_stable',
                'service_id': 31,
                'name': '',
            },
            {
                'id': 2,
                'env': 'prestable',
                'direct_link': 'taxi_service-31_pre_stable',
                'service_id': 31,
                'name': '',
            },
            {
                'id': 3,
                'env': 'stable',
                'direct_link': 'backend2',
                'service_id': 1,
                'name': '',
            },
        ]
        if request.query.get('branch_ids'):
            return [
                branch
                for branch in branches
                if str(branch['id']) in request.query['branch_ids']
            ]
        if request.query.get('service_id'):
            return [
                branch
                for branch in branches
                if str(branch['service_id']) == request.query['service_id']
            ]
        return []

    @mockserver.json_handler('/client-awacs/api/UpdateBackend/')
    def _update_handler(_):
        return {}

    @mock_clownductor('/api/projects')
    def _projects_handler(request):
        projects = [
            {
                'id': 150,
                'name': 'taxi-devops',
                'namespace_id': 1,
                'env_params': {
                    'stable': {
                        'domain': 'taxi.yandex.net',
                        'juggler_folder': 'taxi.platform.prod',
                    },
                    'general': {
                        'project_prefix': 'taxi',
                        'docker_image_tpl': 'taxi/{{ service }}/$',
                    },
                    'testing': {
                        'domain': 'taxi.tst.yandex.net',
                        'juggler_folder': 'taxi.platform.test',
                    },
                    'unstable': {
                        'domain': 'taxi.dev.yandex.net',
                        'juggler_folder': '',
                    },
                },
            },
        ]
        if request.query.get('project_id'):
            return [
                project
                for project in projects
                if str(project['id']) == request.query['project_id']
            ]
        return []

    response = await call_cube(cube_name, input_data)
    result = {'status': 'success'}
    if payload is not None:
        result['payload'] = payload
    result.update(result_extras or {})
    assert response == result

    if cube_name == 'AwacsBackendCreate':
        rows = await web_context.pg.primary.fetch(
            'SELECT * FROM balancers.upstreams',
        )
        if not _create_handler.has_calls:
            assert len(rows) == 2
        else:
            assert _create_handler.times_called == 1
            assert len(rows) == 3
        _upstreams = await models.Upstream.fetch_many(
            context=web_context,
            db_conn=web_context.pg.primary,
            branch_ids=[input_data['branch_id']],
        )
        assert _upstreams.ids == [payload['upstream_id']]

    if cube_name == 'AwacsBackendsCreateByDc':
        rows = await web_context.pg.primary.fetch(
            'SELECT * FROM balancers.upstreams',
        )
        assert _create_handler.times_called == 3
        assert len(rows) == 6
        _upstreams = await models.Upstream.fetch_many(
            context=web_context,
            db_conn=web_context.pg.primary,
            branch_ids=[1, 2],
        )
        assert _upstreams.ids == payload['upstream_ids']

    if cube_name == 'AwacsCreateDcLocalBackends':
        rows = await web_context.pg.primary.fetch(
            'SELECT * FROM balancers.upstreams',
        )
        assert _create_handler.times_called == 3
        assert len(rows) == 6
        _upstreams = await models.Upstream.fetch_many(
            context=web_context,
            db_conn=web_context.pg.primary,
            branch_ids=[input_data['branch_id']],
        )
        assert _upstreams.ids == payload['upstream_ids']


@pytest.mark.parametrize('entry_point_id, upstream_ids', [(41, [1, 2, 3, 4])])
@pytest.mark.pgsql('clowny_balancer', files=['test_add_links_to_db.sql'])
async def test_add_links_to_db(call_cube, entry_point_id, upstream_ids, pgsql):

    response = await call_cube(
        'AwacsBackendAddLinksToDB',
        {'entry_point_id': entry_point_id, 'upstream_ids': upstream_ids},
    )
    assert response == {'status': 'success'}

    cursor = pgsql['clowny_balancer'].cursor()
    query = (
        'select upstream_id from balancers.entry_points_upstreams '
        f'where entry_point_id = {entry_point_id}'
    )
    cursor.execute(query)
    result = [row[0] for row in cursor]
    assert result == upstream_ids
