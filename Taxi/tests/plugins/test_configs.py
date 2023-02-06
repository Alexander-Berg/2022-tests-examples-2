def test_configs(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository[
        '../schemas/schemas/configs/declarations/locales/LOCALES_MAPPING.yaml'
    ] = (
        {
            'default': {'be': 'ru'},
            'description': (
                'Маппинг локалей (например, использовать ru вместо be)'
            ),
            'schema': {
                'type': 'object',
                'additionalProperties': {'type': 'string'},
            },
        }
    )
    default_repository[
        (
            '../schemas/schemas/configs/declarations/locales/'
            'LOCALES_SUPPORTED.yaml'
        )
    ] = (
        {
            'default': ['ru', 'en', 'hy', 'ka', 'kk', 'uk', 'az'],
            'description': 'Поддерживаемые локали',
            'schema': {'type': 'array', 'items': {'type': 'string'}},
        }
    )
    default_repository[
        '../schemas/schemas/configs/declarations/sample/REF.yaml'
    ] = (
        {
            'default': {},
            'description': 'external reference',
            'schema': {'$ref': 'common/ref.yaml#/Obj'},
        }
    )
    default_repository[
        '../schemas/schemas/configs/definitions/common/ref.yaml'
    ] = (
        {
            'Obj': {
                'type': 'object',
                'additionalProperties': True,
                'x-taxi-additional-properties-true-reason': 'because i can',
                'properties': {},
            },
        }
    )
    default_repository['services/test-service/service.yaml']['configs'] = {
        'names': ['LOCALES_MAPPING', 'LOCALES_SUPPORTED', 'REF'],
    }
    generate_services_and_libraries(
        default_repository, 'test_configs/configs', default_base,
    )


def test_oneof_with_discriminator(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository[
        '../schemas/schemas/configs/definitions/dir/file.yaml'
    ] = (
        {
            'Def2': {
                'type': 'object',
                'additionalProperties': False,
                'properties': {'type': {'type': 'string'}},
            },
            'Def': {
                'type': 'object',
                'additionalProperties': False,
                'properties': {'type': {'type': 'string'}},
            },
        }
    )
    default_repository[
        '../schemas/schemas/configs/declarations/some/CONFIG.yaml'
    ] = (
        {
            'default': {'be': 'ru'},
            'description': (
                'Маппинг локалей (например, использовать ru вместо be)'
            ),
            'schema': {
                'type': 'string',
                'definitions': {
                    'OneOfWithDiscriminator': {
                        'oneOf': [
                            {'$ref': 'dir/file.yaml#/Def'},
                            {'$ref': 'dir/file.yaml#/Def2'},
                        ],
                        'discriminator': {
                            'propertyName': 'type',
                            'mapping': {
                                'def': 'dir/file.yaml#/Def',
                                'def2': 'dir/file.yaml#/Def2',
                            },
                        },
                    },
                },
            },
        }
    )
    default_repository['services/test-service/service.yaml']['configs'] = {
        'names': ['CONFIG'],
    }
    generate_services_and_libraries(
        default_repository,
        'test_configs/oneof_with_discriminator',
        default_base,
    )
