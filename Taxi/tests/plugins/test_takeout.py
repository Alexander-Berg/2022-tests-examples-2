def test_takeout_only_paths(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['takeout'] = {
        'codegen_api': True,
    }
    generate_services_and_libraries(
        default_repository, 'test_takeout/test_only_paths', default_base,
    )


def test_takeout_stq(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['takeout'] = {
        'codegen_api': True,
        'use_stq_for_delete': True,
    }
    generate_services_and_libraries(
        default_repository, 'test_takeout/test_stq', default_base,
    )


def test_paths_by_namespaces(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['takeout'] = {
        'codegen_api': True,
        'data_categories': ['data_category_1', 'data_category_2'],
    }
    generate_services_and_libraries(
        default_repository,
        'test_takeout/test_paths_by_namespaces',
        default_base,
    )
