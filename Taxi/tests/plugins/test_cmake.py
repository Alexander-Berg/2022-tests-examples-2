def test_cmake(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['cmake'] = {
        'rerun_depends': ['some/file/3', 'some/file/1', 'some/file/2'],
    }
    generate_services_and_libraries(
        default_repository, 'test_cmake/cmake', default_base,
    )
