def test_config_yaml(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['config-yaml'] = {
        'config_part': {'components_manager': {'components': {'c1': 'data'}}},
    }
    generate_services_and_libraries(
        default_repository, 'test_config_yaml/config_yaml', default_base,
    )


def test_units_common_config_yaml(
        generate_services_and_libraries,
        multi_unit_repository,
        multi_unit_base,
):
    multi_unit_repository.update(
        {
            'services/test-service/configs/shared_configs/'
            'config.user.yaml': {
                'components_manager': {'components': {'c1': 'data1'}},
            },
            'services/test-service/configs/second-unit/config.user.yaml': {
                'components_manager': {'components': {'c2': 'data2'}},
            },
        },
    )
    generate_services_and_libraries(
        multi_unit_repository,
        'test_config_yaml/units_common_config_yaml',
        multi_unit_base,
    )
