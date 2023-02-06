from clowny_balancer.generated.cron import run_cron


async def test_sync_awacs_endpoint_sets(
        patch, mockserver, cron_context, relative_load_plaintext, load_json,
):
    @mockserver.json_handler('/client-awacs/api/GetNamespace/')
    def _get_namespace(request):
        return {'namespace': {'order': {'status': {'status': 'FINISHED'}}}}

    @mockserver.json_handler('/client-awacs/api/ListBalancers/')
    def _list_balansers(request):
        return {
            'balancers': [
                {
                    'status': {
                        'active': {'status': 'True'},
                        'inProgress': {'status': 'False'},
                        'validated': {'status': 'True'},
                    },
                },
                {
                    'status': {
                        'active': {'status': 'True'},
                        'inProgress': {'status': 'False'},
                        'validated': {'status': 'True'},
                    },
                },
            ],
            'total': 2,
        }

    @mockserver.json_handler('/client-awacs/api/ListBackends/')
    def _list_handler(request):
        data = request.json
        namecpase_id = data['namespaceId']
        response = {'annotatedBackends': [], 'backends': [], 'total': 0}
        if namecpase_id == 'stable-ns.yandex.net':
            # pre: sas; stable: sas, man, vla exist locations
            response = load_json('stable_list_backends.json')
        elif namecpase_id == 'testing-ns.yandex.net':
            # man, sas locations
            response = load_json('testing_list_backends.json')
        return response

    @mockserver.json_handler('/client-awacs/api/UpdateBackend/')
    def _update_backend(request):
        expected_endpoint_sets = {
            'taxi-infra_task-processor_pre_stable': [
                {
                    'cluster': 'vla',
                    'endpointSetId': 'taxi_infra_task_processor_pre_stable',
                },
                {
                    'cluster': 'sas',
                    'endpointSetId': 'taxi_infra_task_processor_pre_stable',
                },
            ],
            # add new vla location, and cant remove man
            'taxi_clownductor_testing': [
                {
                    'cluster': 'vla',
                    'endpointSetId': 'taxi_admin_hiring_testing',
                },
                {
                    'cluster': 'sas',
                    'endpointSetId': 'taxi_admin_hiring_testing',
                },
                {
                    'cluster': 'man',
                    'endpointSetId': 'taxi_admin_hiring_testing',
                },
            ],
        }
        data = request.json
        selector = data['spec']['selector']
        assert selector['type'] == 'YP_ENDPOINT_SETS_SD'
        yp_endpoint_set = selector['ypEndpointSets']
        backend_id = data['meta']['id']
        expected_yp_endpoint_set = expected_endpoint_sets.get(backend_id, [])
        assert sorted(yp_endpoint_set, key=lambda x: x['cluster']) == sorted(
            expected_yp_endpoint_set, key=lambda x: x['cluster'],
        )
        return {'backend': {**data}}

    @mockserver.json_handler('/clownductor/v1/branches/')
    def _list_branches(request):
        branch_id = int(request.query['branch_id'])
        if branch_id == 123:
            env = 'stable'
        elif branch_id == 124:
            env = 'prestable'
        elif branch_id == 125:
            env = 'testing'
        else:
            return []
        return [
            {
                'id': branch_id,
                'service_id': 1,
                'name': f'{env}_branch',
                'direct_link': f'{env}_nanny_name',
                'env': env,
            },
        ]

    @mockserver.json_handler('/client-nanny-yp/api/yplite/pod-sets/ListPods/')
    def _list_yp_pods(request):
        data = request.json
        nanny_name = data['serviceId']
        cluster = data['cluster']

        pods = []
        pod = load_json('field_pod.json')

        active_pods = []
        if nanny_name == 'stable_nanny_name':
            active_pods = ['MAN', 'SAS', 'VLA']
        elif nanny_name == 'prestable_nanny_name':
            active_pods = ['VLA']
        elif nanny_name == 'testing_nanny_name':
            active_pods = ['VLA', 'SAS']

        if cluster in active_pods:
            pods.append(pod)
        return {'total': len(pods), 'pods': pods}

    await run_cron.main(
        ['clowny_balancer.crontasks.sync_awacs_endpoint_sets', '-t', '0'],
    )
    assert _list_handler.times_called == 2
    assert _update_backend.times_called == 2  # stable already exists
    assert _list_branches.times_called == 3
    assert _list_yp_pods.times_called == 9


