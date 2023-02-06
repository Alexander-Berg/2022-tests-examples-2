def test_cache(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['cache'] = {
        'dir': '/home/service/cache/dir',
        'monrun': False,
        'debian-prerm-script-enabled': True,
    }
    generate_services_and_libraries(
        default_repository, 'test_cache/cache', default_base,
    )


def test_monrun(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['cache'] = {
        'monrun': {'config': 'MONRUN_CONFIG'},
    }
    config_content = {
        'default': {'be': 'ru'},
        'description': 'Маппинг локалей (например, использовать ru вместо be)',
        'schema': {
            'type': 'object',
            'additionalProperties': {'type': 'string'},
        },
    }

    default_repository[
        (
            '../schemas/schemas/configs/declarations/locales/'
            'MONRUN_CONFIG.yaml'
        )
    ] = config_content
    generate_services_and_libraries(
        default_repository, 'test_cache/monrun', default_base,
    )
