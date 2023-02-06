def test_default(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['main'] = {}
    generate_services_and_libraries(default_repository, default_base)


def test_plugin(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['main'] = {
        'components': [
            ('component3_1', 'components3_2'),
            ('component1_1', 'components1_2'),
            ('component2_1', 'components2_2'),
        ],
        'component_lists': ['cl3', 'cl1', 'cl2'],
        'includes': ['inc3', 'inc1', 'inc2'],
    }
    generate_services_and_libraries(
        default_repository, 'test_main/plugin', default_base,
    )
