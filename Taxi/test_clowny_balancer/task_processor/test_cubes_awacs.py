import pytest


@pytest.mark.parametrize(
    'cube_name, input_data, payload',
    [
        pytest.param(
            'AwacsWaitForL3',
            {'fqdn': 'test-fqdn'},
            {'l3mgrServiceId': '7492'},
        ),
        pytest.param(
            'AwacsWaitForL3',
            {'fqdn': 'test-fqdn-handmade'},
            {'l3mgrServiceId': '6666'},
        ),
        ('AwacsRemoveL3Link', {'fqdn': 'test-fqdn'}, None),
        ('AwacsRemoveNamespace', {'fqdn': 'test-fqdn'}, None),
        (
            'AwacsCheckBalancerNotExists',
            {'fqdn': 'test-fqdn'},
            {'fqdn': 'test-fqdn', 'origin_fqdn': ''},
        ),
        pytest.param(
            'AwacsWaitForNamespace',
            {'fqdn': 'test-fqdn'},
            None,
            marks=pytest.mark.config(
                CLOWNY_BALANCER_FEATURES={
                    '__default__': {'entity_creation_check': True},
                },
            ),
        ),
        (
            'AwacsGetBackends',
            {'fqdn': 'test-fqdn'},
            {
                'l7_nanny_services': [
                    'rtc_balancer_admin-data_taxi_yandex_net_man_sas_vla',
                ],
                'l3_backends': [
                    'rtc_balancer_admin-data_taxi_yandex_net_man_sas_vla',
                    'service_upstream',
                ],
                'system_backends': [
                    'rtc_balancer_admin-data_taxi_yandex_net_man_sas_vla',
                ],
            },
        ),
        (
            'AwacsGetL7NannyServices',
            {'fqdn': 'test-fqdn'},
            {
                'nanny_sas': (
                    'rtc_balancer_callcenter-operators_taxi_yandex_net_sas'
                ),
                'nanny_vla': '',
                'nanny_man': '',
                'nanny_services': [
                    'rtc_balancer_callcenter-operators_taxi_yandex_net_sas',
                ],
                'l7_balancers_ids': [
                    'callcenter-operators.taxi.yandex.net_sas',
                ],
            },
        ),
        (
            'AwacsSetDefaultYaml',
            {'fqdn': 'test-fqdn'},
            {'default_upstream_name': 'default'},
        ),
        ('AwacsSetSlbpingYaml', {'fqdn': 'test-fqdn'}, None),
        (
            'AwacsCreateL3',
            {
                'fqdn': 'test-fqdn',
                'l7_balancers_ids': ['some_id'],
                'service_id': 1,
            },
            None,
        ),
        pytest.param(
            'AwacsSaveNamespace',
            {'service_id': 1, 'env': 'stable', 'fqdn': 'test-fqdn'},
            {
                'namespace_id': 1,
                'entry_point_id': 1,
                'skip_domain_usage': False,
                'awacs_namespace_id': 'test-fqdn',
            },
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES={'use_domains': True},
            ),
        ),
        pytest.param(
            'AwacsSaveNamespace',
            {
                'service_id': 1,
                'env': 'testing',
                'fqdn': 'test-fqdn',
                'branch_name': 'tcustom',
            },
            {
                'namespace_id': 1,
                'entry_point_id': 1,
                'skip_domain_usage': False,
                'awacs_namespace_id': 'test-fqdn',
            },
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES={'use_domains': True},
            ),
        ),
        (
            'AwacsSaveNamespace',
            {
                'service_id': 1,
                'env': 'stable',
                'fqdn': 'test-fqdn',
                'awacs_namespace_id': 'awacs_namespace_1',
            },
            {
                'namespace_id': 1,
                'entry_point_id': 1,
                'skip_domain_usage': True,
                'awacs_namespace_id': 'awacs_namespace_1',
            },
        ),
        (
            'AwacsCreateAwacsNamespace',
            {
                'namespace_id': 2,
                'datacenters': ['sas', 'vla'],
                'active_backend_datacenters': [
                    {'branch_id': 1, 'regions': ['sas', 'vla']},
                ],
            },
            None,
        ),
        (
            'AwacsCreateAwacsNamespace',
            {
                'namespace_id': 2,
                'datacenters': ['sas', 'vla'],
                'active_backend_datacenters': [
                    {'branch_id': 1, 'regions': ['sas', 'vla']},
                ],
                'network': '__ELRUSSO_NETWORK__',
            },
            None,
        ),
        ('AwacsCreateEmptyAwacsNamespace', {'namespace_id': 2}, None),
        (
            'AwacsBalancerChangeProject',
            {'new_project_id': 2, 'service_id': 1},
            None,
        ),
    ],
)
async def test_cubes(
        mock_clownductor,
        abc_mockserver,
        awacs_mockserver,
        call_cube,
        cube_name,
        input_data,
        payload,
):
    abc_mockserver()
    awacs_mockserver()

    @mock_clownductor('/v1/services/')
    def _services_handler(request):
        return [
            {
                'id': 1,
                'name': 'test',
                'cluster_type': 'nanny',
                'project_id': 1,
            },
            {
                'id': 2,
                'name': 'test_old',
                'cluster_type': 'nanny',
                'project_id': 2,
            },
        ]

    @mock_clownductor('/api/projects')
    def _projects_handler(request):
        return [
            {
                'id': 1,
                'name': 'taxi',
                'yp_quota_abc': 'taxi_yp_quota',
                'datacenters': ['SAS', 'VLA', 'MAN'],
                'namespace_id': 1,
            },
            {
                'id': 2,
                'name': 'taxi_old',
                'yp_quota_abc': 'taxi_yp_quota',
                'datacenters': ['SAS', 'VLA', 'MAN'],
                'namespace_id': 1,
            },
            {
                'id': 4,
                'name': 'taxi_new',
                'yp_quota_abc': 'taxi_yp_quota',
                'datacenters': ['SAS', 'VLA', 'MAN'],
                'namespace_id': 1,
            },
        ]

    @mock_clownductor('/v1/branches/')
    def _branches_handler(request):
        return [
            {
                'env': 'stable',
                'id': 1,
                'direct_link': 'taxi-test-stable',
                'service_id': 123,
                'name': 'stable',
            },
            {
                'env': 'prestable',
                'id': 2,
                'direct_link': 'taxi-test-pre_stable',
                'service_id': 123,
                'name': 'pre_stable',
            },
            {
                'env': 'testing',
                'id': 5,
                'direct_link': 'taxi-test-tcustom',
                'service_id': 123,
                'name': 'tcustom',
            },
            {
                'env': 'testing',
                'id': 6,
                'direct_link': 'taxi-test-testing',
                'service_id': 123,
                'name': 'testing',
            },
        ]

    response = await call_cube(cube_name, input_data)
    result = {'status': 'success'}
    if payload is not None:
        result['payload'] = payload
    assert response == result


