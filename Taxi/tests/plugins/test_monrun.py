def test_running(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['monrun'] = {
        'check-running': True,
    }

    generate_services_and_libraries(
        default_repository, 'test_monrun/running', default_base,
    )
