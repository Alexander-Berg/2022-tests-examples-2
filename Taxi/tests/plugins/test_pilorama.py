def test_pilorama_basic_enable(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['pilorama'] = {
        'enable': True,
    }
    generate_services_and_libraries(
        default_repository, 'test_pilorama/basic', default_base,
    )


def test_pilorama_full_config(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['pilorama'] = {
        'config': {
            'unstable': {'file': {'read_interval': '100ms'}},
            'testing': {'file': {'read_interval': '200ms'}},
            'production': {
                'file': {'discover_interval': '5s', 'read_interval': '300ms'},
                'filter': {
                    'removals': ['foo', 'bar'],
                    'put_message': True,
                    'input_format': 'json',
                    'time_formats': ['%Y-%m-%d', '%H:%M:%S'],
                    'escaping': 'simple-escape-bypass',
                },
                'output': {
                    'hosts': ['http://foo/1', 'http://foo/2'],
                    'index': 'my-index-%Y.%m.%d',
                    'error_index': 'my-errors-%Y.%m.%d',
                },
            },
        },
    }
    generate_services_and_libraries(
        default_repository, 'test_pilorama/full', default_base,
    )
