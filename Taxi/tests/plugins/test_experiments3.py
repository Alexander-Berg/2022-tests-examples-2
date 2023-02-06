import os


def test_experiments3(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository[
        os.path.join('services', 'test-service', 'service.yaml')
    ]['experiments3'] = (
        {
            'enabled': True,
            'enable_bulk_get_methods': True,
            'matching_logs': {
                'enabled': True,
                'disabled_for_configs': True,
                'only_for_consumers': ['consumer'],
            },
        }
    )

    path = os.path.join('services', 'test-service', 'experiments3')
    default_repository[
        os.path.join(path, 'kwargs_builders', 'with_consumer.yaml')
    ] = (
        {
            'consumer': 'consumer',
            'enable_app_support': True,
            'kwargs': [
                {
                    'name': 'field3',
                    'type': 'int',
                    'required': False,
                    'whitelisted': True,
                },
                {
                    'name': 'field1',
                    'type': 'string',
                    'required': True,
                    'whitelisted': False,
                },
                {
                    'name': 'field2',
                    'type': 'double',
                    'required': False,
                    'whitelisted': False,
                },
            ],
        }
    )
    default_repository[
        os.path.join(path, 'kwargs_builders', 'without_consumer.yaml')
    ] = (
        {
            'without_consumer_reason': 'test',
            'add_default_kwargs': False,
            'kwargs': [
                {
                    'name': 'f_int',
                    'type': 'int',
                    'required': True,
                    'whitelisted': True,
                },
                {
                    'name': 'f_string',
                    'type': 'string',
                    'required': False,
                    'whitelisted': True,
                },
                {
                    'name': 'f_set_int',
                    'type': 'set_int',
                    'required': True,
                    'whitelisted': False,
                },
                {
                    'name': 'f_set_string',
                    'type': 'set_string',
                    'required': False,
                    'whitelisted': False,
                },
                {
                    'name': 'f_timepoint',
                    'type': 'timepoint',
                    'required': True,
                    'whitelisted': True,
                },
                {
                    'name': 'f_double',
                    'type': 'double',
                    'required': False,
                    'whitelisted': True,
                },
                {
                    'name': 'f_bool',
                    'type': 'bool',
                    'required': True,
                    'whitelisted': False,
                },
                {
                    'name': 'f_application_version',
                    'type': 'application_version',
                    'required': False,
                    'whitelisted': False,
                },
                {
                    'name': 'f_application',
                    'type': 'application',
                    'required': True,
                    'whitelisted': True,
                },
                {
                    'name': 'f_point',
                    'type': 'point',
                    'required': False,
                    'whitelisted': True,
                },
            ],
        }
    )
    default_repository[
        os.path.join(path, 'declarations', 'test_experiment.yaml')
    ] = (
        {
            'name': 'test_experiment',
            'type': 'experiment',
            'value': {
                'schema': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {'int_value': {'type': 'integer'}},
                    'required': ['int_value'],
                },
            },
        }
    )
    default_repository[
        os.path.join(path, 'declarations', 'test_big_experiment.yaml')
    ] = (
        {
            'name': '_e:x:p-W_I_T_H-:-unusual---cHaRs228',
            'type': 'experiment',
            'value': {
                'schema': {
                    'description': 'Internal navi experiment',
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'is_enabled': {'type': 'boolean', 'default': False},
                        'page_id': {'type': 'string'},
                        'some_object': {
                            'type': 'object',
                            'additionalProperties': False,
                            'properties': {
                                'some_field': {
                                    'type': 'integer',
                                    'default': 42,
                                },
                            },
                        },
                        'some_array': {
                            'type': 'array',
                            'items': {
                                'type': 'string',
                                'enum': ['enum_value1', 'enum_value2'],
                            },
                        },
                    },
                    'required': ['some_array'],
                },
            },
        }
    )
    default_repository[
        os.path.join(path, 'declarations', 'test_one_of.yaml')
    ] = (
        {
            'name': 'test_one_of',
            'type': 'config',
            'value': {
                'schema': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'ticket_tags': {
                            'type': 'array',
                            'items': {'type': 'string'},
                        },
                        'ticket_schema': {
                            'type': 'array',
                            'items': {
                                'oneOf': [
                                    {
                                        'type': 'object',
                                        'additionalProperties': False,
                                        'properties': {
                                            'tag': {'type': 'string'},
                                            'name': {'type': 'string'},
                                            'ticket_param_name': {
                                                'type': 'string',
                                            },
                                        },
                                    },
                                    {
                                        'type': 'object',
                                        'additionalProperties': False,
                                        'properties': {
                                            'tag': {'type': 'boolean'},
                                            'name': {'type': 'string'},
                                            'ticket_param_name': {
                                                'type': 'string',
                                            },
                                        },
                                    },
                                ],
                            },
                        },
                    },
                },
            },
        }
    )

    default_repository[
        os.path.join(path, 'declarations', 'test_definitions.yaml')
    ] = (
        {
            'name': 'test_definitions',
            'type': 'union',
            'value': {
                'schema': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'some_int': {'$ref': '#/definitions/SomeInt'},
                        'some_obj': {'$ref': '#/definitions/SomeObj'},
                        'some_list': {'$ref': '#/definitions/SomeList'},
                    },
                    'definitions': {
                        'Ref': {'type': 'string', 'default': 'I am subref'},
                        'SomeInt': {'type': 'integer', 'default': 42},
                        'SomeObj': {
                            'type': 'object',
                            'required': ['sub'],
                            'properties': {
                                'sub': {'$ref': '#/definitions/Ref'},
                            },
                            'additionalProperties': False,
                        },
                        'SomeList': {
                            'type': 'array',
                            'items': {'$ref': '#/definitions/Ref'},
                        },
                    },
                },
            },
        }
    )
    default_repository[
        os.path.join(
            path, 'declarations', 'test_oneof_with_discriminator.yaml',
        )
    ] = (
        {
            'name': 'test_oneof_with_discriminator',
            'type': 'config',
            'value': {
                'schema': {
                    'additionalProperties': {
                        'additionalProperties': {
                            '$ref': '#/definitions/PrioritySettings',
                        },
                        'description': 'screen',
                        'type': 'object',
                    },
                    'definitions': {
                        'ByProviderCustomValue': {
                            'additionalProperties': {
                                '$ref': '#/definitions/DefaultCustomValue',
                            },
                            'type': 'object',
                        },
                        'ConstValue': {
                            'additionalProperties': False,
                            'properties': {
                                'type': {'enum': ['const'], 'type': 'string'},
                                'value': {'minimum': 0, 'type': 'integer'},
                            },
                            'required': ['type', 'value'],
                            'type': 'object',
                        },
                        'CustomValue': {
                            'additionalProperties': False,
                            'properties': {
                                'by_provider': {
                                    '$ref': (
                                        '#/definitions/ByProviderCustomValue'
                                    ),
                                },
                                'type': {'enum': ['value'], 'type': 'string'},
                            },
                            'required': ['type', 'by_provider'],
                            'type': 'object',
                        },
                        'DefaultCustomValue': {
                            'discriminator': {
                                'mapping': {
                                    'by_subtype': (
                                        '#/definitions/DefaultCustom'
                                        'ValueBySubType'
                                    ),
                                    'const': '#/definitions/ConstValue',
                                },
                                'propertyName': 'type',
                            },
                            'oneOf': [
                                {
                                    '$ref': (
                                        '#/definitions/DefaultCustom'
                                        'ValueBySubType'
                                    ),
                                },
                                {'$ref': '#/definitions/ConstValue'},
                            ],
                        },
                        'DefaultCustomValueBySubType': {
                            'additionalProperties': False,
                            'properties': {
                                'type': {
                                    'enum': ['by_subtype'],
                                    'type': 'string',
                                },
                                'value': {'$ref': '#/definitions/ValueMap'},
                            },
                            'required': ['type', 'value'],
                            'type': 'object',
                        },
                        'MultipliedHash': {
                            'additionalProperties': False,
                            'properties': {
                                'by_provider': {
                                    '$ref': '#/definitions/ValueMap',
                                },
                                'type': {
                                    'enum': ['mult_hash'],
                                    'type': 'string',
                                },
                            },
                            'required': ['type', 'by_provider'],
                            'type': 'object',
                        },
                        'PriorityItem': {
                            'additionalProperties': False,
                            'properties': {
                                'name': {'type': 'string'},
                                'payload': {
                                    'discriminator': {
                                        'mapping': {
                                            'mult_hash': (
                                                '#/definitions/MultipliedHash'
                                            ),
                                            'value': (
                                                '#/definitions/CustomValue'
                                            ),
                                        },
                                        'propertyName': 'type',
                                    },
                                    'oneOf': [
                                        {
                                            '$ref': (
                                                '#/definitions/MultipliedHash'
                                            ),
                                        },
                                        {'$ref': '#/definitions/CustomValue'},
                                    ],
                                },
                            },
                            'required': ['payload', 'name'],
                            'type': 'object',
                        },
                        'PrioritySettings': {
                            'additionalProperties': False,
                            'description': (
                                'Тут '
                                'задаем '
                                'содержимое '
                                'кортежа '
                                'приоритетов '
                                'и '
                                'конкретные '
                                'значение '
                                'для '
                                'провайдеров\n'
                            ),
                            'properties': {
                                'priorities_tuple': {
                                    'items': {
                                        '$ref': '#/definitions/PriorityItem',
                                    },
                                    'type': 'array',
                                },
                            },
                            'required': ['priorities_tuple'],
                            'type': 'object',
                        },
                        'ValueMap': {
                            'additionalProperties': {
                                'minimum': 0,
                                'type': 'integer',
                                'x-taxi-cpp-type': 'std::size_t',
                            },
                            'type': 'object',
                        },
                    },
                    'description': 'mode',
                    'type': 'object',
                },
            },
        }
    )

    generate_services_and_libraries(
        default_repository,
        os.path.join('test_experiments3', 'test'),
        default_base,
    )


