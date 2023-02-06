def test_tmv2(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['tvm2'] = {
        'secdist-service-name': 'my-custom-tvm-service-name',
    }
    generate_services_and_libraries(
        default_repository, 'test_tvm2/test', default_base,
    )
