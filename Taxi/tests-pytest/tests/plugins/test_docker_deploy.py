def test_docker_deploy(
        generate_services_and_libraries, default_repository, default_base,
):
    service_yaml = default_repository['services/test-service/service.yaml']
    service_yaml['docker-deploy'] = {
        'extra-packages': ['package1', 'package2'],
        'extra-sources': ['yandex-taxi-xenial', 'yandex-taxi-common'],
    }
    generate_services_and_libraries(
        default_repository, 'test_docker_deploy/test', default_base,
    )


def test_docker_deploy_geobase(
        generate_services_and_libraries, default_repository, default_base,
):
    service_yaml = default_repository['services/test-service/service.yaml']
    service_yaml['docker-deploy'] = {'install_geobase': True}
    generate_services_and_libraries(
        default_repository, 'test_docker_deploy/geobase', default_base,
    )


def test_docker_deploy_geobase6(
        generate_services_and_libraries, default_repository, default_base,
):
    service_yaml = default_repository['services/test-service/service.yaml']
    service_yaml['docker-deploy'] = {'install_geobase': 6}
    generate_services_and_libraries(
        default_repository, 'test_docker_deploy/geobase6', default_base,
    )
