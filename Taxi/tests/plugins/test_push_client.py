import yaml


def test_push_client_clownductor_aliases(generate_service, load_yaml):
    generate_service(
        'test_service_package',
        service_plugins_cfg={
            'docker-deploy': {},
            'clownductor_service_info': {
                'service': {
                    'name': 'first_unit_service',
                    'clownductor_project': 'some_project',
                    'preset': {'production': {'name': 'x2nano'}},
                    'design_review': 'http://a.b',
                    'description': 'privet',
                },
                'aliases': [
                    {'name': 'second_unit_service', 'description': 'privet'},
                ],
            },
            'units': [
                {
                    'name': 'first_unit',
                    'web': {
                        'description': 'Client user app',
                        'log_ident': 'yandex-taxi-some-project-first-unit',
                        'hostname': {
                            'production': ['app.azaza.ru'],
                            'testing': ['app.test.azaza.ru'],
                        },
                        'num_procs': 1,
                    },
                },
                {
                    'name': 'second_unit',
                    'web': {
                        'description': 'Client user app',
                        'log_ident': 'yandex-taxi-some-project-second-unit',
                        'hostname': {
                            'production': ['app.azaza.ru'],
                            'testing': ['app.test.azaza.ru'],
                        },
                        'num_procs': 1,
                    },
                },
            ],
        },
        unit_plugins_cfg_by_unit_name={
            'first_unit': {
                'push-client': {
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
                },
                'docker-deploy': {'clownductor-service': 'first_unit_service'},
                'debian': {
                    'binary_package_name': (
                        'yandex-taxi-some-project-first-unit'
                    ),
                },
            },
            'second_unit': {
                'push-client': {
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
                },
                'docker-deploy': {
                    'clownductor-service': 'second_unit_service',
                },
                'debian': {
                    'binary_package_name': (
                        'yandex-taxi-some-project-second-unit'
                    ),
                },
            },
        },
    )

    with open(
            'generated/services/some-project/push-client/logbroker.yaml',
    ) as infile:
        lb_config = yaml.safe_load(infile)

    assert lb_config == load_yaml('exp_lb_config_clownductor_aliases.yaml')
