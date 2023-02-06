def test_user(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['user'] = {
        'name': 'alberist',
    }
    generate_services_and_libraries(
        default_repository, 'test_user/test', default_base,
    )
