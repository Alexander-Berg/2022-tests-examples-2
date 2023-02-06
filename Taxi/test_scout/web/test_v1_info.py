import pytest

from envoy.service.endpoint.v3 import eds_pb2_grpc as envoy_eds

from test_scout.web import eds_utils

ETHALON_V1_INFO_DATA = [
    {
        'tvm_name': 'different-network',
        'domains': ['different-network.taxi.yandex.net'],
        'endpointsets_names': [
            {
                'name': 'taxi_different_network_service_name_pre_stable',
                'env': 'pre_stable',
            },
            {
                'name': 'taxi_different_network_service_name_stable',
                'env': 'stable',
            },
            {
                'name': 'taxi_different_network_service_name_testing',
                'env': 'testing',
            },
        ],
        'endpoints': [],
        'endpoints_version': 0,
        'endpoints_version_by_location': [],
        'target_tvm_names': [],
        'cluster_type': 'nanny',
        'direct_links': [
            {
                'direct_link': 'taxi_tst_different-network_pre_stable',
                'env': 'pre_stable',
                'network': '__stable_network_macro_project2__',
            },
            {
                'direct_link': 'taxi_tst_different-network_stable',
                'env': 'stable',
                'network': '__stable_network_macro_project2__',
            },
            {
                'direct_link': 'taxi_tst_different-network_testing',
                'env': 'testing',
                'network': '__testing_network_macro_project2__',
            },
        ],
    },
    {
        'tvm_name': 'envoy-exp-alpha',
        'domains': ['envoy-exp-alpha.taxi.yandex.net'],
        'endpointsets_names': [
            {
                'name': 'taxi_envoy_exp_alpha_service_name_pre_stable',
                'env': 'pre_stable',
            },
            {
                'name': 'taxi_envoy_exp_alpha_service_name_stable',
                'env': 'stable',
            },
            {
                'name': 'taxi_envoy_exp_alpha_service_name_testing',
                'env': 'testing',
            },
        ],
        'endpoints': [
            {
                'host': '2a02:6b8:c07:a2b:0:1315:d338:0',
                'port': 82,
                'zone': 'vla',
                'env': 'stable',
            },
            {
                'host': '2aff:6b8:c07:a2b:0:1315:d338:0',
                'port': 82,
                'zone': 'sas',
                'env': 'stable',
            },
            {
                'host': 'ffff:6b8:c07:a2b:0:1315:d338:0',
                'port': 82,
                'zone': 'man',
                'env': 'stable',
            },
            {
                'host': 'cccc:6b8:c07:a2b:0:1315:d338:0',
                'port': 82,
                'zone': 'man',
                'env': 'stable',
            },
        ],
        'endpoints_version': 6876097895610255,
        'endpoints_version_by_location': [
            {'location': 'man_pre_stable', 'version': 1146016315935043},
            {'location': 'man_stable', 'version': 1146016315935042},
            {'location': 'sas_pre_stable', 'version': 1146016315935043},
            {'location': 'sas_stable', 'version': 1146016315935042},
            {'location': 'vla_pre_stable', 'version': 1146016315935043},
            {'location': 'vla_stable', 'version': 1146016315935042},
        ],
        'target_tvm_names': ['envoy-exp-bravo'],
        'cluster_type': 'nanny',
        'direct_links': [
            {
                'direct_link': 'taxi_tst_envoy-exp-alpha_pre_stable',
                'env': 'pre_stable',
                'network': '__stable_network_macro_project1__',
            },
            {
                'direct_link': 'taxi_tst_envoy-exp-alpha_stable',
                'env': 'stable',
                'network': '__stable_network_macro_project1__',
            },
            {
                'direct_link': 'taxi_tst_envoy-exp-alpha_testing',
                'env': 'testing',
                'network': '__testing_network_macro_project1__',
            },
        ],
    },
    {
        'tvm_name': 'envoy-exp-bravo',
        'domains': ['envoy-exp-bravo.taxi.yandex.net'],
        'endpointsets_names': [
            {
                'name': 'taxi_envoy_exp_bravo_service_name_pre_stable',
                'env': 'pre_stable',
            },
            {
                'name': 'taxi_envoy_exp_bravo_service_name_stable',
                'env': 'stable',
            },
            {
                'name': 'taxi_envoy_exp_bravo_service_name_testing',
                'env': 'testing',
            },
        ],
        'endpoints': [],
        'endpoints_version': 0,
        'endpoints_version_by_location': [],
        'target_tvm_names': [
            'different-network',
            'envoy-exp-charlie',
            'envoy-exp-delta',
            'lxc-service',
            'multiple-endpointsets',
            'no-endpointsets',
            'no-network',
        ],
        'cluster_type': 'nanny',
        'direct_links': [
            {
                'direct_link': 'taxi_tst_envoy-exp-bravo_pre_stable',
                'env': 'pre_stable',
                'network': '__stable_network_macro_project1__',
            },
            {
                'direct_link': 'taxi_tst_envoy-exp-bravo_stable',
                'env': 'stable',
                'network': '__stable_network_macro_project1__',
            },
            {
                'direct_link': 'taxi_tst_envoy-exp-bravo_testing',
                'env': 'testing',
                'network': '__testing_network_macro_project1__',
            },
        ],
    },
    {
        'tvm_name': 'envoy-exp-charlie',
        'domains': ['envoy-exp-charlie.taxi.yandex.net'],
        'endpointsets_names': [
            {
                'name': 'taxi_envoy_exp_charlie_service_name_pre_stable',
                'env': 'pre_stable',
            },
            {
                'name': 'taxi_envoy_exp_charlie_service_name_stable',
                'env': 'stable',
            },
            {
                'name': 'taxi_envoy_exp_charlie_service_name_testing',
                'env': 'testing',
            },
        ],
        'endpoints': [],
        'endpoints_version': 0,
        'endpoints_version_by_location': [],
        'target_tvm_names': [],
        'cluster_type': 'nanny',
        'direct_links': [
            {
                'direct_link': 'taxi_tst_envoy-exp-charlie_pre_stable',
                'env': 'pre_stable',
                'network': '__stable_network_macro_project1__',
            },
            {
                'direct_link': 'taxi_tst_envoy-exp-charlie_stable',
                'env': 'stable',
                'network': '__stable_network_macro_project1__',
            },
            {
                'direct_link': 'taxi_tst_envoy-exp-charlie_testing',
                'env': 'testing',
                'network': '__testing_network_macro_project1__',
            },
        ],
    },
    {
        'tvm_name': 'envoy-exp-delta',
        'domains': ['envoy-exp-delta.taxi.yandex.net'],
        'endpointsets_names': [
            {
                'name': 'taxi_envoy_exp_delta_service_name_pre_stable',
                'env': 'pre_stable',
            },
            {
                'name': 'taxi_envoy_exp_delta_service_name_stable',
                'env': 'stable',
            },
            {
                'name': 'taxi_envoy_exp_delta_service_name_testing',
                'env': 'testing',
            },
        ],
        'endpoints': [],
        'endpoints_version': 0,
        'endpoints_version_by_location': [],
        'target_tvm_names': [],
        'cluster_type': 'nanny',
        'direct_links': [
            {
                'direct_link': 'taxi_tst_envoy-exp-delta_pre_stable',
                'env': 'pre_stable',
                'network': '__stable_network_macro_project1__',
            },
            {
                'direct_link': 'taxi_tst_envoy-exp-delta_stable',
                'env': 'stable',
                'network': '__stable_network_macro_project1__',
            },
            {
                'direct_link': 'taxi_tst_envoy-exp-delta_testing',
                'env': 'testing',
                'network': '__testing_network_macro_project1__',
            },
        ],
    },
    {
        'tvm_name': 'multiple-endpointsets',
        'domains': [],
        'endpointsets_names': [
            {
                'name': 'taxi_multiple_endpointsets_service_name_additional',
                'env': 'pre_stable',
            },
            {
                'name': 'taxi_multiple_endpointsets_service_name_pre_stable',
                'env': 'pre_stable',
            },
            {
                'name': 'taxi_multiple_endpointsets_service_name_additional',
                'env': 'stable',
            },
            {
                'name': 'taxi_multiple_endpointsets_service_name_stable',
                'env': 'stable',
            },
            {
                'name': 'taxi_multiple_endpointsets_service_name_additional',
                'env': 'testing',
            },
            {
                'name': 'taxi_multiple_endpointsets_service_name_testing',
                'env': 'testing',
            },
        ],
        'endpoints': [],
        'endpoints_version': 0,
        'endpoints_version_by_location': [],
        'target_tvm_names': [],
        'cluster_type': 'nanny',
        'direct_links': [
            {
                'direct_link': 'taxi_tst_multiple-endpointsets_pre_stable',
                'env': 'pre_stable',
                'network': '__stable_network_macro_project1__',
            },
            {
                'direct_link': 'taxi_tst_multiple-endpointsets_stable',
                'env': 'stable',
                'network': '__stable_network_macro_project1__',
            },
            {
                'direct_link': 'taxi_tst_multiple-endpointsets_testing',
                'env': 'testing',
                'network': '__testing_network_macro_project1__',
            },
        ],
    },
    {
        'tvm_name': 'no-endpointsets',
        'domains': [],
        'endpointsets_names': [],
        'endpoints': [],
        'endpoints_version': 0,
        'endpoints_version_by_location': [],
        'target_tvm_names': [],
        'cluster_type': 'nanny',
        'direct_links': [
            {
                'direct_link': 'taxi_tst_no-endpointsets_pre_stable',
                'env': 'pre_stable',
                'network': '__stable_network_macro_project1__',
            },
            {
                'direct_link': 'taxi_tst_no-endpointsets_stable',
                'env': 'stable',
                'network': '__stable_network_macro_project1__',
            },
            {
                'direct_link': 'taxi_tst_no-endpointsets_testing',
                'env': 'testing',
                'network': '__testing_network_macro_project1__',
            },
        ],
    },
    {
        'tvm_name': 'no-network',
        'domains': ['no-network.taxi.yandex.net'],
        'endpointsets_names': [
            {
                'name': 'taxi_no_network_service_name_pre_stable',
                'env': 'pre_stable',
            },
            {'name': 'taxi_no_network_service_name_stable', 'env': 'stable'},
            {'name': 'taxi_no_network_service_name_testing', 'env': 'testing'},
        ],
        'endpoints': [],
        'endpoints_version': 0,
        'endpoints_version_by_location': [],
        'target_tvm_names': [],
        'cluster_type': 'nanny',
        'direct_links': [
            {
                'direct_link': 'taxi_tst_no-network_pre_stable',
                'env': 'pre_stable',
            },
            {'direct_link': 'taxi_tst_no-network_stable', 'env': 'stable'},
            {'direct_link': 'taxi_tst_no-network_testing', 'env': 'testing'},
        ],
    },
]


@pytest.mark.usefixtures('mock_tvm_rules')
async def test_v1_info(
        taxi_scout_web_oneshot, yp_discovery_mock, grpc_scout_channel,
):
    yp_discovery_mock.alpha_timer = lambda clust_name: 1146016315935042
    yp_discovery_mock.alpha_timer_pre = lambda clust_name: 1146016315935043
    yp_discovery_mock.bravo_timer = lambda clust_name: 1146016315935044
    await taxi_scout_web_oneshot.invalidate_caches()

    discovery_stub = envoy_eds.EndpointDiscoveryServiceStub(grpc_scout_channel)
    await eds_utils.stream_single_endpoint_set(discovery_stub)

    response = await taxi_scout_web_oneshot.get('/v1/info')
    assert response.status == 200
    content = await response.json()
    assert content == ETHALON_V1_INFO_DATA
