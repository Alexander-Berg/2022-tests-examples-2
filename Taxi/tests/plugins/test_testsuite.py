def test_disabled(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['testsuite'] = {
        'enabled': False,
    }
    generate_services_and_libraries(
        default_repository, 'test_testsuite/disabled', default_base,
    )


def test_apikeys(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['testsuite'] = {
        'apikeys': {
            'key3': ['value3', 'vvv', '333'],
            'key1': ['value1', '111'],
            'key2': ['value2'],
        },
    }
    generate_services_and_libraries(
        default_repository, 'test_testsuite/apikeys', default_base,
    )
