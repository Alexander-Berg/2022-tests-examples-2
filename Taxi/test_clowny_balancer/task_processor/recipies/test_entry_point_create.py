# flake8: noqa
import pytest

from clowny_balancer.lib.helpers import awacs

_YAML = (
    """
---
regexp_section:
  matcher: {}
  modules:
  - headers:
      create_func:
        X-Real-IP: realip
      create_weak:
        Host: umlaas.taxi.yandex.net
  - balancer2:
      active:
        delay: 2s
        request: 'GET /ping HTTP/1.1\\nHost: umlaas.taxi.yandex.net\\nUser-agent: l7-balancer\\n\\n'
      attempts: 1
      connection_attempts: '!f count_backends()'
      generated_proxy_backends:
        include_backends:
          ids:
          - taxi_umlaas_stable
          - taxi_umlaas_pre_stable
          type: BY_ID
        proxy_options:
          backend_timeout: 60s
          connect_timeout: 70ms
          fail_on_5xx: false
          keepalive_count: 0
      on_error:
        errordocument:
          content: Service unavailable
          status: 504
      unique_policy: {}
""".lstrip()
)


@pytest.fixture(name='clown_cube_caller')
def _clown_cube_caller(mockserver, clown_cube_caller):
    async def _wrapper(cube, stage, request_data):
        if cube.name == 'NannyCubeGetActiveDatacenters':
            return mockserver.make_response(
                json={
                    'status': 'success',
                    'payload': {
                        'active_datacenters': [
                            {'branch_id': 1, 'regions': ['sas']},
                            {'branch_id': 4, 'regions': ['vla']},
                            {'branch_id': 2, 'regions': ['vla']},
                        ],
                    },
                },
            )
        return await clown_cube_caller(cube, stage, request_data)

    return _wrapper


class OneOf:
    def __init__(self, *choices):
        self._choices = list(choices)

    def __eq__(self, other):
        return other in self._choices

    def __repr__(self):
        return f'OneOf({", ".join(str(x) for x in self._choices)})'


def _request(**kwargs):
    return {
        'namespace_id': 1,
        'branch_id': 1,
        'fqdn': 'some.net',
        'protocol': 'https',
        'awacs_backend_id': 'service_stable',
        'awacs_upstream_id': 'custom-stable',
        **kwargs,
    }


@pytest.fixture()
def mock_clownductor_handlers(mock_clownductor):
    @mock_clownductor('/v1/branches/')
    def _branches_handler(request):
        branches = [
            {
                'id': 1,
                'env': 'stable',
                'direct_link': 'taxi_service_stable',
                'service_id': 1,
                'name': '',
            },
            {
                'id': 2,
                'env': 'prestable',
                'direct_link': 'taxi_service_prestable',
                'service_id': 1,
                'name': '',
            },
            {
                'id': 3,
                'env': 'testing',
                'direct_link': 'taxi_service_testing',
                'service_id': 1,
                'name': '',
            },
            {
                'id': 4,
                'env': 'stable',
                'direct_link': 'taxi_one-service_stable',
                'service_id': 2,
                'name': '',
            },
        ]
        ids = [x['id'] for x in branches]
        if 'branch_ids' in request.query:
            ids = [int(x) for x in request.query['branch_ids'].split(',')]
        elif 'branch_id' in request.query:
            ids = [int(request.query['branch_id'])]
        elif 'service_id' in request.query:
            ids = [
                x['id']
                for x in branches
                if x['service_id'] == int(request.query['service_id'])
            ]
        return [x for x in branches if x['id'] in ids]

    @mock_clownductor('/v1/services/')
    def _services_handler(request):
        _id = int(request.query['service_id'])
        assert _id in {1, 2}
        return [
            {
                'id': _id,
                'name': 'service',
                'project_id': 1,
                'cluster_type': 'nanny',
            },
        ]

    @mock_clownductor('/api/projects')
    def _projects_handler(request):
        assert int(request.query['project_id']) == 1
        return [{'id': 1, 'name': 'taxi', 'namespace_id': 1}]


