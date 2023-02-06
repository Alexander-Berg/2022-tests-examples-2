def test_statistics(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['statistics'] = {
        'port': 2211,
    }
    generate_services_and_libraries(
        default_repository, 'test_statistics/test', default_base,
    )


def test_statistics_multi_unit(
        generate_services_and_libraries,
        multi_unit_repository,
        multi_unit_base,
):
    multi_unit_repository['services/test-service/service.yaml'][
        'statistics'
    ] = {'port': 2211}
    generate_services_and_libraries(
        multi_unit_repository, 'test_statistics/multi_unit', multi_unit_base,
    )
