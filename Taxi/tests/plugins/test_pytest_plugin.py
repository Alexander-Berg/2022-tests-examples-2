def test_service(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['pytest'] = {
        'plugins': ['plugin3', 'plugin1', 'plugin2'],
        'pytest-plugins': [
            'pytest_plugin3',
            'pytest_plugin1',
            'pytest_plugin2',
        ],
        'userver-fixture': {
            'daemon-deps': ['daemon_dep3', 'daemon_dep1', 'daemon_dep2'],
            'service-headers': {
                'header3': 'value_header3',
                'header1': 'value_header1',
                'header2': 'value_header2',
            },
            'client-deps': ['client_dep3', 'client_dep1', 'client_dep2'],
        },
    }
    generate_services_and_libraries(
        default_repository, 'test_pytest_plugin/service', default_base,
    )


def test_library(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['libraries'] = [
        'yandex-taxi-library-test-library',
    ]
    default_repository.update(
        {
            'libraries/test-library/library.yaml': {
                'maintainers': ['you'],
                'description': 'the best from the west',
                'project-name': 'yandex-taxi-library-test-library',
                'pytest': {
                    'plugins': ['plugin3', 'plugin1', 'plugin2'],
                    'pytest-plugins': [
                        'pytest_plugin3',
                        'pytest_plugin1',
                        'pytest_plugin2',
                    ],
                    'userver-fixture': {
                        'daemon-deps': [
                            'daemon_dep3',
                            'daemon_dep1',
                            'daemon_dep2',
                        ],
                        'service-headers': {
                            'header3': 'value_header3',
                            'header1': 'value_header1',
                            'header2': 'value_header2',
                        },
                        'client-deps': [
                            'client_dep3',
                            'client_dep1',
                            'client_dep2',
                        ],
                    },
                },
            },
        },
    )
    generate_services_and_libraries(
        default_repository, 'test_pytest_plugin/library', default_base,
    )