@pytest.fixture(name='job_checker')
def _job_checker(task_processor, run_job_common):
    async def do_it(job):
        await run_job_common(job)
        assert job.job_vars == {
            'active_datacenters': OneOf(['SAS'], ['VLA']),
            'awacs_backend_id': 'service_stable',
            'awacs_domain_id': 'some.net',
            'awacs_namespace_id': OneOf('ns_1', 'ns_2'),
            'awacs_upstream_id': 'custom-stable',
            'clown_branch_id': OneOf(1, 4),
            'clown_service_id': OneOf(1, 2),
            'entry_point_id': 1,
            'env': 'stable',
            'fqdn': 'some.net',
            'ipv6': '2a02:6b8:0:3400:0:4d5:0:7',
            'l3_balancer_id': 'abc',
            'l3mgr_service_id': '123',
            'lock_name': 'some.net:custom-stable',
            'namespace_id': OneOf(3, 4),
            'nanny_endpoint_set_id': OneOf(
                'some-endpointset-id', 'some-endpointset-id-2',
            ),
            'protocol': 'https',
            'upstream_id': OneOf(2, 3),
            'job_id': 2,
            'author': '',
            'st_ticket': '',
        }

    return do_it


@pytest.mark.config(
    CLOWNY_BALANCER_FEATURES={'__default__': {'entity_creation_check': True}},
)
@pytest.mark.usefixtures('mock_clownductor_handlers')
@pytest.mark.parametrize(
    'data, expected_status, expected_result',
    [
        pytest.param(
            _request(namespace_id=4),
            200,
            {'job_id': 1},
            id='ok_for_extending_shared',
        ),
        pytest.param(
            _request(namespace_id=3, branch_id=4),
            200,
            {'job_id': 1},
            id='ok_for_extending_empty',
        ),
    ],
)
async def test_recipe(
        mockserver,
        mock_nanny_yp,
        load_yaml,
        task_processor,
        taxi_clowny_balancer_web,
        get_entry_point,
        job_checker,
        data,
        expected_status,
        expected_result,
):
    @mock_nanny_yp('/endpoint-sets/ListEndpointSets/')
    def _nanny_yp_handler(request):
        _region = request.json['cluster']
        _service_id = request.json['service_id']

        endpoint_sets = [
            {
                'meta': {
                    'id': 'some-endpointset-id',
                    'serviceId': 'taxi_service_stable',
                },
                'region': 'SAS',
            },
            {
                'meta': {
                    'id': 'some-endpointset-id',
                    'serviceId': 'taxi_service_stable',
                },
                'region': 'VLA',
            },
            {
                'meta': {
                    'id': 'some-endpointset-id-2',
                    'serviceId': 'taxi_one-service_stable',
                },
                'region': 'SAS',
            },
            {
                'meta': {
                    'id': 'some-endpointset-id-2',
                    'serviceId': 'taxi_one-service_stable',
                },
                'region': 'VLA',
            },
        ]
        return {
            'endpointSets': [
                x
                for x in endpoint_sets
                if x['meta']['serviceId'] == _service_id
                and x['region'] == _region
            ],
        }

    check_exists_passed = False

    def _backend(id_, ns_id):
        balancer_id = f'{ns_id}:balancer'
        return {
            'meta': {'namespaceId': ns_id, 'id': id_, 'version': '1'},
            'statuses': [
                {
                    'active': {balancer_id: {'status': awacs.TRUE_VAL}},
                    'inProgress': {balancer_id: {'status': awacs.FALSE_VAL}},
                    'validated': {balancer_id: {'status': awacs.TRUE_VAL}},
                },
            ],
        }

    @mockserver.json_handler('/client-awacs/api/GetBackend/')
    def _get_backend_handler(request):
        nonlocal check_exists_passed
        check_exists_passed = True
        if (
                (
                    request.json['id'] == 'service_stable'
                    and request.json['namespaceId'] == 'ns_2'
                )
                or (
                    request.json['id'] == 'service_stable'
                    and request.json['namespaceId'] == 'ns_1'
                    and check_exists_passed
                )
        ):
            return {
                'backend': _backend(
                    request.json['id'], request.json['namespaceId'],
                ),
            }
        return mockserver.make_response(status=404)

    @mockserver.json_handler('/client-awacs/api/ListBackends/')
    def _list_backend_handler(request):
        return {'backends': [_backend('b-1', request.json['namespaceId'])]}

    @mockserver.json_handler('/client-awacs/api/GetNamespace/')
    def _get_namespace_handler(_):
        return {'namespace': {'meta': {'auth': {}}}}

    @mockserver.json_handler('/client-awacs/api/CreateBackend/')
    def _create_backend_handler(request):
        allowed_clusters = {
            'man_pre',
            'iva',
            'vla',
            'myt',
            'sas_test',
            'sas',
            'test_sas',
            'man',
        }
        selector = request.json['spec']['selector']
        assert selector['type'] == 'YP_ENDPOINT_SETS_SD'
        bad_clusters = [
            x['cluster']
            for x in selector['ypEndpointSets']
            if x['cluster'] not in allowed_clusters
        ]
        assert not bad_clusters, bad_clusters
        return {}

    @mockserver.json_handler('/client-awacs/api/CreateUpstream/')
    def _create_upstream_handler(_):
        return {}

    @mockserver.json_handler('/client-awacs/api/GetUpstream/')
    def _get_upstream_handler(request):
        namespace_id = request.json['namespaceId']
        id_ = request.json['id']
        if id_ == 'up_3':
            return mockserver.make_response(status=404)
        return {
            'upstream': {
                'meta': {'version': '166f58fd-8e08-4a87-831d-11709ee6a3b9'},
                'spec': {'yandexBalancer': {'yaml': _YAML}},
                'statuses': [
                    {
                        'active': {
                            f'{namespace_id}:balancer_1': {
                                'status': (
                                    awacs.FALSE_VAL
                                    if id_ == 'up_2'
                                    else awacs.TRUE_VAL
                                ),
                                'reason': '',
                            },
                            f'{namespace_id}:balancer_2': {
                                'status': awacs.TRUE_VAL,
                                'reason': '',
                            },
                        },
                        'inProgress': {
                            f'{namespace_id}:balancer_1': {
                                'status': (
                                    awacs.TRUE_VAL
                                    if id_ == 'up_2'
                                    else awacs.FALSE_VAL
                                ),
                                'reason': '',
                            },
                            f'{namespace_id}:balancer_2': {
                                'status': awacs.FALSE_VAL,
                                'reason': '',
                            },
                        },
                        'validated': {
                            f'{namespace_id}:balancer_1': {
                                'status': awacs.TRUE_VAL,
                                'reason': '',
                            },
                            f'{namespace_id}:balancer_2': {
                                'status': awacs.TRUE_VAL,
                                'reason': '',
                            },
                        },
                    },
                ],
            },
        }

    @mockserver.json_handler('/client-awacs/api/ListL3Balancers/')
    def _l3_list_handler(request):
        assert request.json['fieldMask'] == 'meta.id,spec.l3mgrServiceId'
        return {
            'l3Balancers': [
                {'meta': {'id': 'abc'}, 'spec': {'l3mgrServiceId': '123'}},
            ],
        }

    @mockserver.json_handler('/client-awacs/api/GetL3Balancer/')
    def _l3_get_handler(request):
        assert request.json['id'] == 'abc'
        return {
            'l3Balancer': {
                'meta': {'id': 'abc'},
                'spec': {
                    'realServers': {'backends': [{'id': 'some'}]},
                    'l3mgrServiceId': '123',
                    'incomplete': False,
                },
                'order': {'status': {'status': 'FINISHED'}},
            },
        }

    @mockserver.json_handler('/client-awacs/api/UpdateL3Balancer/')
    def _l3_update_handler(_):
        return {}

    @mockserver.json_handler(r'/l3mgr/service/(?P<service_id>\d+)', regex=True)
    def _l3mgr_service(_, service_id):
        assert service_id == '123'
        return {
            'vs': [
                {
                    'id': 1,
                    'ip': '2a02:6b8:0:3400:0:4d5:0:7',
                    'port': 80,
                    'rs': [1, 2],
                    'group': ['group1', 'group2'],
                },
            ],
            'fqdn': 'service-fqdn.net',
        }

    @mockserver.json_handler('/dns_api/robot-taxi-clown/primitives')
    def _dns_primitive(_):
        pass

    @mockserver.json_handler('/client-awacs/api/CreateDomain/')
    def _create_domain_handler(_):
        return {}

    @mockserver.json_handler('/client-awacs/api/GetDomain/')
    def _get_domain_handler(request):
        return {
            'domain': {
                'statuses': [
                    {
                        'active': {
                            'namespace_id:balancer_id': {
                                'status': awacs.TRUE_VAL,
                            },
                        },
                    },
                ],
            },
        }

    task_processor.load_recipe(load_yaml('EntryPointCreate.yaml')['data'])
    task_processor.load_recipe(
        {
            'name': 'EntryPointEnableSsl',
            'provider_name': 'clowny-balancer',
            'job_vars': [],
            'stages': [],
        },
    )
    response = await taxi_clowny_balancer_web.post(
        '/v1/entry-points/create/', json=data,
    )
    result = await response.json()
    assert response.status == expected_status, result
    if expected_result is not None:
        assert result == expected_result

    data = await response.json()
    job = task_processor.job(data['job_id'])
    await job_checker(job)

    assert await get_entry_point(job.job_vars['entry_point_id'])
