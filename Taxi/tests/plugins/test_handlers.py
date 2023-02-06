def test_definitions(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/docs/yaml/definitions.yaml'] = {
        'definitions': {'Extra': {'type': 'string'}},
    }
    default_repository['services/test-service/docs/yaml/api/api.yaml'][
        'definitions'
    ]['Response'] = (
        {
            'type': 'object',
            'additionalProperties': False,
            'properties': {
                'property': {
                    '$ref': 'test-service/definitions.yaml#/definitions/Extra',
                },
            },
        }
    )
    generate_services_and_libraries(
        default_repository, 'test_handlers/definitions', default_base,
    )


def test_non_verbose_parse_error_message(
        generate_services_and_libraries, default_repository, default_base,
):
    openapi = default_repository[
        'services/test-service/docs/yaml/api/openapi.yaml'
    ]
    operations_openapi = openapi['paths']

    operations_openapi['/handler'] = {
        'post': {
            'description': 'smth',
            'requestBody': {
                'required': True,
                'content': {
                    'application/flatbuffer': {'schema': {'type': 'string'}},
                },
            },
            'responses': {'200': {'description': 'OK'}},
        },
    }

    default_repository['services/test-service/service.yaml']['handlers'] = {
        'verbose-parse-error-messages': False,
    }

    generate_services_and_libraries(
        default_repository,
        'test_handlers/non_verbose_parse_error_message',
        default_base,
    )


def test_library_definitions(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/docs/yaml/api/api.yaml'][
        'definitions'
    ]['Response'] = {'$ref': 'new-lib/definitions.yaml#/definitions/NewExtra'}
    default_repository.update(
        {
            'libraries/new-lib/library.yaml': {
                'maintainers': ['u'],
                'description': 's',
                'project-name': 'yandex-taxi-library-new-lib',
            },
            'libraries/new-lib/docs/yaml/definitions.yaml': {
                'definitions': {
                    'NewExtra': {
                        'x-internal': True,
                        'type': 'object',
                        'additionalProperties': False,
                        'properties': {'new-extra-param': {'type': 'string'}},
                    },
                },
            },
        },
    )
    default_repository['services/test-service/service.yaml']['libraries'] = [
        'yandex-taxi-library-new-lib',
    ]
    generate_services_and_libraries(
        default_repository, 'test_handlers/library_definitions', default_base,
    )


def test_library_injection(
        generate_services_and_libraries, default_repository, default_base,
):
    retrieval = (
        'context.FindComponent<test_libraryname::Component>().GetClient()'
    )
    default_repository.update(
        {
            'libraries/new-lib/library.yaml': {
                'maintainers': ['u'],
                'description': 's',
                'project-name': 'yandex-taxi-library-new-lib',
                'dependencies': {
                    'injections': [
                        {
                            'name': 'test_libraryname_variable',
                            'include-fwd': 'test_libraryname/client_fwd.hpp',
                            'include': 'test_libraryname/component.hpp',
                            'type': 'test_libraryname::Client',
                            'init': retrieval,
                            'get': 'test_libraryname_variable_.Get()',
                        },
                    ],
                },
            },
        },
    )
    default_repository['services/test-service/docs/yaml/api/api.yaml'][
        'definitions'
    ]['Response'] = (
        {
            'type': 'object',
            'additionalProperties': False,
            'properties': {'property': {'type': 'string'}},
        }
    )
    default_repository['services/test-service/service.yaml']['libraries'] = [
        'yandex-taxi-library-new-lib',
    ]
    generate_services_and_libraries(
        default_repository, 'test_handlers/library_inject', default_base,
    )


def test_non_utf8_logging(
        generate_services_and_libraries, default_repository, default_base,
):
    operations_swagger = default_repository[
        'services/test-service/docs/yaml/api/api.yaml'
    ]['paths']

    operations_swagger['/swagger/flatbuffer'] = {
        'post': {
            'description': 'generate flatbuffer logging',
            'consumes': ['application/flatbuffer'],
            'produces': ['application/flatbuffer'],
            'responses': {
                '200': {'description': 'OK', 'schema': {'type': 'string'}},
                '201': {
                    'x-taxi-non-std-type-reason': 'for tests',
                    'description': 'OK',
                },
                '400': {
                    'x-taxi-non-std-type-reason': 'for tests',
                    'description': 'OK',
                },
            },
        },
    }
    operations_swagger['/swagger/protobuffer'] = {
        'post': {
            'description': 'generate protobuffer logging',
            'consumes': ['application/protobuf'],
            'produces': ['application/protobuf'],
            'responses': {
                '200': {'description': 'OK', 'schema': {'type': 'string'}},
            },
        },
    }
    operations_swagger['/swagger/flatbuffer-and-protobuffer'] = {
        'post': {
            'description': 'generate flatbuffer and protobuffer logging',
            'consumes': ['application/flatbuffer', 'application/protobuf'],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        'type': 'object',
                        'additionalProperties': False,
                        'properties': {},
                    },
                },
            },
        },
    }

    openapi = default_repository[
        'services/test-service/docs/yaml/api/openapi.yaml'
    ]
    operations_openapi = openapi['paths']

    operations_openapi['/openapi/flatbuffer'] = {
        'post': {
            'description': 'generate flatbuffer logging',
            'parameters': [
                {
                    'in': 'query',
                    'name': 'param',
                    'schema': {'type': 'integer'},
                    'required': True,
                    'x-taxi-handler-tag': 'tag-name',
                },
                {
                    'in': 'query',
                    'name': 'param2',
                    'schema': {'$ref': '#/components/schemas/Param2'},
                    'required': False,
                    'x-taxi-handler-tag': 'tag-name2',
                },
            ],
            'requestBody': {
                'required': True,
                'content': {
                    'application/flatbuffer': {'schema': {'type': 'string'}},
                },
            },
            'responses': {
                '200': {
                    'description': 'OK',
                    'content': {
                        'application/flatbuffer': {
                            'schema': {'type': 'string'},
                        },
                    },
                },
                '201': {'description': 'OK'},
                '400': {'description': 'invalid input'},
            },
        },
    }
    operations_openapi['/openapi/protobuffer'] = {
        'post': {
            'description': 'generate protobuffer logging',
            'requestBody': {
                'required': True,
                'content': {
                    'application/protobuf': {'schema': {'type': 'string'}},
                },
            },
            'responses': {
                '200': {
                    'description': 'OK',
                    'content': {
                        'application/protobuf': {'schema': {'type': 'string'}},
                    },
                },
            },
        },
    }
    operations_openapi['/openapi/flatbuffer-and-protobuffer'] = {
        'post': {
            'description': 'generate flatbuffer and protobuffer logging',
            'requestBody': {
                'required': True,
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'additionalProperties': False,
                            'properties': {},
                        },
                    },
                },
            },
            'responses': {
                '200': {
                    'description': 'OK',
                    'content': {
                        'application/flatbuffer': {
                            'schema': {'type': 'string'},
                        },
                        'application/protobuf': {'schema': {'type': 'string'}},
                    },
                },
            },
        },
    }
    openapi['components']['schemas']['Param2'] = {'type': 'integer'}

    generate_services_and_libraries(
        default_repository,
        'test_handlers/test_non_utf8_logging',
        default_base,
    )


