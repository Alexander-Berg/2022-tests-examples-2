import pytest

RESPONSE_DATA_FIRST_TEST = {
    'hide_buttons': {
        'can_add_balancer': False,
        'can_add_prestable_balancer': False,
        'can_be_open_to_world': False,
    },
    'namespaces': [
        {
            'id': 1,
            'awacs_namespace': 'ns1',
            'env': 'stable',
            'abc_quota_source': 'abcstable',
            'is_external': True,
            'is_shared': False,
            'entry_points': [
                {
                    'id': 1,
                    'protocol': 'http',
                    'dns_name': 'fqdn.net',
                    'is_external': False,
                    'upstreams': [
                        {
                            'id': 1,
                            'env': 'stable',
                            'branch_id': 1,
                            'awacs_backend_id': 'backend1',
                        },
                        {
                            'id': 2,
                            'env': 'prestable',
                            'branch_id': 2,
                            'awacs_backend_id': 'backend2',
                        },
                    ],
                    'hide_buttons': {
                        'can_add_ssl': True,
                        'can_enable_dc_local': True,
                    },
                    'env': 'stable',
                },
            ],
        },
        {
            'id': 2,
            'awacs_namespace': 'ns2',
            'env': 'testing',
            'abc_quota_source': 'abctesting',
            'is_external': False,
            'is_shared': False,
            'entry_points': [
                {
                    'id': 2,
                    'protocol': 'http',
                    'dns_name': 'fqdn.test.net',
                    'is_external': False,
                    'upstreams': [
                        {
                            'id': 3,
                            'env': 'testing',
                            'branch_id': 3,
                            'awacs_backend_id': 'backend3',
                        },
                    ],
                    'hide_buttons': {
                        'can_add_ssl': True,
                        'can_enable_dc_local': False,
                    },
                    'env': 'testing',
                },
            ],
        },
    ],
}

RESPONSE_DATA_SECOND_TEST = {
    'hide_buttons': {
        'can_add_balancer': True,
        'can_add_prestable_balancer': True,
        'can_be_open_to_world': True,
    },
    'namespaces': [
        {
            'id': 3,
            'awacs_namespace': 'ns3',
            'env': 'stable',
            'abc_quota_source': 'abcstable',
            'is_external': False,
            'is_shared': False,
            'entry_points': [
                {
                    'id': 3,
                    'protocol': 'https',
                    'dns_name': 'fqdn2.net',
                    'is_external': False,
                    'upstreams': [
                        {
                            'id': 4,
                            'env': 'stable',
                            'branch_id': 4,
                            'awacs_backend_id': 'backend4',
                        },
                    ],
                    'hide_buttons': {
                        'can_add_ssl': False,
                        'can_enable_dc_local': False,
                    },
                    'env': 'stable',
                },
            ],
        },
    ],
}

RESPONSE_DATA_THIRD_TEST = {
    'message': 'Upstreams for service 3 not found',
    'code': 'NOT_FOUND',
    'details': {'can_add_balancer': True},
}

RESONSES_TVM_GET_BRANCHES = {
    1: [
        {
            'id': 1,
            'name': 'stable',
            'env': 'stable',
            'direct_link': 'taxi_service_stable',
            'service_id': 1,
        },
        {
            'id': 2,
            'name': 'prestable',
            'env': 'prestable',
            'direct_link': 'taxi_service_prestable',
            'service_id': 1,
        },
        {
            'id': 3,
            'name': 'testing',
            'env': 'testing',
            'direct_link': 'taxi_service_testing',
            'service_id': 1,
        },
    ],
    2: [
        {
            'id': 4,
            'name': 'stable',
            'env': 'stable',
            'direct_link': 'taxi_service_stable',
            'service_id': 2,
        },
        {
            'id': 5,
            'name': 'testing',
            'env': 'testing',
            'direct_link': 'taxi_service_testing',
            'service_id': 2,
        },
    ],
    3: [
        {
            'id': 6,
            'name': 'unstable',
            'env': 'unstable',
            'direct_link': 'taxi_service_unstable',
            'service_id': 3,
        },
    ],
}


@pytest.fixture(name='mock_get_branch')
def mock_tvm_get_branches(mock_clownductor, service_id):
    def get_branches_by_service_id():
        @mock_clownductor('/v1/branches/')
        def _branches(_):
            return RESONSES_TVM_GET_BRANCHES[service_id]

    return get_branches_by_service_id


@pytest.mark.config(
    CLOWNY_BALANCER_FEATURES={
        '__default__': {'hide_buttons_in_get_service': True},
        'project': {'service': {'show_enable_dc_local_button': True}},
    },
)
@pytest.mark.parametrize(
    'service_id, status, response_data',
    [
        (1, 200, RESPONSE_DATA_FIRST_TEST),
        (2, 200, RESPONSE_DATA_SECOND_TEST),
        (3, 404, RESPONSE_DATA_THIRD_TEST),
    ],
)
async def test_get_for_service(
        taxi_clowny_balancer_web,
        mock_get_branch,
        mock_get_service,
        service_id,
        status,
        response_data,
):
    mock_get_branch()
    mock_get_service()
    response = await taxi_clowny_balancer_web.get(
        '/balancers/v1/service/get/', params={'service_id': service_id},
    )
    data = await response.json()
    assert response.status == status, data
    assert data == response_data
