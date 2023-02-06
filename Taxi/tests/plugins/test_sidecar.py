def test_sidecar(
        generate_services_and_libraries, default_repository, default_base,
):
    service_yaml = default_repository['services/test-service/service.yaml']
    service_yaml['uservice_unit']['sidecar'] = {'enabled': True}
    service_yaml['statistics'] = {'solomon-service': 'test_service'}

    generate_services_and_libraries(
        default_repository, 'test_sidecar/test_sidecar', default_base,
    )


def test_sidecar_tvm_mode_fake(
        generate_services_and_libraries, default_repository, default_base,
):
    service_yaml = default_repository['services/test-service/service.yaml']
    service_yaml['uservice_unit']['sidecar'] = {
        'enabled': True,
        'tvm-mode': 'fake',
    }
    service_yaml['statistics'] = {'solomon-service': 'test_service'}

    generate_services_and_libraries(
        default_repository,
        'test_sidecar/test_sidecar_tvm_mode_fake',
        default_base,
    )
