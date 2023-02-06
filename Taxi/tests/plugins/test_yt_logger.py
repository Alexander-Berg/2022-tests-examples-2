def test_yt_logger(
        generate_services_and_libraries, default_repository, default_base,
):
    path = 'services/test-service/yt-uploads/'
    default_repository.update(
        {
            path
            + 'logger3.yaml': {
                'data_format': 'json',
                'topic': 'taxi/taxi-my-some-very-best-name-3-log',
                'includes': ['core/object.hpp'],
                'logfeller': {
                    'autogenerate': True,
                    'lifetimes': {'1h': '1d', '1d': '36500d'},
                },
                'table_meta': {
                    'attributes': {
                        'schema': [
                            {
                                'description': 'no3',
                                'name': 'value3',
                                'type': 'string',
                                'required_cxx': True,
                            },
                            {
                                'description': 'no1',
                                'name': 'value1',
                                'type': 'uint64',
                                'required_cxx': True,
                            },
                            {
                                'description': 'no2',
                                'name': 'value2',
                                'type': 'double',
                                'required_cxx': True,
                            },
                            {
                                'description': 'no4',
                                'name': 'value4',
                                'cpp_type': 'std::int64_t',
                                'required_cxx': True,
                            },
                            {
                                'description': 'no5',
                                'name': 'value5',
                                'cpp_type': 'std::vector<core::Object>',
                                'required_cxx': True,
                            },
                        ],
                    },
                },
            },
            path
            + 'logger1.yaml': {
                'data_format': 'dsv',
                'logfeller': {'autogenerate': False},
                'topic': 'taxi/taxi-my-some-very-best-name-1-log',
                'table_meta': {
                    'attributes': {
                        'schema': [
                            {
                                'description': 'no',
                                'name': 'bool_value',
                                'type': 'boolean',
                                'required_cxx': False,
                            },
                        ],
                    },
                },
            },
            path
            + 'logger2.yaml': {
                'data_format': 'dsv',
                'topic': 'taxi/taxi-my-some-very-best-name-2-log',
                'logfeller': {'autogenerate': True, 'lifetimes': {'1h': '3d'}},
                'table_meta': {
                    'attributes': {
                        'schema': [
                            {
                                'description': 'no',
                                'name': 'any_value',
                                'type': 'any',
                                'required_cxx': True,
                            },
                        ],
                    },
                },
            },
            path
            + 'logger4.yaml': {
                'data_format': 'dsv',
                'topic': 'taxi/taxi-my-some-very-best-name-4-log',
                'logfeller': {'autogenerate': True, 'lifetimes': {'1h': '3d'}},
                'table_meta': {
                    'attributes': {
                        'schema': [
                            {
                                'description': 'no',
                                'name': 'any_value',
                                'type': 'any',
                                'required_cxx': True,
                            },
                        ],
                    },
                },
                'logrotate': {'maxsize': '543G', 'rotate': 42},
            },
            path
            + 'logger5.yaml': {
                'data_format': 'json',
                'topic': 'taxi/taxi-my-some-very-best-name-5-log',
                'logfeller': {'autogenerate': True, 'lifetimes': {'1h': '3d'}},
                'table_meta': {
                    'attributes': {
                        'schema': [
                            {
                                'description': 'no3',
                                'name': 'value3',
                                'type': 'string',
                                'required_cxx': True,
                            },
                        ],
                    },
                },
                'logrotate': {'maxsize': '42G'},
            },
            path
            + 'logger6.yaml': {
                'data_format': 'json',
                'topic': 'taxi/taxi-my-some-very-best-name-6-log',
                'partition_groups': {
                    'production': 3,
                    'testing': 2,
                    'unstable': 1,
                },
                'logfeller': {'autogenerate': True, 'lifetimes': {'1h': '3d'}},
                'table_meta': {
                    'attributes': {
                        'schema': [
                            {
                                'description': 'no3',
                                'name': 'value3',
                                'type': 'string',
                                'required_cxx': True,
                            },
                        ],
                    },
                },
                'logrotate': {'maxsize': '42G', 'rotate_policy': 'monthly'},
            },
        },
    )
    generate_services_and_libraries(
        default_repository, 'test_yt_logger/test', default_base,
    )


