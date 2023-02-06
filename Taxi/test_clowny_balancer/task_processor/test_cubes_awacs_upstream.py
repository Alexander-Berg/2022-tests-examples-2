# flake8: noqa
import pytest

from clowny_balancer.lib import models
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

_YAML2 = (
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
          - backend2
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

_DC_LOCAL_YAML = """
---
l7_upstream_macro:
  version: 0.0.1
  id: default_prefer_local
  can_handle_announce_checks: true
  matcher:
    any: true
  by_dc_scheme:
    dc_balancer:
      weights_section_id: bygeo
      method: LOCAL_THEN_BY_DC_WEIGHT
      attempt_all_dcs: true
    balancer:
      attempts: 1
      backend_timeout: 60s
      connect_timeout: 70ms
      do_not_retry_http_responses: true
      keepalive_count: 1
      max_reattempts_share: 0.2
      max_pessimized_endpoints_share: 0.2
      health_check:
        delay: 2s
        request: 'GET /ping HTTP/1.1\\nHost: service-31.taxi.yandex.net\\nUser-agent: l7-balancer\\n\\n'  # noqa: E501
    on_error:
      static:
        status: 504
        content: Service unavailable
    dcs:
    - name: vla
      backend_ids:
      - backend_vla
    - name: sas
      backend_ids:
      - backend_sas
    - name: myt
      backend_ids:
      - backend_myt
      - backend_myt_pre
"""


@pytest.mark.parametrize(
    'cube_name, input_data, payload, extras',
    [
        (
            'AwacsUpstreamGetYaml',
            {'entry_point_id': 1},
            None,
            {
                'status': 'failed',
                'error_message': 'Failed to find entry point for id 1',
            },
        ),
        (
            'AwacsUpstreamGetYaml',
            {'entry_point_id': 2},
            {
                'yaml': _YAML,
                'awacs_upstream_version': (
                    '166f58fd-8e08-4a87-831d-11709ee6a3b9'
                ),
            },
            None,
        ),
        (
            'AwacsUpstreamChangeUpstreams',
            {
                'entry_point_id': 2,
                'new_upstream_ids': [4],
                'origin_yaml': _YAML,
            },
            {'updated_yaml': _YAML2},
            None,
        ),
        (
            'AwacsUpstreamCreate',
            {
                'namespace_id': 'ns_1',
                'upstream_id': 'up_1',
                'fqdn': 'fqdn-pre.net',
                'backend_id': 'backend_1',
                'entry_point_id': 3,
            },
            None,
            None,
        ),
        (
            'AwacsUpstreamCreate',
            {
                'namespace_id': 'ns_1',
                'upstream_id': 'up_3',
                'fqdn': 'fqdn-pre.net',
                'backend_id': 'backend_1',
                'entry_point_id': 3,
            },
            None,
            None,
        ),
        (
            'AwacsUpstreamWaitFor',
            {'namespace_id': 'ns_1', 'upstream_id': 'up_1'},
            None,
            None,
        ),
        (
            'AwacsUpstreamWaitFor',
            {'namespace_id': 'ns_1', 'upstream_id': 'up_2'},
            None,
            {'sleep_duration': 5, 'status': 'in_progress'},
        ),
        (
            'AwacsUpstreamsDelete',
            {'namespace_id': 'ns_1', 'upstream_ids': ['up_1']},
            {'upstream_ids': ['up_1']},
            None,
        ),
        ('AwacsUpstreamsWaitFor', {'awacs_namespace_id': 'ns_1'}, None, None),
        (
            'AwacsUpstreamsWaitFor',
            {
                'awacs_namespace_id': 'ns_1',
                'for_deleted': True,
                'deleted_awacs_upstream_ids': ['deleted_upstream_id_rtc_now'],
            },
            None,
            None,
        ),
    ],
)
async def test_cubes(
        mockserver,
        awacs_mockserver,
        relative_load_json,
        call_cube,
        cube_name,
        input_data,
        payload,
        extras,
):
    awacs_mockserver()

    @mockserver.json_handler('/client-awacs/api/GetUpstream/')
    def _get_handler(request):
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

    @mockserver.json_handler('/client-awacs/api/CreateUpstream/')
    def _create_handler(request):
        auth = request.json['meta']['auth']
        assert auth == {
            'staff': {
                'owners': {
                    'groupIds': ['50889'],
                    'logins': ['oxcd8o', 'robot-taxi-clown'],
                },
            },
            'type': 'STAFF',
        }
        balancer_conf = request.json['spec']['yandexBalancer']['config']
        assert balancer_conf == {
            'regexpSection': {
                'matcher': {},
                'nested': {
                    'modules': [
                        {
                            'headers': {
                                'createFunc': {'X-Real-IP': 'realip'},
                                'createWeak': [
                                    {'key': 'Host', 'value': 'fqdn.net'},
                                ],
                            },
                        },
                        {'shared': {'uuid': 'fqdn.net-up_3'}},
                        {
                            'balancer2': {
                                'attempts': 1,
                                'fConnectionAttempts': {
                                    'type': 'COUNT_BACKENDS',
                                    'countBackendsParams': {},
                                },
                                'active': {
                                    'delay': '2s',
                                    'request': (
                                        'GET /ping HTTP/1.1\\nHost: fqdn.net'
                                        '\\nUser-agent: l7-balancer\\n\\n'
                                    ),
                                },
                                'balancingPolicy': {'uniquePolicy': {}},
                                'generatedProxyBackends': {
                                    'proxyOptions': {
                                        'connectTimeout': '70ms',
                                        'backendTimeout': '60s',
                                        'keepaliveCount': 1,
                                        'failOn5xx': False,
                                        'keepaliveTimeout': '60s',
                                    },
                                    'includeBackends': {
                                        'type': 'BY_ID',
                                        'ids': ['backend_1'],
                                    },
                                },
                                'onError': {
                                    'errordocument': {
                                        'status': 504,
                                        'content': 'Service unavailable',
                                    },
                                },
                            },
                        },
                    ],
                },
            },
        }
        return {}

    @mockserver.json_handler('/client-awacs/api/RemoveUpstream/')
    def _remove_handler(_):
        return {}

    @mockserver.json_handler('/client-awacs/api/ListUpstreams/')
    def _list_handler(request):
        filename = 'list_upstreams.json'
        return relative_load_json(filename)

    response = await call_cube(cube_name, input_data)
    result = {'status': 'success'}
    if payload is not None:
        result['payload'] = payload
    result.update(extras or {})
    assert response == result, cube_name


@pytest.mark.parametrize(
    'origin_yaml, updated_yaml, awacs_called',
    [
        pytest.param(_YAML, _YAML, False, id='has-no-updates'),
        pytest.param(_YAML, _YAML2, True, id='has-updates'),
    ],
)
async def test_update_upstream_yaml(
        awacs_mockserver, call_cube, origin_yaml, updated_yaml, awacs_called,
):
    awacs_mock = awacs_mockserver()

    response = await call_cube(
        'AwacsUpstreamUpdateYaml',
        {
            'entry_point_id': 2,
            'awacs_upstream_version': 'abc',
            'origin_yaml': origin_yaml,
            'updated_yaml': updated_yaml,
        },
    )
    assert response == {'status': 'success'}
    assert awacs_mock.has_calls == awacs_called


async def test_change_upstreams(call_cube, web_context):
    _entry_point = await models.EntryPoint.fetch_one(
        context=web_context, db_conn=web_context.pg.secondary, id=2,
    )
    assert _entry_point.upstream_ids == [3, 4]

    response = await call_cube(
        'AwacsUpstreamChangeUpstreams',
        {'entry_point_id': 2, 'new_upstream_ids': [4], 'origin_yaml': _YAML},
    )
    assert response == {
        'status': 'success',
        'payload': {'updated_yaml': _YAML2},
    }
    _entry_point = await models.EntryPoint.fetch_one(
        context=web_context, db_conn=web_context.pg.secondary, id=2,
    )
    assert _entry_point.upstream_ids == [4]


@pytest.mark.config(
    CLOWNDUCTOR_AVAILABLE_DATACENTERS={
        'all_datacenters': ['vla', 'man', 'sas', 'iva', 'myt'],
        'projects': [
            {'datacenters': ['sas', 'vla', 'myt'], 'name': 'taxi-devops'},
            {'datacenters': ['sas', 'vla', 'myt'], 'name': '__default__'},
        ],
    },
)
@pytest.mark.pgsql('clowny_balancer', files=['pg_clowny_balancer.sql'])
async def test_create_dc_local_yaml(mock_clownductor, mockserver, call_cube):
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

    @mock_clownductor('/v1/branches/')
    def _branches_handler(request):
        branches = [
            {
                'id': 1,
                'env': 'stable',
                'direct_link': 'taxi_service-31_stable',
                'service_id': 31,
                'name': 'stable',
            },
            {
                'id': 2,
                'env': 'prestable',
                'direct_link': 'taxi_service-31_pre_stable',
                'service_id': 31,
                'name': 'pre_stable',
            },
        ]
        if request.query.get('service_id'):
            return [
                branch
                for branch in branches
                if str(branch['service_id']) == request.query['service_id']
            ]
        return []

    @mockserver.json_handler('/client-nanny-yp/api/yplite/pod-sets/ListPods/')
    def _list_pods_handler(request):
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
    def _get_namespace_handler(request):
        if request.json['id'] == 'taxi-service-31':
            return {'namespace': {'meta': {'auth': {}}}}
        return {}

    @mockserver.json_handler('/client-awacs/api/GetBackend/')
    def _get_backend_handler(request):
        if (
                request.json['namespaceId'] == 'taxi-service-31'
                and request.json['id']
                in (
                    'backend_vla',
                    'backend_man',
                    'backend_sas',
                    'backend_iva',
                    'backend_myt',
                    'backend_vla_pre',
                    'backend_man_pre',
                    'backend_sas_pre',
                    'backend_iva_pre',
                    'backend_myt_pre',
                )
        ):
            return mockserver.make_response(status=404)
        return {}

    @mockserver.json_handler('/client-awacs/api/CreateBackend/')
    def _create_backend_handler(_):
        return {}

    @mockserver.json_handler('/client-awacs/api/GetUpstream/')
    def _get_upstream_handler(request):
        if request.json['id'] == 'dc_local':
            return mockserver.make_response(status=404)
        return {}

    response = await call_cube(
        'AwacsUpstreamCreateDcLocalYaml',
        {
            'entry_point_id': 41,
            'backend_ids_by_env': {
                'stable': {
                    'vla': 'backend_vla',
                    'sas': 'backend_sas',
                    'myt': 'backend_myt',
                },
                'prestable': {'myt': 'backend_myt_pre'},
            },
        },
    )
    assert response == {
        'status': 'success',
        'payload': {'dc_local_yaml': _DC_LOCAL_YAML},
    }


@pytest.mark.pgsql('clowny_balancer', files=['pg_clowny_balancer.sql'])
async def test_create_upstream_from_yaml(mockserver, call_cube):
    @mockserver.json_handler('/client-awacs/api/GetUpstream/')
    def _get_handler(request):
        if request.json['id'] == 'dc_local':
            return mockserver.make_response(status=404)
        return {}

    @mockserver.json_handler('/client-awacs/api/GetNamespace/')
    def _get_namespace(request):
        if request.json['id'] == 'taxi-service-31':
            return {'namespace': {'meta': {'auth': {}}}}
        return mockserver.make_response(status=404)

    @mockserver.json_handler('/client-awacs/api/CreateUpstream/')
    def _create_handler(_):
        return {}

    response = await call_cube(
        'AwacsUpstreamCreateFromYaml',
        {
            'entry_point_id': 41,
            'namespace_id': 'taxi-service-31',
            'yaml': _DC_LOCAL_YAML,
            'upstream_id': 'dc_local',
        },
    )
    assert response == {'status': 'success'}
    assert _create_handler.times_called == 1