def test_experiments3_in_lib(
        generate_services_and_libraries, default_repository, default_base,
):
    lib_path = os.path.join('libraries', 'test-lib')
    service_path = os.path.join('services', 'test-service')
    default_repository[os.path.join(lib_path, 'library.yaml')] = {
        'project-name': 'yandex-taxi-library-test-lib',
        'description': 'just for test',
        'maintainers': ['axolm'],
        'experiments3': {'enabled': True},
    }

    plugin_dir = os.path.join(lib_path, 'experiments3')

    default_repository[
        os.path.join(plugin_dir, 'kwargs_builders', 'test.yaml')
    ] = (
        {
            'consumer': 'consumer_from_lib',
            'kwargs': [
                {
                    'name': 'name',
                    'type': 'string',
                    'required': True,
                    'whitelisted': True,
                },
            ],
        }
    )
    default_repository[
        os.path.join(plugin_dir, 'declarations', 'test_exp.yaml')
    ] = (
        {
            'name': 'test_exp',
            'type': 'experiment',
            'value': {'schema': {'type': 'integer'}},
        }
    )

    default_repository[os.path.join(service_path, 'service.yaml')][
        'libraries'
    ] = ['yandex-taxi-library-test-lib']
    default_repository[os.path.join(service_path, 'service.yaml')][
        'experiments3'
    ] = (
        {
            'enabled': True,
            'enable_bulk_get_methods': True,
            'matching_logs': {'enabled': False, 'log_level': 'warning'},
        }
    )

    default_repository[
        os.path.join(plugin_dir, 'shared_kwargs', 'common_kwargs.yaml')
    ] = {'kwargs': [{'name': 'common_kwarg', 'type': 'int'}]}

    default_repository[
        os.path.join(
            service_path,
            'experiments3',
            'kwargs_builders',
            'with_library_include.yaml',
        )
    ] = (
        {
            'consumer': 'consumer_from_service',
            'kwargs': [{'name': 'unique_kwarg', 'type': 'int'}],
            'include_kwargs': [
                {
                    'path': (
                        'libraries/test-lib/experiments3/'
                        'shared_kwargs/common_kwargs.yaml'
                    ),
                },
            ],
        }
    )

    generate_services_and_libraries(
        default_repository,
        os.path.join('test_experiments3', 'test_libs'),
        default_base,
    )
