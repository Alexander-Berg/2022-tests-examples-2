def test_recursive_schemas(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository[
        'services/test-service/js-pipeline/definitions.yaml'
    ] = (
        {
            'definitions': {
                'RecursiveResourceParams': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'self_ref': {'$ref': '#/definitions/SelfRef'},
                        'array_self_ref': {
                            '$ref': '#/definitions/ArraySelfRef',
                        },
                        'dict_self_ref': {'$ref': '#/definitions/DictSelfRef'},
                        'big_upstack_ref': {
                            '$ref': '#/definitions/BigUpstackRef',
                        },
                        'type_field': {'$ref': '#/definitions/TypeField'},
                    },
                },
                'SelfRef': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {'next': {'$ref': '#/definitions/SelfRef'}},
                },
                'ArraySelfRef': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'others': {
                            'type': 'array',
                            'items': {'$ref': '#/definitions/ArraySelfRef'},
                        },
                    },
                },
                'DictSelfRef': {
                    'type': 'object',
                    'additionalProperties': {
                        '$ref': '#/definitions/DictSelfRef',
                    },
                },
                'BigUpstackRef': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'field': {
                            'type': 'object',
                            'additionalProperties': False,
                            'properties': {
                                'others': {
                                    'type': 'array',
                                    'items': {
                                        '$ref': '#/definitions/BigUpstackRef',
                                    },
                                },
                            },
                        },
                    },
                },
                'TypeField': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'type': 'object',  # random property called type
                        'field': {
                            'type': 'object',
                            'additionalProperties': False,
                            'properties': {
                                'others': {
                                    'type': 'array',
                                    'items': {
                                        '$ref': '#/definitions/TypeField',
                                    },
                                },
                            },
                        },
                    },
                },
            },
        }
    )

    default_repository['services/test-service/js-pipeline/config.yaml'] = {
        'resources': [
            {
                'name': 'test_resource',
                'is_blocking_fetch': True,
                'params-schema': {
                    '$ref': (
                        'definitions.yaml#/definitions/RecursiveResourceParams'
                    ),
                },
            },
            {
                'name': 'test_typed_resource',
                'typed': True,
                'is_blocking_fetch': True,
                'params-schema': {
                    '$ref': (
                        'definitions.yaml#/definitions/RecursiveResourceParams'
                    ),
                },
            },
        ],
        'consumers': [{'name': 'test_consumer'}],
    }

    generate_services_and_libraries(
        default_repository, 'test_js_pipeline/recursive_schemas', default_base,
    )
