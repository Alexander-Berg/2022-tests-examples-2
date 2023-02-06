import pytest


@pytest.mark.parametrize(
    'use_api_flow, test_name',
    [
        pytest.param(True, 'generate_api_request'),
        pytest.param(False, 'not_generate_api_request'),
    ],
)
def test_dashboard(
        generate_services_and_libraries,
        default_repository,
        default_base,
        use_api_flow,
        test_name,
):
    service_yaml_activation = {
        'project_name': 'taxi',
        'service_group': {'rtc': {'name': 'some-service'}},
        'grafana_additional_layouts': ['system'],
    }
    service_yaml_activation.update(
        {
            'use_api_flow': use_api_flow,
            'clownductor_project': 'taxi',
            'clownductor_main_alias': 'test-service',
            'clownductor_aliases': ['test-service'],
        },
    )

    service_yaml = default_repository['services/test-service/service.yaml']
    service_yaml['dashboards'] = service_yaml_activation
    generate_services_and_libraries(
        default_repository,
        f'test_dashboards/dashboards/{test_name}',
        default_base,
    )