async def test_sync_awacs_endpoint_sets_yp_500_response(mockserver, load_json):
    @mockserver.json_handler('/client-awacs/api/GetNamespace/')
    def _get_namespace(request):
        return {'namespace': {'order': {'status': {'status': 'FINISHED'}}}}

    @mockserver.json_handler('/client-awacs/api/ListBalancers/')
    def _list_balansers(request):
        return {
            'balancers': [
                {
                    'status': {
                        'active': {'status': 'True'},
                        'inProgress': {'status': 'False'},
                        'validated': {'status': 'True'},
                    },
                },
                {
                    'status': {
                        'active': {'status': 'True'},
                        'inProgress': {'status': 'False'},
                        'validated': {'status': 'True'},
                    },
                },
            ],
            'total': 2,
        }

    @mockserver.json_handler('/client-awacs/api/ListBackends/')
    def _list_handler(request):
        data = request.json
        namecpase_id = data['namespaceId']
        response = {'annotatedBackends': [], 'backends': [], 'total': 0}
        if namecpase_id == 'stable-ns.yandex.net':
            response = load_json('stable_list_backends.json')
        elif namecpase_id == 'testing-ns.yandex.net':
            response = load_json('testing_list_backends.json')
        return response

    @mockserver.json_handler('/client-awacs/api/UpdateBackend/')
    def _update_backend(request):
        expected_endpoint_sets = {
            'taxi-infra_task-processor_pre_stable': [
                {
                    'cluster': 'vla',
                    'endpointSetId': 'taxi_infra_task_processor_pre_stable',
                },
                {
                    'cluster': 'sas',
                    'endpointSetId': 'taxi_infra_task_processor_pre_stable',
                },
            ],
            'taxi_clownductor_testing': [
                {
                    'cluster': 'vla',
                    'endpointSetId': 'taxi_admin_hiring_testing',
                },
                {
                    'cluster': 'sas',
                    'endpointSetId': 'taxi_admin_hiring_testing',
                },
                {
                    'cluster': 'man',
                    'endpointSetId': 'taxi_admin_hiring_testing',
                },
            ],
        }
        data = request.json
        selector = data['spec']['selector']
        assert selector['type'] == 'YP_ENDPOINT_SETS_SD'
        yp_endpoint_set = selector['ypEndpointSets']
        backend_id = data['meta']['id']
        expected_yp_endpoint_set = expected_endpoint_sets.get(backend_id, [])
        assert sorted(yp_endpoint_set, key=lambda x: x['cluster']) == sorted(
            expected_yp_endpoint_set, key=lambda x: x['cluster'],
        )
        return {'backend': {**data}}

    @mockserver.json_handler('/clownductor/v1/branches/')
    def _list_branches(request):
        branch_id = int(request.query['branch_id'])
        if branch_id == 123:
            env = 'stable'
        elif branch_id == 124:
            env = 'prestable'
        elif branch_id == 125:
            env = 'testing'
        else:
            return []
        return [
            {
                'id': branch_id,
                'service_id': 1,
                'name': f'{env}_branch',
                'direct_link': f'{env}_nanny_name',
                'env': env,
            },
        ]

    @mockserver.json_handler('/client-nanny-yp/api/yplite/pod-sets/ListPods/')
    def _list_yp_pods(request):
        return mockserver.make_response(status=500)

    await run_cron.main(
        ['clowny_balancer.crontasks.sync_awacs_endpoint_sets', '-t', '0'],
    )
    assert _get_namespace.times_called == 2
    assert _list_balansers.times_called == 2
    assert _list_handler.times_called == 2
    assert _update_backend.times_called == 0
    assert _list_branches.times_called == 2
    assert _list_yp_pods.times_called == 6
