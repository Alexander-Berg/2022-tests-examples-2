def test_secdist(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['secdist'] = {
        'testsuite': {
            'values': {
                'settings_override': {
                    'KEY3': 'VALUE3',
                    'KEY1': 'VALUE1',
                    'KEY2': 'VALUE2',
                },
                'some': {
                    'too': {
                        'long': {
                            'depth': {
                                'key3': 'value3',
                                'key1': 'value1',
                                'key2': 'value2',
                            },
                        },
                    },
                },
                'try': {
                    'add': {'dict': {'key': {'directly': ['work', 'fine']}}},
                },
            },
        },
    }
    default_repository['libraries/basic-http-client/library.yaml'][
        'secdist'
    ] = {'testsuite': {'values': {'settings_override': {'KEY': 'VALUE'}}}}
    generate_services_and_libraries(
        default_repository, 'test_secdist/test', default_base,
    )
