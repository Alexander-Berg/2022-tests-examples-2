def test_library(
        generate_services_and_libraries, default_repository, default_base,
):
    data = default_repository['libraries/codegen/library.yaml'].copy()
    default_repository['libraries/pricing-functions/library.yaml'] = data
    data['project-name'] = 'yandex-taxi-library-pricing-functions'
    data['build_quirks'] = {'template-depth': 1024}
    generate_services_and_libraries(
        default_repository, 'test_build_quirks/library', default_base,
    )


def test_unit(
        generate_services_and_libraries, default_repository, default_base,
):
    service_yaml = default_repository['services/test-service/service.yaml']
    service_yaml['build_quirks'] = {'template-depth': 1024}
    generate_services_and_libraries(
        default_repository, 'test_build_quirks/unit', default_base,
    )