def test_yt_logger_multiple_environments(
        generate_services_and_libraries, default_repository, default_base,
):
    path = 'services/test-service/yt-uploads/'
    default_repository.update(
        {
            path
            + 'logger3.yaml': {
                'data_format': 'dsv',
                'topic': {
                    'production': 'taxi/taxi-my-some-very-best-name-3-log',
                },
                'logfeller': {'autogenerate': False},
                'table_meta': {
                    'attributes': {
                        'schema': [
                            {
                                'description': 'no3',
                                'name': 'value3',
                                'type': 'string',
                                'required_cxx': True,
                            },
                            {
                                'description': 'no1',
                                'name': 'value1',
                                'type': 'uint64',
                                'required_cxx': True,
                            },
                            {
                                'description': 'no2',
                                'name': 'value2',
                                'type': 'double',
                                'required_cxx': True,
                            },
                        ],
                    },
                },
            },
            path
            + 'logger1.yaml': {
                'data_format': 'dsv',
                'topic': {
                    'production': 'taxi/taxi-my-some-very-best-name-1-log',
                    'testing': (
                        'taxi/taxi-my-some-very-best-name-testing-1-log'
                    ),
                    'unstable': (
                        'taxi/taxi-my-some-very-best-name-unstable-1-log'
                    ),
                },
                'logfeller': {'autogenerate': False},
                'table_meta': {
                    'attributes': {
                        'schema': [
                            {
                                'description': 'no',
                                'name': 'bool_value',
                                'type': 'boolean',
                                'required_cxx': False,
                            },
                        ],
                    },
                },
            },
            path
            + 'logger2.yaml': {
                'data_format': 'dsv',
                'topic': 'taxi/taxi-my-some-very-best-name-2-log',
                'logfeller': {'autogenerate': False},
                'table_meta': {
                    'attributes': {
                        'schema': [
                            {
                                'description': 'no',
                                'name': 'bool_value',
                                'type': 'any',
                                'required_cxx': True,
                            },
                        ],
                    },
                },
            },
        },
    )
    generate_services_and_libraries(
        default_repository,
        'test_yt_logger/test_multiple_environments',
        default_base,
    )


