def test_saas_push(
        generate_services_and_libraries, default_repository, default_base,
):
    service_yaml = default_repository['services/test-service/service.yaml']
    service_yaml['saas-push'] = {
        'production': {
            'controller': {'http_options': {'port': 9999, 'threads': 1}},
            'telemetry': {'interval': '10m'},
            'server': {
                'search_map': {
                    'ctype': 'PRODUCTION',
                    'dm_host': 'dm_host.yandex',
                    'statica_host': 'statica.yandex',
                    'statica_query': 'query',
                },
                'writer': {
                    'http_options': {'port': 9990, 'threads': 1},
                    'services': [
                        {
                            'alias': 'MY_SERVICE',
                            'name': 'MY_SERVICE_NAME',
                            'ctype': 'PRODUCTION',
                            'server': 'lb.server.yandex',
                            'topics_dir': '/topics/my_service',
                            'tvm': {
                                'destination_alias': 'ALIAS',
                                'destination_client_id': 10,
                            },
                        },
                    ],
                },
            },
        },
        'testing': {
            'controller': {'http_options': {'port': 9999, 'threads': 1}},
            'telemetry': {'interval': '10m'},
            'server': {
                'search_map': {
                    'ctype': 'TESTING',
                    'dm_host': 'dm_host.yandex',
                    'statica_host': 'statica.yandex',
                    'statica_query': 'query',
                },
                'writer': {
                    'http_options': {'port': 9990, 'threads': 1},
                    'services': [
                        {
                            'alias': 'MY_SERVICE',
                            'name': 'MY_SERVICE_NAME',
                            'ctype': 'TESTING',
                            'server': 'lb.server.yandex',
                            'topics_dir': '/topics/my_service',
                            'tvm': {
                                'destination_alias': 'ALIAS',
                                'destination_client_id': 10,
                            },
                        },
                    ],
                },
            },
        },
    }
    generate_services_and_libraries(
        default_repository, 'test_saas_push/test', default_base,
    )


def test_saas_push_services(
        generate_services_and_libraries, default_repository, default_base,
):
    service_yaml = default_repository['services/test-service/service.yaml']
    service_yaml['saas-push'] = {
        'production': {
            'controller': {'http_options': {'port': 9999, 'threads': 1}},
            'telemetry': {'interval': '10m'},
            'server': {
                'search_map': {
                    'ctype': 'PRODUCTION',
                    'dm_host': 'dm_host.yandex',
                    'statica_host': 'statica.yandex',
                    'statica_query': 'query',
                },
                'writer': {
                    'http_options': {'port': 9990, 'threads': 1},
                    'services': [
                        {
                            'alias': 'MY_SERVICE',
                            'name': 'MY_SERVICE_NAME',
                            'ctype': 'PRODUCTION',
                            'server': 'lb.server.yandex',
                            'topics_dir': '/topics/my_service',
                            'tvm': {
                                'destination_alias': 'ALIAS',
                                'destination_client_id': 10,
                            },
                        },
                        {
                            'alias': 'MY_SERVICE_2',
                            'name': 'MY_SERVICE_NAME_2',
                            'ctype': 'PRODUCTION',
                            'server': 'lb.server.yandex',
                            'topics_dir': '/topics/my_service_2',
                            'tvm': {
                                'destination_alias': 'ALIAS_2',
                                'destination_client_id': 20,
                            },
                        },
                    ],
                },
            },
        },
        'testing': {
            'controller': {'http_options': {'port': 9999, 'threads': 1}},
            'telemetry': {'interval': '10m'},
            'server': {
                'search_map': {
                    'ctype': 'TESTING',
                    'dm_host': 'dm_host.yandex',
                    'statica_host': 'statica.yandex',
                    'statica_query': 'query',
                },
                'writer': {
                    'http_options': {'port': 9990, 'threads': 1},
                    'services': [
                        {
                            'alias': 'MY_SERVICE',
                            'name': 'MY_SERVICE_NAME',
                            'ctype': 'TESTING',
                            'server': 'lb.server.yandex',
                            'topics_dir': '/topics/my_service',
                            'tvm': {
                                'destination_alias': 'ALIAS',
                                'destination_client_id': 10,
                            },
                        },
                        {
                            'alias': 'MY_SERVICE_2',
                            'name': 'MY_SERVICE_NAME_2',
                            'ctype': 'TESTING',
                            'server': 'lb.server.yandex',
                            'topics_dir': '/topics/my_service_2',
                            'tvm': {
                                'destination_alias': 'ALIAS_2',
                                'destination_client_id': 20,
                            },
                        },
                    ],
                },
            },
        },
    }
    generate_services_and_libraries(
        default_repository, 'test_saas_push/test_services', default_base,
    )
