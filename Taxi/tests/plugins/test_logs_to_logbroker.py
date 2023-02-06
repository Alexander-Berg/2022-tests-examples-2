import os

import yaml


def test_logs_to_logbroker_units(generate_service, load_yaml):
    generate_service(
        'test_service_package',
        service_plugins_cfg={
            'python_service': {'service_name': 'test-service'},
            'logs-to-logbroker': {
                'enable': True,
                'environments': {
                    'production': True,
                    'testing': True,
                    'unstable': False,
                },
            },
            'docker-deploy': {},
            'clownductor_service_info': {
                'clownductor_project': 'taxi-infra',
                'preset': {'production': {'name': 'x2nano'}},
                'design_review': 'http://a.b',
                'description': 'privet',
            },
            'units': [
                {
                    'name': 'web',
                    'web': {
                        'description': 'web module',
                        'hostname': {
                            'production': ['app.azaza.ru'],
                            'testing': ['app.test.azaza.ru'],
                        },
                        'num_procs': 1,
                    },
                    'debian': {
                        'binary_package_name': 'yandex-taxi-some-service-web',
                    },
                },
                {
                    'name': 'cron',
                    'cron': {
                        'description': 'cron module',
                        'tasks': [
                            {
                                'module': 'cron.module_1',
                                'settings': {
                                    'production': {'launch_at': '* * * * * *'},
                                },
                            },
                        ],
                    },
                    'debian': {
                        'binary_package_name': 'yandex-taxi-some-service-cron',
                    },
                    'logs-to-logbroker': {
                        'environments': {
                            'unstable': {
                                'enable': True,
                                'topic': 'taxi/cron-unstable-custom-topic',
                            },
                        },
                    },
                },
                {
                    'name': 'stq3',
                    'stq-worker': {'description': 'stq3 module', 'queues': []},
                    'debian': {
                        'binary_package_name': 'yandex-taxi-some-service-stq3',
                    },
                    'logs-to-logbroker': {
                        'environments': {'testing': {'enable': False}},
                    },
                },
            ],
        },
    )
    gen_dir = 'generated/services/test-service/push-client'

    def cmp_yaml_files(path1, path2):
        with open(path1) as file:
            file_1 = yaml.safe_load(file)
        file_2 = load_yaml(path2)
        assert file_1 == file_2

    filenames_to_cmp = [
        'logbroker.yaml',
        'push-client-cron.production.logbroker.yandex.net.yaml',
        'push-client-cron.testing.logbroker.yandex.net.yaml',
        'push-client-cron.unstable.logbroker.yandex.net.yaml',
        'push-client-stq3.production.logbroker.yandex.net.yaml',
        'push-client-stq3.testing.logbroker.yandex.net.yaml',
        'push-client-stq3.unstable.logbroker.yandex.net.yaml',
        'push-client-web.production.logbroker.yandex.net.yaml',
        'push-client-web.testing.logbroker.yandex.net.yaml',
        'push-client-web.unstable.logbroker.yandex.net.yaml',
    ]

    for filename in filenames_to_cmp:
        cmp_yaml_files(f'{gen_dir}/{filename}', filename)


def test_no_addditional_configs(generate_service, load_yaml):
    generate_service(
        'test_service_package',
        service_plugins_cfg={
            'python_service': {'service_name': 'test-service-2'},
            'docker-deploy': {},
            'clownductor_service_info': {
                'clownductor_project': 'taxi-infra',
                'preset': {'production': {'name': 'x2nano'}},
                'design_review': 'http://a.b',
                'description': 'privet',
            },
            'units': [
                {
                    'name': 'web',
                    'web': {
                        'description': 'web module',
                        'hostname': {
                            'production': ['app.azaza.ru'],
                            'testing': ['app.test.azaza.ru'],
                        },
                        'num_procs': 1,
                    },
                    'debian': {
                        'binary_package_name': 'yandex-taxi-some-service-web',
                    },
                },
                {
                    'name': 'cron',
                    'cron': {
                        'description': 'cron module',
                        'tasks': [
                            {
                                'module': 'cron.module_1',
                                'settings': {
                                    'production': {'launch_at': '* * * * * *'},
                                },
                            },
                        ],
                    },
                    'debian': {
                        'binary_package_name': 'yandex-taxi-some-service-cron',
                    },
                },
                {
                    'name': 'stq3',
                    'stq-worker': {'description': 'stq3 module', 'queues': []},
                    'debian': {
                        'binary_package_name': 'yandex-taxi-some-service-stq3',
                    },
                },
            ],
        },
    )
    # no push-client directory and other
    assert os.listdir('generated/services/test-service-2') == ['configs']
