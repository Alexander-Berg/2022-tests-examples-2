import pytest

from clowny_balancer.lib.helpers import dc_local_enable

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
    - name: sas
      backend_ids:
      - backend_sas
    - name: vla
      backend_ids:
      - backend_vla
    - name: myt
      backend_ids:
      - backend_myt
      - backend_myt_pre
"""


@pytest.mark.config(
    CLOWNDUCTOR_AVAILABLE_DATACENTERS={
        'all_datacenters': ['vla', 'man', 'sas', 'iva', 'myt'],
        'projects': [
            {
                'datacenters': ['man', 'sas', 'vla', 'myt'],
                'name': 'taxi-devops',
            },
            {'datacenters': ['sas', 'vla', 'myt'], 'name': '__default__'},
        ],
    },
)
@pytest.mark.pgsql('clowny_balancer', files=['init.sql'])
async def test_recipe(
        mock_clownductor,
        mockserver,
        load_yaml,
        task_processor,
        run_job_common,
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
        def _add_ratemask_and_state(pod, status):
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
                                'currentStates': [{'currentState': status}],
                            },
                        },
                    },
                },
            )
            return pod

        if request.json['serviceId'] == 'taxi_service-31_stable':
            if request.json['cluster'] == 'MAN':
                return {
                    'pods': [
                        _add_ratemask_and_state(
                            {}, dc_local_enable.PodState.UNKNOWN.value,
                        ),
                    ],
                }
            if request.json['cluster'] == 'SAS':
                return {
                    'pods': [
                        _add_ratemask_and_state(
                            {}, dc_local_enable.PodState.ACTIVE.value,
                        ),
                        _add_ratemask_and_state(
                            {}, dc_local_enable.PodState.ACTIVE.value,
                        ),
                        _add_ratemask_and_state(
                            {}, dc_local_enable.PodState.PREPARED.value,
                        ),
                    ],
                }
            if request.json['cluster'] == 'VLA':
                return {
                    'pods': [
                        _add_ratemask_and_state(
                            {}, dc_local_enable.PodState.ACTIVE.value,
                        ),
                        _add_ratemask_and_state(
                            {}, dc_local_enable.PodState.ACTIVE.value,
                        ),
                    ],
                }
            if request.json['cluster'] == 'MYT':
                return {
                    'pods': [
                        _add_ratemask_and_state(
                            {}, dc_local_enable.PodState.ACTIVE.value,
                        ),
                    ],
                }
        if request.json['serviceId'] == 'taxi_service-31_pre_stable':
            if request.json['cluster'] == 'MYT':
                return {
                    'pods': [
                        _add_ratemask_and_state(
                            {}, dc_local_enable.PodState.ACTIVE.value,
                        ),
                    ],
                }
        return {'pods': []}

    @mockserver.json_handler('/client-awacs/api/GetNamespace/')
    def _get_namespace_handler(request):
        if request.json['id'] == 'taxi-service-31':
            return {'namespace': {'meta': {'auth': {}}}}
        return {}

    @mockserver.json_handler('/client-awacs/api/GetBackend/')
    def _get_backend_handler(request):
        if request.json['namespaceId'] == 'taxi-service-31' and request.json[
                'id'
        ] in ('backend_sas', 'backend_myt', 'backend_myt_pre'):
            return mockserver.make_response(status=404)
        return {
            'meta': {'namespaceId': 'taxi-service-31', 'id': 'backend_vla'},
        }

    @mockserver.json_handler('/client-awacs/api/CreateBackend/')
    def _create_backend_handler(_):
        return {}

    @mockserver.json_handler('/client-awacs/api/GetUpstream/')
    def _get_upstream_handler(request):
        if request.json['id'] == 'dc_local':
            return mockserver.make_response(status=404)
        return {}

    recipe = task_processor.load_recipe(
        load_yaml('EnableDcLocal.yaml')['data'],
    )
    job = await recipe.start_job(
        job_vars={'entry_point_id': 41, 'upstream_id': 'dc-local'},
        initiator='clowny-balancer',
    )
    await run_job_common(job)

    assert job.job_vars == {
        'entry_point_id': 41,
        'upstream_id': 'dc-local',
        'namespace_id': 'taxi-service-31',
        'upstream_ids': [1, 2, 3, 4],
        'backend_ids_by_env': {
            'stable': {
                'vla': 'backend_vla',
                'sas': 'backend_sas',
                'myt': 'backend_myt',
            },
            'prestable': {'myt': 'backend_myt_pre'},
        },
        'dc_local_yaml': _DC_LOCAL_YAML,
    }
    assert [x.id for x in task_processor.jobs.values()] == [1]