def test_yt_logger_library(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository.update(
        {
            'libraries/codegen/yt-uploads/logger2.yaml': {
                'data_format': 'dsv',
                'topic': 'taxi/taxi-my-some-very-best-name-2-log',
                'logfeller': {'autogenerate': False},
                'table_meta': {
                    'attributes': {
                        'schema': [
                            {
                                'description': 'no',
                                'name': 'bool_value',
                                'type': 'any',
                                'required_cxx': True,
                            },
                        ],
                    },
                },
            },
        },
    )
    generate_services_and_libraries(
        default_repository, 'test_yt_logger/library', default_base,
    )


def test_yt_logger_ts_precision_6(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository.update(
        {
            'libraries/codegen/yt-uploads/logger3.yaml': {
                'data_format': 'dsv',
                'timestamp_format': 'ts-with-tz-s6',
                'topic': 'taxi/taxi-my-some-very-best-name-2-log',
                'logfeller': {'autogenerate': False},
                'table_meta': {
                    'attributes': {
                        'schema': [
                            {
                                'description': 'no',
                                'name': 'bool_value',
                                'type': 'any',
                                'required_cxx': True,
                            },
                        ],
                    },
                },
            },
        },
    )
    generate_services_and_libraries(
        default_repository,
        'test_yt_logger/timestamp_precision_6',
        default_base,
    )


def test_yt_logger_several_topics(
        generate_services_and_libraries, default_repository, default_base,
):
    path = 'services/test-service/yt-uploads/'
    default_repository.update(
        {
            path
            + 'logger_sev_tops_1.yaml': {
                'data_format': 'dsv',
                'timestamp_format': 'ts-with-tz-s6',
                'topics': [
                    {
                        'name': 'name1',
                        'topic': {
                            'production': {
                                'path': 'taxi/taxi-sev-tops1-name1-prod-log',
                                'partitions': 3,
                            },
                            'testing': {
                                'path': 'taxi/taxi-sev-tops1-name1-test-log',
                                'partitions': 2,
                            },
                        },
                    },
                    {
                        'name': 'name2',
                        'topic': {
                            'production': {
                                'path': 'taxi/taxi-sev-tops1-name2-prod-log',
                                'partitions': 1,
                            },
                            'testing': {
                                'path': 'taxi/taxi-sev-tops1-name2-test-log',
                                'partitions': 1,
                            },
                        },
                    },
                ],
                'logfeller': {'autogenerate': False},
                'table_meta': {
                    'attributes': {
                        'schema': [
                            {
                                'description': 'no',
                                'name': 'bool_value',
                                'type': 'any',
                                'required_cxx': True,
                            },
                        ],
                    },
                },
            },
            path
            + 'logger_sev_tops_2.yaml': {
                'data_format': 'dsv',
                'timestamp_format': 'ts-with-tz-s6',
                'topics': [
                    {
                        'name': '',
                        'topic': {
                            'production': {
                                'path': 'taxi/taxi-sev-tops2-name-prod-log',
                                'partitions': 1,
                            },
                            'testing': {
                                'path': 'taxi/taxi-sev-tops2-name-test-log',
                                'partitions': 1,
                            },
                        },
                    },
                    {
                        'name': 'name1',
                        'topic': {
                            'production': {
                                'path': 'taxi/taxi-sev-tops2-name1-prod-log',
                                'partitions': 1,
                            },
                            'testing': {
                                'path': 'taxi/taxi-sev-tops2-name1-test-log',
                                'partitions': 1,
                            },
                        },
                    },
                ],
                'logfeller': {'autogenerate': False},
                'table_meta': {
                    'attributes': {
                        'schema': [
                            {
                                'description': 'no',
                                'name': 'bool_value',
                                'type': 'any',
                                'required_cxx': True,
                            },
                        ],
                    },
                },
            },
            path
            + 'logger_sev_tops_3.yaml': {
                'data_format': 'dsv',
                'timestamp_format': 'ts-with-tz-s6',
                'topics': [
                    {
                        'name': '',
                        'topic': {
                            'production': {
                                'path': 'taxi/taxi-sev-tops3-name-prod-log',
                                'partitions': 1,
                            },
                            'testing': {
                                'path': 'taxi/taxi-sev-tops3-name-test-log',
                                'partitions': 1,
                            },
                        },
                    },
                ],
                'logfeller': {'autogenerate': False},
                'table_meta': {
                    'attributes': {
                        'schema': [
                            {
                                'description': 'no',
                                'name': 'bool_value',
                                'type': 'any',
                                'required_cxx': True,
                            },
                        ],
                    },
                },
            },
        },
    )
    generate_services_and_libraries(
        default_repository, 'test_yt_logger/sev_topics_test', default_base,
    )


def test_yt_logger_overflow_behaviour(
        generate_services_and_libraries, default_repository, default_base,
):
    path = 'services/test-service/yt-uploads/'
    default_repository.update(
        {
            path
            + 'logger_sev_tops_1.yaml': {
                'data_format': 'dsv',
                'timestamp_format': 'ts-with-tz-s6',
                'topics': [
                    {
                        'name': 'name1',
                        'overflow_behavior': '$some_var',
                        'topic': {
                            'production': {
                                'path': 'taxi/taxi-sev-tops1-name1-prod-log',
                                'partitions': 3,
                            },
                            'testing': {
                                'path': 'taxi/taxi-sev-tops1-name1-test-log',
                                'partitions': 2,
                            },
                        },
                    },
                    {
                        'name': 'name2',
                        'topic': {
                            'production': {
                                'path': 'taxi/taxi-sev-tops1-name2-prod-log',
                                'partitions': 1,
                            },
                            'testing': {
                                'path': 'taxi/taxi-sev-tops1-name2-test-log',
                                'partitions': 1,
                            },
                        },
                    },
                ],
                'logfeller': {'autogenerate': False},
                'table_meta': {
                    'attributes': {
                        'schema': [
                            {
                                'description': 'no',
                                'name': 'bool_value',
                                'type': 'any',
                                'required_cxx': True,
                            },
                        ],
                    },
                },
            },
        },
    )
    generate_services_and_libraries(
        default_repository,
        'test_yt_logger/overflow_behaviour_topics_test',
        default_base,
    )
