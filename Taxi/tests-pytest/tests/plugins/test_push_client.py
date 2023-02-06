def test_push_client(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['push-client'] = {
        'files': {
            'production': [
                {'name': 'filename3', 'topic': 'taxi/topic3'},
                {'name': 'filename1', 'topic': 'taxi/topic1'},
                {'name': 'filename2', 'topic': 'taxi/topic2'},
            ],
        },
        'compatibility_primary_host': None,
    }
    generate_services_and_libraries(
        default_repository, 'test_push_client/test', default_base,
    )


def test_push_client_multiple_environments(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['push-client'] = {
        'files': {
            'production': [
                {'name': 'filename3', 'topic': 'taxi/topic3'},
                {'name': 'filename1', 'topic': 'taxi/topic1'},
                {'name': 'filename2', 'topic': 'taxi/topic2'},
            ],
            'testing': [
                {'name': 'filename3', 'topic': 'taxi/log_testing_type3'},
                {'name': 'filename1', 'topic': 'taxi/log_testing_type1'},
                {'name': 'filename2', 'topic': 'taxi/log_testing_type2'},
            ],
            'unstable': [
                {'name': 'filename3', 'topic': 'taxi/log_unstable_type3'},
                {'name': 'filename1', 'topic': 'taxi/log_unstable_type1'},
                {'name': 'filename2', 'topic': 'taxi/log_unstable_type2'},
            ],
        },
        'compatibility_primary_host': None,
    }
    generate_services_and_libraries(
        default_repository,
        'test_push_client/test_multiple_environments',
        default_base,
    )


def test_push_client_multiple_installations_legacy(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['push-client'] = {
        'files': {
            'production': [
                {
                    'name': 'filename3',
                    'topic': 'taxi/topic3',
                    'host': 'lbkx.logbroker.yandex.net',
                },
                {
                    'name': 'filename1',
                    'topic': 'taxi/topic1',
                    'host': 'logbroker.yandex.net',
                },
                {'name': 'filename2', 'topic': 'taxi/topic2'},
            ],
            'testing': [
                {
                    'name': 'filename3',
                    'topic': 'taxi/log_testing_type3',
                    'host': 'lbkx.logbroker.yandex.net',
                },
                {
                    'name': 'filename1',
                    'topic': 'taxi/log_testing_type1',
                    'host': 'logbroker.yandex.net',
                },
                {'name': 'filename2', 'topic': 'taxi/log_testing_type2'},
            ],
            'unstable': [
                {
                    'name': 'filename3',
                    'topic': 'taxi/log_unstable_type3',
                    'host': 'lbkx.logbroker.yandex.net',
                },
                {
                    'name': 'filename1',
                    'topic': 'taxi/log_unstable_type1',
                    'host': 'logbroker.yandex.net',
                },
                {'name': 'filename2', 'topic': 'taxi/log_unstable_type2'},
            ],
        },
        'compatibility_primary_host': 'logbroker.yandex.net',
    }
    generate_services_and_libraries(
        default_repository,
        'test_push_client/test_multiple_installations_legacy',
        default_base,
    )


def test_push_client_multiple_installations(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['push-client'] = {
        'files': {
            'production': [
                {
                    'name': 'filename3',
                    'topic': 'taxi/topic3',
                    'host': 'lbkx.logbroker.yandex.net',
                },
                {
                    'name': 'filename1',
                    'topic': 'taxi/topic1',
                    'host': 'logbroker.yandex.net',
                },
                {'name': 'filename2', 'topic': 'taxi/topic2'},
            ],
            'testing': [
                {
                    'name': 'filename3',
                    'topic': 'taxi/log_testing_type3',
                    'host': 'lbkx.logbroker.yandex.net',
                },
                {
                    'name': 'filename1',
                    'topic': 'taxi/log_testing_type1',
                    'host': 'logbroker.yandex.net',
                },
                {'name': 'filename2', 'topic': 'taxi/log_testing_type2'},
            ],
            'unstable': [
                {
                    'name': 'filename3',
                    'topic': 'taxi/log_unstable_type3',
                    'host': 'lbkx.logbroker.yandex.net',
                },
                {
                    'name': 'filename1',
                    'topic': 'taxi/log_unstable_type1',
                    'host': 'logbroker.yandex.net',
                },
                {'name': 'filename2', 'topic': 'taxi/log_unstable_type2'},
            ],
        },
    }
    generate_services_and_libraries(
        default_repository,
        'test_push_client/test_multiple_installations',
        default_base,
    )


def test_push_client_logrotate(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['push-client'] = {
        'files': {
            'production': [
                {
                    'name': 'filename3',
                    'topic': 'taxi/topic3',
                    'logrotate': False,
                },
                {
                    'name': 'filename1',
                    'topic': 'taxi/topic1',
                    'logrotate': True,
                },
                {'name': 'filename2', 'topic': 'taxi/topic2'},
            ],
        },
        'compatibility_primary_host': 'logbroker.yandex.net',
    }
    generate_services_and_libraries(
        default_repository, 'test_push_client/test_logrotate', default_base,
    )


def test_push_client_logrotate_multi_unit(
        generate_services_and_libraries,
        multi_unit_repository,
        multi_unit_base,
):
    multi_unit_repository['services/test-service/service.yaml']['units'][0][
        'push-client'
    ] = (
        {
            'files': {
                'production': [
                    {
                        'name': 'filename3_first_unit',
                        'topic': 'taxi/topic3_first_unit',
                        'logrotate': False,
                    },
                    {
                        'name': 'filename1_first_unit',
                        'topic': 'taxi/topic1_first_unit',
                        'logrotate': True,
                    },
                    {
                        'name': 'filename2_first_unit',
                        'topic': 'taxi/topic2_first_unit',
                    },
                ],
            },
            'compatibility_primary_host': None,
        }
    )
    multi_unit_repository['services/test-service/service.yaml']['units'][1][
        'push-client'
    ] = (
        {
            'files': {
                'production': [
                    {
                        'name': 'filename3_second_unit',
                        'topic': 'taxi/topic3_second_unit',
                        'logrotate': False,
                    },
                    {
                        'name': 'filename1_second_unit',
                        'topic': 'taxi/topic1_second_unit',
                        'logrotate': True,
                    },
                    {
                        'name': 'filename2_second_unit',
                        'topic': 'taxi/topic2_second_unit',
                    },
                ],
            },
            'compatibility_primary_host': None,
        }
    )
    generate_services_and_libraries(
        multi_unit_repository,
        'test_push_client/test_logrotate_multi_unit',
        multi_unit_base,
    )


def test_partition_groups(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['push-client'] = {
        'files': {
            'production': [
                {
                    'name_prefix': 'filename4',
                    'topic': 'taxi/topic4',
                    'partition_groups': 2,
                },
            ],
        },
        'compatibility_primary_host': None,
    }
    generate_services_and_libraries(
        default_repository, 'test_push_client/partition_groups', default_base,
    )


def test_push_client_clownductor_aliases(
        generate_services_and_libraries,
        multi_unit_repository,
        multi_unit_base,
):
    service_yaml = multi_unit_repository['services/test-service/service.yaml']
    service_yaml['clownductor_service_info'] = {
        'service': {
            'name': 'first_unit_service',
            'clownductor_project': 'some_project',
            'preset': {'production': {'name': 'x2nano'}},
            'design_review': 'http://a.b',
        },
        'aliases': [{'name': 'second_unit_service'}],
    }
    service_yaml['docker-deploy'] = {}
    service_yaml['units'][0]['push-client'] = {
        'files': {
            'production': [
                {
                    'name': 'filename3_first_unit',
                    'topic': 'taxi/topic3_first_unit',
                    'logrotate': False,
                },
                {
                    'name': 'filename1_first_unit',
                    'topic': 'taxi/topic1_first_unit',
                    'logrotate': True,
                },
                {
                    'name': 'filename2_first_unit',
                    'topic': 'taxi/topic2_first_unit',
                },
            ],
        },
        'compatibility_primary_host': None,
    }
    service_yaml['units'][0]['docker-deploy'] = {
        'clownductor-service': 'first_unit_service',
    }
    service_yaml['units'][1]['push-client'] = {
        'files': {
            'production': [
                {
                    'name': 'filename3_second_unit',
                    'topic': 'taxi/topic3_second_unit',
                    'logrotate': False,
                },
                {
                    'name': 'filename1_second_unit',
                    'topic': 'taxi/topic1_second_unit',
                    'logrotate': True,
                },
                {
                    'name': 'filename2_second_unit',
                    'topic': 'taxi/topic2_second_unit',
                },
            ],
        },
        'compatibility_primary_host': None,
    }
    service_yaml['units'][1]['docker-deploy'] = {
        'clownductor-service': 'second_unit_service',
    }

    generate_services_and_libraries(
        multi_unit_repository,
        'test_push_client/test_clownductor_aliases',
        multi_unit_base,
    )