@pytest.mark.parametrize(
    'input_data, wait_cnt',
    [
        ({'new_project_id': 2, 'service_id': 1}, 2),
        ({'new_project_id': 5, 'service_id': 2}, 1),
    ],
)
async def test_change_project_cube(
        input_data, wait_cnt, web_context, call_cube_client,
):
    await call_cube_client.post(
        f'/task-processor/v1/cubes/AwacsBalancerChangeProject/',
        json={
            'input_data': input_data,
            'job_id': 0,
            'task_id': 0,
            'retries': 0,
            'status': 'in_progress',
        },
    )

    result = await web_context.pg.primary.fetch(
        """
        SELECT id,
               project_id,
               env,
               awacs_namespace
        FROM balancers.namespaces
        ORDER BY id DESC
        """,
    )
    project_balancers_cnt = 0
    for bal in result:
        if bal['project_id'] == input_data['new_project_id']:
            project_balancers_cnt += 1
    assert project_balancers_cnt == wait_cnt


@pytest.mark.parametrize(
    'expected_order',
    [
        pytest.param(
            {
                'flowType': 'YP_LITE',
                'backends': {
                    'backend1': {
                        'type': 'YP_ENDPOINT_SETS_SD',
                        'useMtn': False,
                        'ypEndpointSets': [
                            {'cluster': 'sas', 'endpointSetId': 'backend1'},
                        ],
                        'nannySnapshots': [],
                        'gencfgGroups': [],
                        'allowEmptyYpEndpointSets': False,
                    },
                    'backend2': {
                        'type': 'YP_ENDPOINT_SETS_SD',
                        'useMtn': False,
                        'ypEndpointSets': [
                            {'cluster': 'man', 'endpointSetId': 'backend2'},
                            {'cluster': 'vla', 'endpointSetId': 'backend2'},
                        ],
                        'nannySnapshots': [],
                        'gencfgGroups': [],
                        'allowEmptyYpEndpointSets': False,
                    },
                },
                'ypLiteAllocationRequest': {
                    'nannyServiceIdSlug': 'not-used-yet',
                    'locations': ['MAN', 'SAS', 'VLA'],
                    'networkMacro': None,
                    'type': 'PRESET',
                    'preset': {'type': 'SMALL', 'instances_count': 1},
                },
                'alertingSimpleSettings': {'notifyStaffGroupId': 50889},
            },
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES={'use_sd_fast_for_create': True},
            ),
            id='check_sd_fast',
        ),
        pytest.param(
            {
                'flowType': 'YP_LITE',
                'backends': {
                    'backend1': {
                        'type': 'YP_ENDPOINT_SETS',
                        'useMtn': False,
                        'ypEndpointSets': [
                            {'cluster': 'man', 'endpointSetId': 'backend1'},
                            {'cluster': 'vla', 'endpointSetId': 'backend1'},
                            {'cluster': 'sas', 'endpointSetId': 'backend1'},
                        ],
                        'nannySnapshots': [],
                        'gencfgGroups': [],
                        'allowEmptyYpEndpointSets': False,
                    },
                    'backend2': {
                        'type': 'YP_ENDPOINT_SETS',
                        'useMtn': False,
                        'ypEndpointSets': [
                            {'cluster': 'man', 'endpointSetId': 'backend2'},
                            {'cluster': 'vla', 'endpointSetId': 'backend2'},
                            {'cluster': 'sas', 'endpointSetId': 'backend2'},
                        ],
                        'nannySnapshots': [],
                        'gencfgGroups': [],
                        'allowEmptyYpEndpointSets': False,
                    },
                },
                'ypLiteAllocationRequest': {
                    'nannyServiceIdSlug': 'not-used-yet',
                    'locations': ['MAN', 'SAS', 'VLA'],
                    'networkMacro': None,
                    'type': 'PRESET',
                    'preset': {'type': 'SMALL', 'instances_count': 1},
                },
                'alertingSimpleSettings': {'notifyStaffGroupId': 50889},
            },
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES={'use_sd_fast_for_create': False},
            ),
            id='old_flow',
        ),
    ],
)
async def test_create_namespace(
        call_cube,
        mockserver,
        mock_clownductor,
        abc_mockserver,
        expected_order,
):
    abc_mockserver()

    @mockserver.json_handler('/client-awacs/api/GetNamespace/')
    def _get_handler(request):
        return mockserver.make_response(status=404)

    @mockserver.json_handler('/client-awacs/api/CreateNamespace/')
    def _create_handler(request):
        order = request.json['order']
        assert set(order) == set(expected_order)

    @mock_clownductor('/v1/services/')
    def _services_handler(request):
        return [
            {
                'id': 1,
                'name': 'test',
                'cluster_type': 'nanny',
                'project_id': 1,
            },
        ]

    @mock_clownductor('/api/projects')
    def _projects_handler(request):
        return [
            {
                'id': 1,
                'name': 'taxi',
                'yp_quota_abc': 'taxi_yp_quota',
                'datacenters': ['SAS', 'VLA', 'MAN'],
                'namespace_id': 1,
            },
        ]

    @mock_clownductor('/v1/branches/')
    def _branches_handler(request):
        return [
            {
                'env': 'stable',
                'id': 1,
                'direct_link': 'taxi-test-stable',
                'service_id': 123,
                'name': 'stable',
            },
            {
                'env': 'prestable',
                'id': 2,
                'direct_link': 'taxi-test-pre_stable',
                'service_id': 123,
                'name': 'pre_stable',
            },
            {
                'env': 'testing',
                'id': 5,
                'direct_link': 'taxi-test-tcustom',
                'service_id': 123,
                'name': 'tcustom',
            },
            {
                'env': 'testing',
                'id': 6,
                'direct_link': 'taxi-test-testing',
                'service_id': 123,
                'name': 'testing',
            },
        ]

    input_data = {
        'namespace_id': 2,
        'datacenters': ['MAN', 'SAS', 'VLA'],
        'size': 'SMALL',
        'active_backend_datacenters': [
            {'branch_id': 4, 'regions': ['man', 'vla']},
            {'branch_id': 3, 'regions': ['sas']},
        ],
    }
    cube_name = 'AwacsCreateAwacsNamespace'
    response = await call_cube(cube_name, input_data)
    result = {'status': 'success'}
    assert response == result