def test_oneof_with_discriminator(
        generate_services_and_libraries, default_repository, default_base,
):
    defs = default_repository[
        'services/test-service/docs/yaml/api/openapi.yaml'
    ]['components']['schemas']

    defs['SomeCardLikePayment'] = {
        'type': 'object',
        'additionalProperties': False,
        'properties': {
            'type': {'type': 'string'},
            'card-num': {'type': 'string'},
        },
        'required': ['type'],
    }
    defs['SomeApplePayPayment'] = {
        '$ref': '#/components/schemas/SomeCardLikePayment',
    }
    defs['SomeGooglePayPayment'] = {
        '$ref': '#/components/schemas/SomeCardLikePayment',
    }

    defs['SomePayment'] = {
        'oneOf': [
            {'$ref': '#/components/schemas/SomeCardLikePayment'},
            {'$ref': '#/components/schemas/SomeApplePayPayment'},
            {'$ref': '#/components/schemas/SomeGooglePayPayment'},
        ],
        'discriminator': {
            'propertyName': 'type',
            'mapping': {
                'card': '#/components/schemas/SomeCardLikePayment',
                'applepay': '#/components/schemas/SomeApplePayPayment',
                'googlepay': '#/components/schemas/SomeGooglePayPayment',
            },
        },
    }
    defs['SomeOtherPayment'] = {
        'oneOf': [
            {'$ref': '#/components/schemas/SomeCardLikePayment'},
            {'$ref': '#/components/schemas/SomeApplePayPayment'},
            {'$ref': '#/components/schemas/SomeGooglePayPayment'},
        ],
        'discriminator': {
            'propertyName': 'type',
            'mapping': {
                'card': '#/components/schemas/SomeCardLikePayment',
                'card_a': '#/components/schemas/SomeCardLikePayment',
                'card_b': '#/components/schemas/SomeCardLikePayment',
                'applepay': '#/components/schemas/SomeApplePayPayment',
                'googlepay': '#/components/schemas/SomeGooglePayPayment',
            },
        },
    }

    defs['OneOfEnumA'] = {
        'type': 'object',
        'additionalProperties': False,
        'properties': {
            'type': {'type': 'string', 'enum': ['type_a']},
            'field_a': {'type': 'integer'},
        },
        'required': ['type'],
    }

    defs['OneOfEnumBC'] = {
        'type': 'object',
        'additionalProperties': False,
        'properties': {
            'type': {'type': 'string', 'enum': ['type_b', 'type_c']},
            'field_bc': {'type': 'integer'},
        },
        'required': ['type'],
    }

    defs['OneOfEnum'] = {
        'oneOf': [
            {'$ref': '#/components/schemas/OneOfEnumA'},
            {'$ref': '#/components/schemas/OneOfEnumBC'},
        ],
        'discriminator': {
            'propertyName': 'type',
            'mapping': {
                'type_a': '#/components/schemas/OneOfEnumA',
                'type_b': '#/components/schemas/OneOfEnumBC',
                'type_c': '#/components/schemas/OneOfEnumBC',
            },
        },
    }

    generate_services_and_libraries(
        default_repository,
        'test_handlers/test_oneof_with_discriminator',
        default_base,
        sort_keys={'services/test-service/docs/yaml/api/openapi.yaml': False},
    )


def test_multiunit_client(
        generate_services_and_libraries,
        multi_unit_repository,
        multi_unit_base,
):
    service_yaml = multi_unit_repository['services/test-service/service.yaml']
    service_yaml['units'][0]['realm'] = 'bank'
    service_yaml['units'][1]['realm'] = 'taxi'

    service_yaml['handlers'] = {'multiunit-client': True}

    generate_services_and_libraries(
        multi_unit_repository,
        'test_handlers/multiunit_client',
        multi_unit_base,
    )
