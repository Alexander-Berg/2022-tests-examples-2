def test_market_spok_infra(
        generate_services_and_libraries, default_repository, default_base,
):
    service_yaml = default_repository['services/test-service/service.yaml']
    service_yaml['market-spok-infra'] = {
        'enabled': True,
        'description': 'Shine bright like a diamond!',
        'bin_name': 'my_lovely_binary_name',
        'rtc_json_includes': ['market/search/test-projects/my-package.json'],
    }
    generate_services_and_libraries(
        default_repository, 'test_market_spok_infra/test', default_base,
    )
