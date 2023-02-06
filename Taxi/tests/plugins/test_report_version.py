def test_report_version(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml'][
        'report-version'
    ] = {'enabled': True}
    generate_services_and_libraries(
        default_repository, 'test_report_version/report_version', default_base,
    )
