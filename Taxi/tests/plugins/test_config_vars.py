def test_config_vars(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['config-vars'] = {
        'config-vars': {
            'production': {'b': '1', 'a': 2, 'c': 3},
            'testing': {'tst': 'tt'},
            'unstable': {'asdfasdf': 666},
        },
    }

    default_repository.update(
        {
            'services/test-service/configs/config_vars.user.default.yaml': {
                'ss': 'yys',
                'b': 3,
            },
            'services/test-service/configs/config.user.yaml': {
                'components_manager': {
                    'components': {'bla': {'something': '$b', 'other': '$ss'}},
                },
            },
        },
    )
    generate_services_and_libraries(
        default_repository, 'test_config_vars/config_vars', default_base,
    )


def test_config_vars_additional_environments(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['config-vars'] = {
        'config-vars': {'production': {'a': 11}},
        'extra-environments': ['qa'],
    }
    default_repository.update(
        {
            'services/test-service/configs/config_vars.user.qa.yaml': {
                'b': 33,
                'd': 4,
            },
            'services/test-service/configs/config.user.yaml': {
                'components_manager': {
                    'components': {'bla': {'something': '$b', 'other': '$d'}},
                },
            },
        },
    )
    generate_services_and_libraries(
        default_repository,
        'test_config_vars/config_vars_additional_environments',
        default_base,
    )


def test_config_vars_with_rtc(
        generate_services_and_libraries, default_repository, default_base,
):
    repo = default_repository['services/test-service/service.yaml']
    repo['docker-deploy'] = {'skynet-enabled': True}
    generate_services_and_libraries(
        default_repository,
        'test_config_vars/config_vars_docker',
        default_base,
    )


def test_units_config_vars(
        generate_services_and_libraries,
        multi_unit_repository,
        multi_unit_base,
):
    multi_unit_repository.update(
        {
            'services/test-service/configs/first-unit/'
            'config_vars.user.testsuite.yaml': {'ss': 'yys1', 'a': 1},
            'services/test-service/configs/second-unit/'
            'config_vars.user.testsuite.yaml': {'ss': 'yys2', 'b': 1},
            'services/test-service/configs/first-unit/config.user.yaml': {
                'components_manager': {
                    'components': {'bla': {'other': '$ss', 'otherx': '$a'}},
                },
            },
            'services/test-service/configs/second-unit/config.user.yaml': {
                'components_manager': {
                    'components': {
                        'bla': {'something': '$b', 'otherx': '$ss'},
                    },
                },
            },
        },
    )
    generate_services_and_libraries(
        multi_unit_repository,
        'test_config_vars/units_config_vars',
        multi_unit_base,
    )


def test_units_common_config_vars(
        generate_services_and_libraries,
        multi_unit_repository,
        multi_unit_base,
):
    multi_unit_repository.update(
        {
            'services/test-service/configs/shared_configs/'
            'config_vars.user.default.yaml': {'ss': 'yys1', 'a': 1},
            'services/test-service/configs/second-unit/'
            'config_vars.user.default.yaml': {'ss': 'yys2', 'b': 1},
            'services/test-service/configs/shared_configs/config.user.yaml': {
                'components_manager': {
                    'components': {'bla': {'other': '$ss', 'otherx': '$a'}},
                },
            },
            'services/test-service/configs/second-unit/config.user.yaml': {
                'components_manager': {
                    'components': {
                        'bla': {'something': '$b', 'otherx': '$ss'},
                    },
                },
            },
        },
    )
    generate_services_and_libraries(
        multi_unit_repository,
        'test_config_vars/units_common_config_vars',
        multi_unit_base,
    )
