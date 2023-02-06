import pytest

import codegen.plugin_manager as plugin_manager


class DockerDeployMock:
    name = 'docker-deploy'
    scope = 'unit'
    depends = ['push-client-logbroker-config']

    def __init__(self):
        self._clownductor_service = None

    def activate(self, config):
        self._clownductor_service = config['clownductor-service']

    def configure(self, manager: plugin_manager.ConfigureManager):
        if self._clownductor_service is None:
            return

        manager.activate(
            'push-client-logbroker-config',
            {'clownductor-service': self._clownductor_service},
        )


@pytest.mark.parametrize(
    'units, test_data_path',
    [
        (
            {
                'test-service': {
                    'push-client': {
                        'files': {
                            'production': [
                                {'name': 'filename3', 'topic': 'taxi/topic3'},
                                {'name': 'filename1', 'topic': 'taxi/topic1'},
                                {'name': 'filename2', 'topic': 'taxi/topic2'},
                            ],
                        },
                        'compatibility_primary_host': None,
                    },
                    'debian': {'binary_package_name': 'package-name'},
                },
            },
            'test_push_client/test',
        ),
        (
            {
                'test-service': {
                    'debian': {'binary_package_name': 'package-name'},
                    'push-client': {
                        'files': {
                            'production': [
                                {'name': 'filename3', 'topic': 'taxi/topic3'},
                                {'name': 'filename1', 'topic': 'taxi/topic1'},
                                {'name': 'filename2', 'topic': 'taxi/topic2'},
                            ],
                            'testing': [
                                {
                                    'name': 'filename3',
                                    'topic': 'taxi/log_testing_type3',
                                },
                                {
                                    'name': 'filename1',
                                    'topic': 'taxi/log_testing_type1',
                                },
                                {
                                    'name': 'filename2',
                                    'topic': 'taxi/log_testing_type2',
                                },
                            ],
                            'unstable': [
                                {
                                    'name': 'filename3',
                                    'topic': 'taxi/log_unstable_type3',
                                },
                                {
                                    'name': 'filename1',
                                    'topic': 'taxi/log_unstable_type1',
                                },
                                {
                                    'name': 'filename2',
                                    'topic': 'taxi/log_unstable_type2',
                                },
                            ],
                        },
                        'compatibility_primary_host': None,
                    },
                },
            },
            'test_push_client/test_multiple_environments',
        ),
        (
            {
                'test-service': {
                    'debian': {'binary_package_name': 'package-name'},
                    'push-client': {
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
                                {
                                    'name': 'filename2',
                                    'topic': 'taxi/log_testing_type2',
                                },
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
                                {
                                    'name': 'filename2',
                                    'topic': 'taxi/log_unstable_type2',
                                },
                            ],
                        },
                        'compatibility_primary_host': 'logbroker.yandex.net',
                    },
                },
            },
            'test_push_client/test_multiple_installations_legacy',
        ),
        (
            {
                'test-service': {
                    'debian': {'binary_package_name': 'package-name'},
                    'push-client': {
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
                                {
                                    'name': 'filename2',
                                    'topic': 'taxi/log_testing_type2',
                                },
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
                                {
                                    'name': 'filename2',
                                    'topic': 'taxi/log_unstable_type2',
                                },
                            ],
                        },
                    },
                },
            },
            'test_push_client/test_multiple_installations',
        ),
        (
            {
                'test-service': {
                    'debian': {'binary_package_name': 'package-name'},
                    'push-client': {
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
                    },
                },
            },
            'test_push_client/test_logrotate',
        ),
        (
            {
                'first-unit': {
                    'debian': {
                        'binary_package_name': 'yandex-taxi-first-unit',
                    },
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
                },
                'second-unit': {
                    'debian': {
                        'binary_package_name': 'yandex-taxi-second-unit',
                    },
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
                },
            },
            'test_push_client/test_logrotate_multi_unit',
        ),
        (
            {
                'test-service': {
                    'debian': {'binary_package_name': 'package-name'},
                    'push-client': {
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
                    },
                },
            },
            'test_push_client/partition_groups',
        ),
        (
            {
                'first-unit': {
                    'debian': {
                        'binary_package_name': 'yandex-taxi-first-unit',
                    },
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
                    'docker-deploy': {
                        'clownductor-service': 'first_unit_service',
                    },
                },
                'second-unit': {
                    'debian': {
                        'binary_package_name': 'yandex-taxi-second-unit',
                    },
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
                },
            },
            'test_push_client/test_clownductor_aliases',
        ),
        pytest.param(
            {
                'first-unit': {
                    'push-client': {
                        'files': {
                            'production': [
                                {'name': 'filename3', 'topic': 'taxi/topic3'},
                                {'name': 'filename1', 'topic': 'taxi/topic1'},
                                {'name': 'filename2', 'topic': 'taxi/topic2'},
                            ],
                        },
                        'compatibility_primary_host': None,
                    },
                    'debian': {
                        'binary_package_name': 'package-name-first-unit',
                    },
                },
                'second-unit': {
                    'push-client': {
                        'files': {
                            'production': [
                                {'name': 'filename3', 'topic': 'taxi/topic3'},
                                {'name': 'filename1', 'topic': 'taxi/topic1'},
                                {'name': 'filename2', 'topic': 'taxi/topic2'},
                            ],
                        },
                        'compatibility_primary_host': None,
                    },
                    'debian': {
                        'binary_package_name': 'package-name-second-unit',
                    },
                    'docker-deploy': {
                        'clownductor-service': 'second-unit-service',
                    },
                },
            },
            'test_push_client/test_missing_docker_deploy',
        ),
        (
            {
                'test-service': {
                    'push-client': {
                        'logger': {
                            'timeformat': '%Y.%m.%d-%H:%M:%S',
                            'file': (
                                '/var/log/statbox/push-client-test-service.log'
                            ),
                        },
                        'watcher': {
                            'state': '/var/lib/push-client/test-service',
                        },
                        'files': {
                            'production': [
                                {
                                    'name': 'filename3',
                                    'topic': 'taxi/topic3',
                                    'data_types': ['app_logs'],
                                },
                                {
                                    'name': 'filename1',
                                    'topic': 'taxi/topic1',
                                    'data_types': ['traces', 'extra'],
                                },
                                {'name': 'filename2', 'topic': 'taxi/topic2'},
                            ],
                        },
                        'compatibility_primary_host': None,
                    },
                    'debian': {'binary_package_name': 'package-name'},
                },
            },
            'test_push_client/test_custom_fields',
        ),
        (
            {
                'test-service': {
                    'push-client': {
                        'files': {
                            'production': [
                                {
                                    'name': 'filename1',
                                    'topic': 'taxi/topic1',
                                    'data_types': ['app_logs'],
                                },
                                {
                                    'name': 'filename1',
                                    'topic': 'taxi/topic1',
                                    'data_types': ['extra'],
                                },
                            ],
                        },
                        'compatibility_primary_host': None,
                    },
                    'debian': {'binary_package_name': 'package-name'},
                },
            },
            'test_push_client/test_content_types_merge',
        ),
    ],
)
def test_simple(
        tmpdir,
        plugin_manager_test,
        base_service,
        dir_comparator,
        units,
        test_data_path,
):
    tmp_dir = tmpdir.mkdir('repo')

    del base_service['debian']['binary_package_name']

    plugin_manager_test(
        tmp_dir, service=base_service, units=units, plugins=[DockerDeployMock],
    )

    dir_comparator(tmp_dir, test_data_path)


@pytest.mark.parametrize(
    'units',
    [
        {
            'test-service': {
                'push-client': {
                    'logger': {'file': ('/wrong/path.log',)},
                    'compatibility_primary_host': None,
                },
                'debian': {'binary_package_name': 'package-name'},
            },
        },
        {
            'test-service': {
                'push-client': {
                    'watcher': {'state': '/wrong/state/path'},
                    'compatibility_primary_host': None,
                },
                'debian': {'binary_package_name': 'package-name'},
            },
        },
    ],
)
def test_error(
        tmpdir, plugin_manager_test, base_service, dir_comparator, units,
):
    tmp_dir = tmpdir.mkdir('repo')

    del base_service['debian']['binary_package_name']

    with pytest.raises(SystemExit):
        plugin_manager_test(
            tmp_dir,
            service=base_service,
            units=units,
            plugins=[DockerDeployMock],
        )
